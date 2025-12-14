# scoring.py
# 24 ballik tizimni 75 ballik tizimga o‘tkazish
# Milliy sertifikat rasmiy jadvaliga mos

SCORE_TABLE = {
    24: 75,
    23.5: 74,
    23: 73,
    22.5: 72,
    22: 71,
    21.5: 70,
    21: 69,
    20.5: 68,
    20: 67,
    19.5: 66,
    19: 65,
    18.5: 64,
    18: 63,
    17.5: 62,
    17: 61,
    16.5: 60,
    16: 59,
    15.5: 58,
    15: 57,
    14.5: 56,
    14: 55,
    13.5: 54,
    13: 53,
    12.5: 52,
    12: 51,
    11.5: 50,
    11: 49,
    10.5: 48,
    10: 47,
    9.5: 46,
    9: 45,
    8.5: 44,
    8: 43,
    7.5: 42,
    7: 41,
    6.5: 40,
    6: 39,
    5.5: 38,
    5: 37,
    4.5: 36,
    4: 35,
    3.5: 34,
    3: 33,
    2.5: 32,
    2: 31,
    1.5: 30,
    1: 29,
    0.5: 28,
    0: 0
}


def convert_24_to_75(score_24: float) -> int:
    """
    24 ballik umumiy natijani 75 ballik tizimga o‘tkazadi
    score_24: 0 dan 24 gacha (0.5 qadam bilan)
    """
    # 0.5 lik aniqlikka keltiramiz
    score_24 = round(score_24 * 2) / 2

    # Jadval bo‘yicha mos ballni qaytaramiz
    return SCORE_TABLE.get(score_24, 0)
