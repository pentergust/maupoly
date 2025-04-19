"""Обработчик игровых событий."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from maupoly.game import MonoGame
    from maupoly.player import Player

# Вспомогательные классы
# ======================


class GameEvents(StrEnum):
    """Все варианты игровых событий.

    Типы событий могут сопровождаться уточняющими данными.

    Игровая сессия:
    - session_start: Началась новая сессия.
    - session_end: Закончилась сессия.
    - session_join: Игрок присоединился к сессии.
    - session_leave: Игрок покинул сессию.
    - session_update: Данные комнаты обновлены. Правила, информация, владелец.

    Игра:
    - game_start: Началась новая игра.
    - game_end: Игра завершилась.
    - game_join: Игрой зашёл в игру.
    - game_leave: Игрок вышел, проиграл, выиграл, был исключён, застрелился.
    - game_next: Переход к следующему игроку.
    - game_turn: Переход к следующему ходу.
    - game_state: Изменение состояния игры.

    Игрок:
    - player_dice: Был выброшен кубик с некоторым числом.
    - player_move: Перемещение игрока по полю.
    - player_buy: Игрок оплатил налог или получил возмещение.
    - player_chance: Игрок попал на поле шанс.
    - player_prison: Игрок попал в тюрьму.
    - player_casino: Игрок попал на поле казино.
    """

    # Игровые сессии
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    SESSION_JOIN = "session_join"
    SESSION_LEAVE = "session_leave"
    SESSION_UPDATE = "session_update"

    # Игровые события
    GAME_START = "game_start"
    GAME_END = "game_end"
    GAME_JOIN = "game_join"
    GAME_LEAVE = "game_leave"
    GAME_NEXT = "game_next"
    GAME_TURN = "game_turn"
    GAME_STATE = "game_state"

    # События игрока
    PLAYER_DICE = "player_dice"
    PLAYER_MOVE = "player_move"
    PLAYER_BUY = "player_buy"
    PLAYER_CHANCE = "player_chance"
    PLAYER_PRISON = "player_prison"
    PLAYER_CASINO = "player_casino"


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
