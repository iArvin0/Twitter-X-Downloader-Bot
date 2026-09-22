from pathlib import Path

from app.utils import (
    build_caption,
    compact_error,
    extract_twitter_url,
    format_count,
    format_duration,
    image_files,
    is_supported_twitter_url,
    media_files,
    media_kind,
    twitter_username_from_url,
    video_files,
)


def test_supported_x_status_url() -> None:
    assert is_supported_twitter_url("https://x.com/example/status/123456789")


def test_supported_twitter_status_url() -> None:
    assert is_supported_twitter_url("https://twitter.com/example/status/123456789")


def test_supported_tco_url() -> None:
    assert is_supported_twitter_url("https://t.co/AbCdEf12")


def test_rejects_non_twitter_url() -> None:
    assert not is_supported_twitter_url("https://example.com/user/status/123456789")


def test_extract_url_from_message() -> None:
    text = "Download this: https://x.com/example/status/123456789 please"
    assert extract_twitter_url(text) == "https://x.com/example/status/123456789"


def test_username_from_status_url() -> None:
    assert twitter_username_from_url("https://x.com/iArvin0/status/123456789") == "iArvin0"


def test_format_helpers() -> None:
    assert format_duration(65) == "1:05"
    assert format_duration(3661) == "1:01:01"
    assert format_count(1500) == "1.5K"


def test_compact_error_removes_ansi() -> None:
    assert compact_error("\x1b[31mERROR\x1b[0m test") == "ERROR test"


def test_caption_escapes_html() -> None:
    caption = build_caption(
        {
            "title": "A < B",
            "uploader": "User & Co",
            "duration": 10,
            "view_count": 1500,
        },
        "https://x.com/user/status/123",
    )
    assert "A &lt; B" in caption
    assert "User &amp; Co" in caption


def test_media_files_include_images_and_videos(tmp_path: Path) -> None:
    (tmp_path / "1.mp4").write_bytes(b"x")
    (tmp_path / "2.webp").write_bytes(b"x")
    (tmp_path / "3.jpg").write_bytes(b"x")
    (tmp_path / "note.txt").write_text("x", encoding="utf-8")

    assert [p.name for p in media_files(tmp_path)] == ["1.mp4", "2.webp", "3.jpg"]
    assert [p.name for p in video_files(tmp_path)] == ["1.mp4"]
    assert [p.name for p in image_files(tmp_path)] == ["2.webp", "3.jpg"]


def test_media_kind() -> None:
    assert media_kind(Path("a.jpg")) == "image"
    assert media_kind(Path("a.mp4")) == "video"
    assert media_kind(Path("a.txt")) == "other"
