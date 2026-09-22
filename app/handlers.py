from __future__ import annotations

import asyncio
import logging
import tempfile
from pathlib import Path

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from .config import Settings
from .downloader import TwitterDownloader
from .errors import UserFacingError
from .utils import build_caption, extract_twitter_url, media_kind

logger = logging.getLogger(__name__)

START_TEXT = """\
🐦 <b>X / Twitter Downloader Bot</b>

Send me a public X/Twitter post link and I will download its media.

<b>Supported media:</b>
• Photos
• Videos
• GIF/video media
• Multiple media items in one post

<b>Supported links:</b>
• x.com/.../status/...
• twitter.com/.../status/...
• t.co short links

Use /help for details.
"""

HELP_TEXT = """\
<b>How to use</b>

1. Copy a public X/Twitter post URL.
2. Send the URL to this bot.
3. Wait while the post media is resolved, downloaded, and uploaded.

<b>Supported</b>
• Public post photos in original/highest available quality
• Public post videos
• GIF/video media
• Multiple media items in one post
• x.com, twitter.com and t.co links

<b>How it works</b>
• yt-dlp handles video/GIF media.
• gallery-dl handles photo media.
• If yt-dlp reports "No video could be found", the bot still checks for photos.

<b>Notes</b>
• Private/protected or deleted posts may not be available.
• Some posts may require an authorized cookies file.
• Large files may exceed this bot's configured Telegram upload limit.
• Large photos are sent as documents when Telegram photo upload is unsuitable.
• The bot does not bypass DRM, paywalls, private-account access, or other restrictions.

Only download media you have permission to save or reuse.
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.effective_message:
        await update.effective_message.reply_text(START_TEXT, parse_mode=ParseMode.HTML)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.effective_message:
        await update.effective_message.reply_text(HELP_TEXT, parse_mode=ParseMode.HTML)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    if not message or not message.text or not user or not chat:
        return

    url = extract_twitter_url(message.text)
    if not url:
        await message.reply_text("❌ Please send a valid public X/Twitter post URL.")
        return

    settings: Settings = context.application.bot_data["settings"]
    downloader: TwitterDownloader = context.application.bot_data["downloader"]
    semaphore: asyncio.Semaphore = context.application.bot_data["download_semaphore"]

    logger.info(
        "Download requested | user_id=%s | chat_id=%s | url=%s",
        user.id,
        chat.id,
        url,
    )

    status = await message.reply_text("🔎 Resolving X/Twitter post…")

    try:
        async with semaphore:
            await status.edit_text("⬇️ Downloading post media…")
            with tempfile.TemporaryDirectory(
                prefix="twitter_",
                dir=settings.download_dir,
            ) as temp_dir:
                result = await downloader.download(url, Path(temp_dir))

                sendable = [
                    path
                    for path in result.files
                    if path.stat().st_size <= settings.max_file_size_bytes
                ]
                oversized = [
                    path
                    for path in result.files
                    if path.stat().st_size > settings.max_file_size_bytes
                ]

                if not sendable:
                    raise UserFacingError(
                        f"The downloaded media is larger than the configured "
                        f"{settings.max_file_size_mb} MB Telegram upload limit."
                    )

                await status.edit_text("⬆️ Uploading to Telegram…")
                total = len(sendable)

                for index, path in enumerate(sendable, start=1):
                    part = f"Media {index}/{total}" if total > 1 else None
                    caption = build_caption(result.info, result.source_url, part)
                    await _send_media(message, path, caption, settings)

                if oversized:
                    await message.reply_text(
                        f"⚠️ {len(oversized)} media file(s) were skipped because they exceed "
                        f"the configured {settings.max_file_size_mb} MB upload limit."
                    )

        await status.edit_text("✅ Done.")

    except UserFacingError as exc:
        logger.info("User-facing error | url=%s | error=%s", url, exc)
        await status.edit_text(
            f"❌ <b>Download failed</b>\n\n{exc}",
            parse_mode=ParseMode.HTML,
        )
    except Exception:
        logger.exception("Unhandled request failure | url=%s", url)
        await status.edit_text(
            "❌ <b>Download failed</b>\n\nAn unexpected error occurred. Check the bot logs.",
            parse_mode=ParseMode.HTML,
        )


async def _send_media(message, path: Path, caption: str, settings: Settings) -> None:
    kind = media_kind(path)

    if kind == "image" and path.stat().st_size <= settings.max_photo_size_bytes:
        try:
            with path.open("rb") as media:
                await message.reply_photo(
                    photo=media,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    read_timeout=120,
                    write_timeout=120,
                    connect_timeout=30,
                    pool_timeout=30,
                )
            return
        except Exception:
            logger.warning(
                "send_photo failed, trying document | file=%s",
                path.name,
                exc_info=True,
            )

    if kind == "video":
        try:
            with path.open("rb") as media:
                await message.reply_video(
                    video=media,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    supports_streaming=True,
                    read_timeout=120,
                    write_timeout=120,
                    connect_timeout=30,
                    pool_timeout=30,
                )
            return
        except Exception:
            logger.warning(
                "send_video failed, trying document | file=%s",
                path.name,
                exc_info=True,
            )

    with path.open("rb") as media:
        await message.reply_document(
            document=media,
            caption=caption,
            parse_mode=ParseMode.HTML,
            read_timeout=120,
            write_timeout=120,
            connect_timeout=30,
            pool_timeout=30,
        )
