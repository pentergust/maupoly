"""Главный файл бота.

Здесь определены функции для запуска бота и регистрации всех обработчиков.
"""

import sys
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.types import ErrorEvent, Update
from aiogram.utils.token import TokenValidationError
from loguru import logger

from polybot.config import config, default, sm
from polybot.events.journal import MessageJournal
from polybot.events.router import er
from polybot.handlers import ROUTERS
from polybot.messages import get_error_message
from polybot.utils import get_context

# Константы
# =========

dp = Dispatcher(sm=sm)

# Настраиваем формат отображения логов loguru
# Обратите внимание что в проекте помимо loguru используется logging
LOG_FORMAT = (
    "<light-black>{time:YYYY MM.DD HH:mm:ss.SSS}</> "
    "{file}:{function} "
    "<lvl>{message}</>"
)

# Middleware
# ==========


@dp.message.middleware()
@dp.callback_query.middleware()
@dp.chat_member.middleware()
async def game_middleware(
    handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
    event: Update,
    data: dict[str, Any],
) -> Awaitable[Any]:
    """Предоставляет экземпляр игры в обработчики сообщений."""
    try:
        context = get_context(sm, event)
        data["game"] = context.game
        data["player"] = context.player
        data["channel"] = (
            sm.event_handler.get_channel(context.game.room_id)
            if context.game is not None
            else None
        )
    except Exception as e:
        logger.error(e)
        data["game"] = None
        data["player"] = None
        data["channel"] = None

    return await handler(event, data)


@dp.errors()
async def catch_errors(event: ErrorEvent) -> None:
    """Простой обработчик для ошибок."""
    logger.warning(event)
    logger.exception(event.exception)

    if event.update.callback_query:
        message = event.update.callback_query.message
    elif event.update.message:
        message = event.update.message
    else:
        message = None

    if message is not None:
        await message.answer(get_error_message(event.exception))


# Главная функция запуска бота
# ============================


async def main() -> None:
    """Запускает бота.

    Настраивает журнал
    Загружает все необходимые обработчики.
    После запускает обработку событий.
    """
    logger.remove()
    logger.add(sys.stdout, format=LOG_FORMAT)

    logger.info("Setup bot ...")
    try:
        bot = Bot(
            token=config.telegram_token.get_secret_value(), default=default
        )
    except TokenValidationError as e:
        logger.error(e)
        logger.info("Check your bot token in .env file.")
        sys.exit(1)

    logger.info("Load handlers ...")
    for router in ROUTERS:
        dp.include_router(router)
        logger.debug("Include router {}", router.name)

    logger.info("Set event handler")
    sm.set_handler(MessageJournal(bot, er))

    logger.success("Start polling!")
    await dp.start_polling(bot)
