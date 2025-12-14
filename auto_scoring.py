# auto_scoring.py
# Esse matnidan avtomatik band_scores chiqarish

import re
from collections import Counter


def word_stats(text: str):
    words = re.findall(r"[a-zA-Zʻ’‘ʼ-]+", text.lower())
    return words, len(words), len(set(words))


def count_punctuation(text: str):
    return sum(text.count(p) for p in ".,!?;:")


def auto_score(text: str) -> dict:
    words, total_words, unique_words = word_stats(text)
    punct_count = count_punctuation(text)
    paragraphs = text.count("\n") + 1

    # ---- 1–6 bandlar (mazmun va mantiq) ----
    content_score = 2 if total_words >= 180 else 1.5 if total_words >= 120 else 1

    # ---- 7-band: imlo (sodda model) ----
    typo_estimate = sum(1 for w in words if len(w) > 20)
    if typo_estimate == 0:
        spelling = 2
    elif typo_estimate <= 2:
        spelling = 1.5
    elif typo_estimate <= 4:
        spelling = 1
    else:
        spelling = 0.5

    # ---- 8-band: punktuatsiya ----
    if punct_count >= total_words / 10:
        punctuation = 2
    elif punct_count >= total_words / 15:
        punctuation = 1.5
    else:
        punctuation = 1

    # ---- 11-band: leksik boylik ----
    diversity = unique_words / total_words if total_words else 0
    if diversity > 0.6:
        vocab = 2
    elif diversity > 0.45:
        vocab = 1.5
    else:
        vocab = 1

    # ---- 12-band: noo‘rin birliklar ----
    slang = ["akan", "opam", "zo‘r", "gap yo‘q", "ha endi"]
    slang_count = sum(1 for s in slang if s in text.lower())
    bad_style = 2 if slang_count == 0 else 1.5 if slang_count == 1 else 1

    return {
        1: content_score,
        2: content_score,
        3: content_score,
        4: 2 if paragraphs >= 3 else 1.5,
        5: 1.5,
        6: 1.5,
        7: spelling,
        8: punctuation,
        9: 1.5,
        10: 1.5,
        11: vocab,
        12: bad_style
    }
