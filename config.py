"""Runtime configuration. Secrets are supplied through environment variables."""
import os

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", "")
OAUTH_CALLBACK_HOST = os.environ.get("OAUTH_CALLBACK_HOST", "0.0.0.0")
OAUTH_CALLBACK_PORT = int(os.environ.get("PORT", os.environ.get("OAUTH_CALLBACK_PORT", "8080")))
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
