"""Обработчики действий для текущего хода."""

from aiogram import F, Router
from aiogram.types import CallbackQuery

from maupoly.dice import Dice
from maupoly.game import MonoGame
from maupoly.player import Player
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


@router.callback_query(F.data == "buy_field", filters.NowPlaying())
async def buy_field(query: CallbackQuery, player: Player) -> None:
    """покупает поле, на котором находится игрок."""
    player.buy_field()
