from __future__ import annotations

import asyncio
import logging

from telegram import BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from .config import Settings
from .downloader import TwitterDownloader
from .handlers import handle_text, help_command, start
from .logging_config import configure_logging

logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    await application.bot.set_my_commands(
        [
            BotCommand("start", "Start the bot"),
            BotCommand("help", "Show help"),
        ]
    )


async def error_handler(update: object, context) -> None:
    del update
    logger.error("Telegram update error", exc_info=context.error)


def main() -> None:
    settings = Settings.from_env()
    configure_logging(settings.log_dir, settings.log_level, settings.bot_token)

    logger.info("Starting X / Twitter Downloader Bot")

    application = (
        Application.builder()
        .token(settings.bot_token)
        .post_init(post_init)
        .build()
    )

    application.bot_data["settings"] = settings
    application.bot_data["downloader"] = TwitterDownloader(settings)
    application.bot_data["download_semaphore"] = asyncio.Semaphore(
        settings.max_concurrent_downloads
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_error_handler(error_handler)

    application.run_polling(drop_pending_updates=True)
