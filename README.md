# MyKad Reader & Reference

> An open documentation and tooling collection for the Malaysian MyKad identity card — format, checksum algorithm, smart-chip reading, OCR research, and interactive learning tools.

This repository is the result of extensive research into how Malaysia's national identity card actually works — how the 12-digit IC number is structured, how its hidden checksum is computed, how the embedded smart chip can be read, and why OCR is surprisingly difficult on the physical card. It's intended as a reference for developers integrating MyKad functionality, researchers studying national ID systems, and anyone curious about the math hiding inside their own IC number.

**All information in this repository is compiled from publicly available sources.** Everything is either public knowledge, community-researched, or original work. No real personal data is included, and no insider information was used.

---

## 🌐 Try the tools online

The interactive tools are hosted live via GitHub Pages — no download needed:

**→ [deadboy18.github.io/mykad-reader](https://deadboy18.github.io/mykad-reader/)**

Direct links:
- [IC Checksum Tutorial](https://deadboy18.github.io/mykad-reader/ic-checksum-tutorial.html) — interactive, 3 languages, narrated
- [IC Generator & Analyzer](https://deadboy18.github.io/mykad-reader/12digits_identifier_system.html) — generate, validate, batch tools
- [MyKad Validator](https://deadboy18.github.io/mykad-reader/mykad-validator.html) — lightweight community reference

---

## Table of contents

1. [What is MyKad?](#what-is-mykad)
2. [Card variants](#card-variants)
3. [What's in this repository](#whats-in-this-repository)
4. [What this repo is NOT](#what-this-repo-is-not)
5. [Quick start — where to begin](#quick-start--where-to-begin)
6. [Repository structure](#repository-structure)
7. [Documentation folder](#-documentation)
8. [Tools — interactive generator and tutorial](#-mykad-generator_checksum)
9. [OCR research and code](#-mykad_ocr)
10. [Main project code](#-mykad-project)
11. [Third-party samples and references](#-other-github-mykad-project-sample)
12. [Key technical concepts](#key-technical-concepts)
13. [Disclaimer](#disclaimer)
14. [Privacy and responsible use](#privacy-and-responsible-use)
15. [A note on sources and credits](#a-note-on-sources-and-credits)
16. [Credits and sources](#credits-and-sources)
17. [License](#license)
18. [Feedback and contributions](#feedback-and-contributions)

---

## What is MyKad?

**MyKad** (Kad Pengenalan Malaysia) is Malaysia's compulsory national identity card, issued by **JPN** (Jabatan Pendaftaran Negara — the National Registration Department) to every citizen aged 12 and above. It was introduced in September 2001, replacing the earlier laminated High-Quality Identity Card (Kad Pengenalan Bermutu Tinggi). Malaysia was the first country in the world to issue an ID card that combined a printed photograph, biometric fingerprint data, and a smart card chip — the technology was developed locally by IRIS Corporation Berhad, a Malaysian company that also invented the world's first ePassport in 1998.

The history of Malaysian ID cards goes back further still. The first identity card was issued in 1948 and was known colloquially as the "Rice Card," originally intended to help curb the communist insurgency during the Malayan Emergency. The format evolved through paper, plastic, and laminated variants over the next half-century before arriving at the current smart-chip-embedded MyKad.

Every MyKad carries a **12-digit IC number** laser-engraved into the polycarbonate body. For example:

```
900523-13-5029
```

Those 12 digits are not arbitrary. They encode:

| Segment | Digits | Meaning |
|---------|--------|---------|
| YYMMDD | 1–6 | Date of birth |
| PB | 7–8 | Place of birth (state code, or country code if born abroad) |
| ### | 9–11 | Sequence number assigned by JPN |
| G | 12 | Gender indicator (odd = male, even = female) **and** a math checksum |

The last digit is the clever part. It performs **two jobs simultaneously**: it shows the holder's gender through its parity (odd or even), *and* it is the answer to an ISO 7064 Mod 11,2 checksum calculated from the first 11 digits. If anyone mistypes the IC number by even one digit, the checksum fails and the system detects the error immediately. This same checksum family is used by China's Resident Identity Card and several other national ID systems worldwide.

Beyond the number, the physical card is a high-security document — polycarbonate layers fused together with laser-engraved text, rainbow printing, guilloche background patterns, a ghost image, UV fluorescent ink, and an 80KB ISO 7816 smart chip that stores the holder's photo, fingerprints, and address, all readable via standard PC/SC APDU commands.

This repository documents all of that.

---

## Card variants

Malaysia issues several variants of the identity card, all sharing the same 12-digit IC number format but differing in colour, holder type, and sometimes additional chip data:

| Card | Issued to | Card colour | Notes |
|------|-----------|-------------|-------|
| **MyKad** | Citizens aged 12+ | Blue | The standard card most references describe |
| **MyKid** | Citizens under 12 | Pink | Same format, issued to minors |
| **MyPR** | Permanent residents | Red | Same format |
| **MyKAS** | Temporary residents | Green | Same format, less-tested with the checksum |
| **MyTentera** | Military personnel | Silver | Variant with military-specific extensions |
| **MyPolis** | Police personnel | Varies | Police-specific variant |

A new generation of MyKad is planned to begin issuance in mid-2026 with a QR code feature for on-the-spot digital verification, enhanced laser engraving and holograms, and expanded biometric data. Existing cards will be gradually replaced. The 12-digit IC number format and checksum algorithm are not expected to change.

---

## What's in this repository

Five categories of material:

1. **Written research documents** — long-form technical references in Markdown, PDF, and Word formats covering the MyKad format, checksum algorithm, OCR feasibility studies, and a complete developer guide.

2. **Interactive web tools** — self-contained HTML files that teach the checksum system and let you generate or validate IC numbers visually. No install, no server, just open in a browser.

3. **Reference code** — Python implementation of the chip reader using PC/SC APDU commands, a Python OCR pipeline, and Go services for AI-powered vision extraction.

4. **Third-party samples** — vendor driver SDKs and other open-source MyKad project snapshots for reference.

5. **Historical materials** — government infographics, JPN reference documents, and visual breakdowns of the card structure.

---

## What this repo is NOT

Setting expectations clearly:

- **Not a production-ready product.** These are reference implementations and research materials. Adapt as needed for real deployments, with appropriate security review.
- **Not a lookup or verification service.** There's no way to query whether an IC number belongs to a real person from this repo. That would require authorized access to JPN's databases, which this does not and cannot provide.
- **Not endorsed by JPN or IRIS Corporation.** This is independent community documentation. The checksum algorithm in particular has never been officially confirmed — see the [Disclaimer](#disclaimer).
- **Not a forgery guide.** Physical MyKad counterfeiting requires millions of ringgit worth of specialized equipment (lasers, polycarbonate lamination presses, hologram origination) plus proprietary materials that aren't publicly available. This repo documents how the card works; it does not enable making fake ones.
- **Does not contain real personal data.** All IC numbers in tutorials, examples, and generators are fictitious. Any resemblance to real persons is coincidental.

---

## Quick start — where to begin

Pick a path based on what you're trying to do:

### I just want to understand how the IC number works
→ Open **[`Mykad Generator_Checksum/ic-checksum-tutorial.html`](Mykad%20Generator_Checksum/ic-checksum-tutorial.html)** in any browser. Interactive step-by-step walkthrough, supports English / Bahasa Malaysia / 中文, includes narration, dark mode, and a full final animation. Works offline, no setup.

### I want to validate or generate IC numbers
→ Open **[`Mykad Generator_Checksum/12digits_identifier_system.html`](Mykad%20Generator_Checksum/12digits_identifier_system.html)**. Generator/analyzer tool with batch generation, custom parameters, export options, and full state-code reference.

### I want the technical deep-dive
→ Read **[`Documentation/MyKad_Complete_Technical_Reference_v3_LLM.md`](Documentation/MyKad_Complete_Technical_Reference_v3_LLM.md)** — 23 chapters covering every aspect of the card: chip architecture, APDU command reference, file structure, checksum algorithm, cross-language validators in 7 languages, and more.

### I want to build a chip reader
→ Check **[`MyKad project/mykad.py`](MyKad%20project/mykad.py)** for a working Python APDU implementation. Requires a PC/SC smart card reader (USB ISO 7816 compliant).

### I'm researching OCR on MyKad
→ Read **[`Documentation/MyKad_OCR_Vision_Research_Report.md`](Documentation/MyKad_OCR_Vision_Research_Report.md)** for the full research writeup on why traditional OCR fails and why vision LLMs succeed. Then see **[`MyKad project/mykad_ocr_v2.py`](MyKad%20project/mykad_ocr_v2.py)** for the implementation.

### I want to understand the checksum in abstract terms
→ Read **[`Documentation/Self_Validating_12_Digit_Identifier_System.md`](Documentation/Self_Validating_12_Digit_Identifier_System.md)** — the algorithm documented in a generic, country-neutral way.

---

## Repository structure

```
mykad-reader/
├── Documentation/                      Written research and reference materials
├── Mykad Generator_Checksum/           Interactive web tools (HTML)
├── MyKad_OCR/                          OCR research and Go services
├── MyKad project/                      Core Python implementations
├── Other Github Mykad Project sample/  Third-party vendor SDKs and open-source references
├── README.md                           You are here
└── LICENSE                             MIT License
```

---

## 📁 Documentation

The `Documentation/` folder contains the written research corpus. Every major document is provided in multiple formats (Markdown, PDF, DOCX) so you can read it in whatever is convenient.

| File | Size | What it is |
|------|------|------------|
| `MyKad_Complete_Technical_Reference_v3_LLM.md` | 49 KB | **The main technical reference.** 23 chapters, covering card physical specs, security features, IC number format, place-of-birth code directory, checksum algorithm deep-dive with worked examples, chip architecture, APDU command reference, file structure byte-level parsing, data decoding, Python/C/Go/Node.js implementations, cross-language checksum validators (JS, Python, C#, PHP, Go, Java, C), server API architecture, database schema, and security/PDPA best practices. Written for developers. Markdown version is LLM-friendly — paste into any AI tool for context. |
| `MyKad_Complete_Technical_Reference_v3.pdf` | 749 KB | PDF version of the above — formatted for reading/printing. |
| `MyKad_Complete_Technical_Reference_v3.docx` | 3.3 MB | Word document version — for editing or re-exporting. |
| `MyKad_OCR_Vision_Research_Report.md` | 36 KB | **OCR and Vision feasibility report.** Covers physical security features of the card, why free OCR engines (Tesseract, PaddleOCR, EasyOCR) fail, why vision LLMs achieve 98–100% accuracy, the "pre-processing graveyard" of OpenCV approaches that don't work, hardware mitigations like cross-polarised lighting for kiosks, and UI/UX fallback strategies. Based on extensive hands-on testing. |
| `MyKad_OCR_Vision_Research_Report.pdf` | 602 KB | PDF version of OCR research. |
| `MyKad_OCR_Vision_Research_Report.docx` | 368 KB | Word version of OCR research. |
| `MyKad_Research_Portfolio.pdf` | 133 KB | High-level portfolio overview of the research work. |
| `MyKad_Research_Portfolio.docx` | 35 KB | Word version. |
| `MyKad_Research_Portfolio_Client.pdf` | 130 KB | Client-facing version of the portfolio (simplified, less technical). |
| `MyKad_Research_Portfolio_Client.docx` | 23 KB | Word version. |
| `Self_Validating_12_Digit_Identifier_System.md` | 8 KB | **Abstracted checksum specification.** Documents the ISO 7064 Mod 11,2 algorithm and the 12-digit identifier system in country-neutral terms — useful reference if you want the math without the Malaysia-specific context. |
| `Self_Validating_12_Digit_Identifier_System.pdf` | 329 KB | PDF version. |
| `Self_Validating_12_Digit_Identifier_System.docx` | 15 KB | Word version. |
| `7_lamp_B_-_senarai_kod_negeri.pdf` | 12 KB | **Official JPN state code reference.** Lists all Malaysian state codes (01–16) and legacy/foreign codes. Useful as an authoritative source. |
| `MyKad.webp` | 347 KB | Card structure image showing where each element is printed. |
| `GOSG_Infografik_Kad_Pengenalan_Draft_1-02.webp` | 347 KB | Malaysia Government portal infographic on MyKad security features — rainbow printing, laser engraving, ghost image, guilloche pattern, anti-copy protection, UV ink, 80K chip. |
| `MyKad_identification_number.jpg` | 68 KB | Visual breakdown of a sample IC number showing which digits mean what (year, month, day, place, sequence, gender). |
| `list-files.ps1` | 3.4 KB | PowerShell script for generating a file-inventory tree of the repo. Useful if you want to regenerate an inventory after making changes. |

---

## 📁 Mykad Generator_Checksum

Interactive browser-based tools. Both are single self-contained HTML files — no build step, no dependencies, no server. Just open in any modern browser.

| File | Size | What it is |
|------|------|------------|
| `ic-checksum-tutorial.html` | 96 KB | **Interactive step-by-step tutorial** explaining how the MyKad checksum works. 14 steps, three languages (English / Bahasa Malaysia / 中文), voice narration via the browser's Web Speech API, dark mode, quick-mode that skips straight to the full animation, autoplay finale, clickable state codes reference, and confetti on successful validation. Designed to be understandable by non-technical users. Built for curious minds who want to understand the math inside their own IC without needing a math background. |
| `12digits_identifier_system.html` | 54 KB | **Full generator and analyzer tool.** Three tabs: Generate (create single or batch IC numbers with custom date ranges, region codes, gender split — up to 500 at once), Analyze (paste any 12-digit IC and see full breakdown including date, place of birth, sequence, checksum verification, and gender), Reference (complete format documentation, state code directory, century determination rules, and checksum math explanation). Exports to TXT, CSV, or JSON. Supports EN/BM, light/dark themes, and batch statistical analysis. |

Both tools are **fully offline** — once the HTML file is loaded, no internet connection is needed. All calculations happen in the browser. Nothing is sent anywhere.

---

## 📁 MyKad_OCR

OCR research materials and Go-language vision services.

| File | Size | What it is |
|------|------|------------|
| `MyKad_OCR_Vision_Research_v1_LLM.md` | 36 KB | Markdown version of the OCR research report (LLM-friendly formatting). Duplicated from `Documentation/` for co-location with the code. |
| `MyKad_OCR_Vision_Research_Report.docx` | 368 KB | Word version of the same report. |
| `Scan Image Base.go` | 2.2 KB | **Go implementation — base prompt** for the vision LLM OCR service. Defines the structured prompt sent to GPT-4.1-nano (or compatible vision model) requesting JSON extraction of IC details. Includes field definitions, date format specifications, card type codes (MyKad, driving licence, passport, etc.), and error handling for blurry or non-ID images. |
| `Scan Image Service.go` | 4.0 KB | **Go implementation — scan service.** Takes an image URL/bytes, sends to the vision LLM API, parses the structured response, and returns a typed `CardDetails` struct. Used for hotel check-in kiosks, mobile app flows, or anywhere you need to OCR a MyKad photo instead of reading the chip. Achieves 98–100% accuracy on fixed-camera setups, 90–95% on handheld photos. |

---

## 📁 MyKad project

Core Python implementations — chip reading and OCR pipeline.

| File | Size | What it is |
|------|------|------------|
| `mykad.py` | 6.8 KB | **Python smart-card reader.** Uses `pyscard` to talk to any PC/SC-compliant USB smart card reader. Implements the full APDU command sequence for reading the JPN application on the MyKad contact chip: selects the app, issues Set Length + Select Info + Read Info commands in 240-byte chunks, parses the returned bytes into personal details (name, IC, gender, DOB, address, race, religion, nationality), and extracts the JPEG photo from File 2. Includes all three critical "chip fixes" documented in the main technical reference. |
| `mykad_ocr_v2.py` | 47 KB | **Full OCR pipeline in Python.** Flask web UI with webcam support, image upload, YOLOv8 field detection for locating the IC number / name / address regions on a card photo, PaddleOCR text extraction, ISO 7064 checksum validation for error correction, and fallback to vision LLM when traditional OCR fails. Intended as a reference implementation — shows the full stack of techniques and where each one succeeds or fails. |
| `Architecture Plan.txt` | 2.3 KB | Architecture notes — how the reader, OCR pipeline, and server components fit together. |
| `MYKAD_PRO.rar` | 83 KB | Compiled source archive of the broader MyKad Pro toolset (server + agent + UI). Extract to read. Verify no database, log files, or real user data are bundled inside before distributing further. |

### Running `mykad.py`

```bash
pip install pyscard pillow
# Linux only: sudo apt install pcscd libpcsclite-dev
python mykad.py
```

You'll need a USB PC/SC smart card reader (ACR39U, ACS ACR38U, or any generic CCID-compliant ISO 7816 reader). Insert a MyKad, run the script, and it will print the extracted identity data as JSON and save the photo as `photo.jpg`. No PIN is required for reading — that's by design, the contact chip is intentionally readable by any PC/SC reader for verification purposes. Writing to the chip, however, is gated behind JPN's Perso Card and Triple-DES keys.

### Running `mykad_ocr_v2.py`

```bash
pip install flask paddleocr ultralytics opencv-python pillow
python mykad_ocr_v2.py
# Opens on http://localhost:5000
```

Requires a trained YOLOv8 weights file (`mykad_ic_best.pt`, not included — train your own using the Roboflow IC dataset or any similar labeled MyKad photo set).

---

## 📁 Other Github Mykad Project sample

Reference materials collected from third-party vendors and open-source projects. These are included for convenience but are **not original work** in this repository.

| File | Size | Source and purpose |
|------|------|---------------------|
| `Admire Rfid.rar` | 28.6 MB | Admire IT smart card reader vendor SDK. Contains drivers, sample code, manuals (English and Chinese), Mac/Linux/Android drivers, Windows installers, and a setup video. Useful if you're using the Admire reader specifically. Original source: Admire IT. |
| `EZ100_Driver_64bit.zip` | 3.0 MB | EZ100 smart card reader driver for 64-bit Windows. |
| `HiTi_CS311_2.zip` | 9.0 MB | HiTi CS311 reader driver. |
| `Malaysia-MyKad-Reader-Webserver-master.zip` | 1.2 MB | Snapshot of [`HakamRaza/Malaysia-MyKad-Reader-Webserver`](https://github.com/HakamRaza/Malaysia-MyKad-Reader-Webserver) — Node.js implementation using `opensc-tool` and stdout parsing. |
| `mykad-reader-main.zip` | 728 KB | Snapshot of a similar public MyKad reader project. |
| `mykad-vb.net-master.zip` | 34 KB | Visual Basic .NET implementation of a MyKad reader, for anyone working in the VB/.NET ecosystem. |
| `index.html` | 18 KB | Sample web-based MyKad reader interface. |
| `MyKad Validator.html` | 19 KB | Older community-made IC number validator — historical reference. Compare to the `12digits_identifier_system.html` tool in this repo for a more modern version. |

> **Note on licensing:** Each third-party sample retains its original license. Vendor SDKs are subject to their manufacturers' terms. Open-source project snapshots are frozen copies — consult the original repositories for the latest versions and license terms. If any rights-holder wants their material removed from this repository, please open an issue and it will be taken down immediately.

---

## Key technical concepts

A quick tour of the most important ideas. For the full deep-dive, see `Documentation/MyKad_Complete_Technical_Reference_v3_LLM.md`.

### The IC number format

```
  9 0 0 5 2 3 - 1 3 - 5 0 2 9
  └─────┬───┘   └┬┘   └──┬──┘
        │        │        │
     YYMMDD      PB     ###G
     birthday  place   seq+gender/checksum
```

- **YYMMDD**: 6-digit birth date. Year is only 2 digits (90 = 1990 or 2090?)
- **PB**: 2-digit state code (01 Johor, 02 Kedah, …, 16 Putrajaya) or country code (60 Brunei, 66 Singapore, 74 China, 75 India, etc.)
- **###**: 3-digit sequence number, assigned by JPN
- **G**: final digit — parity indicates gender, value is the checksum result

### The century rule

Since YY is only 2 digits, the century is disambiguated by the first digit of the sequence (position 9):

| Sequence first digit | Century | Example |
|----------------------|---------|---------|
| 0, 1, 2, 3, 4 | 2000s | YY=05, seq=023x → 2005 |
| 5, 6, 7, 8, 9 | 1900s | YY=89, seq=678x → 1989 |

### The checksum (ISO 7064 Mod 11,2)

The last digit is computed from the first 11 digits using a weighted sum modulo 11:

1. Reverse the first 11 digits.
2. Multiply each reversed digit by its position weight. The 11 weights are constant: `2, 4, 8, 5, 10, 9, 7, 3, 6, 1, 2` (these are successive powers of 2 modulo 11).
3. Sum all the products.
4. Compute `(12 − (sum mod 11)) mod 11`. The result is the check digit.

If the result is 10, that sequence is impossible (can't represent as a single digit) and is permanently excluded. Roughly 9.1% of possible sequences fall into this category. China's ID card handles the same situation by using 'X' as a check character — MyKad just skips these sequences entirely.

### Why modulo 11 specifically?

Because 11 is prime, and it's the smallest prime greater than 10 (the number of possible digit values 0–9). Prime moduli guarantee strong error-detection properties: every single-digit typo is caught, and every swap of two adjacent digits is caught. If the standard used mod 10 instead, these guarantees would break — certain typos would slip through silently. This is exactly why ISO 7064 specifies mod 11, and why virtually every national ID checksum on the planet uses a prime modulus.

### Gender + checksum in one digit

JPN's assignment system iterates through sequence numbers starting from 001 (or 500 for pre-2000 births). For each candidate sequence, it computes the checksum. If the result's parity doesn't match the applicant's gender, it skips. If it does, the IC number is assigned. This is how the last digit elegantly performs both jobs at once — gender indicator *and* math checksum — without either one ever being "chosen" in a way that conflicts with the other.

### The chip

The MyKad has two independent chips:

- **Contact chip (ISO 7816)**: 80KB EEPROM, gold pad on the back of the card. Stores personal data, JPEG photo (~15 KB), fingerprint templates (proprietary IRIS Corp format), residential address, SOCSO number. Readable by any PC/SC USB smart card reader using standard APDU commands — no PIN required. Writing requires JPN's Perso Card and Triple-DES keys.
- **Contactless chip (Mifare Classic 1K, ISO 14443-3A)**: Touch 'n Go e-wallet only. Completely separate from the contact chip. NFC readers (ACR122U, PN532) can see this chip but not the identity chip. Sector keys are held by Touch 'n Go.

The chip runs a proprietary operating system called **M-COS** (MyKad Chip Operating System), developed by IRIS Corporation. M-COS is not publicly available, which is one of the reasons why chip counterfeiting is effectively impossible — you cannot buy the OS, and the Perso Card + Triple-DES keys required to personalize a blank chip are held exclusively by JPN and IRIS inside Hardware Security Modules.

---

## Disclaimer

> **The checksum algorithm documented in this repository was never officially confirmed by JPN.**
>
> The algorithm (ISO 7064 Mod 11,2 applied to the first 11 digits of the IC number with the weight sequence `2, 4, 8, 5, 10, 9, 7, 3, 6, 1, 2`) was reverse-engineered by community researchers — most notably Bryan Lam / beeell1 — by testing it against large corpora of real IC numbers. The match rate is near-perfect, which strongly suggests this is indeed the algorithm JPN uses. But it has never been officially published or confirmed by the Jabatan Pendaftaran Negara.
>
> **What this means practically:**
>
> - A checksum that *passes* does not guarantee the IC number belongs to a real person. It only confirms the internal math is consistent.
> - A checksum that *fails* almost certainly means the IC is malformed (typo, test data, or fabricated), but there's a tiny theoretical chance JPN uses a different algorithm in edge cases not yet discovered.
> - **Do not use checksum validation as the sole means of identity verification.** Always pair with additional checks — chip reading, visual inspection, database lookups by authorized parties, etc.

The IC numbers used in this repository's tutorials, generators, and examples are **fictitious**. Any resemblance to real persons is entirely coincidental.

---

## Privacy and responsible use

This repository is intended for educational and developer-reference purposes. The Malaysian Personal Data Protection Act (PDPA) 2010 applies to anyone processing personal data of Malaysian individuals, and handling of IC numbers in particular is sensitive.

**Don't do:**

- Do not use the generator tool to fabricate IC numbers for fraudulent purposes.
- Do not collect, store, or process real IC numbers without a lawful basis and the individual's informed consent.
- Do not use reader code to extract data from cards that aren't yours, or to build lookup services that query government databases without authorization.

**Do:**

- Use synthetic/generated data for testing and development.
- Implement appropriate security controls if you handle real data — encryption at rest, access logging, retention policies, deletion on request.
- Mask IC numbers in UI displays where full visibility isn't necessary (e.g., `980317-14-***8`).
- Follow the principle of least privilege: only collect what you actually need.

---

## A note on sources and credits

**Everything in this repository is compiled from publicly available information.** This includes JPN's official MyKad documentation, the Malaysia Government Portal, Wikipedia articles, academic papers, community forum posts (Lowyat.NET, Stack Overflow), vendor technical documentation, open-source GitHub projects, and blog posts written by Malaysian developers over the past two decades. No insider information, leaked documents, or proprietary sources were used.

This research represents years of collection and synthesis work across many different sources. I've tried to properly credit original authors, researchers, and projects in the [Credits and sources](#credits-and-sources) section below — but with material gathered over a long period from many places, I may have missed someone.

**If you see your work referenced here without proper attribution, or you feel your contribution has been misattributed or overlooked, please don't hesitate to reach out.** You can:

- Open an issue on this repository
- Message me directly on GitHub ([@deadboy18](https://github.com/deadboy18))

I'll update the credits right away. Honestly, I'd much rather fix a missing credit than leave one wrong — you deserve recognition for your work, and this repo is meant to be a community resource that properly acknowledges everyone it builds on.

The same applies to corrections of any kind. If something is factually wrong, outdated, misleading, or if you have authoritative information that would improve the documentation, please let me know. Quick heads-up and it gets fixed.

**Apologies in advance if I've missed crediting anyone.** It's not intentional, and I'll happily fix it the moment I hear from you.

---

## Credits and sources

This work builds on research and documentation from many sources:

**Standards and specifications:**
- [ISO/IEC 7064 — Check character systems](https://en.wikipedia.org/wiki/ISO/IEC_7064) — the international standard for checksum algorithms including Mod 11,2 used by MyKad
- [ISO/IEC 7816 — Smart cards, contact interface](https://en.wikipedia.org/wiki/ISO/IEC_7816) — the standard for the MyKad contact chip
- ISO/IEC 14443-3A — the standard for the MyKad contactless chip (Touch 'n Go)

**Primary references:**
- [Wikipedia — Malaysian identity card](https://en.wikipedia.org/wiki/Malaysian_identity_card)
- [IRIS Corporation Berhad](https://www.iris.com.my/) — the Malaysian company that developed MyKad
- [Malaysia Government Portal — MyKad information](https://www.malaysia.gov.my/en/categories/personal-identification/identification-card)
- [JPN (Jabatan Pendaftaran Negara)](https://www.jpn.gov.my/) — the issuing authority

**Community research and related projects:**
- [beeell1/malaysian-ic-number-validator](https://github.com/beeell1/malaysian-ic-number-validator) — Bryan Lam's checksum research that originally validated the Mod 11,2 algorithm against real ICs
- [HakamRaza/Malaysia-MyKad-Reader-Webserver](https://github.com/HakamRaza/Malaysia-MyKad-Reader-Webserver) — Node.js MyKad reader
- [amree's blog: How to read MyKad](https://amree.dev/2011/12/05/how-to-read-mykad/) — early documentation of APDU sequences
- [Lowyat.NET forum thread on MyKad APDU](https://forum.lowyat.net/index.php?showtopic=355950) — community discussion
- [Innov8tif — 3 Methods to Read MyKad](https://innov8tif.com/3-methods-to-read-mykad-2/) — overview article
- [amree/mykad-java](https://github.com/amree/mykad-java) — Java implementation
- [firdausramlan/MyKAD-Reader](https://github.com/firdausramlan/MyKAD-Reader) — HTML/JS Chrome plugin approach
- [desmondchoon/HTTP-SmartCard-Reader](https://github.com/desmondchoon/HTTP-SmartCard-Reader) — HTTP-based reader on port 8080
- [yapyeeqiang/mykad-reader](https://github.com/yapyeeqiang/mykad-reader) — multi-language scanner

**Technology and hardware references:**
- [OpenSC Project](https://github.com/OpenSC/OpenSC) — open-source smart card library
- [PC/SC Workgroup](https://pcscworkgroup.com/) — smart card standards
- [pyscard](https://pyscard.sourceforge.io/) — Python smart card library
- [CardLogix](https://www.cardlogix.com/) — polycarbonate card manufacturing reference
- [IAI Industrial Systems](https://www.iai.nl/) — laser engraving technology reference

**Research report sources:**
Full bibliography for the OCR research and technical reference documents is included at the end of each respective file. Over 30 primary sources cited covering polycarbonate card manufacturing, laser engraving technology, DOVID holography, guilloche pattern design, UV security printing, and smart card personalization.

---

## License

The original work in this repository — documentation, interactive tools, and code I've written — is released under the **MIT License**. See the [`LICENSE`](LICENSE) file at the root of the repository. Third-party samples retain their original licenses.

---

## Feedback and contributions

This is primarily a personal research archive, but if you notice errors, have additional references to contribute, or find improvements to the checksum understanding or chip-reading code, feel free to open an issue or pull request.

If you're a JPN representative, an IRIS Corporation employee, or someone with authoritative information about the checksum algorithm — please reach out. The community would love to confirm whether the Mod 11,2 algorithm is officially what's used, and document any edge cases or variants that may exist for MyTentera, MyPR, MyKAS, or MyKid.

---

*Author: Kesh ([@deadboy18](https://github.com/deadboy18))*
*Last updated: April 2026*
