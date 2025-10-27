import time
from typing import Optional
import httpx
from app.domain.entities import Track
from app.infrastructure.spotify.repositories import token_repo
from app.infrastructure.config import SETTINGS

SPOTIFY_API = "https://api.spotify.com/v1"

class SpotifyClient:
    async def _refresh_if_needed(self, tokens: dict) -> dict:
        if tokens and token_repo.is_expired(tokens) and tokens.get("refresh_token"):
            data = {
                "grant_type": "refresh_token",
                "refresh_token": tokens["refresh_token"],
                "client_id": SETTINGS.spotify_client_id
            }
            async with httpx.AsyncClient(timeout=20) as client:
                res = await client.post("https://accounts.spotify.com/api/token", data=data)
            if res.status_code == 200:
                payload = res.json()
                tokens["access_token"] = payload["access_token"]
                tokens["expires_at"] = time.time() + int(payload.get("expires_in", 3600) * 0.95)
        return tokens

    async def get_currently_playing(self, tokens: dict) -> Optional[Track]:
        tokens = await self._refresh_if_needed(tokens)
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        async with httpx.AsyncClient(timeout=15) as client:
            res = await client.get(f"{SPOTIFY_API}/me/player/currently-playing", headers=headers)
        if res.status_code == 204:
            return None
        if res.status_code != 200:
            return None
        data = res.json()
        item = data.get("item")
        if not item:
            return None
        title = item["name"]
        artists = [a["name"] for a in item.get("artists", [])]
        album = item.get("album", {}).get("name")
        duration_ms = item.get("duration_ms")
        track_id = item.get("id")
        return Track(id=track_id, title=title, artists=artists, album=album, duration_ms=duration_ms)
