from typing import Self


# TODO: Написать класс пользователя
class Player:
    def __init__(self, game, user):
        self.game = game
        self.user = user
        self.balance = 15000
        self.index = 0
        self.prison: bool = False


    # Магические методы
    # =================

    def __repr__(self):
        """Представление игрока при отладке."""
        return repr(self.user)

    def __str__(self):
        """Представление игрока в строковом виде."""
        return str(self.user)

    def __eq__(self, other_player: Self) -> bool:
        """Сравнивает двух игроков по UID пользователя."""
        return self.user.id == other_player.user.id

    def __ne__(self, other_player: Self) -> bool:
        """Проверяет что игроки не совпадают."""
        return self.user.id != other_player.user.id
