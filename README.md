---

title: LyricsTranslation

emoji: 🎵

colorFrom: gray

colorTo: indigo

sdk: gradio

sdk_version: 5.48.0

app_file: app.py

pinned: false

---

# Spotify Lyrics Translator (Personal)

FastAPI + Gradio app that shows currently playing track on Spotify, fetches lyrics via LRCLIB (default) or Musixmatch, and optionally translates them via OpenAI or Hugging Face Inference.

Note for Hugging Face Spaces:
- This Space uses FastAPI with Gradio mounted at "/".
- Set the following dependencies (also in requirements.txt):
  - fastapi>=0.110
  - gradio>=4.36
  - uvicorn>=0.30
  - httpx>=0.27
  - pydantic>=2.7
  - python-multipart>=0.0.9
  - Translation provider (choose either):
    - openai>=1.47
    - huggingface_hub>=0.24

## Environment Variables (set in Repository secrets)

Required:
- SPOTIFY_CLIENT_ID
- SPOTIFY_REDIRECT_URI (e.g., https://<your-space>.hf.space/callback and also register on Spotify dashboard)

Optional:
- LYRICS_PROVIDER = lrclib (default) or musixmatch
- MUSIXMATCH_API_KEY (if using Musixmatch)
- Translation (choose either)
  - OPENAI_API_KEY (optional; if using OpenAI)
    - OPENAI_MODEL (optional; default gpt-4o-mini)
  - HUGGINGFACEHUB_API_TOKEN + TRANSLATION_MODEL (if using HF Inference)

Caution: Follow each API’s TOS. Genius official API does not return full lyrics; scraping may violate terms, so not used here.

## Run locally

- Create a .env with variables (or export env vars)
- Install deps: pip install -r requirements.txt
- Run: uvicorn app:app --host 0.0.0.0 --port 7860

## Project structure

```
.
├─ app.py                              # FastAPI + Gradio entrypoint
├─ requirements.txt
├─ README.md
├─ .env.example
└─ app
   ├─ domain
   │  ├─ entities.py
   │  └─ exceptions.py
   ├─ usecases
   │  ├─ get_current_track.py
   │  ├─ get_lyrics.py
   │  └─ translate_lyrics.py
   ├─ infrastructure
   │  ├─ config.py
   │  ├─ spotify
   │  │  ├─ auth.py
   │  │  ├─ client.py
   │  │  └─ repositories.py
   │  ├─ lyrics
   │  │  ├─ base.py
   │  │  ├─ lrclib.py
   │  │  └─ musixmatch.py
   │  └─ translation
   │     ├─ base.py
   │     ├─ openai_translator.py
   │     └─ hf_inference_translator.py
   └─ presentation
      ├─ handlers.py
      └─ ui.py
```

## Security notes
- Do not commit API keys. Use repository secrets / Space secrets.
- OAuth callback should be https in production. For Spaces, set SPOTIFY_REDIRECT_URI to your Space URL + /callback.

