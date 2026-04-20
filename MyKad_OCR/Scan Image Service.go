package repository

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"strings"

	"sentec.io/pms/models"
	"sentec.io/pms/modules/id_card_scanner/model"
	"sentec.io/pms/utils/retry"
)

// Sends image-based text content for OpenAI analysis
func (o *OpenAIRepository) ScanImage(imageUrl string) (model.CardDetails, error) {
	var card model.CardDetails
	card.CardNumber = ""
	requestBody := model.OpenAIRequest{
		Model: "gpt-4.1-nano",
		Messages: []model.Message{
			{
				Role: "user",
				Content: []model.Content{
					{Type: "text", Text: BasePrompt},
					{Type: "image_url", ImageUrl: model.ImageUrl{Url: imageUrl}},
				},
			},
		},
		MaxToken: 300,
	}

	body, _ := json.Marshal(requestBody)
	req, err := http.NewRequest("POST", "https://api.openai.com/v1/chat/completions", bytes.NewBuffer(body))
	if err != nil {
		return card, err
	}
	apiKey := o.Services.Config.OpenAIKey
	req.Header.Set("Authorization", "Bearer "+apiKey)
	req.Header.Set("Content-Type", "application/json")

	response, err := retry.Do(func() (apiResponse, error) {
		response := apiResponse{}
		client := &http.Client{}
		resp, err := client.Do(req)
		if err != nil {
			return response, err
		}
		defer resp.Body.Close()

		response.StatusCode = resp.StatusCode
		response.Body, err = io.ReadAll(resp.Body)
		if resp.StatusCode != 200 {
			err = fmt.Errorf("status code %d (%s)", resp.StatusCode, string(response.Body))
		}
		return response, err
	}, retry.RetrySettings{MaxRetry: 10, UseExponentialBackoff: true,
		MillisecondsPerSlot: 100, JitterFactor: 0.2, MaxSlotsWhenTruncated: 10})
	if err != nil {
		return card, err
	}

	var openAIResponse model.OpenAIResponse
	if err := json.Unmarshal(response.Body, &openAIResponse); err != nil {
		return card, err
	}

	if len(openAIResponse.Choices) > 0 {
		result := openAIResponse.Choices[0].Message.Content
		cleanedJSON := result[8 : len(result)-4] // Remove the ```json\n and \n``` parts
		err = json.Unmarshal([]byte(cleanedJSON), &card)
		if err != nil {
			// just ignore and log the error
			o.Services.Log.Error(fmt.Sprintf("error openai parsing : %+v", err.Error()))
		}
		// log the resulting object
		o.Services.Log.Info(fmt.Sprintf("Card Details: %+v", card))
		//find nationality and country
		// Prepare codes
		nationalityCode := strings.ToLower(strings.TrimSpace(card.NationalityCode))
		countryCode := strings.ToLower(strings.TrimSpace(card.CountryCode))

		var codes []string
		if nationalityCode != "" {
			codes = append(codes, nationalityCode)
		}
		if countryCode != "" && countryCode != nationalityCode {
			codes = append(codes, countryCode)
		}

		if len(codes) > 0 {
			// Build query using only the non-empty codes
			placeholders := "'" + strings.Join(codes, "', '") + "'"
			query := fmt.Sprintf(
				`select * from country where lower(iso2code) IN (%s)`,
				placeholders,
			)
			var countries []models.Country

			err = o.Services.Db.Query(query, &countries)
			if err != nil {
				return card, err
			}
			// Map results
			for _, country := range countries {
				iso := strings.ToLower(strings.TrimSpace(country.ISO2Code))
				if iso == nationalityCode {
					card.NationalityCode = country.ISO2Code
				}
				if iso == countryCode {
					card.CountryCode = country.ISO2Code
				}
			}
		}
	} else {
		err = fmt.Errorf("no response from OpenAI")
		rawResponse, err := json.Marshal(openAIResponse)
		if err != nil {
			// just ignore and log the error
			o.Services.Log.Error(fmt.Sprintf("error openai parsing : %+v", err.Error()))
		}
		o.Services.Log.Error(string(rawResponse))
		return card, err
	}
	if len(card.FieldError) > 0 {
		return card, errors.New(card.FieldError)
	}
	return card, err
}

type apiResponse struct {
	StatusCode int
	Body       []byte
}

func (a *apiResponse) setResponseCode(code int) error {
	a.StatusCode = code
	switch code {
	case 200:
		return nil
	default:
		return fmt.Errorf("status code %d", code)
	}
}
