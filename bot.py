# bot.py
# Esse tekshiruvchi Telegram bot
# Matn + bitta rasm + ALBOM (scanner + OCR) bilan

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

# =====================
# SOZLAMALAR
# =====================
TOKEN = os.getenv("BOT_TOKEN", "PUT_TOKEN_HERE")

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
        "Agar yozuv aniq bo‘lmasa, matn so‘raladi.",
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

    if message.media_group_id:
        # ALBOM
        media_groups[message.media_group_id].append(message)
        await asyncio.sleep(2)

        # Agar albom to‘liq yig‘ilgan bo‘lsa
        if len(media_groups[message.media_group_id]) >= 1:
            messages = media_groups.pop(message.media_group_id)
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

    # BITTA RASM
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

    # Hozircha test uchun o‘rtacha ball
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

    # =====================
    # NATIJANI CHIQARISH
    # =====================
    if result["mode"] in ("zero", "two"):
        msg = (
            f"❌ *Yozma ish tekshirilmadi*\n\n"
            f"📊 Natija: *{result['total_24']} / 24*\n"
            f"📊 75 ballik tizimda: *{result['total_75']}*\n\n"
            f"📌 Sabab: {result['reason']}"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    msg = (
        "✅ *Esse tekshirildi*\n\n"
        f"🧮 So‘zlar soni: *{word_count}*\n"
        f"📊 Jami: *{result['total_24']} / 24*\n"
        f"📊 75 ballik tizimda: *{result['total_75']}*\n\n"
        "📌 *Bandlar bo‘yicha:*"
    )

    for band in result["bands"]:
        msg += (
            f"\n\n*{band['band_id']}. {band['band_name']}*\n"
            f"Ball: {band['score']} / {band['max_score']}\n"
            f"Izoh: {band['explanation']}"
        )

    await update.message.reply_text(msg, parse_mode="Markdown")


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
