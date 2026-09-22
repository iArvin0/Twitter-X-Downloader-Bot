from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


class RedactingFormatter(logging.Formatter):
    def __init__(self, fmt: str, secret: str) -> None:
        super().__init__(fmt)
        self.secret = secret

    def format(self, record: logging.LogRecord) -> str:
        rendered = super().format(record)
        if self.secret:
            rendered = rendered.replace(self.secret, "[REDACTED_BOT_TOKEN]")
        return rendered


def configure_logging(log_dir: Path, level: str, bot_token: str) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(getattr(logging, level, logging.INFO))

    fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    formatter = RedactingFormatter(fmt, bot_token)

    console = logging.StreamHandler()
    console.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        log_dir / "bot.log",
        maxBytes=2 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    root.addHandler(console)
    root.addHandler(file_handler)

    # httpx INFO logs include Telegram Bot API URLs, which contain the bot token.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
