from datetime import datetime
from random import shuffle

from loguru import logger

from maupoly.enums import TurnState
from maupoly.events import BaseEventHandler, Event, GameEvents
from maupoly.exceptions import (
    AlreadyJoinedError,
    LobbyClosedError,
    NoGameInChatError,
)
from maupoly.field import CLASSIC_BOARD, BaseField
from maupoly.player import BaseUser, Player


# TODO: Написать класс игры
class MonoGame:
    def __init__(
        self, journal: BaseEventHandler, room_id: int, owner: BaseUser
    ) -> None:
        self.room_id = room_id
        self.event_handler: BaseEventHandler = journal

        # Игроки
        self.current_player: int = 0
        self.owner = Player(self, owner.id, owner.name)
        self.players: list[Player] = [self.owner]
        self.bankrupts: list[Player] = []
        self.winner: Player | None = None

        # Состояние игры
        self.started: bool = False
        self.open: bool = True
        self.dice = 0
        self.state: TurnState = TurnState.NEXT
        self.fields: list[BaseField] = []
        self.round_counter = 0

        # Таймеры
        self.game_start = datetime.now()
        self.turn_start = datetime.now()

    @property
    def player(self) -> Player:
        """Возвращает текущего игрока."""
        if len(self.players) == 0:
            raise ValueError("Game not started to get players")
        return self.players[self.current_player % len(self.players)]

    def get_player(self, user_id: int) -> Player | None:
        """Получает игрока среди списка игроков по его ID."""
        for player in self.players:
            if player.user_id == user_id:
                return player

        return None

    def push_event(
        self, from_player: Player, event_type: GameEvents, data: str = ""
    ) -> None:
        """Обёртка над методом journal.push.

        Автоматически подставляет текущую игру.
        """
        self.event_handler.push(
            Event(self.room_id, from_player, event_type, data, self)
        )

    def start(self) -> None:
        """Начинает новую игру."""
        logger.info("Start new game in chat {}", self.room_id)
        self.winner = None
        self.bankrupts.clear()
        shuffle(self.players)

        self.started = True
        self.open = False
        self.fields.clear()
        self.fields = CLASSIC_BOARD.copy()
        self.round_counter = 0
        self.state = TurnState.NEXT
        self.game_start = datetime.now()
        self.turn_start = datetime.now()
        self.push_event(self.owner, GameEvents.GAME_START)

    def end(self) -> None:
        """Завершает текущую игру."""
        self.players.clear()
        self.started = False
        self.push_event(self.owner, GameEvents.GAME_END)

    def process_turn(self, dice: int) -> None:
        """Обрабатывает бросок кубика."""
        cur_player = self.player
        self.push_event(cur_player, GameEvents.GAME_DICE, str(dice))
        cur_player.move(dice)

        # TODO: Запускаем действие поля
        # cur_player.field()

        if self.state == TurnState.NEXT:
            self.next_turn()

    def next_turn(self) -> None:
        """Передает ход следующему игроку."""
        logger.info("Next Player")
        self.state = TurnState.NEXT
        self.turn_start = datetime.now()
        self.skip_players()
        self.push_event(self.player, GameEvents.GAME_TURN)

    def add_player(self, user: BaseUser) -> Player:
        """Добавляет игрока в игру."""
        logger.info("Joining {} in game with id {}", user, self.room_id)
        if not self.open:
            raise LobbyClosedError()

        player = self.get_player(user.id)
        if player is not None:
            raise AlreadyJoinedError()

        player = Player(self, user.id, user.name)
        # TODO: Хук для старта
        self.players.append(player)
        self.push_event(player, GameEvents.GAME_JOIN)
        return player

    def remove_player(self, player: Player) -> None:
        """Удаляет пользователя из игры."""
        logger.info("Leaving {} game with id {}", player, self.room_id)
        if player is None:
            # TODO: Тту должно быть более конкретное исключение
            raise NoGameInChatError

        if player.balance >= 0:
            self.winner = player
            self.push_event(player, GameEvents.GAME_LEAVE, "win")
            self.end()
        else:
            self.bankrupts.append(player)
            self.push_event(player, GameEvents.GAME_LEAVE, "lose")

        # TODO: Хук на выход из игры
        # player.on_leave()
        self.players.remove(player)

        if len(self.players) <= 1:
            # Если игрок сам вышел/проиграл. другие побеждают
            if self.started and player == self.player:
                self.winners = self.players[0]
            else:
                self.bankrupts.extend(self.players)
            self.end()

    def skip_players(self, n: int = 1) -> None:
        """Пропустить ход для следующих игроков.

        В зависимости от направления игры пропускает несколько игроков.

        Args:
            n (int): Сколько игроков пропустить (1).

        """
        self.push_event(self.player, GameEvents.GAME_NEXT, str(n))
        self.current_player = (self.current_player + n) % len(self.players)
