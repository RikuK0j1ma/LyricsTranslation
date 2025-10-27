from dataclasses import dataclass
from typing import Optional, List

@dataclass(frozen=True)
class Track:
    id: Optional[str]
    title: str
    artists: List[str]
    album: Optional[str] = None
    duration_ms: Optional[int] = None

    @property
    def artists_text(self) -> str:
        return ", ".join(self.artists)

@dataclass(frozen=True)
class Lyrics:
    text: str
    language: Optional[str] = None
    provider: str = "unknown"
