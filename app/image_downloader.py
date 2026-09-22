from __future__ import annotations

import logging
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from .config import Settings
from .utils import compact_error, image_files

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ImageDownloadAttempt:
    files: list[Path]
    error: str | None = None


class GalleryDLImageDownloader:
    """Download photo media from a single X/Twitter post using gallery-dl."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def build_command(self, url: str, workspace: Path) -> list[str]:
        command = [
            sys.executable,
            "-m",
            "gallery_dl",
            "--config-ignore",
            "--no-input",
            "--no-colors",
            "--no-mtime",
            "--windows-filenames",
            "-D",
            str(workspace),
            "--range",
            f"1-{self.settings.max_media_per_post}",
            "--filesize-max",
            f"{self.settings.max_file_size_mb}M",
            "--filter",
            "extension in ('jpg', 'jpeg', 'png', 'webp', 'avif')",
            "-o",
            "twitter.tweet-endpoint=restid",
            "-o",
            "twitter.cards=false",
            "-o",
            "twitter.quoted=false",
        ]

        if self.settings.cookies_file:
            command.extend(["-C", str(self.settings.cookies_file)])

        command.append(url)
        return command

    def download(self, url: str, workspace: Path) -> ImageDownloadAttempt:
        command = self.build_command(url, workspace)

        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.settings.download_timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired:
            message = "gallery-dl timed out while resolving X/Twitter photos."
            logger.warning("%s | url=%s", message, url)
            return ImageDownloadAttempt(files=image_files(workspace), error=message)
        except OSError as exc:
            message = f"gallery-dl could not start: {exc}"
            logger.warning("%s | url=%s", message, url)
            return ImageDownloadAttempt(files=image_files(workspace), error=message)

        stdout = compact_error(completed.stdout, 1500) if completed.stdout else ""
        stderr = compact_error(completed.stderr, 1500) if completed.stderr else ""

        if stdout:
            logger.debug("gallery-dl | %s", stdout)

        files = image_files(workspace)
        if completed.returncode == 0:
            if files:
                logger.info("gallery-dl downloaded %s photo(s) | url=%s", len(files), url)
            return ImageDownloadAttempt(files=files)

        error = stderr or stdout or f"gallery-dl exited with code {completed.returncode}"
        logger.warning("gallery-dl failed | url=%s | error=%s", url, error)
        return ImageDownloadAttempt(files=files, error=error)
