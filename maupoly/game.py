from datetime import datetime
from random import shuffle

from aiogram import Bot
from loguru import logger

from maupoly.enums import GameState
from maupoly.exceptions import AlreadyJoinedError, LobbyClosedError, NoGameInChatError
from maupoly.field import CLASSIC_BOARD
from maupoly.journal import Journal
from maupoly.player import Player


# TODO: Написать класс игры
class MonoGame:
    def __init__(self, chat_id: int, bot: Bot):
        self.chat_id = chat_id
        self.bot: Bot = bot
        self.lobby_message = None
        self.journal = Journal(self, self.bot)

        # Игроки
        self.current_player: int = 0
        self.start_player = None
        self.players = []
        self.bankrupts = []
        self.winner = None

        # Состояние игры
        self.started: bool = False
        self.open: bool = True
        self.dice = 0
        self.fields = []
        self.round_counter = 0

        # Таймеры
        self.game_start = datetime.now()
        self.turn_start = datetime.now()

    @property
    def player(self) -> Player:
        """Возвращает текущего игрока."""
        return self.players[self.current_player % len(self.players)]

    def get_player(self, user_id: int) -> Player | None:
        """Получает игрока среди списка игроков по его ID."""
        for player in self.players:
            if player.user.id == user_id:
                return player
        return None

    def new_game(self):
        logger.info("Start new game in chat {}", self.chat_id)
        self.winner = None
        self.bankrupts.clear()
        shuffle(self.players)

        self.started = True
        self.open = False
        self.fields.clear()
        self.fields = CLASSIC_BOARD.copy()
        self.round_counter = 0
        self.game_start = datetime.now()
        self.turn_start = datetime.now()

    def end(self) -> None:
        """Завершает текущую игру."""
        self.players.clear()
        self.started = False

    def process_turn(self, dice: int) -> None:
        cur_player = self.player
        cur_player.index = (cur_player.index + dice) % len(self.fields)

    def next_turn(self) -> None:
        logger.info("Next Player")
        self.state = GameState.PREDICE
        self.turn_start = datetime.now()
        self.journal.clear()
        self.skip_players()

    def add_player(self, user) -> None:
        """Добавляет игрока в игру."""
        logger.info("Joining {} in game with id {}", user, self.chat_id)
        if not self.open:
            raise LobbyClosedError()

        player = self.get_player(user.id)
        if player is not None:
            raise AlreadyJoinedError()

        player = Player(self, user)
        self.players.append(player)

    def remove_player(self, user_id: int) -> None:
        """Удаляет пользователя из игры."""
        logger.info("Leaving {} game with id {}", user_id, self.chat_id)

        player = self.get_player(user_id)
        if player is None:
            raise NoGameInChatError()

        if player == self.player:
            self.next_turn()

        if len(player.balance) == 0:
            self.bankrupts.append(player)
        else:
            self.winner = player

        player.on_leave()
        self.players.remove(player)

        if len(self.players) <= 1:
            self.end()

    def skip_players(self, n: int = 1) -> None:
        """Пропустить ход для следующих игроков.

        В зависимости от направления игры пропускает несколько игроков.

        Args:
            n (int): Сколько игроков пропустить (1).

        """
        self.current_player = (self.current_player + n) % len(self.players)
