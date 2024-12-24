"""Telegram RPi Bot."""

import logging
import os
import subprocess

from telegram import ForceReply
from telegram import Update
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes
from telegram.ext import MessageHandler
from telegram.ext import filters

from tele_rpi_bot.immich import get_immich_status
from tele_rpi_bot.immich import start_immich_services
from tele_rpi_bot.immich import stop_immich_services

# Set up logging to a specific file
LOG_FILE = "tele_rpi_bot.log"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler(LOG_FILE),  # Log to the specified file
        logging.StreamHandler(),  # Optional: Log to console as well
    ],
)

# Set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

LOGGER = logging.getLogger(__name__)

BOT_TELEGRAM_TOKEN: str = os.environ.get("BOT_TELEGRAM_TOKEN", "")
BOT_VALID_USERS: tuple = tuple(os.environ.get("BOT_VALID_USERS", "").split(","))

HELP_MESSAGE = """Commands:
⚪ /start – Start Message
⚪ /shutdown – Shutdown RPi
⚪ /restart – Restart RPi
⚪ /immich_status – Get status of immich server
⚪ /immich_up – Start immich server
⚪ /immich_down – Stop immich server
⚪ /help – Show help
"""


# Define a few command handlers. These usually take the two arguments update and
# context.


def is_valid_user(update: Update):
    """Ensure that only the bot owner (you) can shut down the system."""
    user = update.message.from_user.username
    return user in BOT_VALID_USERS


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(
        f"""Hi {user.username}!
        Welcome to Telegram RPi Bot!
        {HELP_MESSAGE}""",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(HELP_MESSAGE)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shutdown rpi."""
    if is_valid_user(update):
        await update.message.reply_text("Shutting down Raspberry Pi...")
        subprocess.run(["sudo", "shutdown", "-h", "now"])  # Shutdown command
    else:
        await update.message.reply_text("You are not authorized to perform this action.")


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Restart rpi."""
    if is_valid_user(update):
        await update.message.reply_text("Restarting Raspberry Pi...")
        subprocess.run(["sudo", "reboot"])  # Reboot command
    else:
        await update.message.reply_text("You are not authorized to perform this action.")


async def immich_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check immich server status."""
    if is_valid_user(update):
        status = get_immich_status()
        await update.message.reply_text(status)
    else:
        await update.message.reply_text("You are not authorized to perform this action.")


async def immich_up(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start immich server."""
    if is_valid_user(update):
        status = start_immich_services()
        await update.message.reply_text(status)
    else:
        await update.message.reply_text("You are not authorized to perform this action.")


async def immich_down(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stop immich server."""
    if is_valid_user(update):
        status = stop_immich_services()
        await update.message.reply_text(status)
    else:
        await update.message.reply_text("You are not authorized to perform this action.")


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TELEGRAM_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("shutdown", shutdown))
    application.add_handler(CommandHandler("restart", restart))
    application.add_handler(CommandHandler("immich_up", immich_up))
    application.add_handler(CommandHandler("immich_down", immich_down))
    application.add_handler(CommandHandler("immich_status", immich_status))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
