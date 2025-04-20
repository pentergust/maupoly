"""Игровые ячейки на игровой доске.

Вся доска поделена не ячейки, по которым перемещаются пользователи.
При попадании на ячейку, совершается некоторое действие.
"""

from enum import IntEnum
from typing import TYPE_CHECKING

from maupoly.enums import GameEvents, TurnState

if TYPE_CHECKING:
    from maupoly.game import MonoGame
    from maupoly.player import Player

# Вспомогательные классы для игры
# ===============================


_FIELD_TYPES = ("💸", "✨", "✈️", "📱", "❓", "💎", "🌀", "👮", "🎰")


class FieldType(IntEnum):
    """Типы ячеек.

    - Buy: Поле покупки/получения монет.
    - Rent: Можно купить, приносит доход с поля.
    - Airport: Подпит Rent, Приносит доход от количества купленных.
    - Communicate: Подтип Rent. Приносит доход от значения кубика.
    - Chance: Карточки шанса с некоторым действием.
    - Prize: Карточки общественной казны с некоторым действиями.
    - Teleport: Перемещают игрока на некоторое поле.
    - Prison: Поле тюрьмы.
    - Casino: Поле казино.
    """

    BUY = 0
    RENT = 1
    AIRPORT = 2
    COMMUNICATE = 3
    CHANCE = 4
    PRIZE = 5
    TELEPORT = 6
    PRISON = 7
    CASINO = 8

    @property
    def symbol(self) -> str:
        """Представление перечисления в виде смайлика."""
        return _FIELD_TYPES[self.value]


_FIELD_COLORS = ("🟤", "⚪", "🟣", "🟠", "🔴", "🟡", "🟢", "🔵")


class FieldColor(IntEnum):
    """Цвета для полей ренты."""

    BROWN = 0
    SKY = 1
    PURPLE = 2
    ORANGE = 3
    RED = 4
    YELLOW = 5
    GREEN = 5
    BLUE = 6

    @property
    def symbol(self) -> str:
        """Представление перечисления в виде смайлика."""
        return _FIELD_COLORS[self.value]


# Игровые поля
# ============


class BaseField:
    """Базовое игровое поле.

    Описывает общий функционал для всех дочерних полей.
    """

    def __init__(self, field_type: FieldType, name: str) -> None:
        self.type = field_type
        self.name = name

    def callback(self, game: "MonoGame", player: "Player") -> None:
        """Действие при попадании на поле игроком.

        Возможные варианты реализации:
        - Прибавление/убавление баланса пользователя.
        - Оплата ренты.
        - Покупка поля.
        - Выполнение карточек шанса или общественной казны.
        """
        raise NotImplementedError

    # Магические методы
    # =================

    def __call__(self, game: "MonoGame", player: "Player") -> None:
        """Более красивая запись использования поля.

        ```py
        start = BuyField("Старт", 1000, True)

        start.callback(game, player)

        # или
        start(game, player)
        ```
        """
        self.callback(game, player)


class BuyField(BaseField):
    """Поле покупки.

    Когда пользователь попадает на поле, он должен заплатить или
    наоборот получить монеты за какую-то услугу.

    Используется для полей:
    - Старт.
    - Подоходный налог.
    - Налог на роскошь.
    """

    def __init__(self, name: str, cost: int, is_reward: bool = False) -> None:
        super().__init__(field_type=FieldType.BUY, name=name)
        self.cost = cost
        self.is_reward = is_reward

    def callback(self, game: "MonoGame", player: "Player") -> None:
        """Оплата или получение монет."""
        if self.is_reward:
            player.give(self.cost)
        else:
            player.pay(self.cost)
        player.push_event(
            GameEvents.PLAYER_BUY, f"{self.cost} {self.is_reward}"
        )


class BaseRentField(BaseField):
    """Базовое поле, которое может купит игрок."""

    def __init__(
        self,
        name: str,
        buy_cost: int,
        base_rent: int,
        field_type: FieldType = FieldType.RENT,
    ) -> None:
        super().__init__(field_type=field_type, name=name)
        self.buy_cost = buy_cost
        self.owner: Player | None = None
        self.base_rent = base_rent

        # Залог поля
        self.deposit_cost = buy_cost // 2
        self.redemption_cost = self.deposit_cost
        self.is_deposit = False

    def count_rent(self) -> int:
        """Считает сколько нужно заплатить игроку ренты."""
        return self.base_rent if not self.is_deposit else 0

    def buy(self, player: "Player") -> None:
        """Покупает поле."""
        player.pay(self.buy_cost)
        self.owner = player

    def deposit(self, player: "Player") -> None:
        """Закладывает поле."""
        player.give(self.deposit_cost)
        self.is_deposit = True

    def redemption(self, player: "Player") -> None:
        """Выкупает заложенное поле."""
        player.pay(self.redemption_cost)
        self.is_deposit = False

    def pay_rent(self, player: "Player") -> None:
        """Платит ренту владельцу поля."""
        if self.owner is None:
            raise ValueError("Field has not owner")

        rent = self.count_rent()
        player.pay(rent)
        self.owner.give(rent)

    def callback(self, game: "MonoGame", player: "Player") -> None:
        """Покупка поля или оплата ренты."""
        if self.owner is None:
            game.set_state(TurnState.BYU)
        else:
            self.pay_rent(player)


