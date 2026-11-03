# Pixel Gemini Telegram Bot

A Telegram bot that links a Google account using the official Google OAuth 2.0
authorization-code flow. It does **not** collect Google passwords, automate
Google sign-in, spoof a device, or bypass CAPTCHA / account security.

## Commands

- `/start` — show available commands
- `/login` — receive a Google authorization link
- `/status` — show whether an account is connected
- `/logout` — disconnect the in-memory session
- `/check_offer` — explain the current offer lookup limitation

## Configuration

Create a Google OAuth client in Google Cloud Console as a **Web application**.
Add the exact public callback URL to its authorized redirect URIs:

`https://YOUR_PUBLIC_HOST/oauth2callback`

Configure these environment variables (Replit Secrets, for example):

| Variable | Description |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token from BotFather |
| `GOOGLE_CLIENT_ID` | OAuth web client ID |
| `GOOGLE_CLIENT_SECRET` | OAuth web client secret |
| `GOOGLE_REDIRECT_URI` | Exact HTTPS callback URL above |
| `PORT` | Public app port, normally supplied by the hosting platform |

The hosting platform must expose the Flask callback server publicly over HTTPS.
The redirect URI configured in Google Cloud must match `GOOGLE_REDIRECT_URI`
exactly. Add the Google OAuth consent-screen test users if the app is in Testing.

## Run

```bash
pip install -r requirements.txt
python main.py
```

Open a private chat with the Telegram bot and run `/login`. Complete consent on
Google's own page, then return to Telegram and run `/status`.

## Important limitation

The current bot only requests OpenID Connect profile scopes (`openid`, `email`,
`profile`). Google does not provide a public API in these scopes for checking
individual Google One / Gemini promotional eligibility or extracting redemption
links. Therefore `/check_offer` directs users to Google One rather than scraping
private pages. Do not request broad account access unless a documented Google API
and a clear user-facing purpose require it.

## Security notes

- Google passwords and one-time codes are never sent to Telegram or this app.
- OAuth state is checked on callback.
- Account credentials are held in process memory only and are lost on restart.
- Use HTTPS for the callback and keep the OAuth client secret private.
