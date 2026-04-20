# A Self-Validating 12-Digit Identifier System

**Complete Specification: Structure, Classification Tables, Parity Logic & Checksum**

---

## 1. Identifier Structure

Every identifier in this system is exactly 12 digits: `D₁D₂D₃D₄D₅D₆D₇D₈D₉D₁₀D₁₁D₁₂`

```
┌──────────┬───────────────┬────────────┬─────────────┐
│ D₁–D₆    │ D₇–D₈        │ D₉–D₁₁    │ D₁₂         │
│ Date      │ Region Code   │ Sequence   │ Check Digit │
│ YYMMDD    │ 2-digit index │ 000–999    │ Computed    │
└──────────┴───────────────┴────────────┴─────────────┘
```

---

## 2. Field Breakdown — Example: `900523075049`

```
9 0 | 0 5 | 2 3 | 0 7 | 5 0 4 | 9
 YY   MM    DD    RC    SEQ    CHK
```

| Field | Digits | Value | Meaning |
|-------|--------|-------|---------|
| Year (YY) | D₁D₂ | 90 | Year component (last 2 digits) |
| Month (MM) | D₃D₄ | 05 | 5th month |
| Day (DD) | D₅D₆ | 23 | 23rd day |
| Region Code (RC) | D₇D₈ | 07 | Region index 07 (see lookup table) |
| Sequence (SEQ) | D₉D₁₀D₁₁ | 504 | 504th assignment for this date+region |
| Check Digit (CHK) | D₁₂ | 9 | Computed checksum + parity classifier |

---

## 3. Century Disambiguation

The year field YY only provides two digits. The century is determined by the first digit of the sequence field (D₉):

| D₉ Value | Century | Full Year Formula | Example |
|----------|---------|-------------------|---------|
| 0, 1, 2, 3, 4 | 2000s | 2000 + YY | YY=05, D₉=0 → 2005 |
| 5, 6, 7, 8, 9 | 1900s | 1900 + YY | YY=90, D₉=5 → 1990 |

For our example: D₉ = 5 ≥ 5 → 1900s → Full year = 1900 + 90 = **1990**

Complete date: **1990-05-23**

---

## 4. Region Code Lookup Table (D₇–D₈)

### 4.1 Primary Codes (01–16)

| Code | Region |
|------|--------|
| 01 | Region Alpha |
| 02 | Region Bravo |
| 03 | Region Charlie |
| 04 | Region Delta |
| 05 | Region Echo |
| 06 | Region Foxtrot |
| 07 | Region Golf |
| 08 | Region Hotel |
| 09 | Region India |
| 10 | Region Juliet |
| 11 | Region Kilo |
| 12 | Region Lima |
| 13 | Region Mike |
| 14 | Region November |
| 15 | Region Oscar |
| 16 | Region Papa |

### 4.2 Legacy / Alternate Codes (21–59)

Some regions have multiple codes due to historical sub-division:

| Code Range | Maps To |
|------------|---------|
| 21–24 | Region Alpha |
| 25–27 | Region Bravo |
| 28–29 | Region Charlie |
| 30 | Region Delta |
| 31, 59 | Region Echo |
| 32–33 | Region Foxtrot |
| 34–35 | Region Golf |
| 36–39 | Region Hotel |
| 40 | Region India |
| 41–44 | Region Juliet |
| 45–46 | Region Kilo |
| 47–49 | Region Lima |
| 50–53 | Region Mike |
| 54–57 | Region November |
| 58 | Region Oscar |

### 4.3 External / Foreign Codes (60–99)

| Code | Classification |
|------|---------------|
| 60 | External Zone A |
| 61 | External Zone B |
| 62 | External Zone C |
| 63 | External Zone D |
| 64 | External Zone E |
| 65 | External Zone F |
| 66 | External Zone G |
| 67 | External Zone H |
| 68 | External Zone I |
| 71–72 | Legacy external (pre-2001 assignments) |
| 74 | External Zone J |
| 75 | External Zone K |
| 76 | External Zone L |
| 77 | External Zone M |
| 78 | External Zone N |
| 79 | External Zone O |
| 82 | Unclassified |
| 83 | Asia-Pacific group |
| 84 | South American group |
| 85 | African group |
| 86 | European group |
| 87 | British-Irish group |
| 88 | Middle Eastern group |
| 89 | Far Eastern group |
| 90 | Caribbean group |
| 91 | North American group |
| 92 | Eastern European / Post-Soviet group |
| 93 | Miscellaneous / Other |
| 98 | Unaffiliated entity |
| 99 | Unspecified / Special case |

For our example: D₇D₈ = 07 → **Region Golf**

---

## 5. Parity Classification (D₁₂)

The check digit simultaneously serves as a binary classifier:

| D₁₂ Parity | Classification | Digit Values |
|-------------|---------------|-------------|
| Odd | **Class A** | 1, 3, 5, 7, 9 |
| Even | **Class B** | 0, 2, 4, 6, 8 |

The assigning system does not freely choose D₁₂. It iterates through sequences (D₉D₁₀D₁₁) until the computed check digit's parity matches the desired classification.

