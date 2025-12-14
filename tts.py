# tts.py
# Matnni ovozli (audio) ko‘rinishga aylantirish

from gtts import gTTS
import uuid
import os


def text_to_speech(text: str, lang: str = "uz") -> str:
    """
    Matnni ovozga aylantiradi va mp3 fayl yo‘lini qaytaradi
    """
    # Juda qisqa matnni o‘qimaymiz
    if not text or len(text.strip()) < 10:
        return None

    # Fayl nomi
    filename = f"/tmp/{uuid.uuid4()}.mp3"

    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(filename)
        return filename
    except Exception as e:
        print("TTS xatosi:", e)
        return None
