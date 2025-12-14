# analysis.py
# Esse (yozma ish)ni 12 band bo‘yicha izohli tahlil qilish

import json
from typing import Dict, Any, List


class EssayAnalyzer:
    def __init__(self, mezonlar_path: str = "mezonlar.json"):
        with open(mezonlar_path, "r", encoding="utf-8") as f:
            self.mezonlar = json.load(f)

        self.bands = self.mezonlar["bands"]
        self.global_rules = self.mezonlar["global_rules"]

    # ---------------------------
    # GLOBAL QOIDALAR
    # ---------------------------
    def check_global_rules(self, essay_text: str, word_count: int) -> Dict[str, Any]:
        """
        0 ball yoki jami 2 ball holatlarini tekshiradi
        """
        text = essay_text.strip()

        # 0 ball holatlari
        if not text:
            return {
                "type": "zero",
                "score": 0,
                "reason": "Yozma ish yozilmagan (bo‘sh)."
            }

        # faqat kirish qismi (juda qisqa matn)
        if word_count < 30:
            return {
                "type": "zero",
                "score": 0,
                "reason": "Faqat kirish qismi yozilgan, topshiriq bajarilmagan."
            }

        # to‘liq kirill alifbosi (sodda tekshiruv)
        latin_letters = sum(ch.isascii() and ch.isalpha() for ch in text)
        cyrillic_letters = sum("А" <= ch <= "я" for ch in text)

        if cyrillic_letters > latin_letters:
            return {
                "type": "zero",
                "score": 0,
                "reason": "Yozma ish to‘liq kirill alifbosida yozilgan."
            }

        # jami 2 ball holatlari
        if word_count < 100:
            return {
                "type": "two",
                "score": 2,
                "reason": "Yozma ish hajmi 100 ta so‘zdan kam."
            }

        # mavzuga mos emas (hozircha manual flag)
        return {"type": "ok"}

    # ---------------------------
    # BANDMA-BAND TAHLIL
    # ---------------------------
    def analyze_bands(self, band_scores: Dict[int, float]) -> Dict[str, Any]:
        """
        band_scores:
        {
            1: 1.5,
            2: 2,
            3: 1,
            ...
        }
        """
        results = []
        total_score = 0.0

        for band in self.bands:
            band_id = band["id"]
            band_name = band["name"]
            max_score = band["max_score"]

            score = band_scores.get(band_id, 0)
            score = min(score, max_score)

            # mos izohni topish
            explanation = ""
            for lvl in band["levels"]:
                if lvl["score"] == score:
                    explanation = lvl["condition"]
                    break

            results.append({
                "band_id": band_id,
                "band_name": band_name,
                "score": score,
                "max_score": max_score,
                "explanation": explanation or "Izoh belgilanmagan."
            })

            total_score += score

        return {
            "bands": results,
            "total_24": round(total_score, 1)
        }

    # ---------------------------
    # ASOSIY FUNKSIYA
    # ---------------------------
    def analyze(
        self,
        essay_text: str,
        word_count: int,
        band_scores: Dict[int, float]
    ) -> Dict[str, Any]:
        """
        Yakuniy tahlil
        """
        global_check = self.check_global_rules(essay_text, word_count)

        # 0 ball yoki 2 ball holati
        if global_check["type"] in ("zero", "two"):
            return {
                "status": "finished",
                "mode": global_check["type"],
                "total_24": global_check["score"],
                "reason": global_check["reason"],
                "bands": []
            }

        # Aks holda 12 band bo‘yicha
        band_result = self.analyze_bands(band_scores)

        return {
            "status": "finished",
            "mode": "full",
            "total_24": band_result["total_24"],
            "bands": band_result["bands"]
      }
