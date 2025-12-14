# ocr.py
# Rasmni SKANER rejimida tozalab, matn chiqarish

import cv2
import pytesseract
import numpy as np
import re


def scan_preprocess(image_path: str):
    """
    Rasmni skaner ko‘rinishiga keltirish
    """
    img = cv2.imread(image_path)

    if img is None:
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Shovqinni kamaytirish
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # Adaptive threshold (scanner effekti)
    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        10
    )

    # Kichik dog‘larni yo‘qotish
    kernel = np.ones((1, 1), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    return cleaned


def clean_text(text: str) -> str:
    """
    OCR natijasini tozalash
    """
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s.,!?;:'\"()\-]", "", text)
    return text.strip()


def image_to_text(image_path: str) -> str | None:
    """
    Rasm → (scanner) → OCR → matn
    """
    processed = scan_preprocess(image_path)

    if processed is None:
        return None

    raw_text = pytesseract.image_to_string(
        processed,
        lang="eng",
        config="--oem 3 --psm 6"
    )

    text = clean_text(raw_text)

    # Juda yomon OCR bo‘lsa rad qilamiz
    if len(text.split()) < 20:
        return None

    return text
