from typing import List, Optional
import httpx
from app_pkg.domain.entities import Lyrics
from app_pkg.infrastructure.lyrics.base import LyricsProvider

class LRCLIBProvider(LyricsProvider):
    name = "lrclib"

    async def get_lyrics(self, track_title: str, artists: List[str]) -> Optional[Lyrics]:
        params = {
            "track_name": track_title,
            "artist_name": ", ".join(artists)
        }
        async with httpx.AsyncClient(timeout=15) as client:
            res = await client.get("https://lrclib.net/api/search", params=params)
        if res.status_code != 200:
            return None
        results = res.json()
        if not results:
            return None
        item = results[0]
        txt = item.get("plainLyrics") or ""
        if not txt.strip() and item.get("syncedLyrics"):
            txt = "\n".join([line.split("]", 1)[-1] for line in item["syncedLyrics"].splitlines() if "]" in line])
        if not txt.strip():
            return None
        return Lyrics(text=txt, language=None, provider=self.name)
