"""
MyKad OCR Scanner v2.0
======================
Author: deadboy18 (Kesh)

Improvements over v1:
- PaddleOCR (better ID card accuracy) with EasyOCR fallback
- IC-Number-First strategy: extract IC, derive fields mathematically
- Full JPN Lampiran B state codes
- ISO 7064 Mod 11,2 checksum validation
- Perspective correction for angled photos
- CLAHE deglare preprocessing
- Camera frame guide (green = card detected)
- Confidence scoring

Install:
  pip install paddleocr paddlepaddle flask flask-cors pillow opencv-python numpy
  OR: pip install easyocr flask flask-cors pillow opencv-python numpy

Usage:
  python mykad_ocr.py                    # Web UI at http://localhost:7788
  python mykad_ocr.py --image card.jpg   # CLI mode
  python mykad_ocr.py --image card.jpg --json
"""

import os, sys, re, json, base64, io, argparse, time, threading, logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger("mykad_ocr")


def check_deps():
    missing = []
    for pkg, install in [("cv2","opencv-python"),("PIL","pillow"),
                         ("flask","flask"),("numpy","numpy"),
                         ("flask_cors","flask-cors")]:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(install)
    if missing:
        print("\n[ERROR] Missing: pip install " + " ".join(missing) + "\n")
        sys.exit(1)


check_deps()

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from flask import Flask, request, jsonify
from flask_cors import CORS


# OCR backend
OCR_BACKEND = None
_ocr_reader = None
_ocr_lock = threading.Lock()


def detect_backend():
    global OCR_BACKEND
    try:
        import paddleocr
        OCR_BACKEND = "paddle"
        logger.info("OCR backend: PaddleOCR")
        return
    except ImportError:
        pass
    try:
        import easyocr
        OCR_BACKEND = "easy"
        logger.info("OCR backend: EasyOCR (fallback)")
        return
    except ImportError:
        pass
    OCR_BACKEND = "none"
    logger.error("No OCR backend! pip install paddleocr paddlepaddle")


detect_backend()


def get_reader():
    global _ocr_reader
    with _ocr_lock:
        if _ocr_reader is None:
            if OCR_BACKEND == "paddle":
                logger.info("Initialising PaddleOCR...")
                from paddleocr import PaddleOCR
                _ocr_reader = PaddleOCR(use_angle_cls=True, lang="en",
                                         use_gpu=False, show_log=False)
                logger.info("PaddleOCR ready")
            elif OCR_BACKEND == "easy":
                logger.info("Initialising EasyOCR...")
                import easyocr
                _ocr_reader = easyocr.Reader(["en"], gpu=False, verbose=False)
                logger.info("EasyOCR ready")
    return _ocr_reader


def run_ocr(img_array):
    """Returns list of (text, confidence) tuples."""
    reader = get_reader()
    if reader is None:
        return []
    if OCR_BACKEND == "paddle":
        result = reader.ocr(img_array, cls=True)
        out = []
        if result and result[0]:
            for line in result[0]:
                bbox, (text, conf) = line
                out.append((text.strip(), float(conf)))
        return out
    elif OCR_BACKEND == "easy":
        result = reader.readtext(img_array, detail=1)
        return [(text.strip(), float(conf)) for (_, text, conf) in result]
    return []


# Full JPN Lampiran B state codes
# Official JPN Lampiran B state codes + IC validator extended codes
# Primary codes 01-16 are from official Lampiran B
# 21-93 are secondary/extended codes used in IC numbers (not in Lampiran B but observed in practice)
IC_STATE_CODES = {
    # Official Lampiran B primary codes
    "01": "Johor",
    "02": "Kedah",
    "03": "Kelantan",
    "04": "Melaka",
    "05": "Negeri Sembilan",
    "06": "Pahang",
    "07": "Pulau Pinang",
    "08": "Perak",
    "09": "Perlis",
    "10": "Selangor",
    "11": "Terengganu",
    "12": "Sabah",
    "13": "Sarawak",
    "14": "Wilayah Persekutuan Kuala Lumpur",
    "15": "Wilayah Persekutuan Labuan",
    "16": "Wilayah Persekutuan Putrajaya",
    # Secondary/extended codes (IC validator data)
    "21": "Johor", "22": "Johor", "23": "Johor", "24": "Johor",
    "25": "Kedah", "26": "Kedah", "27": "Kedah",
    "28": "Kelantan", "29": "Kelantan",
    "30": "Melaka", "31": "Negeri Sembilan",
    "32": "Pahang", "33": "Pahang", "34": "Pahang",
    "35": "Pulau Pinang", "36": "Pulau Pinang",
    "37": "Perak", "38": "Perak", "39": "Perak",
    "40": "Perlis",
    "41": "Selangor", "42": "Selangor", "43": "Selangor", "44": "Selangor",
    "45": "Terengganu", "46": "Terengganu",
    "47": "Sabah", "48": "Sabah", "49": "Sabah",
    "50": "Sarawak", "51": "Sarawak", "52": "Sarawak", "53": "Sarawak",
    "54": "Wilayah Persekutuan Kuala Lumpur", "55": "Wilayah Persekutuan Kuala Lumpur",
    "56": "Wilayah Persekutuan Kuala Lumpur", "57": "Wilayah Persekutuan Kuala Lumpur",
    "58": "Wilayah Persekutuan Labuan", "59": "Negeri Sembilan",
    # Foreign born
    "60": "Brunei", "61": "Indonesia", "62": "Cambodia / Kampuchea", "63": "Laos",
    "64": "Myanmar", "65": "Philippines", "66": "Singapore",
    "67": "Thailand", "68": "Vietnam",
    "71": "Luar Negara (sebelum 2001)", "72": "Luar Negara (sebelum 2001)",
    "74": "China", "75": "India", "76": "Pakistan",
    "77": "Arab Saudi", "78": "Sri Lanka", "79": "Bangladesh",
    "82": "Negeri Tidak Diketahui",
    "83": "Asia Pasifik", "84": "Amerika Selatan", "85": "Afrika",
    "86": "Eropah", "87": "Britain / Ireland", "88": "Timur Tengah",
    "89": "Asia Timur (Jepun/Korea/Taiwan)", "90": "Caribbean / Amerika Tengah",
    "91": "Amerika Utara", "92": "Republik Soviet (bekas)", "93": "Lain-lain",
    # Lampiran B special codes
    "98": "Luar Negeri",
    "99": "Lain-lain Daerah",
}


