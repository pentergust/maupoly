"""Обработчик игровых событий."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from loguru import logger

from maupoly.enums import GameEvents

if TYPE_CHECKING:
    from maupoly.game import MonoGame
    from maupoly.player import Player

# Вспомогательные классы
# ======================


@dataclass(slots=True, frozen=True)
class Event:
    """Игровое событие."""

    room_id: int
    player: "Player"
    event_type: GameEvents
    data: str
    game: "MonoGame"


# Абстрактные классы
# ==================


class BaseEventHandler(ABC):
    """Базовый обработчик событий.

    Пришёл на смену устаревшему журналу событий.
    Наследники реализуют способ обработки игровых событий по своему
    усмотрению.
    """

    @abstractmethod
    def push(self, event: Event) -> None:
        """Отравляет событие в обработчик."""
        pass


class DebugEventHandler(BaseEventHandler):
    """Пример обработчика событий, отправляет изменения в консоль."""

    def push(self, event: Event) -> None:
        """Отравляет событие в консоль."""
        logger.info(event)
