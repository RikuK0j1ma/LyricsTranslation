import os
from pydantic import BaseModel, Field

class Settings(BaseModel):
    spotify_client_id: str = Field(default_factory=lambda: os.getenv("SPOTIFY_CLIENT_ID", ""))
    spotify_redirect_uri: str = Field(default_factory=lambda: os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:7860/callback"))

    allowed_origins: list[str] = Field(default_factory=lambda: os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else [])

    lyrics_provider: str = Field(default_factory=lambda: os.getenv("LYRICS_PROVIDER", "lrclib"))
    musixmatch_api_key: str = Field(default_factory=lambda: os.getenv("MUSIXMATCH_API_KEY", ""))

    # 翻訳
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = Field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    hf_token: str = Field(default_factory=lambda: os.getenv("HUGGINGFACEHUB_API_TOKEN", ""))
    translation_model: str = Field(default_factory=lambda: os.getenv("TRANSLATION_MODEL", ""))

SETTINGS = Settings()