For our example: D₁₂ = 9 → Odd → **Class A**

---

## 6. Sequence Assignment Logic

The system assigns identifiers using this algorithm:

```
INPUT:  date (YYMMDD), region (RC), desired class (A or B)

FOR seq = 000 to 999:
    candidate = YYMMDD + RC + seq (11 digits)
    C = compute_checksum(candidate)

    IF C = 10:
        SKIP (no single-digit representation)

    ELSE IF C is odd AND desired class is A:
        ASSIGN → identifier = candidate + C
        STOP

    ELSE IF C is even AND desired class is B:
        ASSIGN → identifier = candidate + C
        STOP

    ELSE:
        SKIP (parity mismatch)
```

**What this means in practice:**

- ~9.1% of sequences are impossible (C = 10)
- ~45.5% of sequences yield odd check digits (Class A)
- ~45.5% of sequences yield even check digits (Class B)
- The system never "picks" the last digit — it is always computed

---

## 7. Checksum Algorithm (ISO 7064 Mod 11,2)

### 7.1 Weight Function

```
W(i) = 2^(i-1) mod 11    for i = 2, 3, ..., 12
```

Constant values:

```
W(2)=2  W(3)=4  W(4)=8  W(5)=5  W(6)=10  W(7)=9
W(8)=7  W(9)=3  W(10)=6  W(11)=1  W(12)=2
```

### 7.2 Formula

```
Given:  S = D₁D₂D₃D₄D₅D₆D₇D₈D₉D₁₀D₁₁
Let:    R = reverse(S)

Σ = Σⱼ₌₀¹⁰  R[j] × W(j+2)

C = (12 - (Σ mod 11)) mod 11

Valid iff:  C = D₁₂  ∧  C ∈ {0,1,...,9}
```

### 7.3 Edge Cases

| Condition | Result |
|-----------|--------|
| C ∈ {0–9} | Valid check digit, assign normally |
| C = 10 | Impossible sequence, skip entirely |
| (12 - remainder) = 11 | Wraps to 0 via mod 11 |
| (12 - remainder) = 12 | Wraps to 1 via mod 11 |

---

## 8. Worked Example — Full Computation

Identifier: `900523075049`

**Step 1 — Extract first 11 digits and reverse:**

```
S = [9, 0, 0, 5, 2, 3, 0, 7, 5, 0, 4]
R = [4, 0, 5, 7, 0, 3, 2, 5, 0, 0, 9]
```

**Step 2 — Multiply each reversed digit by its weight:**

```
R[0]  × W(2)  =  4 × 2  = 8
R[1]  × W(3)  =  0 × 4  = 0
R[2]  × W(4)  =  5 × 8  = 40
R[3]  × W(5)  =  7 × 5  = 35
R[4]  × W(6)  =  0 × 10 = 0
R[5]  × W(7)  =  3 × 9  = 27
R[6]  × W(8)  =  2 × 7  = 14
R[7]  × W(9)  =  5 × 3  = 15
R[8]  × W(10) =  0 × 6  = 0
R[9]  × W(11) =  0 × 1  = 0
R[10] × W(12) =  9 × 2  = 18
```

**Step 3 — Sum all products:**

```
Σ = 8 + 0 + 40 + 35 + 0 + 27 + 14 + 15 + 0 + 0 + 18 = 157
```

**Step 4 — Modular reduction:**

```
Σ mod 11 = 157 mod 11 = 3

(Verification: 14 × 11 = 154,  157 - 154 = 3)
```

**Step 5 — Compute check digit:**

```
C = (12 - 3) mod 11
C = 9 mod 11
C = 9
```

**Step 6 — Validate:**

```
Computed:  C   = 9
Actual:    D₁₂ = 9
Match:     9 = 9  ✓

Parity:    9 is odd → Class A  ✓
```

---

## 9. Complete Decoded Summary

```
Identifier:      900523075049
                  ┌──┬──┬──┬──┬───┬─┐
                  │90│05│23│07│504│9│
                  └──┴──┴──┴──┴───┴─┘
                   YY MM DD RC SEQ CHK

Date:             1990-05-23  (D₉=5 ≥ 5 → 1900s)
Region:           07 → Region Golf
Sequence:         504
Check Digit:      9 (computed, verified ✓)
Classification:   Class A (odd)
Checksum Valid:   YES
```

---

## 10. System Properties

| Property | Description |
|----------|-------------|
| Error detection | Any single-digit error in D₁–D₁₁ causes checksum mismatch |
| Dual-purpose D₁₂ | Simultaneously encodes binary classification and integrity check |
| Impossible sequences | ~9.1% of sequences yield C=10, are permanently excluded |
| Parity-balanced | ~50/50 split between Class A and Class B assignments |
| Base | Modular arithmetic over Z₁₁ |
| Standard | ISO 7064 Mod 11,2 |
| Self-validating | Any recipient can verify integrity with just the 12 digits — no external lookup required |

---

*This is a complete, self-contained specification for a structured numeric identifier system with embedded date encoding, regional classification, binary parity assignment, and weighted modular checksum validation.*
