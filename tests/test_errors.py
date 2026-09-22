from app.errors import map_download_error


def test_private_error_mapping() -> None:
    error = map_download_error("This post is from a private account")
    assert "not publicly accessible" in str(error)


def test_rate_limit_error_mapping() -> None:
    error = map_download_error("HTTP Error 429: Too Many Requests")
    assert "rate-limited" in str(error)


def test_ffmpeg_error_mapping() -> None:
    error = map_download_error("ffmpeg not found")
    assert "FFmpeg was not found" in str(error)


def test_no_video_error_mentions_all_media_types() -> None:
    error = map_download_error("No video could be found in this tweet")
    assert "No downloadable photo, video, or GIF" in str(error)
