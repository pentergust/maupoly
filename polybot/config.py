"""Настройки бота и Игры.

Находятся в одном месте, чтобы все обработчики могли получить доступ
к настройкам.
Загружаются один раз при запуске бота и больше не изменяются.
"""

from pathlib import Path

from aiogram.client.default import DefaultBotProperties
from loguru import logger
from pydantic import BaseModel, SecretStr

# Общие настройки бота
# ====================

CONFIG_PATh = Path("config.json")

class Config(BaseModel):
    """Общие настройки для Telegram бота, касающиеся Uno."""

    token: SecretStr
    admin_list: list[int]
    db_url: str = "sqlite://poly.sqlite"
    open_lobby: bool = True
    min_players: int = 2

try:
    with open(CONFIG_PATh) as f:
        config: Config = Config.model_validate_json(f.read())
except FileNotFoundError as e:
    logger.error(e)
    logger.info("Copy config.json.sample, then edit it")


# Параметры по умолчанию для бота aiogram
# =======================================

# Настройки бота по умолчанию
default = DefaultBotProperties(
    parse_mode="html"
)