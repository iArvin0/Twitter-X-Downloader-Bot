from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from .config import Settings
from .errors import UserFacingError, map_download_error
from .image_downloader import GalleryDLImageDownloader
from .utils import compact_error, media_files, twitter_username_from_url, video_files

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class DownloadResult:
    files: list[Path]
    info: dict[str, Any]
    source_url: str


class YTDLPLogger:
    def debug(self, message: str) -> None:
        if message.startswith("[debug]"):
            logger.debug("yt-dlp | %s", compact_error(message, 1000))

    def warning(self, message: str) -> None:
        logger.warning("yt-dlp | %s", compact_error(message, 1000))

    def error(self, message: str) -> None:
        logger.error("yt-dlp | %s", compact_error(message, 1000))


class TwitterDownloader:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.image_downloader = GalleryDLImageDownloader(settings)

    async def download(self, url: str, workspace: Path) -> DownloadResult:
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(self._download_sync, url, workspace),
                timeout=self.settings.download_timeout_seconds + 10,
            )
        except TimeoutError as exc:
            raise UserFacingError(
                "The download took too long and was stopped. Please try again later."
            ) from exc

    def _download_sync(self, url: str, workspace: Path) -> DownloadResult:
        info: dict[str, Any] = {}
        video_error: str | None = None

        try:
            extracted = self._download_video(url, workspace)
            if extracted:
                info = self._pick_info(extracted)
        except DownloadError as exc:
            video_error = compact_error(str(exc), 1200)
            logger.warning("yt-dlp video attempt failed | url=%s | error=%s", url, video_error)
        except Exception as exc:
            video_error = compact_error(str(exc), 1200)
            logger.exception("Unexpected yt-dlp failure | url=%s", url)

        image_attempt = self.image_downloader.download(url, workspace)

        files = media_files(workspace)[: self.settings.max_media_per_post]
        if files:
            if not info:
                info = self._fallback_info(url)
            logger.info(
                "Media resolved | url=%s | videos=%s | images=%s | total=%s",
                url,
                len(video_files(workspace)),
                len(image_attempt.files),
                len(files),
            )
            return DownloadResult(files=files, info=info, source_url=url)

        # An image-only post normally produces "No video could be found" in yt-dlp.
        # Only surface that after gallery-dl has also failed to find any photos.
        if image_attempt.error:
            if video_error and "no video could be found" not in video_error.lower():
                raise map_download_error(video_error)
            raise map_download_error(image_attempt.error)

        if video_error:
            raise map_download_error(video_error)

        raise UserFacingError(
            "No downloadable photo, video, or GIF was found in this post. "
            "The post may be text-only."
        )

    def _download_video(self, url: str, workspace: Path) -> dict[str, Any] | None:
        options: dict[str, Any] = {
            "format": "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/b",
            "merge_output_format": "mp4",
            "outtmpl": str(workspace / "video_%(id)s_%(playlist_index|0)s.%(ext)s"),
            "restrictfilenames": True,
            "windowsfilenames": True,
            "playlistend": self.settings.max_media_per_post,
            "quiet": True,
            "no_warnings": False,
            "logger": YTDLPLogger(),
            "socket_timeout": 30,
            "retries": 3,
            "fragment_retries": 3,
            "continuedl": True,
            "nopart": False,
        }

        if self.settings.cookies_file:
            options["cookiefile"] = str(self.settings.cookies_file)

        with YoutubeDL(options) as ydl:
            return ydl.extract_info(url, download=True)

    @staticmethod
    def _pick_info(info: dict[str, Any]) -> dict[str, Any]:
        entries = info.get("entries")
        if entries:
            first = next((entry for entry in entries if entry), None)
            if isinstance(first, dict):
                merged = dict(info)
                merged.update({key: value for key, value in first.items() if value is not None})
                return merged
        return info

    @staticmethod
    def _fallback_info(url: str) -> dict[str, Any]:
        username = twitter_username_from_url(url)
        info: dict[str, Any] = {"title": "X / Twitter post"}
        if username:
            info["uploader_id"] = username
        return info
