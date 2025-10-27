from app_pkg.domain.entities import Track, Lyrics
from app_pkg.domain.exceptions import LyricsNotFoundError
from app_pkg.infrastructure.lyrics.base import LyricsProvider

class GetLyricsUseCase:
    def __init__(self, provider: LyricsProvider):
        self.provider = provider

    async def execute(self, track: Track) -> Lyrics:
        lyrics = await self.provider.get_lyrics(track.title, track.artists)
        if not lyrics or not lyrics.text.strip():
            raise LyricsNotFoundError("Lyrics not found.")
        return lyrics
