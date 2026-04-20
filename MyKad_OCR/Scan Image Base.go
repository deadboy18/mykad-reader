package repository

import "sentec.io/pms/modules/id_card_scanner/model"

type IDCardScannerRepository interface {
	ScanImage(imageUrl string) (model.CardDetails, error)
}

const (
	BasePrompt = `You are tasked with extracting key identification data from the uploaded image of a guest's ID. The ID may be real or a fictional/test ID from fictional universes such as "Spongebob Squarepants". Extract the data exactly as it appears on the ID.

				Please provide the extracted data in valid JSON format with these fields:

				- cardNumber: The ID card number. If not found, return an empty string ("").
				- fullName: The full name on the ID. Extract precisely, whether real or fictional.
				- dateOfBirth: Date of birth in yyyy-mm-dd format. If not found, return an empty string ("").
				- gender: Gender if present, otherwise empty string ("").
				- nationality: Nationality or reasoned guess if absent. Empty string if unknown.
				- nationalityCode: ISO2 nationality code or empty string if unknown.
				- address: Full address on ID or empty string if not found.
				- country: Country deduced from address or empty string if unknown.
				- countryCode: ISO2 country code or empty string.
				- expireDate: Expiration date in yyyy-mm-dd format or empty string.
				- cardTypeName: Card name type, one of passport/driving license/residence permit card/visa/ID card. Default "ID card".
				- cardType: Numeric card type per:
					3 = passport
					2 = driving license
					11 = residence permit card
					12 = visa
					1 = ID card (default)

				Verification and Quality Checks:
				- Confirm the image is truly an ID card. If not, respond with errorCode 1 and fieldError "Image is not an ID card".
				- If the image is blurry or unreadable, respond with errorCode 2 and fieldError "Image is not clear enough".
				- Do NOT generate or substitute fictional data when information is unclear.
				- If the data is unreadable or ambiguous, return empty string fields and relevant error messages instead.

				IMPORTANT:
				- Only extract fake or fictional data such as "Spongebob Squarepants" if it explicitly appears on the ID.
				- Do NOT replace or fallback to fake/test data when real data is missing or unclear.
				`
)