class RentField(BaseRentField):
    """Поле ренты.

    Сначала пользователь покупает это поле.
    Если он отказывается от покупки, оно попадает на аукцион.
    Когда другой игрок попадает на это поле, он платит владельцу ренту.
    При покупке всех полей одного цвета, можно начать строить
    недвижимость.
    """

    def __init__(
        self,
        name: str,
        color: FieldColor,
        buy_cost: int,
        base_rent: int,
        level_cost: int,
    ) -> None:
        super().__init__(
            name=name,
            buy_cost=buy_cost,
            base_rent=base_rent,
            field_type=FieldType.RENT,
        )

        # Основная характеристика
        self.color = color
        self.level = 0
        self.level_cost = level_cost


class AirportField(BaseRentField):
    """Самолёты.

    Похоже на обычные поля ренты.
    Рента на полез зависит от количество полей, которые есть у владельца.
    Не имеет цвета и возможности строительства.
    """

    def __init__(self, name: str, buy_cost: int, base_rent: int) -> None:
        super().__init__(
            name=name,
            buy_cost=buy_cost,
            base_rent=base_rent,
            field_type=FieldType.AIRPORT,
        )


class CommunicateField(BaseRentField):
    """Коммуникация.

    Похоже на обычные поля ренты.
    Рента на полез зависит от значения кубика игрока, что попал на поле.
    Также стоимость ренты зависит от количество ячеек у владельца.
    Не имеет цвета и возможности строительства.
    """

    def __init__(self, name: str, buy_cost: int, base_rent: int) -> None:
        super().__init__(
            name=name,
            buy_cost=buy_cost,
            base_rent=base_rent,
            field_type=FieldType.AIRPORT,
        )


class ChanceField(BaseField):
    """Поле шанса.

    При попадании на это поле совершается некоторое случайное действие.
    К примеру перемещение по полю, получения монет и прочее.
    """

    def __init__(self) -> None:
        super().__init__(field_type=FieldType.CHANCE, name="Шанс")

    def callback(self, game: "MonoGame", player: "Player") -> None:
        """Случайное действие карточки шанс."""
        game.player.push_event(GameEvents.PLAYER_CHANCE, "No implemented")


class PrizeField(BaseField):
    """Поле общественной казны.

    При попадании на это поле совершается некоторое случайное действие.
    К примеру перемещение по полю, получения монет и прочее.
    """

    def __init__(self) -> None:
        super().__init__(field_type=FieldType.PRIZE, name="Общественная казна")

    def callback(self, game: "MonoGame", player: "Player") -> None:
        """Случайное действие карточки шанс."""
        game.player.push_event(GameEvents.PLAYER_CHANCE, "No implemented")


class TeleportField(BaseField):
    """Поле телепорта.

    Перемещает пользователя на указанное поле.
    """

    def __init__(self, name: str, to_field: int) -> None:
        super().__init__(field_type=FieldType.TELEPORT, name=name)
        self.to_field = to_field

    def callback(self, game: "MonoGame", player: "Player") -> None:
        """Случайное действие карточки общественная казна."""
        game.player.move_to(self.to_field)


class PrisonField(BaseField):
    """Поле тюрьмы.

    Если пользователь проходит мимо, с ним ничего не будет.
    Если пользователь попал в тюрьму, то он может либо попытаться
    выкинуть дубль, либо заплатить за выход из тюрьмы.
    """

    def __init__(self) -> None:
        super().__init__(field_type=FieldType.PRISON, name="Тюрьма")

    def callback(self, game: "MonoGame", player: "Player") -> None:
        """игрок попал в тюрьму."""
        game.player.push_event(GameEvents.PLAYER_PRISON)


class CasinoField(BaseField):
    """Поле казино.

    Участник может либо отказаться, либо сделать свою ставку.
    Если сделать ставку, то можно либо выиграть. либо проиграть.
    """

    def __init__(self) -> None:
        super().__init__(field_type=FieldType.CASINO, name="Казино")

    def callback(self, game: "MonoGame", player: "Player") -> None:
        """игрока попал на поле казино."""
        game.player.push_event(GameEvents.PLAYER_CASINO)


