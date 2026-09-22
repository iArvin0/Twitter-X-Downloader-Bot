from __future__ import annotations

import html
import re
from pathlib import Path
from urllib.parse import urlparse

ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
URL_RE = re.compile(r"https?://[^\s<>()]+", re.IGNORECASE)

VIDEO_EXTENSIONS = {".mp4", ".m4v", ".mov", ".webm", ".mkv"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".avif"}

TWITTER_HOSTS = {
    "x.com",
    "www.x.com",
    "mobile.x.com",
    "twitter.com",
    "www.twitter.com",
    "mobile.twitter.com",
    "t.co",
    "www.t.co",
}


def extract_twitter_url(text: str) -> str | None:
    for match in URL_RE.finditer(text):
        candidate = match.group(0).rstrip(".,;:!?)]}'\"")
        if is_supported_twitter_url(candidate):
            return candidate
    return None


def is_supported_twitter_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except ValueError:
        return False

    if parsed.scheme not in {"http", "https"}:
        return False

    host = parsed.netloc.lower()
    if host not in TWITTER_HOSTS:
        return False

    if host in {"t.co", "www.t.co"}:
        return bool(parsed.path.strip("/"))

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) >= 3 and parts[-2].lower() == "status":
        return parts[-1].isdigit()

    return False


def twitter_username_from_url(url: str) -> str | None:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if host in {"t.co", "www.t.co"}:
        return None

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) >= 3 and parts[-2].lower() == "status":
        username = parts[-3]
        if username.lower() not in {"i", "web"}:
            return username
    return None


def strip_ansi(value: str) -> str:
    return ANSI_RE.sub("", value).strip()


def compact_error(value: str, limit: int = 500) -> str:
    value = strip_ansi(value)
    value = re.sub(r"\s+", " ", value).strip()
    if len(value) > limit:
        return value[: limit - 1] + "…"
    return value


def format_duration(seconds: int | float | None) -> str | None:
    if not seconds:
        return None
    total = int(seconds)
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def format_count(value: int | float | None) -> str | None:
    if value is None:
        return None
    number = int(value)
    if number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.1f}B"
    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    if number >= 1_000:
        return f"{number / 1_000:.1f}K"
    return str(number)


def build_caption(info: dict, source_url: str, part: str | None = None) -> str:
    title = info.get("title") or "X / Twitter media"
    uploader = info.get("uploader") or info.get("channel")
    uploader_id = info.get("uploader_id") or info.get("channel_id")
    duration = format_duration(info.get("duration"))
    likes = format_count(info.get("like_count"))
    reposts = format_count(info.get("repost_count") or info.get("retweet_count"))
    views = format_count(info.get("view_count"))

    lines = [f"🐦 <b>{html.escape(str(title))}</b>"]
    if uploader:
        creator = str(uploader)
        if uploader_id and str(uploader_id).lower() not in creator.lower():
            creator += f" (@{uploader_id})"
        lines.append(f"👤 {html.escape(creator)}")
    elif uploader_id:
        lines.append(f"👤 @{html.escape(str(uploader_id))}")

    if duration:
        lines.append(f"⏱ {duration}")
    if views:
        lines.append(f"👁 {views}")
    if likes:
        lines.append(f"❤️ {likes}")
    if reposts:
        lines.append(f"🔁 {reposts}")
    if part:
        lines.append(f"📦 {html.escape(part)}")

    lines.append(f'🔗 <a href="{html.escape(source_url, quote=True)}">Open post</a>')
    return "\n".join(lines)[:1000]


def media_kind(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in IMAGE_EXTENSIONS:
        return "image"
    if suffix in VIDEO_EXTENSIONS:
        return "video"
    return "other"


def media_files(directory: Path) -> list[Path]:
    allowed = VIDEO_EXTENSIONS | IMAGE_EXTENSIONS
    return sorted(
        (
            path
            for path in directory.iterdir()
            if path.is_file()
            and path.suffix.lower() in allowed
            and not path.name.endswith((".part", ".ytdl"))
        ),
        key=lambda path: path.name,
    )


def video_files(directory: Path) -> list[Path]:
    return [path for path in media_files(directory) if media_kind(path) == "video"]


def image_files(directory: Path) -> list[Path]:
    return [path for path in media_files(directory) if media_kind(path) == "image"]
