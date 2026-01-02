FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# install core dependencies first to avoid conflicts
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir numpy pandas && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir scikit-learn transformers && \
    pip install --no-cache-dir sqlalchemy psycopg2-binary && \
    pip install --no-cache-dir fastapi uvicorn httpx && \
    pip install --no-cache-dir python-dotenv requests && \
    pip install --no-cache-dir beautifulsoup4 bs4 dateparser && \
    pip install --no-cache-dir yfinance coinmetrics-api-client && \
    pip install --no-cache-dir pandas_ta && \
    pip install --no-cache-dir tqdm schedule && \
    pip install --no-cache-dir --no-deps ta || true

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
