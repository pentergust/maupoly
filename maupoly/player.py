from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from maupoly.events import Event, GameEvents
from maupoly.field import BaseField

if TYPE_CHECKING:
    from maupoly.game import MonoGame


@dataclass(frozen=True, slots=True)
class BaseUser:
    """Абстрактное представление пользователя.

    Представляет собой хранимую о пользователе информацию.
    Чтобы отвязать пользователя от конкретной реализации.
    """

    id: int
    name: str


# TODO: Написать класс пользователя
class Player:
    def __init__(self, game: "MonoGame", user_id: int, user_name: str) -> None:
        self.game = game
        self.user_id = user_id
        self._user_name = user_name
        self.balance = 15000
        self.index = 0

    @property
    def name(self) -> str:
        """Возвращает имя игрока с упоминанием пользователя ядл бота."""
        return self._user_name

    @property
    def is_current(self) -> bool:
        """Имеет ли право хода текущий игрок."""
        return self == self.game.player

    def push_event(self, event_type: GameEvents, data: str = "") -> None:
        """Отправляет событие в журнал.

        Автоматически подставляет игрока и игру.
        """
        self.game.event_handler.push(
            Event(self.game.room_id, self, event_type, data, self.game)
        )

    @property
    def field(self) -> BaseField:
        """Сокращение для получения поля, на котором стоит игрок."""
        return self.game.fields[self.index]

    # Магические методы
    # =================

    def __repr__(self) -> str:
        """Представление игрока при отладке."""
        return repr(self.user_id)

    def __str__(self) -> str:
        """Представление игрока в строковом виде."""
        return str(self._user_name)

    def __eq__(self, other_player: Self) -> bool:
        """Сравнивает двух игроков по UID пользователя."""
        return self.user_id == other_player.user_id

    def __ne__(self, other_player: Self) -> bool:
        """Проверяет что игроки не совпадают."""
        return self.user_id != other_player.user_id

    def move(self, steps: int) -> None:
        """Перемещает игрока на N клеток по полю."""
        self.push_event(GameEvents.GAME_MOVE, str(steps))
        self.index = (self.index + steps) % len(self.game.fields)
