# MyKad OCR & Vision Research — Complete Physical & Technical Reference
**Version:** 1.0 | **Date:** April 2026 | **Author:** Kesh (deadboy18)
**Repo:** https://github.com/deadboy18/mykad-reader

> This document is LLM-optimised: plain markdown, no binary content, all tables in pipe format, all code in fenced blocks. Paste or upload directly to any AI tool, model, or developer platform. It contains everything needed for a developer from any country to understand the MyKad system, its physical security features, manufacturing process, chip architecture, and why OCR fails on this card.

---

# 1. Executive Summary

This document is the definitive technical reference for the Malaysian National Identity Card (MyKad) system, covering physical specifications, security features, manufacturing process, chip architecture, IC number format, and OCR/Vision feasibility analysis. It is written for developers from any country who need to understand how the MyKad works at every level — from the polycarbonate layers and laser engraving to the APDU commands that read data from the smart card chip.

**Bottom Line on OCR:** Free OCR engines (Tesseract, PaddleOCR, EasyOCR) cannot reliably read MyKad text. Vision LLM APIs (GPT-4.1-nano) achieve 98–100% accuracy. USB chip readers achieve 100% accuracy offline.

---

# 2. Card Overview & History

## 2.1 What is MyKad

MyKad (Malaysia Kad) is the compulsory national identity card issued by Jabatan Pendaftaran Negara (JPN — National Registration Department) to all Malaysian citizens aged 12 and above. Introduced on 5 September 2001, it replaced the High Quality Identity Card (Kad Pengenalan Bermutu Tinggi).

Malaysia was the first country in the world to use an identification card incorporating both photo identification and fingerprint biometric data on an embedded computer chip. The technology was developed by IRIS Corporation Berhad, a Malaysian company that also invented the world's first ePassport in 1998.

