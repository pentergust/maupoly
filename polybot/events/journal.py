"""Обработчик игровых событий движка."""

import asyncio
from collections import deque
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from aiogram import Bot
from aiogram.types import BufferedInputFile, InlineKeyboardMarkup, Message
from loguru import logger

from maupoly.events import BaseEventHandler, Event, GameEvents
from polybot.boardgen import generate_board
from polybot.keyboards import TURN_MARKUP

FuncType = Callable[..., Any] | Callable[..., Awaitable[Any]]

T = TypeVar("T", bound=FuncType)


class EventContext:
    """Вспомогательный класс контекст событий."""

    def __init__(self, event: Event, journal: "MessageJournal") -> None:
        self.event = event
        self.journal = journal
        self._channel: MessageChannel = self.journal.get_channel(
            self.event.room_id
        )

    # Сокращение для методов
    # ======================

    async def send_lobby(
        self, message: str, reply_markup: InlineKeyboardMarkup | None = None
    ) -> None:
        """Отправляет сообщение-лобби о начале новой игры."""
        return await self._channel.send_lobby(message, reply_markup)

    async def send_message(self, text: str) -> Message:
        """Отправляет сообщение в комнату."""
        return await self._channel.send_message(text)

    async def send(self) -> None:
        """Отправляет журнал в чат.

        Если до этого журнал не отправлялся, будет создано отправлено
        новое сообщение с журналом.
        Если же журнал привязан, то изменится текст сообщения.
        По умолчанию журнал очищается при каждом новом ходе игрока.
        """
        await self._channel.send()

    async def clear(self) -> None:
        """Очищает буфер событий и сбрасывает клавиатуру."""
        await self._channel.clear()

    def set_markup(self, markup: InlineKeyboardMarkup | None) -> None:
        """Устанавливает клавиатуру для игровых событий."""
        self._channel.set_markup(markup)

    def add(self, text: str) -> None:
        """Добавляет новую запись в буфер сообщений."""
        self._channel.add(text)

    def gen_board(self) -> None:
        """Обновляет игровое поле."""
        self._channel.gen_board(self.event)


class EventRouter:
    """Привязывает обработчики к конкретным событиям."""

    def __init__(self) -> None:
        self._handlers: dict[GameEvents, FuncType] = {}

    async def process(self, event: Event, journal: "MessageJournal") -> None:
        """Обрабатывает пришедшее событие."""
        logger.debug(event)
        handler = self._handlers.get(event.event_type)

        if handler is None:
            logger.warning("No handler on: {}", event)
            return None

        await handler(EventContext(event, journal))

    def handler(self, event: GameEvents) -> Callable:
        """Декоратор для добавления новых обработчиков событий."""

        def wrapper(func: T) -> T:
            self._handlers[event] = func
            return func

        return wrapper


class MessageChannel:
    """Канал сообщений, привязанный к конкретному чату."""

    def __init__(
        self, room_id: int, bot: Bot, default_markup: InlineKeyboardMarkup
    ) -> None:
        self.room_id = room_id
        self.lobby_message: Message | None = None
        self.room_message: Message | None = None
        self.message_queue: deque[str] = deque(maxlen=10)
        self.bot = bot
        self.default_markup = default_markup
        self.markup: InlineKeyboardMarkup | None = self.default_markup
        self.board: BufferedInputFile | None = None

        self.semaphore = asyncio.Semaphore()

    async def send_lobby(
        self, message: str, reply_markup: InlineKeyboardMarkup | None = None
    ) -> None:
        """Отправляет сообщение-лобби о начале новой игры."""
        if self.lobby_message is None:
            lobby_message = await self.bot.send_message(
                text=message,
                chat_id=self.room_id,
                reply_markup=reply_markup,
            )
            if isinstance(lobby_message, Message):
                self.lobby_message = lobby_message

        else:
            await self.lobby_message.edit_text(
                text=message,
                reply_markup=reply_markup,
            )

    async def send_message(self, text: str) -> Message:
        """Отправляет сообщение в комнату."""
        if self.board is None:
            raise ValueError("Board image not generated")

        return await self.bot.send_photo(
            photo=self.board,
            chat_id=self.room_id,
            caption=text,
            reply_markup=self.markup,
        )

    async def send(self) -> None:
        """Отправляет журнал в чат.

        Если до этого журнал не отправлялся, будет создано отправлено
        новое сообщение с журналом.
        Если же журнал привязан, то изменится текст сообщения.
        По умолчанию журнал очищается при каждом новом ходе игрока.
        """
        if len(self.message_queue) == 0:
            return None

        async with self.semaphore:
            if self.room_message is None:
                self.room_message = await self.send_message(
                    text="\n".join(self.message_queue),
                )
            else:
                await self.room_message.edit_caption(
                    caption="\n".join(self.message_queue),
                    reply_markup=self.markup,
                )

    async def clear(self) -> None:
        """Очищает буфер событий и сбрасывает клавиатуру."""
        self.markup = self.default_markup
        self.lobby_message = None
        if self.room_message is not None:
            await self.room_message.edit_reply_markup(reply_markup=None)
            self.room_message = None
        self.message_queue = deque(maxlen=10)

    def set_markup(self, markup: InlineKeyboardMarkup | None) -> None:
        """Устанавливает клавиатуру для игровых событий."""
        self.markup = markup

    def add(self, text: str) -> None:
        """Добавляет новую запись в буфер сообщений."""
        self.message_queue.append(text)

    def gen_board(self, event: Event) -> None:
        """Обновляет игровое поле."""
        self.board = generate_board(event.game)


class MessageJournal(BaseEventHandler):
    """Обрабатывает события в рамках Telegram бота."""

    def __init__(self, bot: Bot, router: EventRouter) -> None:
        self.channels: dict[int, MessageChannel] = {}
        self._loop = asyncio.get_running_loop()
        self.bot: Bot = bot
        self.default_markup = TURN_MARKUP
        self.router = router

    def push(self, event: Event) -> None:
        """Обрабатывает входящие события."""
        logger.debug(event)
        self._loop.create_task(self.router.process(event, self))

    def get_channel(self, room_id: int) -> MessageChannel:
        """Получает/создаёт канал сообщений для чата."""
        channel = self.channels.get(room_id)
        if channel is None:
            channel = MessageChannel(room_id, self.bot, self.default_markup)
            self.channels[room_id] = channel

        return channel

    def remove_channel(self, room_id: int) -> None:
        """Устанавливает канал сообщений для чата."""
        self.channels.pop(room_id)
