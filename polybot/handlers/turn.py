"""Обработчики действий для текущего хода."""

from random import randint

from aiogram import F, Router
from aiogram.types import CallbackQuery

from polybot import keyboards
from maupoly.game import MonoGame
from maupoly.player import Player

router = Router(name="Turn")


# Обработчики
# ===========

@router.callback_query(F.data=="dice")
async def roll_dice(
    query: CallbackQuery,
    game: MonoGame | None,
    player: Player | None
):
    if (game is None or player is None or game.player != player):
        await query.answer("🍉 А вы точно сейчас ходите?")

    dice_1 = randint(1, 6)
    dice_2 = randint(1, 6)
    dice_res = dice_1 + dice_2
    game.process_turn(dice_res)

    game.journal.add(
        f"🎲 Вы бросаете кубики... {dice_res} ({dice_1}, {dice_2})"
    )
    game.journal.add(
        f"💎 Вы попали на поле {game.fields[game.player.index].name}!"
    )

    game.journal.set_markup(None)
    await game.journal.send_journal()
    # TODO: Костыль кароче тут

    game.next_turn()
    game.journal.add(
        f"🍰 <b>Следующий ходит</b>: {game.player.user.mention_html()}"
    )
    game.journal.set_markup(keyboards.TURN_MARKUP)
    await game.journal.send_journal()
