from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from maupoly.field import BaseRentField
from maupoly.game import MonoGame
from maupoly.player import Player

TURN_MARKUP = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🎲 Бросить кубик", callback_data="dice")]
    ]
)

NEXT_MARKUP = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🌟 Завершить ход", callback_data="next")]
    ]
)


def get_room_markup(game: MonoGame) -> InlineKeyboardMarkup:
    """Вспомогательная клавиатура для управления комнатой."""
    buttons = [[InlineKeyboardButton(text="☕ Зайти", callback_data="join")]]
    if len(game.players) >= 2:  # noqa: PLR2004
        buttons.append(
            [InlineKeyboardButton(text="🎮 Начать", callback_data="start_game")]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_buy_field_markup(player: Player) -> InlineKeyboardMarkup:
    """Клавиатура для покупки поля."""
    buttons = [
        InlineKeyboardButton(text="👋 Отказаться", callback_data="next"),
    ]

    if (
        isinstance(player.field, BaseRentField)
        and player.balance > player.field.buy_cost
    ):
        buttons.append(
            InlineKeyboardButton(text="💸 Купить", callback_data="buy_field"),
        )

    return InlineKeyboardMarkup(inline_keyboard=[buttons])
