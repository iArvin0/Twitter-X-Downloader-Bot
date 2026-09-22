from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True, slots=True)
class Settings:
    bot_token: str
    download_dir: Path
    log_dir: Path
    log_level: str
    max_file_size_mb: int
    max_photo_size_mb: int
    max_concurrent_downloads: int
    max_media_per_post: int
    download_timeout_seconds: int
    cookies_file: Path | None

    @classmethod
    def from_env(cls) -> Settings:
        load_dotenv()

        bot_token = os.getenv("BOT_TOKEN", "").strip()
        if not bot_token:
            raise RuntimeError(
                "BOT_TOKEN is missing. Copy .env.example to .env and add your BotFather token."
            )

        download_dir = Path(os.getenv("DOWNLOAD_DIR", "downloads")).expanduser()
        log_dir = Path(os.getenv("LOG_DIR", "logs")).expanduser()

        cookies_raw = os.getenv("YTDLP_COOKIES_FILE", "").strip()
        cookies_file = Path(cookies_raw).expanduser() if cookies_raw else None
        if cookies_file and not cookies_file.is_file():
            raise RuntimeError(f"YTDLP_COOKIES_FILE does not exist: {cookies_file}")

        settings = cls(
            bot_token=bot_token,
            download_dir=download_dir,
            log_dir=log_dir,
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            max_file_size_mb=_positive_int("MAX_FILE_SIZE_MB", 49),
            max_photo_size_mb=_positive_int("MAX_PHOTO_SIZE_MB", 10),
            max_concurrent_downloads=_positive_int("MAX_CONCURRENT_DOWNLOADS", 2),
            max_media_per_post=_bounded_int("MAX_MEDIA_PER_POST", 4, 1, 4),
            download_timeout_seconds=_positive_int("DOWNLOAD_TIMEOUT_SECONDS", 300),
            cookies_file=cookies_file,
        )
        settings.download_dir.mkdir(parents=True, exist_ok=True)
        settings.log_dir.mkdir(parents=True, exist_ok=True)
        return settings

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    @property
    def max_photo_size_bytes(self) -> int:
        return self.max_photo_size_mb * 1024 * 1024


def _positive_int(name: str, default: int) -> int:
    raw = os.getenv(name, str(default))
    try:
        value = int(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer.") from exc
    if value < 1:
        raise RuntimeError(f"{name} must be at least 1.")
    return value


def _bounded_int(name: str, default: int, minimum: int, maximum: int) -> int:
    value = _positive_int(name, default)
    if not minimum <= value <= maximum:
        raise RuntimeError(f"{name} must be between {minimum} and {maximum}.")
    return value
