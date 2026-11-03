"""Telegram bot with Google OAuth 2.0 account linking."""
import logging
import sys

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

import config
from oauth_auth import (
    create_authorization_url,
    disconnect,
    get_account,
    start_callback_server,
)

logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "Pixel Gemini bot\n\n"
        "/login - Connect a Google account securely with Google's OAuth page\n"
        "/status - Show connection status\n"
        "/logout - Disconnect this Telegram session\n"
        "/check_offer - Explain current offer lookup support\n\n"
        "Never send your Google password or verification code to this bot."
    )


async def login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type != "private":
        await update.effective_message.reply_text(
            "For account safety, please run /login in a private chat with this bot."
        )
        return
    try:
        url = create_authorization_url(update.effective_chat.id)
        await update.effective_message.reply_text(
            "Open this Google authorization link and sign in on Google's official page. "
            "The bot will not see your password. After approval, return here and run /status:\n"
            + url,
            disable_web_page_preview=True,
        )
    except Exception as exc:
        logger.exception("Could not start OAuth")
        await update.effective_message.reply_text(f"OAuth setup error: {exc}")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    account = get_account(update.effective_chat.id)
    if account:
        await update.effective_message.reply_text(
            f"Google account connected: {account['email']}\n"
            "Only basic profile identity was requested."
        )
    else:
        await update.effective_message.reply_text(
            "No Google account connected. Run /login to connect through Google OAuth."
        )


async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    disconnect(update.effective_chat.id)
    await update.effective_message.reply_text(
        "Google account disconnected from this bot session."
    )


async def check_offer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    account = get_account(update.effective_chat.id)
    if not account:
        await update.effective_message.reply_text("Run /login first to connect your Google account.")
        return
    await update.effective_message.reply_text(
        f"Google OAuth is connected for {account['email']}, but Google does not expose "
        "personal Google One / Gemini promotional eligibility or redemption links through "
        "the basic profile API used by this bot. I won't scrape private pages or automate "
        "browser sign-in. Please check available plans directly at https://one.google.com/"
    )


def main() -> None:
    if not config.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not configured.")
        sys.exit(1)
    start_callback_server()
    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("login", login))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("logout", logout))
    app.add_handler(CommandHandler("check_offer", check_offer))
    logger.info("Telegram bot started.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
