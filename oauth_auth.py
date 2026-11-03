"""Google OAuth 2.0 authorization-code flow for Telegram users.

The bot never asks for or handles Google passwords. OAuth state and tokens are
kept in memory; configure a public HTTPS callback URL in Google Cloud Console.
"""
import logging
import threading
from typing import Dict
from urllib.parse import urlparse

import requests
from flask import Flask, request
from google_auth_oauthlib.flow import Flow

import config

logger = logging.getLogger(__name__)
app = Flask(__name__)
_lock = threading.Lock()
_pending: Dict[str, tuple] = {}
_accounts: Dict[int, dict] = {}
_server_started = False

SCOPES = ["openid", "email", "profile"]


def _client_config():
    if not all((config.GOOGLE_CLIENT_ID, config.GOOGLE_CLIENT_SECRET,
                config.GOOGLE_REDIRECT_URI)):
        raise RuntimeError(
            "Thiếu GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET hoặc GOOGLE_REDIRECT_URI."
        )
    return {
        "web": {
            "client_id": config.GOOGLE_CLIENT_ID,
            "client_secret": config.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [config.GOOGLE_REDIRECT_URI],
        }
    }


def create_authorization_url(chat_id: int) -> str:
    flow = Flow.from_client_config(_client_config(), scopes=SCOPES,
                                   redirect_uri=config.GOOGLE_REDIRECT_URI)
    url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    with _lock:
        _pending[state] = (chat_id, flow)
    return url


def get_account(chat_id: int):
    with _lock:
        return _accounts.get(chat_id)


def disconnect(chat_id: int) -> None:
    with _lock:
        _accounts.pop(chat_id, None)


@app.get("/oauth2callback")
def oauth_callback():
    state = request.args.get("state", "")
    with _lock:
        pending = _pending.pop(state, None)
    if not pending:
        return ("Authorization expired or invalid. Return to Telegram and run /login again.", 400)

    chat_id, flow = pending
    if request.args.get("error"):
        return ("Google authorization was not completed. Return to Telegram and run /login again.", 400)

    try:
        flow.fetch_token(authorization_response=request.url)
        response = requests.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {flow.credentials.token}"},
            timeout=15,
        )
        response.raise_for_status()
        profile = response.json()
        email = profile.get("email")
        if not email or not profile.get("email_verified", False):
            raise RuntimeError("Google did not return a verified email address.")
        with _lock:
            _accounts[chat_id] = {
                "email": email,
                "credentials": flow.credentials,
            }
        logger.info("Google OAuth completed for Telegram chat %s", chat_id)
        return ("Google account connected successfully. You can return to Telegram.", 200)
    except Exception:
        logger.exception("Google OAuth callback failed")
        return ("Could not complete Google authorization. Return to Telegram and run /login again.", 400)


def start_callback_server() -> None:
    global _server_started
    if _server_started:
        return
    _server_started = True
    thread = threading.Thread(
        target=lambda: app.run(host=config.OAUTH_CALLBACK_HOST,
                               port=config.OAUTH_CALLBACK_PORT,
                               threaded=True, use_reloader=False),
        name="google-oauth-callback",
        daemon=True,
    )
    thread.start()
