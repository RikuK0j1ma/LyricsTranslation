from typing import Optional
from app_pkg.domain.entities import Track
from app_pkg.domain.exceptions import NotLoggedInError, NotPlayingError
from app_pkg.infrastructure.spotify.client import SpotifyClient
from app_pkg.infrastructure.spotify.repositories import TokenRepository

class GetCurrentTrackUseCase:
    def __init__(self, token_repo: TokenRepository, spotify_client: SpotifyClient):
        self.token_repo = token_repo
        self.spotify = spotify_client

    async def execute(self, session_id: Optional[str]) -> Track:
        if not session_id:
            raise NotLoggedInError("Please log in to Spotify.")

        tokens = self.token_repo.get(session_id)
        if not tokens:
            raise NotLoggedInError("Spotify session not found. Please log in.")

        track = await self.spotify.get_currently_playing(tokens)
        if track is None:
            raise NotPlayingError("Please play a track on Spotify.")
        return track
