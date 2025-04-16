"""Взаимодействие пользователя с игровыми комнатами.

Присоединение, отключение.
"""

from aiogram import Bot, F, Router
from aiogram.filters import (
    IS_MEMBER,
    IS_NOT_MEMBER,
    ChatMemberUpdatedFilter,
    Command,
)
from aiogram.types import CallbackQuery, ChatMemberUpdated, Message
from loguru import logger

from polybot import keyboards, messages
from polybot.messages import (
    NO_ROOM_MESSAGE,
    NOT_ENOUGH_PLAYERS,
    get_closed_room_message,
    get_room_status,
)
from maupoly.exceptions import (
    AlreadyJoinedError,
    DeckEmptyError,
    LobbyClosedError,
    NoGameInChatError,
)
from maupoly.game import MonoGame
from maupoly.session import SessionManager

router = Router(name="Player")

# Обработчики
# ===========

@router.message(Command("join"))
async def join_player(message: Message,
    sm: SessionManager,
    game: MonoGame | None,
    bot: Bot
):
    """Подключает пользователя к игре."""
    try:
        sm.join(message.chat.id, message.from_user)
    except NoGameInChatError:
        await message.answer(NO_ROOM_MESSAGE)
    except LobbyClosedError:
        await message.answer(get_closed_room_message(game))
    except AlreadyJoinedError:
        await message.answer("🍰 Вы уже с нами в комнате.")
    except DeckEmptyError:
        await message.answer("👀 К сожалению у нас не осталось для вас карт.")
    else:
        try:
            await message.delete()
        except Exception as e:
            logger.warning("Unable to delete message: {}", e)
            await message.answer(
                "👀 Пожалуйста выдайте мне права удалять сообщения в чате."
            )

    if game is not None:
        if not game.started:
            await bot.edit_message_text(
                text=get_room_status(game),
                chat_id=game.chat_id,
                message_id=game.lobby_message,
                reply_markup=keyboards.get_room_markup(game)
            )
        else:
            game.journal.add(
                "🍰 Добро пожаловать в игру, "
                f"{message.from_user.mention_html()}!"
            )
            await game.journal.send_journal()

@router.message(Command("leave"))
async def leave_player(message: Message,
    sm: SessionManager,
    game: MonoGame | None
):
    """Выход пользователя из игры."""
    if game is None:
        return await message.answer(NO_ROOM_MESSAGE)

    try:
        game.remove_player(message.from_user.id)
        sm.user_to_chat.pop(message.from_user.id)
    except NoGameInChatError:
        return await message.answer("👀 Вас нет в комнате чтобы выйти из неё.")

    if game.started:
        game.journal.add(text=(
            "🍰 Ладненько, следующих ход за "
            f"{game.player.user.mention_html()}."
        ))
        game.journal.set_markup(keyboards.TURN_MARKUP)
        await game.journal.send_journal()
    else:
        status_message = (
            f"{NOT_ENOUGH_PLAYERS}\n\n{messages.end_game_message(game)}"
        )
        sm.remove(message.chat.id)
        await message.answer(status_message)


# Обработчики для кнопок
# ======================

@router.callback_query(F.data=="join")
async def join_callback(query: CallbackQuery,
    sm: SessionManager,
    game: MonoGame |  None
):
    """Добавляет игрока в текущую комнату."""
    try:
        sm.join(query.message.chat.id, query.from_user)
    except LobbyClosedError:
        await query.message.answer(get_closed_room_message(game))
    except AlreadyJoinedError:
        await query.message.answer("🍰 Вы уже и без того с нами в комнате.")
    else:
        await query.message.edit_text(
            text=get_room_status(game),
            reply_markup=keyboards.get_room_markup(game)
        )


# Обработчики событий
# ===================

@router.chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def on_user_leave(event: ChatMemberUpdated,
    game: MonoGame | None,
    sm: SessionManager
):
    """Исключаем пользователя, если тот осмелился выйти из чата."""
    if game is None:
        return

    try:
        game.remove_player(event.from_user.id)
        sm.user_to_chat.pop(event.from_user.id)
    except NoGameInChatError:
        pass

    if game.started:
        game.journal.add(
           f"Ладненько, следующих ход за {game.player.user.mention_html()}."
        )
        game.journal.set_markup(keyboards.TURN_MARKUP)
        await game.journal.send_journal()
    else:
        status_message = NOT_ENOUGH_PLAYERS
        sm.remove(event.chat.id)
        await event.answer(status_message)
