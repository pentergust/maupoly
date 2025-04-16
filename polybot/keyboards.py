from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from maupoly.game import MonoGame
from polybot.config import config

TURN_MARKUP = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(
        text="🎲 Бросить кубик", callback_data="dice"
    )
]])


def get_room_markup(game: MonoGame) -> InlineKeyboardMarkup:
    """Вспомогательная клавиатура для управления комнатой."""
    buttons = [[
        InlineKeyboardButton(text="☕ Зайти", callback_data="join")
    ]]
    if len(game.players) >= config.min_players:
        buttons.append([InlineKeyboardButton(text="🎮 Начать",
            callback_data="start_game"
        )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

