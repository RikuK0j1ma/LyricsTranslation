from typing import List, Optional
import httpx
from app.domain.entities import Lyrics
from app.infrastructure.lyrics.base import LyricsProvider

class MusixmatchProvider(LyricsProvider):
    name = "musixmatch"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def _search_track_id(self, title: str, artists: List[str]) -> Optional[int]:
        params = {
            "q_track": title,
            "q_artist": ", ".join(artists),
            "f_has_lyrics": 1,
            "apikey": self.api_key,
            "s_track_rating": "desc",
            "page_size": 1,
        }
        async with httpx.AsyncClient(timeout=15) as client:
            res = await client.get("https://api.musixmatch.com/ws/1.1/track.search", params=params)
        if res.status_code != 200:
            return None
        body = res.json()
        try:
            return body["message"]["body"]["track_list"][0]["track"]["track_id"]
        except Exception:
            return None

    async def get_lyrics(self, track_title: str, artists: List[str]) -> Optional[Lyrics]:
        if not self.api_key:
            return None
        track_id = await self._search_track_id(track_title, artists)
        if not track_id:
            return None
        params = {"track_id": track_id, "apikey": self.api_key}
        async with httpx.AsyncClient(timeout=15) as client:
            res = await client.get("https://api.musixmatch.com/ws/1.1/track.lyrics.get", params=params)
        if res.status_code != 200:
            return None
        body = res.json()
        lyr = body["message"]["body"].get("lyrics", {})
        text = lyr.get("lyrics_body", "")
        if not text.strip():
            return None
        text = text.replace("******* This Lyrics is NOT for Commercial use *******", "").strip()
        return Lyrics(text=text, provider=self.name)
