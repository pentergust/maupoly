"""Игровые ячейки поля."""

from enum import IntEnum

# TODO: Добавить статическую типизацию

# Вспомогательные классы для игры
# ===============================


class FieldType(IntEnum):
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
    def __init__(self, field_type: FieldType, name: str) -> None:
        self.type = field_type
        self.name = name

    def field_callback(self, game) -> None:
        raise NotImplementedError

    # Магические методы
    # =================

    def __call__(self, game) -> None:
        self.field_callback(game)


class BuyField(BaseField):
    def __init__(self, name: str, cost: int, reward: bool = False) -> None:
        super().__init__(field_type=FieldType.BUY, name=name)
        self.cost = cost
        self.reward = reward


class RentField(BaseField):
    def __init__(self, name: str, color: FieldColor) -> None:
        super().__init__(field_type=FieldType.RENT, name=name)
        self.color = color
        self.buy_cost = None
        self.level_cost = None
        self.deposit_cost = 0
        self.redemption_cost = 0

        self.is_deposit = False
        self.owner = None
        self.level = 0


class AirportField(BaseField):
    def __init__(self, name: str) -> None:
        super().__init__(field_type=FieldType.AIRPORT, name=name)


class CommunicateField(BaseField):
    def __init__(self, name: str) -> None:
        super().__init__(field_type=FieldType.AIRPORT, name=name)


class ChanceField(BaseField):
    def __init__(self) -> None:
        super().__init__(field_type=FieldType.AIRPORT, name="Шанс")


class PrizeField(BaseField):
    def __init__(self) -> None:
        super().__init__(
            field_type=FieldType.AIRPORT, name="Общественная казна"
        )


class TeleportField(BaseField):
    def __init__(self, name: str) -> None:
        super().__init__(field_type=FieldType.AIRPORT, name=name)


class PrisonField(BaseField):
    def __init__(self) -> None:
        super().__init__(field_type=FieldType.AIRPORT, name="Тюрьма")


class CasinoField(BaseField):
    def __init__(self) -> None:
        super().__init__(field_type=FieldType.CASINO, name="Казино")


# Игровые поля
# ============

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
    TeleportField("В тюрьму"),
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
