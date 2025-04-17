"""Маршрутизация событий от движка."""

from maupoly.events import GameEvents
from polybot import keyboards, messages
from polybot.config import sm
from polybot.events.journal import EventContext, EventRouter

er = EventRouter()


# Обработчик сессий
# =================


@er.handler(event=GameEvents.SESSION_START)
async def start_session(ctx: EventContext) -> None:
    """Отправляет лобби, когда начинается новая сессия в чате."""
    lobby_message = (
        f"{messages.get_room_status(ctx.event.game)}\n\n"
        f"🔥 {ctx.event.player.name}, Начинает новую игру!"
    )
    await ctx.send_lobby(
        message=lobby_message,
        reply_markup=keyboards.get_room_markup(ctx.event.game),
    )


@er.handler(event=GameEvents.SESSION_END)
async def end_session(ctx: EventContext) -> None:
    """Очищает устаревший канал сообщений."""
    ctx.journal.remove_channel(ctx.event.room_id)


# Обработка событий игры
# ======================


@er.handler(event=GameEvents.GAME_JOIN)
async def join_player(ctx: EventContext) -> None:
    """Оповещает что пользователь зашёл в игру."""
    if ctx.event.game.started:
        ctx.add(f"🍰 Добро пожаловать в игру, {ctx.event.player.name}!")
        await ctx.send()
    else:
        lobby_message = (
            f"{messages.get_room_status(ctx.event.game)}\n\n"
            f"👋 {ctx.event.player.name}, добро пожаловать в комнату!"
        )
        await ctx.send_lobby(
            message=lobby_message,
            reply_markup=keyboards.get_room_markup(ctx.event.game),
        )


@er.handler(event=GameEvents.GAME_LEAVE)
async def leave_player(ctx: EventContext) -> None:
    """Оповещает что пользователь зашёл в игру."""
    # Это может бывать выход из игры до её начала
    if ctx.event.data == "win":
        ctx.add(f"👑 {ctx.event.player.name} победил(а)!\n")
    else:
        ctx.add(f"👋 {ctx.event.player.name} покидает игру!\n")

    if not ctx.event.game.started:
        ctx.set_markup(None)

    await ctx.send()


@er.handler(event=GameEvents.GAME_DICE)
async def say_uno(ctx: EventContext) -> None:
    """Оповещает что пользователь зашёл в игру."""
    ctx.gen_board()
    ctx.add(f"🎲 На кубике {ctx.event.data}")
    await ctx.send()


@er.handler(event=GameEvents.GAME_START)
async def start_game(ctx: EventContext) -> None:
    """Оповещает что пользователь зашёл в игру."""
    ctx.gen_board()
    await ctx.send_message(messages.get_new_game_message(ctx.event.game))


@er.handler(event=GameEvents.GAME_END)
async def end_game(ctx: EventContext) -> None:
    """Оповещает что пользователь зашёл в игру."""
    ctx.add(messages.end_game_message(ctx.event.game))
    ctx.set_markup(None)
    sm.remove(ctx.event.room_id)
    await ctx.send()


@er.handler(event=GameEvents.GAME_STATE)
async def set_game_state(ctx: EventContext) -> None:
    """Изменение игрового состояния."""
    ctx.add(f"⚙️ Новое состояние: {ctx.event.data}")
    await ctx.send()


@er.handler(event=GameEvents.GAME_TURN)
async def next_turn(ctx: EventContext) -> None:
    """Оповещает что пользователь зашёл в игру."""
    await ctx.clear()
    ctx.gen_board()
    ctx.add(
        f"\n🍰 <b>ход</b>: {ctx.event.game.player.name} "
        f"(💸 {ctx.event.player.balance})"
    )
    await ctx.send()
