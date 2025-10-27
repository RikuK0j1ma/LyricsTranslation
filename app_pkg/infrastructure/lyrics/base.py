from typing import List, Optional
from app_pkg.domain.entities import Lyrics

class LyricsProvider:
    name: str = "base"
    async def get_lyrics(self, track_title: str, artists: List[str]) -> Optional[Lyrics]:
        raise NotImplementedError
