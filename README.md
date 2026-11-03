# Pixel Gemini — Telegram bot + Google OAuth

A single Flask web service hosts the website, Google OAuth callback, and Telegram webhook. It is designed to minimize Render services: one **Free Web Service**, no Background Worker and no database.

## Render deployment

1. Create a Render Web Service from this repository and choose branch `render-free-telegram-webhook`.
2. Use the included `render.yaml` Blueprint settings, or set:
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn app:app --workers 1 --threads 4 --timeout 120`
3. In Render → Environment, set:
   - `GOOGLE_CLIENT_ID`: Google OAuth Web client ID
   - `GOOGLE_CLIENT_SECRET`: Google OAuth client secret
   - `GOOGLE_REDIRECT_URI`: `https://YOUR-SERVICE.onrender.com/oauth2callback`
   - `TELEGRAM_BOT_TOKEN`: token from BotFather
   - `FLASK_SECRET_KEY`: long random secret (Render can generate it)
   - `TELEGRAM_WEBHOOK_SECRET`: random secret containing only letters, digits, underscores or hyphens
4. In Google Cloud Console → Google Auth Platform → Clients, add the exact `GOOGLE_REDIRECT_URI` above as an Authorized redirect URI. It must match exactly.
5. After deployment, set the Telegram webhook. Replace the placeholders and run this command in a terminal (do not post the bot token or webhook secret in chat):

   ```bash
   curl -X POST "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook" \
     -d "url=https://YOUR-SERVICE.onrender.com/telegram/webhook" \
     -d "secret_token=<TELEGRAM_WEBHOOK_SECRET>"
   ```

6. Open the website and test Google login. Then open the bot in a private Telegram chat and send `/start`, `/login`, `/status`, and `/check_offer`.

## Commands

- `/start` — show help
- `/login` — create a short-lived signed OAuth state and send the official Google authorization URL
- `/status` — show whether an account is linked in the current process
- `/logout` — clear the in-memory link
- `/check_offer` — explain how to check offers on Google's official site

## Free-tier limitations

- Render Free Web Services can spin down when idle; the first webhook or page request after inactivity may be delayed.
- This configuration intentionally uses one Gunicorn worker because account-link status is held in process memory. Deploy/restart or sleep/wake can clear that status. The OAuth success notification is sent to Telegram when the callback completes, but `/status` is not durable across restarts.
- This design has no database and does not persist Google access or refresh tokens.
- For durable account-link status or consistently fast bot responses, use a persistent database and an always-on worker/service plan.

## Security and scope

- Google login uses the official OAuth 2.0 / OpenID Connect flow and requests only `openid`, `email`, and `profile`.
- The bot never asks for Google passwords or one-time codes.
- OAuth state for Telegram linking is signed and expires after 10 minutes. Telegram webhook requests are checked using Telegram's secret-token header.
- The app stores only the verified email in process memory. Google OAuth tokens are not persisted.
- This app cannot verify personal Google One / Gemini promotion eligibility or retrieve private redemption links through the basic profile API. Check current offers directly at https://one.google.com/.
- No password-based browser automation, CAPTCHA bypass, device spoofing, or private-page scraping is included.

## Local development

Set the environment variables above, then:

```bash
pip install -r requirements.txt
python app.py
```

For local webhook testing, use a public HTTPS tunnel and configure Telegram's webhook URL accordingly.
