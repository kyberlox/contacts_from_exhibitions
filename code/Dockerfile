FROM python:3.12

WORKDIR /app

COPY requirements.txt .

# RUN apt-get update
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-rus \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# RUN apt-get update && apt-get install -y \
#     tesseract-ocr \
#     tesseract-ocr-rus \
#     poppler-utils \
#     libglib2.0-0 \
#     libsm6 \
#     libxext6 \
#     libxrender-dev \
#     && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["python", "main.py"]