def validate_ic_checksum(ic_clean):
    """ISO 7064 Mod 11,2. Returns True/False/None."""
    if len(ic_clean) != 12 or not ic_clean.isdigit():
        return None
    digits = [int(d) for d in ic_clean]
    work = list(reversed(digits[:11]))
    total = sum(work[j] * (pow(2, j + 1) % 11) for j in range(11))
    check = (12 - (total % 11)) % 11
    if check == 10:
        return False
    return check == digits[11]


def parse_ic_number(ic_clean):
    """Derive all fields from IC number mathematically."""
    if len(ic_clean) != 12 or not ic_clean.isdigit():
        return {}
    from datetime import date
    yy = int(ic_clean[0:2])
    mm = int(ic_clean[2:4])
    dd = int(ic_clean[4:6])
    state_code = ic_clean[6:8]
    last_digit = int(ic_clean[11])
    today = date.today()
    cur_yy = today.year % 100
    century = 1900 if (yy > cur_yy and yy > 0) else 2000
    birth_year = century + yy
    dob_str = ""
    age = None
    try:
        dob = date(birth_year, mm, dd)
        dob_str = dob.isoformat()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    except ValueError:
        pass
    gender = "Male" if last_digit % 2 == 1 else "Female"
    birth_place = IC_STATE_CODES.get(state_code, "Code " + state_code)
    checksum_ok = validate_ic_checksum(ic_clean)
    return {"dob": dob_str, "age": age, "gender": gender,
            "birth_place": birth_place, "_state_code": state_code,
            "_checksum_ok": checksum_ok}


def correct_perspective(img):
    """Detect card quad and apply perspective warp."""
    try:
        h, w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blur, 30, 100)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
        closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return img
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        for c in contours[:5]:
            area = cv2.contourArea(c)
            if area < h * w * 0.15:
                continue
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            if len(approx) == 4:
                pts = approx.reshape(4, 2).astype(np.float32)
                s = pts.sum(axis=1)
                diff = np.diff(pts, axis=1)
                ordered = np.array([pts[np.argmin(s)], pts[np.argmin(diff)],
                    pts[np.argmax(s)], pts[np.argmax(diff)]], dtype=np.float32)
                tw = max(w, 800)
                th = int(tw / 1.585)
                dst = np.array([[0,0],[tw,0],[tw,th],[0,th]], dtype=np.float32)
                M = cv2.getPerspectiveTransform(ordered, dst)
                warped = cv2.warpPerspective(img, M, (tw, th))
                logger.info("Perspective corrected")
                return warped
    except Exception as e:
        logger.debug("Perspective skip: %s", e)
    return img


def apply_clahe(img):
    """CLAHE contrast enhancement for glare reduction."""
    try:
        lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        lab2 = cv2.merge([clahe.apply(l), a, b])
        return cv2.cvtColor(lab2, cv2.COLOR_LAB2RGB)
    except Exception:
        return img


def preprocess(img):
    h, w = img.shape[:2]
    if w < 1200:
        scale = 1200 / w
        img = cv2.resize(img, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_CUBIC)
    img = correct_perspective(img)
    h2, w2 = img.shape[:2]
    if h2 > w2:
        img = np.rot90(img)
    img = apply_clahe(img)
    return img


def crop_norm(img, t, l, b, r):
    h, w = img.shape[:2]
    return img[int(t*h):int(b*h), int(l*w):int(r*w)]


# MyKad region definitions (normalised t,l,b,r for landscape orientation)
# Calibrated from real MyKad layout:
#  - IC number: top-centre, large bold
#  - Name: below IC number, left side
#  - Address: below name, left side
#  - WARGANEGARA/religion: bottom-right of text area
#  - Face: right side, behind/above text area
REGIONS = {
    "ic":      (0.07, 0.15, 0.35, 0.68),  # wider to catch IC number better
    "name":    (0.35, 0.03, 0.58, 0.58),  # name line
    "address": (0.52, 0.03, 0.90, 0.58),  # address block
    "warga":   (0.62, 0.45, 0.97, 0.87),  # warganegara/religion/gender block
}


IC_RE = re.compile(r"\b(\d{6})[\s\-]+(\d{2})[\s\-]+(\d{4})\b")
IC_PLAIN = re.compile(r"\b(\d{12})\b")
IC_SPACED = re.compile(r"\b(\d{6})\s+(\d{2})\s+(\d{4})\b")


def find_ic(texts):
    for t in texts:
        cleaned = re.sub(r"[^0-9\s\-]", "", t)
        m = IC_RE.search(cleaned)
        if m:
            cand = m.group(1) + m.group(2) + m.group(3)
            if len(cand) == 12:
                return m.group(1) + "-" + m.group(2) + "-" + m.group(3)
        m = IC_SPACED.search(cleaned)
        if m:
            return m.group(1) + "-" + m.group(2) + "-" + m.group(3)
        m = IC_PLAIN.search(cleaned)
        if m:
            raw = m.group(1)
            return raw[:6] + "-" + raw[6:8] + "-" + raw[8:]
    return ""


def ocr_region_enhanced(img, region_key):
    region = crop_norm(img, *REGIONS[region_key])
    if region.size == 0:
        return []
    gray = cv2.cvtColor(region, cv2.COLOR_RGB2GRAY)
    up = cv2.resize(gray, (gray.shape[1]*2, gray.shape[0]*2), interpolation=cv2.INTER_CUBIC)
    thresh = cv2.adaptiveThreshold(up, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY, 15, 8)
    proc = cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB)
    results = run_ocr(proc)
    return [t for (t, c) in results if t.strip()]


def extract_ic_from_image(img):
    texts = ocr_region_enhanced(img, "ic")
    logger.info("IC region texts: %s", texts)
    ic = find_ic(texts)
    if not ic:
        full_texts = [t for (t, c) in run_ocr(img)]
        ic = find_ic(full_texts)
        if ic:
            logger.info("IC found via full-image fallback: %s", ic)
    return ic


MY_STATES_UPPER = [
    "JOHOR", "KEDAH", "KELANTAN", "MELAKA", "NEGERI SEMBILAN", "PAHANG",
    "PULAU PINANG", "PERAK", "PERLIS", "SELANGOR", "TERENGGANU", "SABAH",
    "SARAWAK", "KUALA LUMPUR", "LABUAN", "PUTRAJAYA", "W. PERSEKUTUAN",
    "WILAYAH PERSEKUTUAN", "W.P.",
]
POSTCODE_RE = re.compile(r"\b(\d{5})\b")


