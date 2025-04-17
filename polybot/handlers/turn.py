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


@router.callback_query(F.data == "dice", filters.ActivePlayer())
async def roll_dice(
    query: CallbackQuery,
    game: MonoGame,
    player: Player,
    channel: MessageChannel,
) -> None:
    """Обрабатывает бросок кубика."""
    if game is None or player is None or game.player != player:
        await query.answer("🍉 А вы точно сейчас ходите?")

    dice_1 = randint(1, 6)
    dice_2 = randint(1, 6)
    dice_res = dice_1 + dice_2
    game.process_turn(dice_res)

    # TODO: Ты поедешь в другое место
    channel.add(f"💎 Вы попали на поле {game.fields[game.player.index].name}!")

    # TODO: Костыль кароче тут
    game.next_turn()
