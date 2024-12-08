"""Хранилище игровых сессий."""

from aiogram import Bot
from loguru import logger

from milipoly.milipoly.exceptions import (
    LobbyClosedError,
    NoGameInChatError,
)
from milipoly.milipoly.game import MonoGame
from milipoly.milipoly.player import Player


class SessionManager:
    """Управляет всеми играми Uno.

    Каждая игра (сессия) привязывается к конкретному чату.
    Предоставляет методы для создания и завершения сессий.
    """

    def __init__(self, bot: Bot):
        self.games: dict[str, MonoGame] = {}
        self.user_to_chat: dict[int, int] = {}
        self.bot: Bot = bot


    # Управление игроками в сессии
    # ============================

    def join(self, chat_id: int, user) -> None:
        """Добавляет нового игрока в игру.

        Более высокоуровневая функция, совершает больше проверок.
        """
        game = self.games.get(chat_id)
        if game is None:
            raise NoGameInChatError()
        if not game.open:
            raise  LobbyClosedError()

        game.add_player(user)
        self.user_to_chat[user.id] = chat_id
        logger.debug(self.user_to_chat)

    def leave(self, player: Player) -> None:
        """Убирает игрока из игры."""
        chat_id = self.user_to_chat.get(player.user.id)
        if chat_id is None:
            raise NoGameInChatError()

        game = self.games[chat_id]

        if player is game.player:
            game.next_turn()

        player.on_leave()
        game.players.remove(player)
        self.user_to_chat.pop(player.user.id)

        if len(game.players) <= 1:
            game.end()

    def get_player(self, user_id: int) -> Player | None:
        """Получает игрока по его id."""
        chat_id = self.user_to_chat.get(user_id)
        if chat_id is None:
            return None
        return self.games[chat_id].get_player(user_id)


    # Управление сессиями
    # ===================

    def create(self, chat_id: int) -> MonoGame:
        """Создает новую игру в чате."""
        logger.info("Create new session in chat {}", chat_id)
        game = MonoGame(chat_id, self.bot)
        self.games[chat_id] = game
        return game

    def remove(self, chat_id: int):
        """Полностью завершает игру в конкретном чате.

        Если вы хотите завершить текущий раунд - воспользуйтесь методов
        `MonoGame.end()`.
        """
        try:
            game = self.games.pop(chat_id)
            for player in game.players:
                self.user_to_chat.pop(player.user.id)
        except KeyError as e:
            logger.warning(e)
            raise NoGameInChatError()
