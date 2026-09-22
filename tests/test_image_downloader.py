from pathlib import Path
from types import SimpleNamespace

from app.image_downloader import GalleryDLImageDownloader


def test_gallery_dl_command_downloads_only_images(tmp_path: Path) -> None:
    settings = SimpleNamespace(
        max_media_per_post=4,
        max_file_size_mb=49,
        download_timeout_seconds=300,
        cookies_file=None,
    )
    downloader = GalleryDLImageDownloader(settings)
    command = downloader.build_command(
        "https://x.com/example/status/123456789",
        tmp_path,
    )

    assert "gallery_dl" in command
    assert "--filter" in command
    assert "extension in ('jpg', 'jpeg', 'png', 'webp', 'avif')" in command
    assert "twitter.tweet-endpoint=restid" in command


def test_gallery_dl_command_uses_cookie_file(tmp_path: Path) -> None:
    cookie_file = tmp_path / "cookies.txt"
    settings = SimpleNamespace(
        max_media_per_post=4,
        max_file_size_mb=49,
        download_timeout_seconds=300,
        cookies_file=cookie_file,
    )
    downloader = GalleryDLImageDownloader(settings)
    command = downloader.build_command(
        "https://x.com/example/status/123456789",
        tmp_path,
    )

    assert "-C" in command
    assert str(cookie_file) in command
