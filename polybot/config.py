"""Настройки бота и Игры.

Находятся в одном месте, чтобы все обработчики могли получить доступ
к настройкам.
Загружаются один раз при запуске бота и больше не изменяются.
"""

from pathlib import Path

from aiogram.client.default import DefaultBotProperties
from pydantic import BaseModel, SecretStr
from pydantic_settings import SettingsConfigDict

from maupoly.session import SessionManager

# Общие настройки бота
# ====================


class Config(BaseModel):
    """Общие настройки для Telegram бота, касающиеся игры.

    - telegram_token: Токен от Telegram бота.
    - assets_path: Путь к директории с игровыми асетами (поле).
    """

    telegram_token: SecretStr
    assets_path: Path

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )


config: Config = Config()  # type: ignore


# Параметры по умолчанию для бота aiogram
# =======================================

# Настройки бота по умолчанию
default = DefaultBotProperties(parse_mode="html")
# FIXME: Аннотации типов не хватает немного
sm = SessionManager()
