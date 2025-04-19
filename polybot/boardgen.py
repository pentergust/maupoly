"""Генератор изображения игрового поля.

Используется чтобы передавать актуальное состояние игры в Telegram бота.
На изображении игровой доски есть:

- Активный игрок.
- Положение всех игроков.
"""

import io
from pathlib import Path
from time import time
from typing import NamedTuple

from aiogram.types import BufferedInputFile
from PIL import Image
from PIL.ImageFile import ImageFile

from maupoly.game import MonoGame

# Коллекция асетов изображений
ASSETS_PATH = Path("assets/")


class Asset(NamedTuple):
    """Игровой асет из файла.

    Содержит в себе путь к файлу и координаты, по которым надо его
    установить.
    """

    name: str
    x: int
    y: int

    def paste_to(self, board: ImageFile | Image.Image) -> None:
        """Вспомогательный метод для быстрой установки асета на изображение."""
        asset_image = Image.open(ASSETS_PATH / Path(self.name)).convert("RGBA")
        board.paste(asset_image, (self.x, self.y))


# Просчитанные координаты для поля
# ================================

PLAYER_ASSET = [
    Asset("player_red.png", 448, 288),
    Asset("player_yellow.png", 288, 448),
    Asset("player_green.png", 608, 448),
    Asset("player_blue.png", 448, 608),
]

POINTER_COORDINATES = [
    # UP
    (104, 104),
    (208, 128),
    (280, 128),
    (352, 128),
    (424, 128),
    (496, 128),
    (568, 128),
    (640, 128),
    (712, 128),
    (784, 128),
    # Right
    (888, 104),
    (872, 208),
    (872, 280),
    (872, 352),
    (872, 424),
    (872, 496),
    (872, 568),
    (872, 640),
    (872, 712),
    (872, 784),
    # Down
    (888, 888),
    (784, 872),
    (712, 872),
    (640, 872),
    (568, 872),
    (496, 872),
    (424, 872),
    (352, 872),
    (280, 872),
    (208, 872),
    (104, 888),
    (120, 784),
    (120, 712),
    (120, 640),
    (120, 568),
    (120, 496),
    (120, 424),
    (120, 352),
    (120, 280),
    (120, 208),
]

FIELD_COORDINATES = [
    # Rotate 0 / up
    (192, 88),
    (336, 88),
    (480, 88),
    (624, 88),
    (696, 88),
    (768, 88),
    # Rotate 1 / right
    (840, 192),
    (840, 264),
    (840, 336),
    (840, 408),
    (840, 480),
    (840, 552),
    (840, 696),
    (840, 768),
    # Rotate 2 / Down
    (768, 840),
    (624, 840),
    (552, 840),
    (480, 840),
    (408, 840),
    (336, 840),
    (264, 840),
    (192, 840),
    # Rotate 3 / Right
    (88, 768),
    (88, 696),
    (88, 552),
    (88, 480),
    (88, 336),
    (88, 192),
]


def get_rotate(index: int) -> int:
    """Получает поворот поля в зависимости от индекса."""
    if index < 6:  # noqa: PLR2004
        return 0
    elif index < 14:  # noqa: PLR2004
        return 1
    elif index < 22:  # noqa: PLR2004
        return 2
    else:
        return 3


# Вспомогательные функции отрисовки
# =================================


def paste_player_pointer(board: Image.Image, index: int, color: int) -> None:
    """Вставляет указатель на игрока нв изображение."""
    coordinates = POINTER_COORDINATES[index]
    player_pointer = Asset(
        f"pointer_{color}.png", coordinates[0], coordinates[1]
    )
    player_pointer.paste_to(board)


def paste_field(board: ImageFile, index: int, color: int, locked: bool) -> None:
    """Вставляет занятую клетку на доске."""
    # Просчитанные заранее координаты
    coordinates = FIELD_COORDINATES[index]
    rotate = get_rotate(index)

    # Вставляем изображение
    field_asset = Asset(
        f"cell{rotate}/cell_{color}{'l' if locked else ''}.png",
        coordinates[0],
        coordinates[1],
    )
    field_asset.paste_to(board)


# Главная функция
# ===============


def generate_board(game: MonoGame) -> BufferedInputFile:
    """Собирает изображение игрового поля для бота."""
    board = Image.open(ASSETS_PATH / "board.png")
    draw_layer = Image.new("RGBA", board.size)
    pointer_layer = Image.new("RGBA", board.size)

    # Кто сейчас ходит
    PLAYER_ASSET[game.current_player].paste_to(draw_layer)

    # Указатели игроков
    for i, player in enumerate(game.players):
        paste_player_pointer(pointer_layer, player.index, i)

    # TODO: Что там по занятым полям?

    # Сохраняем изображение
    composite = Image.alpha_composite(
        board, Image.alpha_composite(draw_layer, pointer_layer)
    )
    buffer = io.BytesIO()
    composite.save(buffer, format="PNG")
    return BufferedInputFile(buffer.getvalue(), f"board_{int(time())}.png")