def is_name_line(text):
    """
    Determine if a line of OCR text is likely a person's name.
    Malaysian names: mostly ALL CAPS, may include:
      BIN, BINTI, A/L, A/P, @, common Malay/Chinese/Indian name patterns
    """
    t = text.strip()
    # Minimum length
    if len(t) < 4: return False
    # Strip common OCR noise chars
    t_clean = re.sub(r"[^A-Za-z /\\@\.\-]", " ", t).strip()
    if len(t_clean) < 4: return False
    letters = re.sub(r"[^A-Za-z]", "", t_clean)
    if len(letters) < 3: return False

    # Must be mostly uppercase (names are printed in caps on MyKad)
    upper_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
    if upper_ratio < 0.70: return False  # slightly looser to handle OCR case errors

    # Reject known non-name keywords
    non_name_kw = [
        "WARGANEGARA", "ISLAM", "BUDDHA", "LELAKI", "PEREMPUAN",
        "JALAN", "BLOK", "LORONG", "TAMAN", "FLAT", "DESA", "SRI",
        "KRISTIAN", "HINDU", "SIKH", "TIADA", "KAD", "PENGENALAN",
        "MALAYSIA", "IDENTITY", "CARD", "MYKAD",
        "KAWASAN", "BANDAR", "PEKAN", "MUKIM",
        "CONTOH", "SAMPLE", "SELANGOR", "PERAK", "JOHOR", "KEDAH",
        "KELANTAN", "MELAKA", "PAHANG", "PINANG", "SABAH", "SARAWAK",
        "TERENGGANU", "PUTRAJAYA", "LABUAN",
    ]
    t_up = t.upper()
    if any(kw in t_up for kw in non_name_kw): return False

    # Positive signal: contains typical Malaysian name patterns
    positive_kw = ["BIN", "BINTI", "BINTE", "A/L", "A/P", "@"]
    has_positive = any(kw in t_up for kw in positive_kw)

    # Name should have at least one word >= 3 letters
    words = [w for w in t_clean.split() if len(re.sub(r"[^A-Za-z]","",w)) >= 3]
    if not words and not has_positive: return False

    # Final: if it has a positive keyword, it IS a name
    if has_positive: return True

    # Otherwise: must have 2+ words and mostly uppercase
    return len(t_clean.split()) >= 2 and upper_ratio >= 0.80


def clean_addr_line(line):
    """Clean up a single address line from OCR output."""
    t = line.strip()
    # Remove leading/trailing punctuation noise
    t = re.sub(r"^[,\.\-\/\s]+", "", t)
    t = re.sub(r"[,\.\-\/\s]+$", "", t)
    return t.strip()

def is_valid_addr_line(line):
    """Check if a line is a real address component."""
    t = line.strip()
    if len(t) < 3: return False
    # Reject: standalone numbers 1-3 digits
    if re.match(r"^\d{1,3}$", t): return False
    # Reject: known noise words
    noise = {"NO","NO.","NUM","NOMBOR","UNIT","ARAS","TINGKAT"}
    if t.upper() in noise: return False
    # Reject: single-word that's less than 3 chars after stripping non-alpha
    alpha = re.sub(r"[^A-Za-z]","",t)
    if len(alpha) < 2: return False
    return True

def extract_name_address(img):
    out = {"name":"","address1":"","address2":"","address3":"",
           "postcode":"","city":"","state":""}
    all_texts = []
    for rk in ["name","address"]:
        region = crop_norm(img, *REGIONS[rk])
        if region.size == 0: continue
        gray = cv2.cvtColor(region, cv2.COLOR_RGB2GRAY)
        up = cv2.resize(gray,(gray.shape[1]*2,gray.shape[0]*2),interpolation=cv2.INTER_CUBIC)
        # Multiple preprocessing passes for better accuracy
        # Pass 1: denoised
        denoised = cv2.fastNlMeansDenoising(up, h=10)
        proc = cv2.cvtColor(denoised, cv2.COLOR_GRAY2RGB)
        results = run_ocr(proc)
        texts = [t for (t,c) in results if c > 0.25 and t.strip()]
        logger.info("%s texts: %s", rk, texts)
        all_texts.extend(texts)

    if not all_texts: return out

    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for t in all_texts:
        key = t.strip().upper()
        if key not in seen:
            seen.add(key)
            deduped.append(t)
    all_texts = deduped

    name_idx = -1
    for i, t in enumerate(all_texts):
        if is_name_line(t):
            out["name"] = t.strip()
            name_idx = i; break

    addr_lines = all_texts[name_idx+1:] if name_idx >= 0 else all_texts

    # Extract state (last line usually)
    state_found = ""
    state_idx = -1
    for i, line in enumerate(addr_lines):
        lu = line.upper()
        if any(s in lu for s in MY_STATES_UPPER):
            state_found = line.strip()
            state_idx = i; break

    # Extract postcode + city
    postcode_line = None
    postcode_idx = -1
    for i, line in enumerate(addr_lines):
        pm = POSTCODE_RE.search(line)
        if pm:
            out["postcode"] = pm.group(1)
            after = line[pm.end():].strip().lstrip(",").strip()
            if after and len(after) > 2:
                out["city"] = after
            postcode_line = line
            postcode_idx = i; break

    # City might be on next line after postcode
    if out["postcode"] and not out["city"] and postcode_idx >= 0:
        for line in addr_lines[postcode_idx+1:]:
            if len(line.strip()) > 2 and line.strip().upper() != state_found.upper():
                out["city"] = line.strip()
                break

    # Build address lines excluding postcode/city/state lines
    skip_lines = set()
    if state_found: skip_lines.add(state_found.upper())
    if postcode_line: skip_lines.add(postcode_line.upper())
    if out["city"]: skip_lines.add(out["city"].upper())

    addr_clean = []
    for line in addr_lines:
        cleaned = clean_addr_line(line)
        if not cleaned: continue
        if cleaned.upper() in skip_lines: continue
        if cleaned == out["name"]: continue
        if not is_valid_addr_line(cleaned): continue
        # Avoid duplicating the city in address lines
        if out["city"] and cleaned.upper() == out["city"].upper(): continue
        addr_clean.append(cleaned)

    if addr_clean: out["address1"] = addr_clean[0]
    if len(addr_clean)>1: out["address2"] = addr_clean[1]
    if len(addr_clean)>2: out["address3"] = addr_clean[2]
    if state_found: out["state"] = state_found
    return out