**Sources:**
- Wikipedia: Malaysian identity card — [https://en.wikipedia.org/wiki/Malaysian_identity_card](https://en.wikipedia.org/wiki/Malaysian_identity_card)
- IRIS Corporation Berhad — [https://www.iris.com.my/](https://www.iris.com.my/)
- Malaysia Government Portal — [https://www.malaysia.gov.my/en/categories/personal-identification/identification-card](https://www.malaysia.gov.my/en/categories/personal-identification/identification-card)


[Image: MyKad Evolution]

*Figure 4: Evolusi Kad Pengenalan — Evolution of Malaysian Identity Cards (Source: JPN Official)*

## 2.2 Evolution of Malaysian Identity Cards

The Malaysian identity card system has evolved through multiple generations:

| Year | Card Name | Region | Notes |
|------|-----------|--------|-------|
| 1948 | Kad Pengenalan (Kertas) | Tanah Melayu (Peninsular) | Paper card, known as the "Rice Card", issued to curb communist threat |
| 1949 | Kad Pengenalan (Kertas Berlipat) | Sarawak | Folded paper card |
| 1960 | Kad Pengenalan (Plastik) | Semenanjung Malaysia | First plastic card for Peninsular Malaysia |
| 1960 | Kad Pengenalan (Bersalut) | Sarawak | Coated card |
| 1963–1972 | Kad Pengenalan (Oren) | Sabah | Orange card, 6-digit number |
| 1966 | Kad Pengenalan (Plastik) | Sarawak | Plastic card |
| 1972 | Kad Pengenalan Plastik (Biru) | Sabah | Blue plastic card, 7-digit number |
| 1990 | Kad Pengenalan Bermutu Tinggi | All Malaysia | High Quality Identity Card, introduced 12-digit IC format (YYMMDD-PB-####) |
| 1999 | Kad Pengenalan Bermutu Tinggi (Updated) | All Malaysia | Updated security features |
| 2001 | MyKad (Kad Pengenalan Pelbagaiguna Kerajaan) | All Malaysia | Government Multi-Purpose Card, 32KB chip, contact-only |
| 2002 | MyKad (64KB) | All Malaysia | Chip upgraded to 64KB, thumbprint data added |
| 2012 | MyKad Struktur Baru | All Malaysia | New structure, 80KB chip, hybrid contact+contactless (TnG) |
| 2026 (planned) | Next-Gen MyKad | All Malaysia | QR code feature, enhanced security, polycarbonate with laser engraving and hologram |

**Source:** JPN Official — Evolusi Kad Pengenalan infographic (Jabatan Pendaftaran Negara, Kementerian Dalam Negeri)
**Source:** Lowyat.NET — [https://www.lowyat.net/2025/374652/malaysia-next-gen-mykad-qr-code-feature/](https://www.lowyat.net/2025/374652/malaysia-next-gen-mykad-qr-code-feature/)
**Source:** iLoveBorneo — [https://www.iloveborneo.my/mykad-lama-bakal-digantikan-ketahui-ciri-ciri-kad-pengenalan-baharu/](https://www.iloveborneo.my/mykad-lama-bakal-digantikan-ketahui-ciri-ciri-kad-pengenalan-baharu/)

## 2.3 Card Variants by Colour

| Card | Issued To | Colour | Hex (Approx.) | Malay Label |
|------|-----------|--------|---------------|-------------|
| MyKad | Citizens aged 12+ | Blue | #0032A0 | KAD PENGENALAN MALAYSIA |
| MyKid | Citizens under 12 | Pink | #E91E63 | KAD PENGENALAN MALAYSIA (KANAK-KANAK) |
| MyPR | Permanent residents | Red | #CC0000 | KAD PENGENALAN MALAYSIA PEMASTAUTIN TETAP |
| MyKAS | Temporary residents | Green | #008000 | KAD PENGENALAN SEMENTARA |
| MyTentera | Military personnel | Silver | #C0C0C0 | Armed Forces logo, replacing BAT C 10 form |
| MyPolis | Police personnel | Varies | — | Police variant |

**Source:** ClearTax Malaysia — [https://www.cleartax.com/my/en/mykad-malaysia](https://www.cleartax.com/my/en/mykad-malaysia)

---

# 3. Physical Card Specifications

## 3.1 Dimensions & Material

| Property | Value |
|----------|-------|
| Card Standard | ID-1 (ISO/IEC 7810) — same as a standard credit card |
| Width | 85.6 mm (3.370 inches) |
| Height | 53.98 mm (2.125 inches) |
| Thickness | 0.76 mm (0.030 inches) |
| Corner Radius | 3.18 mm (standard ID-1) |
| Material | Polycarbonate (PC) — NOT PVC |
| Weight | ~5–6 grams |
| Primary Colour | MyKad Blue (#0032A0 approximate) |
| Orientation | Landscape (wider than tall) |
| Lifespan | 10 years (card body), 20 years (chip data retention) |
| Testing Standard | ISO 10373 |

**Source:** CardLogix — [https://www.cardlogix.com/product/id-grade-polycarbonate-card-cr80-30-mil-laser-engravable/](https://www.cardlogix.com/product/id-grade-polycarbonate-card-cr80-30-mil-laser-engravable/)
**Source:** Datasonic/APCS — [https://www.apcscard.com/polycarbonate-card-laser-engrave-coated-overlay/](https://www.apcscard.com/polycarbonate-card-laser-engrave-coated-overlay/)

## 3.2 Why Polycarbonate, Not PVC

Polycarbonate is chosen over PVC for several critical reasons: it is the same material used for bulletproof glass and CDs. Multiple polycarbonate layers fuse together under heat and pressure into a "monolithic block" — the layers cannot be separated without destroying the card. This makes photo swapping or data tampering physically impossible without visible damage. PVC cards (like credit cards) use adhesive lamination which can be peeled apart.

**Source:** DSS Plastics / PolycarbonateCard.com — [https://www.polycarbonatecard.com/more/](https://www.polycarbonatecard.com/more/)

## 3.3 Embedded Chips

### Contact Chip (Identity Data)
| Property | Value |
|----------|-------|
| Standard | ISO 7816 |
| Type | Contact smart card |
| Location | BACK of card, lower-right quadrant |
| Visible As | Gold contact pad with 8 pins |
| EEPROM | 80KB (current), was 32KB (2001), then 64KB (2002) |
| Operating System | M-COS (MyKad Chip Operating System), proprietary to IRIS Corporation |
| Access | Reading: no PIN required. Writing: requires JPN Perso Card + Triple-DES key |

### Contact Chip Data Contents
| Data Field | Approximate Size | Notes |
|------------|-----------------|-------|
| IC Number | 12 bytes | Stored as ASCII digits, no dashes |
| Full Name | Up to 80 bytes | UTF-8 encoded |
| Date of Birth | 8 bytes | YYYYMMDD format |
| Gender | 1 byte | M or F |
| Race | Variable | Malay encoding |
| Religion | Variable | Malay encoding |
| Nationality | Variable | WARGANEGARA or PENDUDUK TETAP |
| Address | ~200 bytes | 3 lines + postcode + city + state |
| JPEG Photo | ~15KB | Stored in 4000-byte allocation, ~200×250 pixels |
| Fingerprint (Right Thumb) | ~500 bytes | IRIS Corp proprietary format (NOT NIST/ISO minutiae) |
| Fingerprint (Left Thumb) | ~500 bytes | Same proprietary format |
| SOCSO/PERKESO Number | Variable | Social security reference |
| JPJ Driving Licence | Separate application | On same chip, different file |
| Immigration Data | Separate application | Passport references |
| PKI Digital Certificates | Optional | Can store 2 certificates from MSCTrustgate or DigiCert |

### Contactless Chip (Touch 'n Go)
| Property | Value |
|----------|-------|
| Standard | ISO 14443-3A |
| Type | Mifare Classic 1K |
| Location | Embedded inside card body (not visible) |
| Sectors | 16 sectors, each with proprietary sector keys |
| Access | Keys held by Touch 'n Go Sdn Bhd — unauthorised readers cannot access |
| Data | E-wallet stored value and transaction history ONLY — no personal identity data |
| NFC Readable | Detectable by NFC readers (ACR122U etc.) but data inaccessible without keys |

### Can the Chip Data Be Modified?
**Contact chip:** NO — not by the public. Reading requires only a PC/SC reader and standard APDU commands (documented in MyKad_Complete_Technical_Reference_v3_LLM.md). Writing requires: (1) a JPN Personalisation Card (a special operator smart card), (2) Triple-DES authentication keys stored in Hardware Security Modules (HSMs) at JPN/IRIS Corporation facilities. Without both, all write commands are rejected by the chip's access control system.

**Contactless TnG chip:** Only by authorised Touch 'n Go terminals. The Mifare Classic 1K sector keys are proprietary. While Mifare Classic has known cryptographic weaknesses (Crypto-1 has been broken by academic researchers), exploiting this on a production MyKad would be illegal under Malaysian law.

**Source:** IRIS Corporation — [https://www.iris.com.my/smart-card-solution/](https://www.iris.com.my/smart-card-solution/)
**Source:** Innov8tif — [https://innov8tif.com/3-methods-to-read-mykad-2/](https://innov8tif.com/3-methods-to-read-mykad-2/)

---


[Image: MyKad Structure Diagram]

*Figure 1: Malaysia MyKad Structure (Source: The Rakyat Post)*

[Image: MyKad Front Layout]

*Figure 2: MyKad Front Face Element Map*

# 4. Front Face — Detailed Element Map

All positions are described as percentages of total card width (W=85.6mm) and height (H=53.98mm), measured from the top-left corner. This mapping is essential for OCR region detection and YOLO training.

## 4.1 Header Region (Top 0–18% H)

| Element | Position | Details |
|---------|----------|---------|
| "KAD PENGENALAN" | Top-left, 5–40% W, 0–6% H | White/silver text, small font, serif-like |
| "MALAYSIA" | Below KAD PENGENALAN, 5–40% W, 5–12% H | LARGEST header text, white/silver, all caps |
| "IDENTITY CARD" | Below MALAYSIA, 5–40% W, 10–15% H | Smaller English text |
| Jata Negara (Coat of Arms) | Centre, ~42–55% W, 0–15% H | Small printed emblem, ~8mm wide |
| "MyKad" Logo | Right of centre, ~58–75% W, 2–12% H | Stylised script font with MSC Malaysia branding |
| Malaysian Flag | Top-right, ~78–95% W, 2–12% H | Jalur Gemilang, small printed flag |

## 4.2 Personal Data Region (18–95% H)

| Element | Position | Details |
|---------|----------|---------|
| IC Number | 18–32% H, 15–65% W | LARGEST TEXT ON CARD. Format: YYMMDD-PB-####. Laser-engraved monospaced font. This is the primary OCR target and the hardest to read due to laser engraving over guilloche. |
| Contact Chip Pad | 25–65% H, 3–22% W | Gold ISO 7816 contact pad. 8-pin layout. Positioned on the LEFT side of the card front. |
| Ghost Image (Secondary) | 25–65% H, ~45–65% W | Small, translucent laser-engraved portrait of the holder. Semi-transparent, overlaid on the guilloche pattern. Serves as anti-tampering feature — must match the main photo. |
| Main Photo | 20–80% H, 65–95% W | Colour photograph, ~25×32mm. Blue background. Positioned on the RIGHT side. Printed under polycarbonate overlay. No guilloche behind the photo area. |
| Full Name | 55–68% H, 3–55% W | ALL UPPERCASE. Laser-engraved. May include BIN/BINTI (Malay), A/L/A/P (Indian), or @ (alias). |
| Address | 68–90% H, 3–55% W | 1–3 lines, printed (not engraved), smaller font. Includes street, postcode (5 digits), city, state. ALL UPPERCASE. |
| Nationality | 85–95% H, 50–75% W | "WARGANEGARA" (Citizen) or "PENDUDUK TETAP" (PR) |
| Religion | Below nationality | ISLAM / KRISTIAN / BUDDHA / HINDU / SIKH / TIADA AGAMA |
| Gender | 85–95% H, 75–95% W | LELAKI (Male) / PEREMPUAN (Female) |
| Hibiscus Watermark | Bottom-right corner, ~90–98% W, 85–98% H | Small "K" or hibiscus flower symbol (Bunga Raya — national flower) |

## 4.3 Photo Specifications (JPN Requirements)
| Property | Value |
|----------|-------|
| Size on card | ~25mm × 32mm |
| Background | Blue (#0066CC approximate) |
| Face position | Centred, 70–80% of frame height |
| Resolution on chip | ~200 × 250 pixels, JPEG, ~15KB |
| Taken at | JPN counter with standardised camera setup |

**Source:** The Rakyat Post — MyKad Structure infographic (www.therakyatpost.com)
**Source:** CTOS eKYC — [https://ctoscredit.com.my/business/evaluate-new-customer/ctos-ekyc/document-id-holder-verification/](https://ctoscredit.com.my/business/evaluate-new-customer/ctos-ekyc/document-id-holder-verification/)

---

# 5. Back Face — Element Map

| Element | Position | Details |
|---------|----------|---------|
| Ghost Image (Large) | Upper-centre, 5–45% H | Laser-engraved monochrome portrait, larger than front ghost |
| "KETUA PENGARAH PENDAFTARAN NEGARA" | Centre, 45–55% H | Director General title with printed signature (not personalised) |
| IC Number (Repeated) | Centre, 55–65% H | Same YYMMDD-PB-#### format, printed (NOT laser-engraved on back), easier to read optically |
| 80K Chip Pad | Lower-right, 65–90% H, 75–95% W | Gold ISO 7816 contact pad, labelled "80K chip" |
| Serial Number | Bottom edge, 90–98% H | Small printed manufacturing serial (e.g., "D1024NF513"), NOT the IC number |
| Card Count | After IC number | 2-digit suffix indicating how many MyKads the person has held |

---


[Image: MyKad Security Features]

*Figure 3: MyKad Security Features Overview (Reference: Jabatan Pendaftaran Negara)*

# 6. Security Features — Technical Analysis

## 6.1 Laser Engraving
- **Location:** IC number, name, ghost image (front), ghost image (back)
- **Technology:** Ytterbium fibre-doped laser, up to 1200 DPI resolution
- **Process:** Laser beam causes carbonisation of the polycarbonate polymer at the focal point, creating darkened marks INSIDE the card body (not on the surface)
- **OCR Impact:** CRITICAL — variable reflectivity depending on viewing angle and lighting direction. The same digit appears differently in every photo.
- **Source:** IAI Industrial Systems — [https://www.iai.nl/personalisation-experts/personalisation-technologies/laser-engraving/](https://www.iai.nl/personalisation-experts/personalisation-technologies/laser-engraving/)
- **Source:** CampusIDNews — [https://www.campusidnews.com/laser-engraving-ids-catching-on/](https://www.campusidnews.com/laser-engraving-ids-catching-on/)
- **Source:** Identis Group — [https://identisgroup.com/newsroom/2018/03/laser-personalization-for-high-security-id-cards/](https://identisgroup.com/newsroom/2018/03/laser-personalization-for-high-security-id-cards/)

## 6.2 Guilloche Pattern
- **Location:** Entire card surface (both sides), except photo area
- **Description:** Mathematically-generated interlocking curved lines (hypotrochoid/spirograph pattern)
- **Line width:** ~0.1mm, visible under magnification
- **Generation:** Requires specialised security design software with complex mathematical parameters. The exact parameters are secret.
- **OCR Impact:** SEVERE — OCR engines interpret fine lines as text fragments
- **Source:** Ben Hodosi (Security Document Designer) — [https://benhodosi.com/](https://benhodosi.com/)
- **Source:** SZIMAGETECH — [https://szimagetech.com/explore-comprehensive-id-card-security-features/](https://szimagetech.com/explore-comprehensive-id-card-security-features/)

## 6.3 Rainbow Printing (Iris/Split-Fountain)
- **Location:** Card background, most visible at edges
- **Process:** Offset printing with two colours loaded in the same ink fountain with gradient blend
- **Visual effect:** Colour shifts from red to purple when card is tilted
- **OCR Impact:** MODERATE — breaks colour-based binarisation

## 6.4 Holographic Overlay (DOVID)
- **Location:** Transparent overlay across front face
- **Type:** Diffractive Optically Variable Image Device (DOVID)
- **Structure:** Nano-scale diffractive gratings embossed into thin film, metallised with aluminium via vacuum deposition
- **Visual effects:** Rainbow diffractive colours, dynamic images that change with viewing angle
- **OCR Impact:** SEVERE — creates moving specular reflections (glare)
- **Source:** OVD Kinegram — [https://www.kinegram.com/events-insights/details/what-is-secure-hologram-technology](https://www.kinegram.com/events-insights/details/what-is-secure-hologram-technology)
- **Source:** Wikipedia (DOVID) — [https://en.wikipedia.org/wiki/Diffractive_optically_variable_image_device](https://en.wikipedia.org/wiki/Diffractive_optically_variable_image_device)

## 6.5 UV Fluorescent Printing
- **Location:** Various positions across card
- **Technology:** Special fluorescent compounds in ink that react to ultraviolet (365nm) light
- **Visible under:** UV/black light only — invisible under normal lighting
- **OCR Impact:** None under normal lighting
- **Source:** Troy Group — [https://www.troygroup.com/blog/uv-ink-for-security](https://www.troygroup.com/blog/uv-ink-for-security)

## 6.6 Anti-Copy Protection
- **Features:** Micro-printing (<0.5mm characters), moiré interference patterns, fine-line structures
- **Effect:** Photocopies and scans show visible degradation artifacts
- **Source:** ID Management — [https://www.idmanagement.com/card-security](https://www.idmanagement.com/card-security)

## 6.7 Hibiscus Watermark
- **Location:** Bottom-right corner of front face
- **Description:** Small printed Bunga Raya (hibiscus — Malaysian national flower) symbol or letter "K"

---

# 7. Manufacturing Process — Step by Step

## 7.1 Card Body Production (Factory — IRIS Corporation / Datasonic)

**Step 1: Polycarbonate Sheet Preparation**
Multiple layers of polycarbonate film (~0.076mm per layer) are prepared. Each layer serves a specific purpose: core layers for structural integrity, print-receiving layers for offset artwork, and laser-sensitive layers containing polymer that carbonises when hit by a laser beam.

**Step 2: Offset Printing**
The guilloche pattern, rainbow gradient, UV fluorescent elements, fixed text ("KAD PENGENALAN MALAYSIA / IDENTITY CARD"), MyKad logo, Malaysian flag, and coat of arms are printed onto inner polycarbonate layers using offset lithography at 2400+ DPI. This is done in bulk — thousands of card sheets at once.

**Step 3: Chip Embedding**
The ISO 7816 contact chip module (80KB EEPROM with M-COS operating system) and the Mifare Classic 1K contactless antenna/chip are placed between polycarbonate layers at precise positions. The contact chip goes to the front-left position, the contactless antenna is embedded throughout the card body.

**Step 4: Lamination (Fusion)**
All polycarbonate layers are fused together under high heat (~180°C) and pressure in an industrial lamination press. No adhesives are used — the polycarbonate layers molecularly bond into a single monolithic block. This is the key security step: the layers CANNOT be separated without destroying the card.

**Step 5: Die Cutting**
Individual cards are precision-cut from the laminated sheet to ID-1 dimensions (85.6 × 53.98mm) with 3.18mm corner radius.

**Step 6: DOVID Application**
The holographic overlay (DOVID) is heat-sealed or transferred onto the card surface. This is a thin film (<10 microns) containing nano-scale diffractive structures.

**Result:** A blank card body with all security printing, chips, and hologram — ready for personalisation.

## 7.2 Personalisation (At JPN Counter or Regional Centre)

**Step 7: Enrolment**
At the JPN counter, the officer captures: digital photo (against blue background), both thumbprints (via biometric scanner), and verifies/enters personal data into the JPN system.

**Step 8: Laser Personalisation (~30–60 seconds)**
The blank card body is loaded into a laser engraving machine. A Ytterbium fibre laser engraves: IC number (front, large), full name (front), passport photo (front, greyscale laser image), ghost image (front, semi-transparent), and ghost image (back, monochrome). The laser operates at different power levels to produce 256 greyscales for the photographic images.

**Step 9: Chip Personalisation**
Via APDU commands authenticated by the JPN Perso Card + Triple-DES keys: personal identity data, JPEG photo (~15KB), fingerprint templates, residential address, and SOCSO number are written to the contact chip. The TnG contactless chip is initialised if applicable.

**Step 10: Quality Control**
Automated optical inspection verifies laser engraving quality. Chip read-back verifies all data was written correctly. Card is tested against ISO 10373 standards.

**Step 11: Delivery**
Card is handed to the applicant at the counter (for walk-in applications) or mailed to the registered address.

**Equipment at JPN:**
- Laser engraving system (Ytterbium fibre laser, ~$50,000–$100,000+)
- Contact smart card reader/writer with Perso Card slot
- Biometric fingerprint scanner (FBI-certified)
- Digital camera with blue background
- JPN personalisation software connected to central database

---

# 8. What It Would Take to Counterfeit a MyKad

This section is included for security awareness — understanding the barriers helps developers appreciate why the card's physical security is effective.

| Component | Equipment Needed | Approximate Cost | Availability |
|-----------|-----------------|------------------|--------------|
| Polycarbonate card stock (ID-grade, multi-layer) | Specialist supplier | RM50–200 per sheet | Controlled — tracked by suppliers |
| Offset printing (guilloche, UV, rainbow) | Offset lithography press, 2400+ DPI | RM500,000+ | Available but requires guilloche design codes |
| Chip module (80KB EEPROM, M-COS) | IRIS Corporation proprietary | NOT AVAILABLE | M-COS is proprietary, not sold publicly |
| Mifare Classic 1K | Commercial supplier | RM2–5 per chip | Available, but sector keys are TnG proprietary |
| Lamination press (polycarbonate fusion) | Industrial lamination press, 180°C | RM1,000,000+ | Available from industrial suppliers |
| Holographic overlay (DOVID) | Hologram origination + replication | RM50,000+ (origination) + RM1+/card | 10–12 weeks lead time, custom design |
| Laser engraving system | Ytterbium fibre laser, 1200 DPI | RM200,000–450,000 | Available but controlled |
| Chip personalisation | JPN Perso Card + Triple-DES keys | NOT AVAILABLE | Keys stored in HSMs at JPN/IRIS only |
| Total minimum investment | All above | RM2,000,000+ | Multiple items are NOT publicly available |

**Key barriers:**
1. The M-COS chip operating system is proprietary to IRIS Corporation — you cannot buy it
2. The JPN Perso Card and Triple-DES keys are held exclusively by JPN — you cannot obtain them
3. Even with all equipment, the guilloche mathematical parameters are secret
4. Any card reader running official IRIS SDK will detect a counterfeit chip immediately
5. Attempting to counterfeit a MyKad is a serious criminal offence under Malaysian law

---

# 9. Next-Generation MyKad (2026)

Malaysia's Deputy Home Minister, Datuk Seri Dr. Shamsul Anuar Nasarah, announced that new MyKad cards will begin issuance from June 2026. Key changes:

- **QR Code:** A dedicated QR code for digital on-the-spot authentication by authorities
- **Enhanced laser engraving and hologram** features
- **Polycarbonate construction** (continuing from current generation)
- **Larger chip capacity** and higher security standards
- **Biometric data expansion** — potentially additional biometric modalities beyond thumbprints
- All functions of the old MyKad will be discontinued once the new generation is fully rolled out

The new supply contract also covers updated versions of MyTentera (Armed Forces) and MyPoCA (ex-convict) cards.

**Source:** Lowyat.NET (27 Nov 2025) — [https://www.lowyat.net/2025/374652/malaysia-next-gen-mykad-qr-code-feature/](https://www.lowyat.net/2025/374652/malaysia-next-gen-mykad-qr-code-feature/)
**Source:** iLoveBorneo (20 Nov 2024) — [https://www.iloveborneo.my/mykad-lama-bakal-digantikan-ketahui-ciri-ciri-kad-pengenalan-baharu/](https://www.iloveborneo.my/mykad-lama-bakal-digantikan-ketahui-ciri-ciri-kad-pengenalan-baharu/)

---

# 10. OCR & Vision Feasibility — Test Results

## 10.1 Approaches Tested

| Approach | IC Accuracy | Name Accuracy | Speed (CPU) | Verdict |
|----------|------------|---------------|-------------|---------|
| Tesseract 5.x | 30–40% | 20–30% | ~2s/region | NOT VIABLE |
| PaddleOCR v5 | 50–60% | 40–50% | ~300s total pipeline | NOT VIABLE |
| EasyOCR | ~50–60% | ~40–50% | Similar to PaddleOCR | NOT VIABLE |
| YOLO v8-nano + PaddleOCR | 55–65% | 45–55% | ~180s | NOT VIABLE |
| Multi-Pass OCR (5 variants) | +5–10% improvement | Marginal | ~300s (20+ OCR calls) | NOT VIABLE — too slow |
| Checksum Error Correction | +5–15% on IC | N/A | <1ms | Helps but insufficient alone |
| Vision LLM (GPT-4.1-nano) | 98–100% | 95–100% | 2–3s | WORKS — requires internet |
| USB Chip Reader (APDU) | 100% | 100% | 3–5s | GOLD STANDARD — fully offline |


[Image: OCR Test Result]

*Figure 5: OCR Pipeline Test Result — IC number not detected (mykad_ocr_v2.py with PaddleOCR + YOLO)*

## 10.2 Why Vision LLMs Succeed Where OCR Fails

Vision LLMs don't read characters independently — they apply contextual reasoning. The LLM knows an IC number must be YYMMDD-PB-####, validates the date, checks the state code, and cross-references the gender digit parity. OCR engines treat each character independently with no structural understanding.

**Critical note:** Vision LLM accuracy is highest with a FIXED camera position relative to the card. For kiosk deployments, use a fixed-mount camera with a card slot. Handheld phone photos achieve ~90–95% accuracy (vs 98–100% fixed).

## 10.3 Recommended Architecture

1. **Primary:** USB smart card chip reader (offline, 100% accurate, 3–5 seconds)
2. **Secondary:** Vision LLM API for photo-based flows (internet required, ~$0.001/scan)
3. **Tertiary:** OCR pipeline as degraded fallback (low accuracy, flag for manual verification)

## 10.4 The Pre-processing "Graveyard" (What Doesn't Work)

Developers often assume that applying standard OpenCV filters will magically make the laser-engraved text readable. Extensive testing confirms that software pre-processing cannot fix the optical interference caused by the guilloche pattern.

The following standard approaches were tested and failed:

- **Adaptive Thresholding:** Fails because the dark lines of the guilloche pattern intersect with the laser-engraved text, causing the characters to bridge together into unreadable blobs.
- **CLAHE (Contrast Limited Adaptive Histogram Equalization):** Amplifies the background noise of the rainbow printing just as much as the text it's supposed to enhance.
- **Canny Edge Detection:** Creates a chaotic web of edges due to the holographic DOVID overlay — the diffractive nanostructures produce edge responses indistinguishable from actual text strokes.
- **Morphological Dilation/Erosion:** Smudges the tightly packed 12-digit IC number into an unreadable solid block. The digit spacing is too tight relative to the guilloche line spacing for any structuring element to separate them cleanly.
- **Morphological Black-Hat (Guilloche Removal):** Produces visually cleaner digit images but PaddleOCR still misreads them frequently. The laser engraving's variable reflectivity defeats any fixed-threshold approach.
- **Multi-Pass OCR (5 Preprocessing Variants):** Running OCR on 5 different preprocessed versions (raw, adaptive threshold, Otsu, CLAHE, sharpened) gives marginal accuracy improvement (+5–10%) at catastrophic speed cost (20+ OCR calls × 15s each = 300s total).

**Conclusion:** Do not waste time trying to clean the image via OpenCV. Rely on contextual AI (Vision LLMs) or skip optics entirely via the smart card chip.

## 10.5 Hardware Mitigation: Cross-Polarised Lighting

If you are building a physical kiosk and must rely on optical scanning, you can physically eliminate the severe glare from the Holographic Overlay (DOVID) using cross-polarisation.

- **The Setup:** Place a linear polarising film over your kiosk's LED light source. Place a second polarising film over the camera lens, rotated exactly 90 degrees offset from the light's filter.
- **The Result:** This completely blocks all direct specular reflections (glare) bouncing off the plastic and hologram, allowing the camera to see straight through to the printed and laser-engraved layers beneath the DOVID.
- **Cost:** Polarising film sheets are approximately RM20–50 per sheet. This is the cheapest hardware modification that yields the most significant optical improvement.
- **Limitation:** Cross-polarisation eliminates glare but does NOT eliminate the guilloche pattern interference, which is a printed feature inside the card body. OCR will still struggle with the guilloche even with perfect glare-free images — but Vision LLMs handle it significantly better when glare is removed.

## 10.6 UI/UX Fallback Strategies

Because optical extraction (even via Vision LLMs) has a 5–10% failure rate when users upload handheld photos, your software must handle failures gracefully.

- **Do not block the user:** If the LLM returns low confidence or if the extracted IC number fails the Mod 11,2 checksum validation, do not throw a hard error. Dead-end error screens frustrate users and increase abandonment rates.
- **Pre-fill and Flag:** Pre-fill the form with whatever data was successfully extracted, highlight the failing fields (e.g., in yellow), and prompt the user to manually correct only the flagged values. This turns a failed scan into a 5-second manual correction instead of a full re-entry.
- **Auto-retry with guidance:** If the first scan fails, show the user specific guidance: "Hold the card flat, avoid shadows on the IC number area, ensure even lighting." Then allow a one-tap re-scan rather than requiring re-upload.
- **Checksum as silent validator:** Run the ISO 7064 Mod 11,2 checksum on the extracted IC number in the background. If it passes, the IC is almost certainly correct. If it fails, flag the IC field specifically and tell the user which digits look suspicious (based on the checksum correction algorithm's best guesses).

---

# 11. Technical Assets & Files

| File | Description |
|------|-------------|
| mykad_ocr_v2.py (~1,700 lines) | Complete OCR pipeline: Flask web UI, webcam, upload, YOLO, PaddleOCR, checksum correction |
| train_yolo.py (~180 lines) | YOLOv8-nano training script for 6-class MyKad field detection |
| mykad_ic_best.pt | Trained YOLOv8-nano weights |
| Scan_Image_Service.go (~130 lines) | Go service for Vision LLM API scanning |
| Scan_Image_Base.go (~50 lines) | Base prompt for Vision LLM extraction |
| MyKad_Complete_Technical_Reference_v3_LLM.md (~1,400 lines) | 23-chapter technical reference |
| Self_Validating_12_Digit_Identifier_System.md (~300 lines) | Abstracted checksum specification |

---

# 12. References & Sources

1. Wikipedia — Malaysian identity card: [https://en.wikipedia.org/wiki/Malaysian_identity_card](https://en.wikipedia.org/wiki/Malaysian_identity_card)
2. Wikipedia — Malaysian passport: [https://en.wikipedia.org/wiki/Malaysian_passport](https://en.wikipedia.org/wiki/Malaysian_passport)
3. Wikipedia — DOVID: [https://en.wikipedia.org/wiki/Diffractive_optically_variable_image_device](https://en.wikipedia.org/wiki/Diffractive_optically_variable_image_device)
4. IRIS Corporation Berhad: [https://www.iris.com.my/](https://www.iris.com.my/)
5. IRIS Smart Card Solutions: [https://www.iris.com.my/smart-card-solution/](https://www.iris.com.my/smart-card-solution/)
6. Malaysia Government Portal (MyKad): [https://www.malaysia.gov.my/en/categories/personal-identification/identification-card](https://www.malaysia.gov.my/en/categories/personal-identification/identification-card)
7. Lowyat.NET — Next-Gen MyKad QR Code: [https://www.lowyat.net/2025/374652/malaysia-next-gen-mykad-qr-code-feature/](https://www.lowyat.net/2025/374652/malaysia-next-gen-mykad-qr-code-feature/)
8. iLoveBorneo — MyKad Baharu: [https://www.iloveborneo.my/mykad-lama-bakal-digantikan-ketahui-ciri-ciri-kad-pengenalan-baharu/](https://www.iloveborneo.my/mykad-lama-bakal-digantikan-ketahui-ciri-ciri-kad-pengenalan-baharu/)
9. CTOS eKYC Document Verification: [https://ctoscredit.com.my/business/evaluate-new-customer/ctos-ekyc/document-id-holder-verification/](https://ctoscredit.com.my/business/evaluate-new-customer/ctos-ekyc/document-id-holder-verification/)
10. The Rakyat Post — MyKad Structure: www.therakyatpost.com
11. CardLogix — Polycarbonate Cards: [https://www.cardlogix.com/product/id-grade-polycarbonate-card-cr80-30-mil-laser-engravable/](https://www.cardlogix.com/product/id-grade-polycarbonate-card-cr80-30-mil-laser-engravable/)
12. DSS Plastics / PolycarbonateCard.com: [https://www.polycarbonatecard.com/more/](https://www.polycarbonatecard.com/more/)
13. Datasonic (DMSB/APCS) — Malaysian PC Card Manufacturer: [https://www.apcscard.com/polycarbonate-card-laser-engrave-coated-overlay/](https://www.apcscard.com/polycarbonate-card-laser-engrave-coated-overlay/)
14. IAI Industrial Systems — Laser Engraving: [https://www.iai.nl/personalisation-experts/personalisation-technologies/laser-engraving/](https://www.iai.nl/personalisation-experts/personalisation-technologies/laser-engraving/)
15. CampusIDNews — Laser Engraving IDs: [https://www.campusidnews.com/laser-engraving-ids-catching-on/](https://www.campusidnews.com/laser-engraving-ids-catching-on/)
16. Identis Group — Laser Personalisation: [https://identisgroup.com/newsroom/2018/03/laser-personalization-for-high-security-id-cards/](https://identisgroup.com/newsroom/2018/03/laser-personalization-for-high-security-id-cards/)
17. OVD Kinegram — Hologram Technology: [https://www.kinegram.com/events-insights/details/what-is-secure-hologram-technology](https://www.kinegram.com/events-insights/details/what-is-secure-hologram-technology)
18. Keesing Platform — Holography for ID Security: [https://platform.keesingtechnologies.com/holography-on-the-frontline-of-id-security-and-protection/](https://platform.keesingtechnologies.com/holography-on-the-frontline-of-id-security-and-protection/)
19. IDEMIA — LASINK Helios DOVID: [https://www.idemia.com/secondary-color-portrait-dovid](https://www.idemia.com/secondary-color-portrait-dovid)
20. Security Printing — OVD Types: [https://www.securityprinting.co.uk/holograms-ovds.php](https://www.securityprinting.co.uk/holograms-ovds.php)
21. Troy Group — UV Ink Security: [https://www.troygroup.com/blog/uv-ink-for-security](https://www.troygroup.com/blog/uv-ink-for-security)
22. SZIMAGETECH — ID Card Security Features: [https://szimagetech.com/explore-comprehensive-id-card-security-features/](https://szimagetech.com/explore-comprehensive-id-card-security-features/)
23. Ben Hodosi — Guilloche Design: [https://benhodosi.com/](https://benhodosi.com/)
24. ID Management — Card Security Features: [https://www.idmanagement.com/card-security](https://www.idmanagement.com/card-security)
25. Innov8tif — 3 Methods to Read MyKad: [https://innov8tif.com/3-methods-to-read-mykad-2/](https://innov8tif.com/3-methods-to-read-mykad-2/)
26. ClearTax — MyKad Types: [https://www.cleartax.com/my/en/mykad-malaysia](https://www.cleartax.com/my/en/mykad-malaysia)
27. Malaysia Central — MyKad Identity Number: [http://www.malaysiacentral.com/information-directory/mykad-identity-number-mykad-the-malaysia-government-multipurpose-smart-identity-card/](http://www.malaysiacentral.com/information-directory/mykad-identity-number-mykad-the-malaysia-government-multipurpose-smart-identity-card/)
28. IDP Americas — Holographic ID Cards: [https://www.idpamericas.com/holographic-id-cards/](https://www.idpamericas.com/holographic-id-cards/)
29. Jasuindo — UV Ink Security Printing: [https://jasuindo.com/2026/01/13/uv-ink-in-security-printing/](https://jasuindo.com/2026/01/13/uv-ink-in-security-printing/)
30. Holoteam — Anti-Counterfeit Printing Patterns: [https://www.holoteam.com/post/security-printing-pattern](https://www.holoteam.com/post/security-printing-pattern)

---

*Kesh (deadboy18) — April 2026 — Confidential Research Document*
*Addendum to: MyKad Developer Ecosystem Research Portfolio*
