# ocr.py
# Rasmni skaner rejimida tozalab, matn chiqarish (OPTIMALLASHTIRILGAN)

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

    # Shovqinni kamaytirish (yumshoqroq)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # Adaptive threshold (scanner effekti, lekin haddan oshmagan)
    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        25,
        12
    )

    # Mayda shovqinlarni tozalash
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
    Yomon natijada None qaytaradi
    """
    processed = scan_preprocess(image_path)

    if processed is None:
        return None

    raw_text = pytesseract.image_to_string(
        processed,
        lang="eng",  # lotin yozuvi uchun eng barqaror
        config="--oem 3 --psm 4"
    )

    text = clean_text(raw_text)

    # Juda qisqa yoki yaroqsiz OCR bo‘lsa
    if len(text.split()) < 20:
        return None

    return text