# Игровые поля
# ============

# TODO: Может мы лучше это в класс какой затолкаем?
CLASSIC_BOARD = [
    BuyField("Старт", 1000, True),
    RentField(
        "Санкт-Петербург",
        FieldColor.BROWN,
        buy_cost=200,
        base_rent=60,
        level_cost=100,
    ),
    PrizeField(),
    RentField(
        "Красноярск",
        FieldColor.BROWN,
        buy_cost=200,
        base_rent=60,
        level_cost=100,
    ),
    BuyField("Подоходный налог", 2000),
    AirportField(
        "Шереметьево",
        buy_cost=200,
        base_rent=60,
    ),
    RentField(
        "Самара",
        FieldColor.SKY,
        buy_cost=200,
        base_rent=60,
        level_cost=100,
    ),
    ChanceField(),
    RentField(
        "Чебоксары",
        FieldColor.SKY,
        buy_cost=200,
        base_rent=60,
        level_cost=100,
    ),
    RentField(
        "Пенза",
        FieldColor.SKY,
        buy_cost=200,
        base_rent=60,
        level_cost=100,
    ),
    PrisonField(),
    RentField(
        "Челябинск",
        FieldColor.PURPLE,
        buy_cost=200,
        base_rent=60,
        level_cost=100,
    ),
    CommunicateField(
        "Мобильная связь",
        buy_cost=200,
        base_rent=60,
    ),
    RentField(
        "Барнаул",
        FieldColor.PURPLE,
        buy_cost=200,
        base_rent=60,
        level_cost=100,
    ),
    RentField(
        "Псков",
        FieldColor.PURPLE,
        buy_cost=200,
        base_rent=60,
        level_cost=100,
    ),
    AirportField(
        "Толмачёво",
        buy_cost=200,
        base_rent=60,
    ),
    RentField(
        "Батайск",
        FieldColor.ORANGE,
        buy_cost=200,
        base_rent=60,
        level_cost=100,
    ),
    PrizeField(),
    RentField(
        "Воронеж",
        FieldColor.ORANGE,
        buy_cost=200,
        base_rent=60,
        level_cost=100,
    ),
    RentField(
        "Сыктывкар",
        FieldColor.ORANGE,
        buy_cost=200,
        base_rent=60,
        level_cost=100,
    ),
    CasinoField(),
    RentField(
        "Ростов-на-Дону",
        FieldColor.RED,
        buy_cost=200,
        base_rent=60,
        level_cost=100,
    ),
    ChanceField(),
    RentField(
        "Рязань",
        FieldColor.RED,
        buy_cost=200,
        base_rent=60,
        level_cost=100,
    ),
    RentField(
        "Москва",
        FieldColor.RED,
        buy_cost=200,
        base_rent=60,
        level_cost=100,
    ),
    AirportField(
        "Пулково",
        buy_cost=200,
        base_rent=60,
    ),
    RentField(
        "Архангельск",
        FieldColor.YELLOW,
        buy_cost=200,
        base_rent=60,
        level_cost=100,
    ),
    RentField(
        "Обнинск",
        FieldColor.YELLOW,
        buy_cost=200,
        base_rent=60,
        level_cost=100,
    ),
    CommunicateField(
        "Интернет",
        buy_cost=200,
        base_rent=60,
    ),
    RentField(
        "Новосибирск",
        FieldColor.YELLOW,
        buy_cost=200,
        base_rent=60,
        level_cost=100,
    ),
    TeleportField("В тюрьму", to_field=10),
    RentField(
        "Северодвинск",
        FieldColor.GREEN,
        buy_cost=200,
        base_rent=60,
        level_cost=100,
    ),
    RentField(
        "Курган",
        FieldColor.GREEN,
        buy_cost=200,
        base_rent=60,
        level_cost=100,
    ),
    PrizeField(),
    RentField(
        "Сургут",
        FieldColor.GREEN,
        buy_cost=200,
        base_rent=60,
        level_cost=100,
    ),
    AirportField(
        "Кольцово",
        buy_cost=200,
        base_rent=60,
    ),
    ChanceField(),
    RentField(
        "Пермь",
        FieldColor.BLUE,
        buy_cost=200,
        base_rent=60,
        level_cost=100,
    ),
    BuyField("Налог на роскошь", 1000),
    RentField(
        "Екатеринбург",
        FieldColor.BLUE,
        buy_cost=200,
        base_rent=60,
        level_cost=100,
    ),
]
