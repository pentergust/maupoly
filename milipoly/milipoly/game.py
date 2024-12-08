from datetime import datetime
from random import shuffle

from aiogram import Bot

from milipoly.milipoly.field import CLASSIC_BOARD
from milipoly.milipoly.journal import Journal


# TODO: Написать класс игры
class MonoGame:
    def __init__(self, chat_id: int, bot: Bot):
        self.chat_id = chat_id
        self.bot: Bot = bot
        self.journal = Journal(self, self.bot)

        # Игроки
        self.current_player: int = 0
        self.start_player = None
        self.players = []
        self.bankrupts = []
        self.winners = None

        # Состояние игры
        self.started: bool = False
        self.open: bool = True
        self.dice = 0
        self.fields = []
        self.round_counter = 0

        # Таймеры
        self.game_start = datetime.now()
        self.turn_start = datetime.now()

    def new_game(self):
        shuffle(self.players)

        self.started = True
        self.open = False
        self.fields.clear()
        self.fields = CLASSIC_BOARD.copy()
        self.round_counter = 0
        self.game_start = datetime.now()
        self.turn_start = datetime.now()
