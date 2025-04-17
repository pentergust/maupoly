"""Взаимодействие пользователя с игровыми комнатами.

Присоединение, отключение.
"""

from aiogram import F, Router
from aiogram.filters import (
    Command,
)
from aiogram.types import CallbackQuery, Message
from loguru import logger

from maupoly.exceptions import (
    AlreadyJoinedError,
)
from maupoly.player import BaseUser, Player
from maupoly.session import SessionManager
from polybot import filters

router = Router(name="Player")

# Обработчики
# ===========


@router.message(Command("join"), filters.ActiveGame())
async def join_player(message: Message, sm: SessionManager) -> None:
    """Подключает пользователя к игре."""
    if message.from_user is None:
        raise ValueError("User can`t be none")

    sm.join(
        str(message.chat.id),
        BaseUser(message.from_user.id, message.from_user.mention_html()),
    )

    try:
        await message.delete()
    except Exception as e:
        logger.warning("Unable to delete message: {}", e)
        await message.answer(
            "👀 Пожалуйста выдайте мне права удалять сообщения в чате."
        )


@router.message(Command("leave"), filters.ActivePlayer())
async def leave_player(
    message: Message, sm: SessionManager, player: Player
) -> None:
    """Выход пользователя из игры."""
    sm.leave(player)


# Обработчики для кнопок
# ======================


@router.callback_query(F.data == "join", filters.ActiveGame())
async def join_callback(query: CallbackQuery, sm: SessionManager) -> None:
    """Добавляет игрока в текущую комнату."""
    if not isinstance(query.message, Message):
        raise ValueError("Query message should be Message instance")

    try:
        sm.join(
            str(query.message.chat.id),
            BaseUser(query.from_user.id, query.from_user.mention_html()),
        )
    except AlreadyJoinedError:
        await query.answer("👋 Вы уже с нами в комнате")