def extract_warga(img):
    out = {"nationality":"","race":"","religion":""}
    region = crop_norm(img, *REGIONS["warga"])
    if region.size == 0: return out
    gray = cv2.cvtColor(region, cv2.COLOR_RGB2GRAY)
    up = cv2.resize(gray,(gray.shape[1]*2,gray.shape[0]*2),interpolation=cv2.INTER_CUBIC)
    proc = cv2.cvtColor(up, cv2.COLOR_GRAY2RGB)
    results = run_ocr(proc)
    combined = " ".join(t.upper() for (t,_) in results)
    if "WARGANEGARA" in combined: out["nationality"] = "WARGANEGARA"
    elif "PENDUDUK TETAP" in combined: out["nationality"] = "PENDUDUK TETAP"
    for rel in ["ISLAM","KRISTIAN","BUDDHA","HINDU","SIKH","TIADA AGAMA"]:
        if rel in combined: out["religion"] = rel.title(); break
    for race in ["MELAYU","CINA","INDIA","KADAZAN","IBAN","DUSUN","MURUT",
                  "BAJAU","SIKH","ORANG ASLI","MELANAU","BIDAYUH"]:
        if race in combined: out["race"] = race.title(); break
    return out


def extract_face(img):
    """
    Extract face photo from MyKad.
    MyKad layout (landscape): face is right-centre, roughly:
      - Top 10-85% of card height
      - Right 52-72% of card width
    The holographic ghost/watermark is in the bottom-right corner (>70% width, >65% height)
    — we avoid that region by cropping conservatively.
    We use Haar cascade to find the LARGEST face (most likely the real photo, not hologram).
    """
    try:
        h, w = img.shape[:2]
        # Primary face region: right ~52-72%, top ~10-88%
        # This avoids the chip (left) and the holographic watermark (far right bottom)
        face_reg = crop_norm(img, 0.08, 0.52, 0.88, 0.73)
        if face_reg.size == 0: return ""

        path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        if os.path.exists(path):
            cascade = cv2.CascadeClassifier(path)
            gray = cv2.cvtColor(face_reg, cv2.COLOR_RGB2GRAY)
            # Detect all faces, pick the LARGEST (real photo vs tiny hologram ghost)
            faces = cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=3,
                                              minSize=(30, 30))
            if len(faces) > 0:
                # Sort by area descending, take largest
                faces = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
                x, y, fw, fh = faces[0]
                # Verify it's a reasonable size (at least 15% of region width)
                if fw > face_reg.shape[1] * 0.15:
                    pad = 10
                    x = max(0, x-pad); y = max(0, y-pad)
                    fw = min(face_reg.shape[1]-x, fw+pad*2)
                    fh = min(face_reg.shape[0]-y, fh+pad*2)
                    face_reg = face_reg[y:y+fh, x:x+fw]
                    logger.info("Face detected by cascade: %dx%d", fw, fh)
                else:
                    logger.debug("Detected face too small (%d), using region crop", fw)

        # Ensure the region has colour (not greyscale hologram)
        # Check colour saturation — real photo has colour, hologram is near-greyscale
        hsv = cv2.cvtColor(face_reg, cv2.COLOR_RGB2HSV)
        mean_sat = hsv[:,:,1].mean()
        logger.info("Face region mean saturation: %.1f", mean_sat)
        if mean_sat < 15:
            # Very low saturation = likely holographic ghost, not real photo
            logger.warning("Face region appears to be greyscale/hologram (sat=%.1f), skipping", mean_sat)
            return ""

        pil = Image.fromarray(face_reg)
        buf = io.BytesIO()
        pil.save(buf, format="JPEG", quality=88)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        logger.debug("Face extract failed: %s", e)
        return ""


def extract_mykad(image_path=None, image_bytes=None):
    t0 = time.time()
    result = {
        "ic":"","name":"","dob":"","age":None,"gender":"",
        "nationality":"WARGANEGARA","race":"","religion":"",
        "address1":"","address2":"","address3":"",
        "postcode":"","city":"","state":"","birth_place":"",
        "old_ic":"","socso":"","photo_b64":"",
        "_ocr":True,"_backend":OCR_BACKEND,
        "_ic_checksum_valid":None,"_confidence":0,
        "_warnings":[],"_processing_time_s":0.0,
    }
    try:
        if image_bytes:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        elif image_path:
            img = cv2.imread(image_path)
            if img is None: raise ValueError("Cannot read: " + image_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            raise ValueError("No image")
    except Exception as e:
        result["_warnings"].append("Image load: " + str(e)); return result
    img = preprocess(img)
    logger.info("Preprocessed: %dx%d", img.shape[1], img.shape[0])
    logger.info("Step 1: IC number...")
    ic = extract_ic_from_image(img)
    result["ic"] = ic
    if ic:
        ic_clean = ic.replace("-","")
        derived = parse_ic_number(ic_clean)
        result.update(derived)
        result["_ic_checksum_valid"] = derived.get("_checksum_ok")
        logger.info("IC=%s DOB=%s Gender=%s Place=%s Checksum=%s",
                    ic,derived.get("dob"),derived.get("gender"),
                    derived.get("birth_place"),derived.get("_checksum_ok"))
    else:
        result["_warnings"].append(
            "IC number not detected. Try: better lighting, card flat, no glare.")
    logger.info("Step 2: Name + address...")
    na = extract_name_address(img)
    result.update({k:v for k,v in na.items() if v})
    logger.info("Step 3: Nationality/race/religion...")
    wg = extract_warga(img)
    result.update({k:v for k,v in wg.items() if v})
    logger.info("Step 4: Face photo...")
    photo = extract_face(img)
    if photo: result["photo_b64"] = photo
    score = 0
    if result["ic"]:          score += 40
    if result["name"]:        score += 20
    if result["address1"]:    score += 10
    if result["dob"]:         score += 10
    if result["gender"]:      score += 5
    if result["birth_place"]: score += 5
    if result["state"]:       score += 5
    if result["photo_b64"]:   score += 5
    result["_confidence"] = score
    result["_processing_time_s"] = round(time.time()-t0, 2)
    logger.info("Done: %.2fs IC=%s Name=%s Conf=%d%%",
                result["_processing_time_s"],result["ic"],result["name"],score)
    return result


app = Flask(__name__)
CORS(app)

# Web UI HTML (stored as a module-level string to avoid file dependency)
_HTML = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ocr_ui.html")).read() if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ocr_ui.html")) else None

