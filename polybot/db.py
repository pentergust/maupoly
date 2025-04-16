"""Работа с базой данных.

База данных используется для сохранения статистический ифнормации
об игроке.
"""

from tortoise import Model, fields


class User(Model):
    """База данных игрока.

    Используется при сборе статистической информации об играх.

    - id: Telegram User ID
    - first_places: Количество первых мест в играх.
    - game_played: Сколько всего партий сыграно.
    """

    id = fields.BigIntField(primary_key=True)
    first_places = fields.IntField(default=0)
    total_games = fields.IntField(default=0)
