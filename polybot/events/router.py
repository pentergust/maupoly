"""Маршрутизация событий от движка."""

from maupoly.enums import GameEvents
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


@er.handler(event=GameEvents.GAME_START)
async def start_game(ctx: EventContext) -> None:
    """Оповещает что пользователь зашёл в игру."""
    ctx.gen_board()
    ctx.add(messages.get_new_game_message(ctx.event.game))
    await ctx.send()


@er.handler(event=GameEvents.GAME_END)
async def end_game(ctx: EventContext) -> None:
    """Оповещает что пользователь зашёл в игру."""
    ctx.add(messages.end_game_message(ctx.event.game))
    ctx.set_markup(None)
    sm.remove(ctx.event.room_id)
    await ctx.send()


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


@er.handler(event=GameEvents.GAME_TURN)
async def next_turn(ctx: EventContext) -> None:
    """Оповещает что пользователь зашёл в игру."""
    # Отправляем накопленный буфер сообщений
    ctx.add("🍺 Завершаю ход")
    await ctx.send()

    # Создаём новое сообщение
    await ctx.clear()
    ctx.gen_board()
    ctx.add(
        f"\n🍰 <b>ход</b>: {ctx.event.game.player.name} "
        f"(💸 {ctx.event.player.balance})"
    )
    await ctx.send()


# Обработка игровых состояний
# ===========================


@er.handler(event=GameEvents.GAME_STATE)
async def new_game_state(ctx: EventContext) -> None:
    """Изменение игрового состояния."""
    if ctx.event.data == "buy":
        ctx.add(f"👀 {ctx.event.player.name} задумывается о покупке.")
        ctx.set_markup(keyboards.get_buy_field_markup(ctx.event.player))
    else:
        ctx.add(f"⚙️ Новое состояние: {ctx.event.data}")
        ctx.set_markup(keyboards.NEXT_MARKUP)
    await ctx.send()


# События игрока
# ==============


@er.handler(event=GameEvents.PLAYER_DICE)
async def roll_dice(ctx: EventContext) -> None:
    """Оповещает что пользователь зашёл в игру."""
    ctx.add(f"🎲 На кубике {ctx.event.data}")


@er.handler(event=GameEvents.PLAYER_MOVE)
async def move_player(ctx: EventContext) -> None:
    """Когда игрок перемещается по полю."""
    field_status = messages.field_status(ctx.event.player.field)
    ctx.add(f"🧭 Вы попали на поле {field_status}!")


@er.handler(event=GameEvents.PLAYER_BUY)
async def pay_field(ctx: EventContext) -> None:
    """Когда пользователь попал на поле, которое можно купить."""
    cost, is_reward = ctx.event.data.split()
    if is_reward == "true":
        ctx.add(f"💸 {ctx.event.player.name} Получает {cost}")
    else:
        ctx.add(f"💸 {ctx.event.player.name} должен заплатить {cost}")
    ctx.set_markup(keyboards.NEXT_MARKUP)
    await ctx.send()


@er.handler(event=GameEvents.PLAYER_BUY_FIELD)
async def byu_field(ctx: EventContext) -> None:
    """Когда игрок купил поле."""
    ctx.add(f"💸 {ctx.event.player.name} покупает поле.")


@er.handler(event=GameEvents.PLAYER_CHANCE)
async def player_chance(ctx: EventContext) -> None:
    """Когда игрок попал на поле шанс или общественная казна."""
    ctx.add(f"✨ {ctx.event.data}!")


@er.handler(event=GameEvents.PLAYER_PRISON)
async def player_prison(ctx: EventContext) -> None:
    """Когда игрок попал в тюрьму."""
    ctx.add("⚡ вы были арестованы!")


@er.handler(event=GameEvents.PLAYER_CASINO)
async def player_casino(ctx: EventContext) -> None:
    """Когда игрок попал в казино."""
    ctx.add("🎰 вас приветствует казино!")
    ctx.set_markup(keyboards.NEXT_MARKUP)
    await ctx.send()
