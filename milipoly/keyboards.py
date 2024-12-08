from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from milipoly.config import config
from milipoly.milipoly.game import MonoGame

TURN_MARKUP = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(
        text="🎲 Бросить кубик", switch_inline_query_current_chat=""
    )
]])


def get_room_markup(game: MonoGame) -> InlineKeyboardMarkup:
    """Вспомогательная клавиатура для управления комнатой."""
    buttons = [[
        # InlineKeyboardButton(text="⚙️ Правила",
        #     callback_data="room_settings"
        # ),
        InlineKeyboardButton(text="☕ Зайти", callback_data="join")
    ]]
    if len(game.players) >= config.min_players:
        buttons.append([InlineKeyboardButton(text="🎮 Начать",
            callback_data="start_game"
        )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

