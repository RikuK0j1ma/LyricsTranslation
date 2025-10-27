import base64, os, secrets, time, hashlib
from typing import Optional
import httpx
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, PlainTextResponse

from app_pkg.infrastructure.config import SETTINGS
from app_pkg.infrastructure.spotify.repositories import token_repo

router = APIRouter()

# 状態・PKCE保管（簡易メモリ）
_state_pkce: dict[str, str] = {}

def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')

def _new_code_verifier() -> str:
    return _b64url(os.urandom(64))

def _code_challenge(verifier: str) -> str:
    return _b64url(hashlib.sha256(verifier.encode("ascii")).digest())

def _new_session_id() -> str:
    return secrets.token_urlsafe(32)

@router.get("/login")
async def login():
    if not SETTINGS.spotify_client_id or not SETTINGS.spotify_redirect_uri:
        raise HTTPException(status_code=500, detail="Spotify Client ID / Redirect URI is not configured.")

    state = secrets.token_urlsafe(16)
    verifier = _new_code_verifier()
    challenge = _code_challenge(verifier)
    _state_pkce[state] = verifier

    scopes = ["user-read-currently-playing", "user-read-playback-state"]
    params = {
        "client_id": SETTINGS.spotify_client_id,
        "response_type": "code",
        "redirect_uri": SETTINGS.spotify_redirect_uri,
        "code_challenge_method": "S256",
        "code_challenge": challenge,
        "state": state,
        "scope": " ".join(scopes),
    }
    query = httpx.QueryParams(params)
    url = f"https://accounts.spotify.com/authorize?{query}"
    return RedirectResponse(url)

@router.get("/callback")
async def callback(request: Request, code: Optional[str] = None, state: Optional[str] = None, error: Optional[str] = None):
    if error:
        return PlainTextResponse(f"Spotify authorization error: {error}", status_code=400)
    if not code or not state or state not in _state_pkce:
        return PlainTextResponse("Invalid state/code.", status_code=400)

    verifier = _state_pkce.pop(state)
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SETTINGS.spotify_redirect_uri,
        "client_id": SETTINGS.spotify_client_id,
        "code_verifier": verifier,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        token_res = await client.post("https://accounts.spotify.com/api/token", data=data)
    if token_res.status_code != 200:
        return PlainTextResponse(f"Token exchange failed: {token_res.text}", status_code=400)

    payload = token_res.json()
    session_id = _new_session_id()
    token_repo.save(session_id, {
        "access_token": payload["access_token"],
        "refresh_token": payload.get("refresh_token"),
        "expires_at": time.time() + int(payload.get("expires_in", 3600) * 0.95),
    })

    # Attach session via cookie
    resp = RedirectResponse(url="/")
    resp.set_cookie("session_id", session_id, max_age=60*60*24*7, secure=True, httponly=True, samesite="lax", path="/")
    return resp

@router.get("/logout")
async def logout(request: Request):
    sid = request.cookies.get("session_id")
    if sid:
        token_repo.delete(sid)
    resp = RedirectResponse(url="/")
    resp.delete_cookie("session_id", path="/")
    return resp
