from dataclasses import dataclass
from typing import TYPE_CHECKING

from maupoly.enums import GameEvents
from maupoly.events import Event
from maupoly.field import BaseField, BaseRentField

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
        self.own_fields: list[BaseRentField] = []

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
    def field(self) -> BaseField | BaseRentField:
        """Сокращение для получения поля, на котором стоит игрок."""
        return self.game.fields[self.index]

    def on_leave(self) -> None:
        """Действия игрока при выходе из игры."""
        pass

    # Магические методы
    # =================

    def __repr__(self) -> str:
        """Представление игрока при отладке."""
        return repr(self.user_id)

    def __str__(self) -> str:
        """Представление игрока в строковом виде."""
        return str(self._user_name)

    def __eq__(self, other_player: object) -> bool:
        """Сравнивает двух игроков по UID пользователя."""
        if not isinstance(other_player, Player):
            raise ValueError("Other player muse be Player instance")
        return self.user_id == other_player.user_id

    def __ne__(self, other_player: object) -> bool:
        """Проверяет что игроки не совпадают."""
        if not isinstance(other_player, Player):
            raise ValueError("Other player muse be Player instance")
        return self.user_id != other_player.user_id

    # Перемещение игрока
    # ==================

    def move(self, steps: int) -> None:
        """Перемещает игрока на N клеток по полю."""
        self.push_event(GameEvents.PLAYER_MOVE, str(steps))
        self.index = (self.index + steps) % len(self.game.fields)

    def move_to(self, index: int) -> None:
        """Перемещает игрока на конкретное поле."""
        self.push_event(GameEvents.PLAYER_MOVE, str(index))
        self.index = index % len(self.game.fields)

    # Оплата услуг
    # ============

    def pay(self, amount: int) -> None:
        """Оплачивает услуги за монеты."""
        if amount > self.balance:
            self.balance = 0
            self.game.remove_player(self)
            return

        self.balance -= amount

    def give(self, amount: int) -> None:
        """Выплачивает монеты пользователю."""
        self.balance += amount

    # Управление полями
    # =================

    def buy_field(self) -> None:
        """Покупает активное поле."""
        if not isinstance(self.field, BaseRentField):
            raise ValueError(f"Can`t buy {type(self.field)} field")
        self.field.buy(self)
        self.own_fields.append(self.field)
        self.push_event(GameEvents.PLAYER_BUY_FIELD, str(self.field.buy_cost))
        self.game.next_turn()