BASIC_HTML = """
<!DOCTYPE html>
<html lang="en" data-theme="dark"><head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>MyKad OCR v2</title>
<style>
:root{--a:#00e5a0;--a2:#2563eb;}
[data-theme=dark]{--bg:#000;--bg2:#0d0d0d;--bg3:#1a1a1a;--bdr:rgba(255,255,255,.08);--t:#f0f0f0;--t2:#888;--t3:#444;}
[data-theme=light]{--bg:#f0f2f8;--bg2:#fff;--bg3:#f5f5f5;--bdr:rgba(0,0,0,.1);--t:#0a0a14;--t2:#555;--t3:#bbb;}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:system-ui,sans-serif;background:var(--bg);color:var(--t);padding:16px;max-width:960px;margin:0 auto;}
h1{font-size:20px;font-weight:800;background:linear-gradient(135deg,var(--a),var(--a2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:3px;}
.sub{font-size:11.5px;color:var(--t2);margin-bottom:14px;}
.layout{display:grid;grid-template-columns:1fr 1fr;gap:14px;}
@media(max-width:720px){.layout{grid-template-columns:1fr;}}
.card{background:var(--bg2);border:1.5px solid var(--bdr);border-radius:10px;padding:14px;margin-bottom:10px;}
.ch{font-size:10px;font-weight:800;color:var(--t2);text-transform:uppercase;letter-spacing:.1em;margin-bottom:10px;}
.cam-wrap{position:relative;background:#000;border-radius:8px;overflow:hidden;margin-bottom:8px;display:none;}
#camvid{width:100%;display:block;max-height:240px;object-fit:cover;}
.cam-overlay{position:absolute;inset:0;pointer-events:none;display:flex;align-items:center;justify-content:center;}
.cam-frame{width:82%;aspect-ratio:1.585;border:3px solid var(--fc,rgba(255,255,255,.4));border-radius:6px;transition:border-color .3s,box-shadow .3s;box-shadow:0 0 0 1500px rgba(0,0,0,.4);position:relative;}
.cam-frame.ok{--fc:#00e5a0;box-shadow:0 0 0 1500px rgba(0,0,0,.4),0 0 16px rgba(0,229,160,.5);}
.cam-frame.bad{--fc:#ef4444;box-shadow:0 0 0 1500px rgba(0,0,0,.4),0 0 16px rgba(239,68,68,.4);}
.cam-frame::before,.cam-frame::after,.cbr,.cbl{content:"";position:absolute;width:16px;height:16px;border-color:var(--fc,rgba(255,255,255,.8));border-style:solid;}
.cam-frame::before{top:-3px;left:-3px;border-width:3px 0 0 3px;border-radius:4px 0 0 0;}
.cam-frame::after{top:-3px;right:-3px;border-width:3px 3px 0 0;border-radius:0 4px 0 0;}
.cbr{position:absolute;bottom:-3px;right:-3px;border-width:0 3px 3px 0;border-radius:0 0 4px 0;}
.cbl{position:absolute;bottom:-3px;left:-3px;border-width:0 0 3px 3px;border-radius:0 0 0 4px;}
.cam-hint{position:absolute;bottom:6px;left:50%;transform:translateX(-50%);background:rgba(0,0,0,.65);color:#fff;font-size:11px;font-weight:600;padding:3px 10px;border-radius:99px;white-space:nowrap;}
.cam-hint.ok{color:#00e5a0;}.cam-hint.bad{color:#f87171;}
.cam-row{display:flex;gap:7px;margin-bottom:8px;flex-wrap:wrap;}
.drop{border:2px dashed var(--bdr);border-radius:8px;padding:24px 12px;text-align:center;cursor:pointer;transition:.15s;}
.drop:hover,.drop.over{border-color:var(--a);background:rgba(0,229,160,.04);}
#prev{width:100%;max-height:180px;object-fit:contain;border-radius:6px;display:none;margin-top:6px;border:1px solid var(--bdr);}
.btn{display:inline-flex;align-items:center;gap:5px;padding:8px 16px;border-radius:8px;font-size:12px;font-weight:700;cursor:pointer;border:none;transition:all .12s;font-family:inherit;}
.btn-a{background:linear-gradient(135deg,var(--a),var(--a2));color:#000;width:100%;justify-content:center;margin-top:8px;font-size:13px;}
.btn-a:hover{opacity:.9;}.btn-a:disabled{opacity:.35;cursor:not-allowed;}
.btn-s{background:var(--bg3);border:1.5px solid var(--bdr);color:var(--t);}
.btn-s:hover{border-color:var(--a);}
.rh{display:flex;gap:10px;align-items:flex-start;margin-bottom:12px;}
#faceimg{width:68px;height:85px;object-fit:cover;border-radius:7px;border:2px solid var(--bdr);display:none;flex-shrink:0;}
.face-ph{width:68px;height:85px;display:flex;align-items:center;justify-content:center;font-size:26px;opacity:.25;background:var(--bg3);border-radius:7px;border:2px solid var(--bdr);flex-shrink:0;}
.oname{font-size:16px;font-weight:800;color:var(--t);margin-bottom:2px;}
.oic{font-family:monospace;font-size:13px;color:var(--a);margin-bottom:5px;}
.conf-row{display:flex;align-items:center;gap:7px;font-size:11px;color:var(--t2);margin:7px 0;}
.cbar{flex:1;height:4px;background:var(--bg3);border-radius:2px;overflow:hidden;}
.cfill{height:100%;border-radius:2px;background:linear-gradient(90deg,var(--a),var(--a2));transition:width .5s;}
.warn-box{background:rgba(245,158,11,.1);border:1px solid rgba(245,158,11,.25);border-radius:7px;padding:8px 10px;color:#fbbf24;font-size:11.5px;margin-top:7px;line-height:1.6;}
.ftbl{width:100%;border-collapse:collapse;font-size:12px;}
.ftbl td{padding:4px 7px;border-bottom:1px solid var(--bdr);}
.ftbl tr:last-child td{border-bottom:none;}
.ftbl td:first-child{color:var(--t2);font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.04em;width:36%;}
.ftbl td:last-child{font-family:monospace;font-size:11.5px;color:var(--t);}
.ftbl td.fic{color:var(--a);}
.spin{width:26px;height:26px;border:3px solid var(--bg3);border-top-color:var(--a);border-radius:50%;animation:sp .6s linear infinite;margin:0 auto 8px;}
@keyframes sp{to{transform:rotate(360deg)}}
.scanning{text-align:center;padding:28px;display:none;}
.scanning.show{display:block;}
.empty{text-align:center;padding:28px;color:var(--t3);font-size:12px;}
.jbox{background:#03040a;border:1px solid var(--bdr);border-radius:7px;padding:10px;font-family:monospace;font-size:10px;color:#00e5a0;white-space:pre-wrap;overflow:auto;max-height:220px;margin-top:7px;display:none;}
.topbar{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px;}
.tip{background:rgba(0,229,160,.05);border:1px solid rgba(0,229,160,.12);border-radius:7px;padding:8px 10px;color:var(--t2);font-size:11px;margin-top:8px;line-height:1.7;}
</style>
</head><body>
<div class="topbar"><div>
<h1>MyKad OCR Scanner v2</h1>
<div class="sub">IC-first strategy &middot; Offline &middot; deadboy18 &middot; Backend: <span id="be">checking...</span></div>
</div>
<button class="btn btn-s" onclick="toggleTheme()">&#127769; Theme</button>
</div>
<div class="layout">
<div>
<div class="card">
<div class="ch">&#128247; Camera</div>
<div class="cam-wrap" id="camwrap">
<video id="camvid" autoplay playsinline muted></video>
<div class="cam-overlay">
<div class="cam-frame" id="camframe"><div class="cbr"></div><div class="cbl"></div></div>
</div>
<div class="cam-hint" id="camhint">Align card &mdash; auto-captures when ready</div>
</div>
<div class="cam-row">
<button class="btn btn-s" id="btn-start" onclick="startCam()">&#128247; Open Camera</button>
<button class="btn btn-s" id="btn-snap" onclick="snapCam()" style="display:none">&#128248; Capture</button>
<button class="btn btn-s" id="btn-stop" onclick="stopCam()" style="display:none">&#10005; Stop</button>
<button class="btn btn-s" id="btn-flip" onclick="flipCam()" style="display:none;font-size:11px">&#128260; Flip</button>
</div>
<canvas id="camcanvas" style="display:none"></canvas>
</div>
<div class="card">
<div class="ch">&#128193; Upload Image</div>
<div class="drop" id="dropzone" onclick="document.getElementById('fi').click()"
 ondragover="event.preventDefault();this.classList.add('over')"
 ondragleave="this.classList.remove('over')"
 ondrop="handleDrop(event)">
<input type="file" id="fi" accept="image/*" onchange="handleFile(this.files[0])"/>
<div style="font-size:32px;opacity:.3">&#128268;</div>
<div style="font-size:12px;color:var(--t2);margin-top:5px">Drop MyKad front face here or click to browse</div>
<div style="font-size:11px;color:var(--t3);margin-top:3px">JPG &middot; PNG &middot; WEBP &mdash; full card, good lighting</div>
</div>
<img id="prev" alt="Preview"/>
<button class="btn btn-a" id="sbtn" disabled onclick="doScan()">&#9711; Extract Data</button>
<div class="tip">&#10003; Card flat &amp; fully visible<br/>&#10003; Even lighting, no glare on IC number<br/>&#10003; Sharp focus, clean lens<br/>&#10003; Whole card in frame</div>
</div>
</div>
<div>
<div class="card">
<div class="ch">&#128203; Extracted Data</div>
<div class="scanning" id="scanning">
<div class="spin"></div>
<div style="color:var(--t2);font-size:12px" id="scanmsg">Running OCR...</div>
<div style="color:var(--t3);font-size:10.5px;margin-top:3px">First run: ~30s (model download). Subsequent: ~3-5s CPU.</div>
</div>
<div class="empty" id="emptystate">Upload or capture a MyKad front face to extract data</div>
<div id="resbody" style="display:none">
<div class="rh">
<div><div class="face-ph" id="faceph">&#129489;</div><img id="faceimg" alt="face"/></div>
<div style="flex:1;min-width:0">
<div class="oname" id="oname">-</div>
<div class="oic" id="oic">-</div>
</div>
</div>
<div class="conf-row">
<span>Confidence</span>
<div class="cbar"><div class="cfill" id="cfill" style="width:0"></div></div>
<span id="cpct" style="font-family:monospace;font-size:11px">0%</span>
<span style="margin-left:6px;font-size:11px">Time: <span id="otime" style="font-family:monospace">-</span>s</span>
</div>
<div id="warnbox"></div>
<table class="ftbl" id="ftbl" style="margin-top:7px"></table>
<div style="display:flex;gap:6px;margin-top:8px;flex-wrap:wrap;">
<button class="btn btn-s" onclick="toggleJ()">{ } JSON</button>
<button class="btn btn-s" onclick="copyJ()">&#128203; Copy</button>
<button class="btn btn-s" onclick="saveSrv()">&#128190; Save to Server</button>
</div>
<div class="jbox" id="jbox"></div>
</div>
</div>
</div>
</div>
<script>
var cur=null,last=null,camStream=null,facing="environment",frameTimer=null;
fetch("/backend").then(function(r){return r.json();}).then(function(d){
  document.getElementById("be").textContent=d.backend+(d.ready?" (ready)":" (loading...)");
}).catch(function(){});
function toggleTheme(){
  var d=document.documentElement;
  d.setAttribute("data-theme",d.getAttribute("data-theme")==="dark"?"light":"dark");
}
function startCam(){
  if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia){alert("Camera not available on this browser/device.");return;}
  navigator.mediaDevices.getUserMedia({video:{facingMode:facing,width:{ideal:1920}}}).then(function(stream){
    camStream=stream;
    var v=document.getElementById("camvid");v.srcObject=stream;
    document.getElementById("camwrap").style.display="block";
    document.getElementById("btn-snap").style.display="";
    document.getElementById("btn-stop").style.display="";
    document.getElementById("btn-flip").style.display="";
    document.getElementById("btn-start").style.display="none";
    startFrameCheck();
  }).catch(function(e){alert("Camera error: "+e.message);});
}
function flipCam(){
  facing=facing==="environment"?"user":"environment";
  stopCam();setTimeout(startCam,300);
}
function stopCam(){
  if(camStream){camStream.getTracks().forEach(function(t){t.stop();});camStream=null;}
  stopFrameCheck();
  document.getElementById("camwrap").style.display="none";
  document.getElementById("btn-snap").style.display="none";
  document.getElementById("btn-stop").style.display="none";
  document.getElementById("btn-flip").style.display="none";
  document.getElementById("btn-start").style.display="";
}
function snapCam(){
  var v=document.getElementById("camvid"),c=document.getElementById("camcanvas");
  c.width=v.videoWidth;c.height=v.videoHeight;
  c.getContext("2d").drawImage(v,0,0);
  c.toBlob(function(blob){
    cur=new File([blob],"cam.jpg",{type:"image/jpeg"});
    var pr=document.getElementById("prev");
    pr.src=URL.createObjectURL(blob);pr.style.display="block";
    document.getElementById("sbtn").disabled=false;
    _autoCapturing=false;_goodFrameCount=0;
    stopCam();
    // Auto scan immediately after capture
    setTimeout(doScan,200);
  },"image/jpeg",0.94);
}
// Auto-capture state
var _goodFrameCount = 0;
var _autoCapturing = false;
var _GOOD_FRAMES_NEEDED = 3;  // need N consecutive good frames before auto-capturing
var _lastSharpness = 0;

function startFrameCheck(){frameTimer=setInterval(checkFrame,400);}  // check faster
function stopFrameCheck(){
  if(frameTimer){clearInterval(frameTimer);frameTimer=null;}
  _goodFrameCount=0;_autoCapturing=false;
  setGuide("","Align card within the frame");
}
function setGuide(cls,msg){
  var g=document.getElementById("camframe"),h=document.getElementById("camhint");
  g.className="cam-frame "+cls;h.textContent=msg;h.className="cam-hint "+cls;
}

function measureSharpness(ctx,gx,gy,gw,gh){
  // Laplacian variance as sharpness metric — blurry images have low variance
  var imgd=ctx.getImageData(gx,gy,gw,gh);
  var data=imgd.data,w=gw,h=gh;
  if(w<4||h<4)return 0;
  var lap=0,cnt=0;
  for(var y=1;y<h-1;y+=4){for(var x=1;x<w-1;x+=4){
    var i=(y*w+x)*4;
    // grey value
    var c=(data[i]+data[i+1]+data[i+2])/3;
    var n=((y-1)*w+x)*4; var s=((y+1)*w+x)*4;
    var lv=((data[n]+data[n+1]+data[n+2])/3);
    var sv=((data[s]+data[s+1]+data[s+2])/3);
    var wv=((data[(y*w+x-1)*4]+data[(y*w+x-1)*4+1]+data[(y*w+x-1)*4+2])/3);
    var ev=((data[(y*w+x+1)*4]+data[(y*w+x+1)*4+1]+data[(y*w+x+1)*4+2])/3);
    var diff=Math.abs(-4*c+lv+sv+wv+ev);
    lap+=diff;cnt++;
  }}
  return cnt>0?lap/cnt:0;
}

function checkFrame(){
  var v=document.getElementById("camvid");
  if(!v||!camStream||v.readyState<2)return;
  if(_autoCapturing)return;
  var c=document.getElementById("camcanvas");
  c.width=v.videoWidth||320;c.height=v.videoHeight||240;
  var ctx=c.getContext("2d");ctx.drawImage(v,0,0);
  var w=c.width,h=c.height;
  var imgd=ctx.getImageData(0,0,w,h);
  var data=imgd.data;

  // Measure brightness inside guide frame region
  var gx=Math.floor(w*0.11),gy=Math.floor(h*0.08);
  var gw=Math.floor(w*0.78),gh=Math.floor(h*0.84);
  var bs=0,cnt=0,step=6;
  for(var y=gy;y<gy+gh&&y<h;y+=step){for(var x=gx;x<gx+gw&&x<w;x+=step){
    var i=(y*w+x)*4;bs+=(data[i]+data[i+1]+data[i+2])/3;cnt++;}}
  var ab=cnt>0?bs/cnt:0;

  // Measure brightness outside guide (corners)
  var cs=0,cc=0;
  var corners=[[0,0,gx,gy],[gx+gw,0,w,gy],[0,gy+gh,gx,h],[gx+gw,gy+gh,w,h]];
  for(var ci=0;ci<corners.length;ci++){
    var co=corners[ci];
    for(var cy=co[1];cy<co[3]&&cy<h;cy+=step){for(var cx=co[0];cx<co[2]&&cx<w;cx+=step){
      var ii=(cy*w+cx)*4;cs+=(data[ii]+data[ii+1]+data[ii+2])/3;cc++;}}}
  var cb=cc>0?cs/cc:0;

  // Sharpness of the guide region
  var sharpness=measureSharpness(ctx,gx,gy,gw,gh);
  _lastSharpness=sharpness;

  // Card present: inside brighter than corners AND not too dark
  var cardPresent=(ab>90&&ab>cb*1.10);
  // Sharp: Laplacian variance > threshold (tune based on testing)
  var isSharp=(sharpness>3.0);
  // Not overexposed
  var notOver=(ab<230);

  if(!cardPresent){
    _goodFrameCount=0;
    if(ab<60){setGuide("bad","Too dark - improve lighting");}
    else{setGuide("","Align card within the frame");}
    return;
  }
  if(!isSharp){
    _goodFrameCount=0;
    setGuide("bad","Hold steady - image is blurry (sharpness: "+sharpness.toFixed(1)+")");
    return;
  }
  if(!notOver){
    _goodFrameCount=0;
    setGuide("bad","Too bright - reduce lighting");
    return;
  }

  // Good frame!
  _goodFrameCount++;
  var remaining=_GOOD_FRAMES_NEEDED-_goodFrameCount;
  if(remaining>0){
    setGuide("ok","Hold still... ("+(remaining)+" more)");
  } else {
    // Enough good frames — auto capture!
    setGuide("ok","Good - capturing now...");
    _autoCapturing=true;
    _goodFrameCount=0;
    setTimeout(function(){
      if(camStream)snapCam();
    },150);
  }
}
function handleFile(f){
  if(!f)return;cur=f;
  var reader=new FileReader();
  reader.onload=function(e){
    var pr=document.getElementById("prev");
    pr.src=e.target.result;pr.style.display="block";
  };
  reader.readAsDataURL(f);
  document.getElementById("sbtn").disabled=false;
}
function handleDrop(e){
  e.preventDefault();
  document.getElementById("dropzone").classList.remove("over");
  var f=e.dataTransfer.files[0];
  if(f&&f.type.indexOf("image/")===0)handleFile(f);
}
function setScanMsg(m){document.getElementById("scanmsg").textContent=m;}
async function doScan(){
  if(!cur)return;
  document.getElementById("emptystate").style.display="none";
  document.getElementById("resbody").style.display="none";
  document.getElementById("scanning").classList.add("show");
  document.getElementById("sbtn").disabled=true;
  setScanMsg("Uploading + preprocessing...");
  var fd=new FormData();fd.append("image",cur);
  try{
    setScanMsg("Running OCR (first run ~30s for model download)...");
    var r=await fetch("/ocr",{method:"POST",body:fd});
    var res=await r.json();
    if(!r.ok||res.error)throw new Error(res.error||"OCR failed");
    last=res;showResult(res);
  }catch(e){
    document.getElementById("scanning").classList.remove("show");
    document.getElementById("emptystate").style.display="block";
    document.getElementById("emptystate").innerHTML="<span style='color:#f87171'>Error: "+e.message+"</span>";
  }
  document.getElementById("sbtn").disabled=false;
}
function showResult(res){
  document.getElementById("scanning").classList.remove("show");
  document.getElementById("emptystate").style.display="none";
  document.getElementById("resbody").style.display="block";
  document.getElementById("oname").textContent=res.name||"Name not detected";
  document.getElementById("oic").textContent=res.ic||"IC not detected";
  var conf=res._confidence||0;
  document.getElementById("cfill").style.width=conf+"%";
  document.getElementById("cpct").textContent=conf+"%";
  document.getElementById("otime").textContent=res._processing_time_s||"-";
  if(res.photo_b64){
    document.getElementById("faceph").style.display="none";
    var fi=document.getElementById("faceimg");
    fi.src="data:image/jpeg;base64,"+res.photo_b64;fi.style.display="block";
  }
  var wb=document.getElementById("warnbox");
  if(res._warnings&&res._warnings.length){
    wb.innerHTML="<div class='warn-box'>&#9888; "+res._warnings.join("<br/>&#9888; ")+"</div>";
  }else{wb.innerHTML="";}
  var tbl=document.getElementById("ftbl");
  tbl.innerHTML="";
  var fields=[
    ["IC Number",res.ic,false],
    ["Date of Birth",res.dob,true],
    ["Age",res.age?res.age+" years old":null,true],
    ["Gender",res.gender,true],
    ["Birth State",res.birth_place,true],
    ["Race",res.race,false],
    ["Religion",res.religion,false],
    ["Nationality",res.nationality,false],
    ["Address 1",res.address1,false],
    ["Address 2",res.address2,false],
    ["Address 3",res.address3,false],
    ["Postcode",res.postcode,false],
    ["City",res.city,false],
    ["State",res.state,false]
  ];
  fields.forEach(function(f){
    if(!f[1])return;
    var tr=document.createElement("tr");
    var td1=document.createElement("td");
    td1.textContent=f[0]+(f[2]?" ★":"");
    var td2=document.createElement("td");
    td2.textContent=f[1];
    if(f[2])td2.className="fic";
    tr.appendChild(td1);tr.appendChild(td2);tbl.appendChild(tr);
  });
  document.getElementById("jbox").textContent=JSON.stringify(res,null,2);
}
function toggleJ(){
  var b=document.getElementById("jbox");
  b.style.display=b.style.display==="none"?"block":"none";
}
function copyJ(){
  if(!last)return;
  navigator.clipboard.writeText(JSON.stringify(last,null,2)).then(function(){alert("JSON copied!");});
}
function saveSrv(){
  if(!last)return;
  var token=localStorage.getItem("mk_token")||prompt("Enter API token from MyKad Server settings:");
  if(!token)return;
  localStorage.setItem("mk_token",token);
  fetch("/save",{method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify(Object.assign({},last,{token:token}))}).then(function(r){return r.json();}).then(function(res){
    alert(res.ok?"Saved to server!":"Save failed: "+(res.error||"unknown"));
  }).catch(function(e){alert("Error: "+e.message);});
}
</script>
</body></html>
"""


