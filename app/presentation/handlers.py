import gradio as gr

from app.infrastructure.config import SETTINGS
from app.infrastructure.spotify.client import SpotifyClient
from app.infrastructure.spotify.repositories import token_repo
from app.infrastructure.lyrics.lrclib import LRCLIBProvider
from app.infrastructure.lyrics.musixmatch import MusixmatchProvider
from app.infrastructure.translation.openai_translator import OpenAITranslator
from app.infrastructure.translation.hf_inference_translator import HFInferenceTranslator
from app.usecases.get_current_track import GetCurrentTrackUseCase
from app.usecases.get_lyrics import GetLyricsUseCase
from app.usecases.translate_lyrics import TranslateLyricsUseCase
from app.domain.exceptions import NotLoggedInError, NotPlayingError, LyricsNotFoundError, TranslationError

def _lyrics_provider():
    if SETTINGS.lyrics_provider == "musixmatch" and SETTINGS.musixmatch_api_key:
        return MusixmatchProvider(api_key=SETTINGS.musixmatch_api_key)
    return LRCLIBProvider()

def _translator_or_none():
    # 優先: OpenAI -> HF Inference。どちらも未設定なら None を返す。
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
                f"Provider: {lyrics.provider} / Translator: 未設定 "
                "(OPENAI_API_KEY または HUGGINGFACEHUB_API_TOKEN + TRANSLATION_MODEL を設定してください)"
            )
        else:
            translate_uc = TranslateLyricsUseCase(translator)
            translated = await translate_uc.execute(lyrics, lang_code)
            status = f"Provider: {lyrics.provider} / Translator: {translator.__class__.__name__}"

    except NotLoggedInError:
        status = "Spotify と連携してください。"
    except NotPlayingError:
        status = "Spotify で何らかの曲を再生してください。"
    except LyricsNotFoundError:
        status = "歌詞が見つかりませんでした。"
    except TranslationError as e:
        status = f"翻訳に失敗しました: {e}"
    except Exception as e:
        status = f"エラー: {e}"

    return title, artists, original, translated, status

async def poll_now_playing(lang_code: str, request: gr.Request):
    return await fetch_and_translate(lang_code, request)
