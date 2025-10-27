from app_pkg.domain.entities import Lyrics
from app_pkg.domain.exceptions import TranslationError
from app_pkg.infrastructure.translation.base import Translator

class TranslateLyricsUseCase:
    def __init__(self, translator: Translator):
        self.translator = translator

    async def execute(self, lyrics: Lyrics, target_lang: str) -> str:
        try:
            return await self.translator.translate(text=lyrics.text, target_language=target_lang)
        except Exception as e:
            raise TranslationError(str(e)) from e
