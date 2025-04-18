"""Обработчики действий для текущего хода."""

from random import randint

from aiogram import F, Router
from aiogram.types import CallbackQuery

from maupoly.game import MonoGame
from maupoly.player import Player
from polybot import filters
from polybot.events.journal import MessageChannel

router = Router(name="Turn")


# Обработчики
# ===========


@router.callback_query(F.data == "dice", filters.NowPlaying())
async def roll_dice(
    query: CallbackQuery,
    game: MonoGame,
    player: Player,
    channel: MessageChannel,
) -> None:
    """Обрабатывает бросок кубика."""
    game.process_turn(randint(1, 6) + randint(1, 6))
