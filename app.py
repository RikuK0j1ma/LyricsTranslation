from fastapi import FastAPI
import gradio as gr
from app_pkg.presentation.ui import build_ui
from app_pkg.infrastructure.spotify.auth import router as auth_router

fastapi_app = FastAPI(title="Spotify Lyrics Translator (Personal)")
fastapi_app.include_router(auth_router, prefix="")  # /login, /callback, /logout

demo = build_ui()
app = gr.mount_gradio_app(fastapi_app, demo, path="/")