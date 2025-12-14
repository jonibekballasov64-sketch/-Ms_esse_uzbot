# bot.py
# Esse tekshiruvchi Telegram bot (matn asosida)
# analysis.py + scoring.py bilan bog‘langan

import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from analysis import EssayAnalyzer

# =====================
# SOZLAMALAR
# =====================
TOKEN = "BOT_TOKEN_BU_YERGA_QO‘YILADI"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

analyzer = EssayAnalyzer()


# =====================
# /start
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✍️ *Esse tekshiruvchi bot*\n\n"
        "📌 Esseni *matn ko‘rinishida* yuboring.\n"
        "📌 Bot yozma ishni 12 band bo‘yicha baholaydi.\n"
        "📌 Natijada 24 va 75 ballik tizimda baho beradi.\n\n"
        "❗ Hozircha rasm va ovoz qo‘llab-quvvatlanmaydi.",
        parse_mode="Markdown"
    )


# =====================
# ESSENI QABUL QILISH
# =====================
async def handle_essay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if len(text) < 20:
        await update.message.reply_text(
            "⚠️ Yuborilgan matn juda qisqa. Iltimos, to‘liq esse yuboring."
        )
        return

    # So‘zlar soni
    word_count = len(text.split())

    # ⚠️ HOZIRCHA MANUAL BAHOLASH
    # Keyin AI/OCR qo‘shiladi
    # Hozir test uchun O‘RTACHA ball beramiz
    band_scores = {
        1: 1.5,
        2: 1.5,
        3: 1,
        4: 2,
        5: 1.5,
        6: 1,
        7: 1,
        8: 1.5,
        9: 1,
        10: 1.5,
        11: 1,
        12: 2
    }

    result = analyzer.analyze(
        essay_text=text,
        word_count=word_count,
        band_scores=band_scores
    )

    # =====================
    # JAVOBNI FORMATLASH
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

    # To‘liq baholash
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
# BOTNI ISHGA TUSHIRISH
# =====================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_essay))

    print("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
