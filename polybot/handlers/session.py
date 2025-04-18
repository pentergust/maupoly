"""Управляет игровыми сессиями.

Позволяет создавать комнаты, удалять их, переключать настройки.
Если вас интересует взаимодействий игроков в сессиями, то перейдите
в роутер `player`.
"""

from aiogram import F, Router
from aiogram.filters import Command

# from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, Message
from loguru import logger

from maupoly.exceptions import NoGameInChatError, NotEnoughPlayersError
from maupoly.game import MonoGame
from maupoly.player import BaseUser
from maupoly.session import SessionManager
from polybot import filters, messages
from polybot.events.journal import MessageChannel

router = Router(name="Sessions")

ROOM_SETTINGS = (
    "⚙️ <b>Настройки комнаты</b>:\n\n"
    "В этом разделе вы можете настроить дополнительные параметры для игры.\n"
    "Они привносят дополнительное разнообразие в игровые правила.\n\n"
    "Пункты помеченные 🌟 <b>активированы</b> и уже наводят суету."
)


# Обработчики
# ===========


@router.message(Command("game"))
async def create_game(
    message: Message, sm: SessionManager, game: MonoGame | None
) -> None:
    """Создаёт новую комнату."""
    if message.chat.type == "private":
        await message.answer("👀 Игры создаются в групповом чате.")

    if game is not None and game.started:
        await message.answer(
            "🔑 Игра уже начата. Для начала её нужно завершить. (/stop)"
        )
        return

    if message.from_user is None:
        raise ValueError("None User tries create new game")

    game = sm.create(
        message.chat.id,
        BaseUser(message.from_user.id, message.from_user.mention_html()),
    )


@router.message(Command("start"))
async def start_gama(message: Message, game: MonoGame | None) -> None:
    """Запускает игру в комнате."""
    if message.chat.type == "private":
        await message.answer(messages.HELP_MESSAGE)
        return

    if game is None:
        message.answer(messages.NO_ROOM_MESSAGE)
        return

    elif game.started:
        await message.answer("🌳 Игра уже началась ранее.")

    elif len(game.players) < 2:  # noqa: PLR2004
        raise NotEnoughPlayersError

    else:
        try:
            await message.delete()
        except Exception as e:
            logger.warning("Unable to delete message: {}", e)
            await message.answer(
                "🧹 Пожалуйста выдайте мне права удалять сообщения в чате."
            )

        game.start()


@router.message(Command("stop"), filters.GameOwner())
async def stop_gama(
    message: Message, game: MonoGame, sm: SessionManager
) -> None:
    """Принудительно завершает текущую игру."""
    sm.remove(game.room_id)


# Управление участниками комнатами
# ================================


@router.message(Command("kick"), filters.GameOwner())
async def kick_player(
    message: Message,
    game: MonoGame,
    sm: SessionManager,
    channel: MessageChannel,
) -> None:
    """Выкидывает участника из комнаты."""
    if (
        message.reply_to_message is None
        or message.reply_to_message.from_user is None
    ):
        raise ValueError(
            "🍷 Перешлите сообщение негодника, которого нужно исключить."
        )

    kicked_user = message.reply_to_message.from_user
    kick_player = game.get_player(kicked_user.id)
    channel.add(
        f"🧹 {game.owner.name} выгнал "
        f"{kicked_user} из игры за плохое поведение.\n"
    )
    await channel.send()
    if kick_player is not None:
        sm.leave(kick_player)


@router.message(Command("skip"), filters.GameOwner())
async def skip_player(
    message: Message, game: MonoGame, channel: MessageChannel
) -> None:
    """пропускает участника за долгое бездействие."""
    skip_player = game.player
    channel.add(
        f"☕ {skip_player.name} потерял свои кубики.\n"
        "Мы их нашли и дали игроку ещё немного карт от нас.\n"
    )
    game.next_turn()
    await channel.send()


# Обработчики событий
# ===================


@router.callback_query(F.data == "start_game")
async def start_game_call(query: CallbackQuery, game: MonoGame | None) -> None:
    """Запускает игру в комнате."""
    if not isinstance(query.message, Message):
        raise ValueError("Query.message is not a Message")

    try:
        await query.message.delete()
    except Exception as e:
        logger.warning("Unable to delete message: {}", e)
        await query.message.answer(
            "👀 Пожалуйста выдайте мне права удалять сообщения в чате."
        )

    if game is None:
        raise NoGameInChatError

    game.start()
