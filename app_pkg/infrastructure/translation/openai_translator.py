from app_pkg.infrastructure.translation.base import Translator
from app_pkg.infrastructure.config import SETTINGS

try:
    from openai import AsyncOpenAI
except Exception:
    AsyncOpenAI = None

SYSTEM_PROMPT = """You are a meticulous lyrics translator.
- Translate into the target language while preserving line breaks.
- Do NOT add commentary or transliterations unless they already exist in the source.
- Keep rhyme and tone when possible, but prioritize accuracy.
"""

class OpenAITranslator(Translator):
    def __init__(self):
        if not SETTINGS.openai_api_key or AsyncOpenAI is None:
            raise RuntimeError("OpenAI Translator unavailable")
        self.client = AsyncOpenAI(api_key=SETTINGS.openai_api_key)
        self.model = SETTINGS.openai_model or "gpt-4o-mini"

    async def translate(self, text: str, target_language: str) -> str:
        target_language = target_language.strip()
        prompt = f"Target language: {target_language}\n\n<lyrics>\n{text}\n</lyrics>"
        resp = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()
