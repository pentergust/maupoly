"""Игровые ячейки на игровой доске.

Вся доска поделена не ячейки, по которым перемещаются пользователи.
При попадании на ячейку, совершается некоторое действие.
"""

from enum import IntEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from maupoly.game import MonoGame
    from maupoly.player import Player

# Вспомогательные классы для игры
# ===============================


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


class RentField(BaseField):
    """Поле ренты.

    Сначала пользователь покупает это поле.
    Если он отказывается от покупки, оно попадает на аукцион.
    Когда другой игрок попадает на это поле, он платит владельцу ренту.
    При покупке всех полей одного цвета, можно начать строить
    недвижимость.
    """

    def __init__(self, name: str, color: FieldColor) -> None:
        super().__init__(field_type=FieldType.RENT, name=name)

        # Основная характеристика
        self.color = color
        self.buy_cost = None
        self.owner = None

        # Уровень поля
        self.level = 0
        self.level_cost = None

        # Залог поля
        self.deposit_cost = None
        self.redemption_cost = None
        self.is_deposit = False


class AirportField(BaseField):
    """Самолёты.

    Похоже на обычные поля ренты.
    Рента на полез зависит от количество полей, которые есть у владельца.
    Не имеет цвета и возможности строительства.
    """

    def __init__(self, name: str) -> None:
        super().__init__(field_type=FieldType.AIRPORT, name=name)
        self.buy_cost = None
        self.owner = None

        # Залог поля
        self.deposit_cost = None
        self.redemption_cost = None
        self.is_deposit = False


class CommunicateField(BaseField):
    """Коммуникация.

    Похоже на обычные поля ренты.
    Рента на полез зависит от значения кубика игрока, что попал на поле.
    Также стоимость ренты зависит от количество ячеек у владельца.
    Не имеет цвета и возможности строительства.
    """

    def __init__(self, name: str) -> None:
        super().__init__(field_type=FieldType.COMMUNICATE, name=name)
        self.buy_cost = None
        self.owner = None

        # Залог поля
        self.deposit_cost = None
        self.redemption_cost = None
        self.is_deposit = False


class ChanceField(BaseField):
    """Поле шанса.

    При попадании на это поле совершается некоторое случайное действие.
    К примеру перемещение по полю, получения монет и прочее.
    """

    def __init__(self) -> None:
        super().__init__(field_type=FieldType.CHANCE, name="Шанс")


class PrizeField(BaseField):
    """Поле общественной казны.

    При попадании на это поле совершается некоторое случайное действие.
    К примеру перемещение по полю, получения монет и прочее.
    """

    def __init__(self) -> None:
        super().__init__(field_type=FieldType.PRIZE, name="Общественная казна")


class TeleportField(BaseField):
    """Поле телепорта.

    Перемещает пользователя на указанное поле.
    """

    def __init__(self, name: str, to_field: int) -> None:
        super().__init__(field_type=FieldType.TELEPORT, name=name)
        self.to_field = to_field


class PrisonField(BaseField):
    """Поле тюрьмы.

    Если пользователь проходит мимо, с ним ничего не будет.
    Если пользователь попал в тюрьму, то он может либо попытаться
    выкинуть дубль, либо заплатить за выход из тюрьмы.
    """

    def __init__(self) -> None:
        super().__init__(field_type=FieldType.PRISON, name="Тюрьма")


class CasinoField(BaseField):
    """Поле казино.

    Участник может либо отказаться, либо сделать свою ставку.
    Если сделать ставку, то можно либо выиграть. либо проиграть.
    """

    def __init__(self) -> None:
        super().__init__(field_type=FieldType.CASINO, name="Казино")


# Игровые поля
# ============

# TODO: Может мы лучше это в класс какой затолкаем?
CLASSIC_BOARD = [
    BuyField("Старт", 1000, True),
    RentField("Санкт-Петербург", FieldColor.BROWN),
    PrizeField(),
    RentField("Красноярск", FieldColor.BROWN),
    BuyField("Подоходный налог", 2000),
    AirportField("Шереметьево"),
    BuyField("Самара", FieldColor.SKY),
    ChanceField(),
    BuyField("Чебоксары", FieldColor.SKY),
    BuyField("Пенза", FieldColor.SKY),
    PrisonField(),
    BuyField("Челябинск", FieldColor.PURPLE),
    CommunicateField("Мобильная связь"),
    BuyField("Барнаул", FieldColor.PURPLE),
    BuyField("Псков", FieldColor.PURPLE),
    AirportField("Толмачёво"),
    BuyField("Батайск", FieldColor.ORANGE),
    PrizeField(),
    BuyField("Воронеж", FieldColor.ORANGE),
    BuyField("Сыктывкар", FieldColor.ORANGE),
    CasinoField(),
    BuyField("Ростов-на-Дону", FieldColor.RED),
    ChanceField(),
    BuyField("Рязань", FieldColor.RED),
    BuyField("Москва", FieldColor.RED),
    AirportField("Пулково"),
    BuyField("Архангельск", FieldColor.YELLOW),
    BuyField("Обнинск", FieldColor.YELLOW),
    CommunicateField("Интернет"),
    BuyField("Новосибирск", FieldColor.YELLOW),
    TeleportField("В тюрьму", to_field=10),
    BuyField("Северодвинск", FieldColor.GREEN),
    BuyField("Курган", FieldColor.GREEN),
    PrizeField(),
    BuyField("Сургут", FieldColor.GREEN),
    AirportField("Кольцово"),
    ChanceField(),
    BuyField("Пермь", FieldColor.BLUE),
    BuyField("Налог на роскошь", 1000),
    BuyField("Екатеринбург", FieldColor.BLUE),
]
