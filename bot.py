# bot.py
# Esse tekshiruvchi Telegram bot
# Matn + rasm + ALBOM (scanner + OCR) + OVOZLI TAHLIL

import os
import uuid
import asyncio
import logging
from collections import defaultdict

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from analysis import EssayAnalyzer
from ocr import image_to_text
from tts import text_to_speech   # 🔊 OVOZ QO‘SHILDI

# =====================
# SOZLAMALAR
# =====================
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

analyzer = EssayAnalyzer()

# Albomlar uchun vaqtinchalik xotira
media_groups = defaultdict(list)


# =====================
# /start
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✍️ *Esse tekshiruvchi bot*\n\n"
        "Yuborish mumkin:\n"
        "📝 Matn ko‘rinishida esse\n"
        "📸 Bitta rasm\n"
        "🖼 Bir nechta rasm (ALBOM)\n\n"
        "Bot rasmni skaner qilib o‘qiydi.\n"
        "Natijani matn va ovoz ko‘rinishida beradi.",
        parse_mode="Markdown"
    )


# =====================
# MATN QABUL QILISH
# =====================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    await process_essay(update, context, text)


# =====================
# RASM / ALBOM QABUL QILISH
# =====================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    # ===== ALBOM =====
    if message.media_group_id:
        media_groups[message.media_group_id].append(message)
        await asyncio.sleep(2)

        messages = media_groups.pop(message.media_group_id, [])
        if not messages:
            return

        full_text = ""
        for msg in messages:
            file = await msg.photo[-1].get_file()
            filename = f"/tmp/{uuid.uuid4()}.jpg"
            await file.download_to_drive(filename)

            text = image_to_text(filename)
            if text:
                full_text += " " + text

        if not full_text.strip():
            await update.message.reply_text(
                "⚠️ Rasm(lar)dagi yozuv aniq tanilmadi.\n"
                "Iltimos, esseni *matn ko‘rinishida* yuboring.",
                parse_mode="Markdown"
            )
            return

        await process_essay(update, context, full_text)
        return

    # ===== BITTA RASM =====
    file = await message.photo[-1].get_file()
    filename = f"/tmp/{uuid.uuid4()}.jpg"
    await file.download_to_drive(filename)

    text = image_to_text(filename)
    if not text:
        await update.message.reply_text(
            "⚠️ Rasmda yozuv aniq tanilmadi.\n"
            "Iltimos, esseni *matn ko‘rinishida* yuboring.",
            parse_mode="Markdown"
        )
        return

    await process_essay(update, context, text)


# =====================
# ASOSIY TAHLIL
# =====================
async def process_essay(update, context, text: str):
    word_count = len(text.split())

    # ⚠️ Hozircha qo‘lda ball (3-qadamda AI qiladi)
    band_scores = {
        1: 1.5, 2: 1.5, 3: 1, 4: 2,
        5: 1.5, 6: 1, 7: 1, 8: 1.5,
        9: 1, 10: 1.5, 11: 1, 12: 2
    }

    result = analyzer.analyze(
        essay_text=text,
        word_count=word_count,
        band_scores=band_scores
    )

    # ===== GLOBAL HOLAT =====
    if result["mode"] in ("zero", "two"):
        msg = (
            f"❌ *Yozma ish tekshirilmadi*\n\n"
            f"📊 Natija: *{result['total_24']} / 24*\n"
            f"📊 75 ballik tizimda: *{result['total_75']}*\n\n"
            f"📌 Sabab: {result['reason']}"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    # ===== MATNLI NATIJA =====
    msg = (
        "✅ *Esse tekshirildi*\n\n"
        f"🧮 So‘zlar soni: *{word_count}*\n"
        f"📊 Jami: *{result['total_24']} / 24*\n"
        f"📊 75 ballik tizimda: *{result['total_75']}*\n\n"
        "📌 *Bandlar bo‘yicha:*"
    )

    voice_text = (
        f"Esse tekshirildi. "
        f"So‘zlar soni {word_count}. "
        f"Yigirma to‘rt ballik tizimda {result['total_24']} ball. "
        f"Yetmish besh ballik tizimda {result['total_75']} ball. "
    )

    for band in result["bands"]:
        msg += (
            f"\n\n*{band['band_id']}. {band['band_name']}*\n"
            f"Ball: {band['score']} / {band['max_score']}\n"
            f"Izoh: {band['explanation']}"
        )

        voice_text += (
            f"{band['band_id']}-band. "
            f"{band['band_name']}. "
            f"{band['score']} ball. "
        )

    await update.message.reply_text(msg, parse_mode="Markdown")

    # ===== OVOZLI NATIJA =====
    audio_path = text_to_speech(voice_text)
    if audio_path:
        try:
            await context.bot.send_audio(
                chat_id=update.effective_chat.id,
                audio=open(audio_path, "rb"),
                caption="🔊 Esse tahlilining ovozli varianti"
            )
        except Exception as e:
            logging.error(f"Ovoz yuborishda xato: {e}")


# =====================
# ISHGA TUSHIRISH
# =====================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    logging.info("Bot ishga tushdi")
    app.run_polling()


if __name__ == "__main__":
    main()
