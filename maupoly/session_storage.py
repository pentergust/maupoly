"""Хранилище игровых сессий."""

from abc import ABC, abstractmethod

from maupoly import exceptions
from maupoly.events import BaseEventHandler
from maupoly.game import MonoGame


class BaseStorage(ABC):
    """Базовое хранилище сессий.

    Описывает как должно работать хранилище сессий.
    Оно позволяет сохранять состояние игр в памяти.
    """

    # Игроки
    # ======

    @abstractmethod
    def add_player(self, room_id: str, user_id: str) -> None:
        """Добавляет игрока в хранилище."""
        pass

    @abstractmethod
    def remove_player(self, user_id: str) -> None:
        """Удаляет пользователя из хранилища."""
        pass

    @abstractmethod
    def get_room(self, user_id: str) -> str:
        """Получает room_id для указанного игрока."""
        pass

    @abstractmethod
    def get_player_game(self, user_id: str) -> MonoGame:
        """Получает игру, в которой находится игрок."""
        pass

    # Игры
    # ====

    @abstractmethod
    def add_game(self, room_id: str, game: MonoGame) -> None:
        """Добавляет новую игру в хранилище."""
        pass

    @abstractmethod
    def get_game(self, room_id: str) -> MonoGame:
        """Получает игру по room_id."""
        pass

    @abstractmethod
    def remove_game(self, room_id: str) -> MonoGame:
        """Удаляет комнату из хранилища."""
        pass


class MemoryStorage(BaseStorage):
    """Хранилище сессий в памяти.

    Самые простой вид хранилища.
    Просто сохраняет данные в оперативной памяти.
    Сессии будут очищены после перезапуска движка.

    У каждого игрока может быть только одна активная игра.
    """

    def __init__(self) -> None:
        self.games: dict[str, MonoGame] = {}
        self.user_to_room: dict[str, str] = {}
        self.game_journal: dict[str, BaseEventHandler]

    def add_player(self, room_id: str, user_id: str) -> None:
        """Добавляет игрока в хранилище."""
        self.user_to_room[user_id] = room_id

    def remove_player(self, user_id: str) -> None:
        """Удаляет пользователя из хранилища."""
        self.user_to_room.pop(user_id)

    def get_room(self, user_id: str) -> str:
        """Получает room_id для указанного игрока."""
        try:
            return self.user_to_room[user_id]
        except KeyError:
            raise exceptions.NoGameInChatError from KeyError

    def get_player_game(self, user_id: str) -> MonoGame:
        """Получает игру, в которой находится игрок."""
        try:
            room_id = self.user_to_room[user_id]
            return self.games[room_id]
        except KeyError:
            raise exceptions.NoGameInChatError from KeyError

    def get_game(self, room_id: str) -> MonoGame:
        """Получает игру по room_id."""
        try:
            return self.games[room_id]
        except KeyError:
            raise exceptions.NoGameInChatError from KeyError

    def add_game(self, room_id: str, game: MonoGame) -> None:
        """Добавляет новую игру в хранилище."""
        self.games[room_id] = game

    def remove_game(self, room_id: str) -> MonoGame:
        """Удаляет комнату из хранилища."""
        try:
            return self.games.pop(room_id)
        except KeyError:
            raise exceptions.NoGameInChatError from KeyError
