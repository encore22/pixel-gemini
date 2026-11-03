"""Pixel Gemini: standalone Flask website with Google OpenID Connect login."""
import os
from urllib.parse import urlparse

import requests
from flask import Flask, flash, redirect, render_template, request, session, url_for
from google_auth_oauthlib.flow import Flow

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=3600,
)

CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", "")
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]


def oauth_ready():
    return bool(app.secret_key and CLIENT_ID and CLIENT_SECRET and REDIRECT_URI)


def make_flow(state=None):
    if not oauth_ready():
        raise RuntimeError("Google OAuth chưa được cấu hình đầy đủ trong Environment Variables.")
    client_config = {
        "web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [REDIRECT_URI],
        }
    }
    return Flow.from_client_config(
        client_config, scopes=SCOPES, state=state, redirect_uri=REDIRECT_URI
    )


@app.get("/")
def index():
    return render_template("index.html", account=session.get("account"), ready=oauth_ready())


@app.get("/login")
def login():
    try:
        flow = make_flow()
        authorization_url, state = flow.authorization_url(
            access_type="online",
            include_granted_scopes="true",
            prompt="select_account",
        )
        session["oauth_state"] = state
        session.permanent = True
        return redirect(authorization_url)
    except Exception as exc:
        app.logger.exception("Could not start Google OAuth")
        flash(str(exc), "error")
        return redirect(url_for("index"))


@app.get("/oauth2callback")
def oauth2callback():
    expected_state = session.pop("oauth_state", None)
    received_state = request.args.get("state")
    if not expected_state or not received_state or received_state != expected_state:
        flash("Phiên đăng nhập không hợp lệ hoặc đã hết hạn. Vui lòng thử lại.", "error")
        return redirect(url_for("index"))
    if request.args.get("error"):
        flash("Bạn đã hủy hoặc Google không hoàn tất đăng nhập.", "error")
        return redirect(url_for("index"))

    try:
        flow = make_flow(state=expected_state)
        flow.fetch_token(authorization_response=REDIRECT_URI + '?' + request.query_string.decode('ascii'))
        response = requests.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {flow.credentials.token}"},
            timeout=15,
        )
        response.raise_for_status()
        profile = response.json()
        if not profile.get("email") or not profile.get("email_verified", False):
            raise RuntimeError("Google không trả về địa chỉ email đã xác minh.")
        session.clear()
        session["account"] = {
            "email": profile["email"],
            "name": profile.get("name", ""),
            "picture": profile.get("picture", ""),
        }
        session.permanent = True
        flash("Đăng nhập Google thành công.", "success")
    except Exception:
        app.logger.exception("Google OAuth callback failed")
        flash("Không thể hoàn tất đăng nhập Google. Vui lòng thử lại.", "error")
    return redirect(url_for("index"))


@app.post("/logout")
def logout():
    session.clear()
    flash("Bạn đã đăng xuất.", "success")
    return redirect(url_for("index"))


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))
