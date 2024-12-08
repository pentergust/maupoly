"""Игровой журнал событий.

Игровой журнал используется чтобы отслеживать состояние игры и отправлять его
в чат.
"""

from datetime import datetime
from typing import TYPE_CHECKING, NamedTuple

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, Message

if TYPE_CHECKING:
    from milipoly.milipoly import MonoGame

# Вспомогательные классы
# ======================

class Event(NamedTuple):
    """Запись об игровом событии.

    Содержит некоторую цельную запись о ходе игры.
    Примером события может служить взятие карт игроком, специальные
    предложения и так далее.

    Каждое событие содержит некоторую полезную информацию о себе.
    Когда оно было совершено, кто был инициатором, насколько оно важное.
    """

    date: datetime
    text: str

    def __str__(self) -> str:
        """Представление события в виде строки."""
        return f"{self.text}\n"


# Основной класс
# ==============

class Journal:
    """Класс журнала игровых событий.

    Используется для отслеживания статуса игры и оправки игровых
    событий в связанный с игрой чат.
    Каждый журнал привязывается к конкретной игре и обновляется в
    зависимости от действий участников.
    """

    def __init__(self, game: 'MonoGame', bot: Bot):
        self.game: 'MonoGame' = game
        self.bot: Bot = bot
        self.events: list[Event] = []
        self.reply_markup: InlineKeyboardMarkup | None = None
        self.message: Message | None = None

    # Управление журналом
    # ===================

    def add(self,
        text: str,
    ) -> None:
        """Добавляет новое событие в журнал."""
        self.events.append(Event(
            date=datetime.now(),
            text=text,
        ))

    def set_markup(self,
        reply_markup: InlineKeyboardMarkup | None = None
    ) -> None:
        self.reply_markup = reply_markup

    def get_journal_message(self):
        res = ""
        for event in self.events:
            res += str(event)
        return res

    async def send_journal(self):
        journal_message = self.get_journal_message()
        if self.message is None:
            self.message = await self.bot.send_message(
                chat_id=self.game.chat_id,
                text=journal_message,
                reply_markup=self.reply_markup
            )
        else:
            await self.message.edit_text(
                text=journal_message,
                reply_markup=self.reply_markup
            )

    def clear(self) -> None:
        """Очищает журнал событий."""
        self.events.clear()
        self.reply_markup = None
        self.message = None


    # Магические методы
    # =================

    def __len__(self) -> int:
        """Возвращает количество записей в журнале."""
        return len(self.events)

    def __getitem__(self, i: int) -> Event:
        """Получает событие по индексу."""
        return self.events[i]

    def __setitem__(self, i: int, event: Event) -> None:
        """Изменяет событие по индексу."""
        if not isinstance(event, Event):
            return ValueError("Journal can only contains Event instances")
        self.events[i] = event
