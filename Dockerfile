# ベース
FROM python:3.11-slim

# 必要ライブラリ
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 依存を先に入れてレイヤーを効かせる
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリ本体
COPY . .

# Spaces の既定ポート
EXPOSE 7860

# uvicorn で FastAPI(＋Gradioをマウントした app) を起動
# app.py 内の ASGI 変数名が "app" であることが前提
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
