import gradio as gr

from app_pkg.infrastructure.config import SETTINGS
from app_pkg.infrastructure.spotify.client import SpotifyClient
from app_pkg.infrastructure.spotify.repositories import token_repo
from app_pkg.infrastructure.lyrics.lrclib import LRCLIBProvider
from app_pkg.infrastructure.lyrics.musixmatch import MusixmatchProvider
from app_pkg.infrastructure.translation.openai_translator import OpenAITranslator
from app_pkg.infrastructure.translation.hf_inference_translator import HFInferenceTranslator
from app_pkg.usecases.get_current_track import GetCurrentTrackUseCase
from app_pkg.usecases.get_lyrics import GetLyricsUseCase
from app_pkg.usecases.translate_lyrics import TranslateLyricsUseCase
from app_pkg.domain.exceptions import NotLoggedInError, NotPlayingError, LyricsNotFoundError, TranslationError

def _lyrics_provider():
    if SETTINGS.lyrics_provider == "musixmatch" and SETTINGS.musixmatch_api_key:
        return MusixmatchProvider(api_key=SETTINGS.musixmatch_api_key)
    return LRCLIBProvider()

def _translator_or_none():
    # Priority: OpenAI -> HF Inference. If neither is configured, return None.
    try:
        if SETTINGS.openai_api_key:
            return OpenAITranslator()
    except Exception:
        pass
    try:
        if SETTINGS.hf_token and SETTINGS.translation_model:
            return HFInferenceTranslator()
    except Exception:
        pass
    return None

spotify_client = SpotifyClient()

async def fetch_and_translate(lang_code: str, request: gr.Request):
    session_id = request.cookies.get("session_id")
    get_track = GetCurrentTrackUseCase(token_repo, spotify_client)
    lyrics_uc = GetLyricsUseCase(_lyrics_provider())

    status = ""
    title = ""
    artists = ""
    original = ""
    translated = ""

    try:
        track = await get_track.execute(session_id)
        title = track.title
        artists = track.artists_text

        lyrics = await lyrics_uc.execute(track)
        original = lyrics.text

        translator = _translator_or_none()
        if translator is None:
            translated = ""
            status = (
                f"Provider: {lyrics.provider} / Translator: Not configured "
                "(Please set OPENAI_API_KEY or HUGGINGFACEHUB_API_TOKEN + TRANSLATION_MODEL)"
            )
        else:
            translate_uc = TranslateLyricsUseCase(translator)
            translated = await translate_uc.execute(lyrics, lang_code)
            status = f"Provider: {lyrics.provider} / Translator: {translator.__class__.__name__}"

    except NotLoggedInError:
        status = "Please connect with Spotify."
    except NotPlayingError:
        status = "Please play a track on Spotify."
    except LyricsNotFoundError:
        status = "Lyrics not found."
    except TranslationError as e:
        status = f"Translation failed: {e}"
    except Exception as e:
        status = f"Error: {e}"

    return title, artists, original, translated, status

async def poll_now_playing(lang_code: str, prev_translated: str, request: gr.Request):
    session_id = request.cookies.get("session_id")
    get_track = GetCurrentTrackUseCase(token_repo, spotify_client)
    lyrics_uc = GetLyricsUseCase(_lyrics_provider())

    status = ""
    title = ""
    artists = ""
    original = ""

    try:
        track = await get_track.execute(session_id)
        title = track.title
        artists = track.artists_text

        lyrics = await lyrics_uc.execute(track)
        original = lyrics.text

        translator = _translator_or_none()
        if translator is None:
            status = (
                f"Provider: {lyrics.provider} / Translator: Not configured (translation runs only when you click the button)"
            )
        else:
            status = (
                f"Provider: {lyrics.provider} / Translator: {translator.__class__.__name__} (translation runs only when you click the button)"
            )

    except NotLoggedInError:
        status = "Please connect with Spotify."
    except NotPlayingError:
        status = "Please play a track on Spotify."
    except LyricsNotFoundError:
        status = "Lyrics not found."
    except Exception as e:
        status = f"Error: {e}"

    return title, artists, original, prev_translated, status
