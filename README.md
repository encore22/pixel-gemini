# Pixel Gemini — standalone website

A Flask website that signs users in with Google's official OAuth 2.0 / OpenID Connect flow. No Telegram bot is required.

## Features
- Google sign-in using Google's official consent page
- Requests only `openid`, `email`, and `profile`
- Shows verified email and basic profile after login
- Logout clears the local session
- No Google passwords or verification codes are collected
- No browser automation, CAPTCHA bypass, or private-page scraping

## Deploy on Render (free web service)
1. Create a Render **Web Service** from this GitHub repository and select branch `web-oauth`.
2. Use the settings in `render.yaml` (or configure manually): Build command `pip install -r requirements.txt`; Start command `gunicorn app:app`.
3. After Render creates the service, copy its public HTTPS hostname, e.g. `https://your-service.onrender.com`.
4. In Google Cloud Console → Google Auth Platform → Clients, edit your OAuth client (type **Web application**) and add this exact Authorized redirect URI: `https://your-service.onrender.com/oauth2callback`.
5. In Render → Environment, set:
   - `GOOGLE_CLIENT_ID`: OAuth client ID
   - `GOOGLE_CLIENT_SECRET`: OAuth client secret
   - `GOOGLE_REDIRECT_URI`: exactly the callback URI above
   - `FLASK_SECRET_KEY`: long random secret (Render blueprint can generate it)
6. Redeploy, open the Render URL, and test **Continue with Google**.

The redirect URI in Google Cloud and `GOOGLE_REDIRECT_URI` must match exactly. If the OAuth app is in Testing mode, add test accounts under **Audience → Test users**.

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Set `FLASK_SECRET_KEY`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_REDIRECT_URI` first. For local testing, configure a matching localhost redirect URI in Google Cloud.

## Scope and limitations
This app verifies identity and displays basic Google profile information. It does not access Google One subscriptions, Gemini promotions, private account pages, or promotional eligibility. Google does not expose those details through the basic OpenID Connect scopes used here.

## Session and privacy
The app stores basic profile details in a signed, secure session cookie. OAuth access tokens are not persisted. Use HTTPS in production and keep the client secret private. Render's free service may spin down when idle; its ephemeral runtime is not intended for durable data storage.
