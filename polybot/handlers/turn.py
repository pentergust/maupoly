"""Обработчики действий для текущего хода."""

from aiogram import F, Router
from aiogram.types import CallbackQuery

from maupoly.dice import Dice
from maupoly.game import MonoGame
from polybot import filters

router = Router(name="Turn")


# Обработчики
# ===========


@router.callback_query(F.data == "dice", filters.NowPlaying())
async def roll_dice(query: CallbackQuery, game: MonoGame) -> None:
    """Обрабатывает бросок кубика."""
    game.process_turn(Dice.new())


@router.callback_query(F.data == "next", filters.NowPlaying())
async def next_turn(query: CallbackQuery, game: MonoGame) -> None:
    """Завершает ход и передаёт ход следующему игроку."""
    game.next_turn()
