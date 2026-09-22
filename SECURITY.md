# Security

## Secrets

Never commit any of the following:

- `.env`
- Telegram bot tokens
- browser cookies
- `cookies.txt`
- session files

If a bot token is ever exposed in logs, screenshots, commits, or chat messages,
revoke it immediately in BotFather and create a new token.

## Supported content

This project is intended for media that is publicly accessible or content that
the user is authorized to access. It does not bypass DRM, paywalls, private
account permissions, or other access controls.

## Reporting

Please open a GitHub issue without including secrets, cookies, or private URLs.
