FROM python:3.10-slim

# OCR uchun tizim paketlari
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev \
    && rm -rf /var/lib/apt/lists/*

# Ishchi katalog
WORKDIR /app

# Python kutubxonalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Loyihadagi barcha fayllarni ko‘chirish
COPY . .

# Botni ishga tushirish
CMD ["python", "bot.py"]
