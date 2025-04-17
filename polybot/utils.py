"""Игровой контекст.

Вспомогательные функции для получения игрового контекста.
"""

from dataclasses import dataclass

from aiogram.types import (
    CallbackQuery,
    ChatMemberUpdated,
    ChosenInlineResult,
    InlineQuery,
    Message,
    Update,
)

from maupoly.game import MonoGame
from maupoly.player import Player
from maupoly.session import SessionManager


@dataclass(frozen=True, slots=True)
class GameContext:
    """Игровой контекст.

    Передаётся в обработчики команд и фильтры.
    Содержит экземпляр активной игры, а также игрока.
    """

    game: MonoGame | None
    player: Player | None


def get_context(
    sm: SessionManager,
    event: Message | ChatMemberUpdated | CallbackQuery | Message | Update,
) -> GameContext:
    """Получает игровой контекста."""
    if isinstance(event, Message | ChatMemberUpdated):
        game = sm.storage.get_game(str(event.chat.id))

    elif isinstance(event, CallbackQuery):
        if event.message is None:
            game = sm.storage.get_player_game(str(event.from_user.id))
        else:
            game = sm.storage.get_game(str(event.message.chat.id))

    elif isinstance(event, InlineQuery | ChosenInlineResult):
        game = sm.storage.get_player_game(str(event.from_user.id))

    else:
        raise ValueError("Unknown update type")

    player = (
        None
        if game is None or event.from_user is None
        else game.get_player(str(event.from_user.id))
    )
    return GameContext(game=game, player=player)
