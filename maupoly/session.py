"""Хранилище игровых сессий.

Занимается общей обработкой всех существующих сессий.
Отвечает за создание новых игр и привязыванию их к чату.
"""

from typing import Generic, TypeVar, cast

from loguru import logger

from maupoly.events import (
    BaseEventHandler,
    DebugEventHandler,
    Event,
    GameEvents,
)
from maupoly.exceptions import LobbyClosedError, NoGameInChatError
from maupoly.game import MonoGame
from maupoly.player import BaseUser, Player
from maupoly.session_storage import BaseStorage, MemoryStorage

_H = TypeVar("_H", bound=BaseEventHandler)


class SessionManager(Generic[_H]):
    """Управляет всеми играми Uno.

    Каждая игра (сессия) привязывается к конкретному чату.
    Предоставляет методы для создания и завершения сессий.
    """

    def __init__(
        self,
        storage: BaseStorage | None = None,
        event_handler: _H | None = None,
    ) -> None:
        self.storage: BaseStorage = storage or MemoryStorage()
        self.event_handler = event_handler or cast(_H, DebugEventHandler())

    def set_handler(self, handler: _H) -> None:
        """Устанавливает обработчик событий."""
        self.event_handler = handler

    # Управление игроками в сессии
    # ================W============

    def join(self, room_id: int, user: BaseUser) -> None:
        """Добавляет нового игрока в игру.

        Более высокоуровневая функция, совершает больше проверок.
        """
        game = self.storage.get_game(room_id)
        if not game.open:
            raise LobbyClosedError

        player = game.add_player(user)
        self.storage.add_player(room_id, player.user_id)
        self.event_handler.push(
            Event(room_id, player, GameEvents.SESSION_JOIN, "", game)
        )

    def leave(self, player: Player) -> None:
        """Убирает игрока из игры."""
        game = self.storage.get_player_game(player.user_id)
        game.remove_player(player)
        self.storage.remove_player(player.user_id)
        self.event_handler.push(
            Event(game.room_id, player, GameEvents.SESSION_LEAVE, "", game)
        )

    def get_player(self, user_id: int) -> Player | None:
        """Получает игрока комнаты по его user id."""
        try:
            return self.storage.get_player_game(user_id).get_player(user_id)
        except NoGameInChatError:
            logger.warning("No game found for user {}", user_id)
            return None

    # Управление сессиями
    # ===================

    def create(self, room_id: int, user: BaseUser) -> MonoGame:
        """Создает новую игру в чате."""
        logger.info("User {} Create new game session in {}", user, room_id)
        game = MonoGame(self.event_handler, room_id, user)
        self.storage.add_game(room_id, game)
        self.storage.add_player(room_id, user.id)
        self.event_handler.push(
            Event(room_id, game.owner, GameEvents.SESSION_START, "", game)
        )
        return game

    def remove(self, room_id: int) -> None:
        """Полностью завершает игру в конкретном чате.

        Если вы хотите завершить текущий кон - воспользуйтесь методов
        `MonoGame.end()`.
        """
        try:
            game: MonoGame = self.storage.remove_game(room_id)
            for player in game.players:
                self.storage.remove_player(player.user_id)
            self.event_handler.push(
                Event(room_id, game.owner, GameEvents.SESSION_END, "", game)
            )
        except KeyError as e:
            logger.warning(e)
            raise NoGameInChatError() from e
