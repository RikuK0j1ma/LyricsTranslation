import time
from typing import Optional, Dict, Any

class TokenRepository:
    """セッションID -> トークン情報（簡易メモリ保持）"""
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}

    def save(self, session_id: str, tokens: Dict[str, Any]) -> None:
        self._store[session_id] = tokens

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self._store.get(session_id)

    def delete(self, session_id: str) -> None:
        self._store.pop(session_id, None)

    def is_expired(self, token: Dict[str, Any]) -> bool:
        return token.get("expires_at", 0) <= time.time()

token_repo = TokenRepository()
