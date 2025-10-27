from app_pkg.infrastructure.translation.base import Translator
from app_pkg.infrastructure.config import SETTINGS

try:
    from huggingface_hub import AsyncInferenceClient
except Exception:
    AsyncInferenceClient = None

INSTRUCTION_TMPL = """You are a careful lyrics translator.
Translate the following lyrics into {lang}. Preserve line breaks. No commentary.
Lyrics:
{lyrics}
"""

class HFInferenceTranslator(Translator):
    def __init__(self):
        if not SETTINGS.hf_token or not SETTINGS.translation_model or AsyncInferenceClient is None:
            raise RuntimeError("HF Inference Translator unavailable")
        self.client = AsyncInferenceClient(token=SETTINGS.hf_token)
        self.model = SETTINGS.translation_model

    async def translate(self, text: str, target_language: str) -> str:
        prompt = INSTRUCTION_TMPL.format(lang=target_language, lyrics=text)
        out = await self.client.text_generation(
            prompt, model=self.model, max_new_tokens=1024, temperature=0.2, return_full_text=False
        )
        return out.strip()