@app.route("/")
def index():
    return BASIC_HTML


@app.route("/backend")
def backend_info():
    return jsonify({"backend": OCR_BACKEND, "ready": _ocr_reader is not None})


@app.route("/ocr", methods=["POST"])
def ocr_endpoint():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400
    f = request.files["image"]
    image_bytes = f.read()
    if not image_bytes:
        return jsonify({"error": "Empty file"}), 400
    try:
        result = extract_mykad(image_bytes=image_bytes)
        return jsonify(result)
    except Exception as e:
        logger.error("OCR error: %s", e, exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/save", methods=["POST"])
def save_to_server():
    data = request.json or {}
    token = data.pop("token","") or os.environ.get("MYKAD_TOKEN","")
    server_url = os.environ.get("MYKAD_SERVER","http://localhost:9944")
    if not token:
        return jsonify({"error": "Set MYKAD_TOKEN env var"}), 400
    try:
        import urllib.request
        payload = json.dumps(data).encode()
        req = urllib.request.Request(server_url+"/api/records",
            data=payload,
            headers={"Content-Type":"application/json","X-Token":token},
            method="POST")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return jsonify(json.loads(resp.read()))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def main():
    parser = argparse.ArgumentParser(description="MyKad OCR v2")
    parser.add_argument("--image","-i")
    parser.add_argument("--json","-j",action="store_true")
    parser.add_argument("--port","-p",type=int,default=7788)
    parser.add_argument("--host",default="0.0.0.0")
    args = parser.parse_args()
    if args.image:
        if not os.path.exists(args.image):
            print("[ERROR] Not found: "+args.image); sys.exit(1)
        result = extract_mykad(image_path=args.image)
        if args.json:
            print(json.dumps(result,indent=2,ensure_ascii=False))
        else:
            print("\n"+"="*52)
            print("  MyKad OCR v2 - Results")
            print("="*52)
            for k,v in result.items():
                if not k.startswith("_") and v:
                    print("  "+k.ljust(15)+": "+str(v))
            print("-"*52)
            print("  Confidence: "+str(result["_confidence"])+"%")
            print("  Backend   : "+str(result["_backend"]))
            print("  Time      : "+str(result["_processing_time_s"])+"s")
            cs = result.get("_ic_checksum_valid")
            print("  IC Check  : "+("Valid" if cs is True else "?" if cs is None else "Invalid"))
            if result.get("_warnings"):
                for w in result["_warnings"]: print("  WARN: "+w)
            print("="*52)
    else:
        print("\n  MyKad OCR v2 | http://localhost:"+str(args.port))
        print("  Backend: "+OCR_BACKEND)
        print("  IC-derived fields marked with (IC) in UI\n")
        threading.Thread(target=get_reader, daemon=True).start()
        app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
