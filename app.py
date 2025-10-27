from fastapi import FastAPI
import gradio as gr

from app_pkg.presentation.ui import build_ui
from app_pkg.infrastructure.spotify.auth import router as auth_router

# FastAPI 本体
fastapi_app = FastAPI(title="Spotify Lyrics Translator (Personal)")

# Spotify OAuth ルーター
fastapi_app.include_router(auth_router, prefix="")

# Gradio UI を FastAPI にマウント
demo = build_ui()
app = gr.mount_gradio_app(fastapi_app, demo, path="/")