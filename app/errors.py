class UserFacingError(Exception):
    """An error that is safe to display to Telegram users."""


def map_download_error(message: str) -> UserFacingError:
    lowered = message.lower()

    if "ffmpeg" in lowered and ("not found" in lowered or "not installed" in lowered):
        return UserFacingError("FFmpeg was not found. Install FFmpeg and restart the bot.")

    if "no video could be found" in lowered:
        return UserFacingError(
            "No downloadable photo, video, or GIF was found in this post. "
            "The post may be text-only or X/Twitter may not be exposing its media."
        )

    if any(
        marker in lowered
        for marker in (
            "login required",
            "authentication required",
            "not authorized",
            "private",
            "protected account",
            "cookies",
            "loginerror",
        )
    ):
        return UserFacingError(
            "This post requires authentication or is not publicly accessible. "
            "For content your own account is authorized to view, configure "
            "YTDLP_COOKIES_FILE with a Netscape-format cookies file."
        )

    if any(
        marker in lowered
        for marker in (
            "does not exist",
            "deleted",
            "no longer available",
            "tweet not found",
            "post not found",
        )
    ):
        return UserFacingError("This post is unavailable or has been deleted.")

    if "unsupported url" in lowered or "unsupportedurlerror" in lowered:
        return UserFacingError(
            "This URL is not supported. Send a public x.com or twitter.com post URL."
        )

    if "429" in lowered or "too many requests" in lowered or "rate limit" in lowered:
        return UserFacingError(
            "X/Twitter temporarily rate-limited this request. Please try again later."
        )

    if "403" in lowered or "forbidden" in lowered:
        return UserFacingError(
            "X/Twitter rejected this request. If the post is public, try again later."
        )

    return UserFacingError(
        "The media could not be downloaded. The post may be unavailable or X/Twitter "
        "may have changed how it serves media."
    )
