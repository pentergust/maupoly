"""Все использованные сообщения в боте, доступные в общем доступе.

Разные обработчики могут получить доступ к данным сообщениям.
"""

from datetime import datetime

from maupoly import exceptions
from maupoly.field import BaseField, BaseRentField, FieldType
from maupoly.game import MonoGame

# Статические сообщения
# =====================

# Когда пользователь пишет сообщение /help
HELP_MESSAGE = (
    "🍰 <b>Три простых шага чтобы начать</b>:\n"
    "1. Добавьте бота в группу.\n"
    "2. В группе начните новую игру через /game или подключитесь через /join.\n"
    "3. Если вас двое и больше, начинайте игру при помощи /start!\n\n"
    "Игроки могут подключиться в любое время.\n"
    "Чтобы покинуть игру используйте /leave.\n"
    "Если игрок долго думает. его можно пропустить командой /skip.\n"
    "☕ О прочих командах можно узнать в <b>меню</b>.\n"
)

# Если в данном чате ещё не создано ни одной комнаты
NO_ROOM_MESSAGE = (
    "👀 В данном чате ещё <b>нет игровой комнаты</b>.\n"
    "🍰 Вы можете <b>создайте новую</b> при помощи команды /game."
)

NO_JOIN_MESSAGE = (
    "🍓 Для начала надо <b>зайти в комнату</b>.\n"
    "🍰 Сделать это можно командой /join.\n"
    "🔑 Если комната <b>закрыта</b> дождитесь окончания игры."
)

# Когда недостаточно игроков для продолжения игры
NOT_ENOUGH_PLAYERS = (
    "🌳 <b>Недостаточно игроков</b> (минимум 2) для игры.\n"
    "Если игра ещё <b>не началась</b> воспользуйтесь командой "
    "/join чтобы зайти в комнату.\n"
    "🍰 Или создайте новую комнату при помощи /game."
)


def get_closed_room_message(game: MonoGame) -> str:
    """Когда пользователь пытается подключиться в закрытую комнату."""
    return (
        "🔒 К сожалению данная комната <b>закрыта</b>.\n"
        f"Вы можете попросить {game.owner.name} открыть"
        "комнату или дождаться окончания игра."
    )


# Вспомогательные функции
# =======================


def plural_form(n: int, v: tuple[str, str, str]) -> str:
    """Возвращает склонённое значение в зависимости от числа.

    Возвращает склонённое слово: "для одного", "для двух",
    "для пяти" значений.
    """
    return v[2 if (4 < n % 100 < 20) else (2, 0, 1, 1, 1, 2)[min(n % 10, 5)]]  # noqa: PLR2004


def get_str_timedelta(seconds: int) -> str:
    """Возвращает строковое представление времени из количества секунд."""
    m, s = divmod(seconds, 60)
    if m == 0:
        return f"{s} {plural_form(m, ('секунду', 'секунды', 'секунд'))}"
    if s == 0:
        return f"{m} {plural_form(m, ('минуту', 'минуты', 'минут'))}"
    return (
        f"{m} {plural_form(m, ('минуту', 'минуты', 'минут'))} и "
        f"{s} {plural_form(m, ('секунду', 'секунды', 'секунд'))}"
    )


# Комната
# =======


def get_all_room_players(game: MonoGame) -> str:
    """Собирает список участников игры без описания карт и текущего игрока."""
    if len(game.players) == 0:
        return "✨ В комнате пока никого нету.\n"
    players_list = f"✨ всего игроков {len(game.players)}:\n"
    for player in game.players:
        players_list += f"- {player.name}\n"
    return players_list


def get_room_players(game: MonoGame) -> str:
    """Собирает список игроков для текущей комнаты."""
    players_list = f"✨ Игроки ({len(game.players)}):\n"
    for i, player in enumerate(game.players):
        if i == game.current_player:
            players_list += f"- <b>{player.name}</b>\n"
        else:
            players_list += f"- {player.name}\n"
    return players_list


def get_new_game_message(game: MonoGame) -> str:
    """Сообщение о начале новой игры в комнате.

    Показывает кто первым ходит, полный список игроков и выбранные
    режимы игры.
    """
    return (
        "🌳 Да начнётся <b>Новая игра!</b>!\n"
        f"✨ И первым у нас ходит {game.player.name}\n"
        "/rules чтобы изменить игровые правила.\n"
        "/close чтобы закрыть комнату от посторонних.\n\n"
        f"{get_all_room_players(game)}\n"
        # f"{get_room_rules(game)}"
    )


def get_room_status(game: MonoGame) -> str:
    """Отображает статус текущей комнаты."""
    if not game.started:
        return (
            f"☕ Новая <b>Игровая комната</b>!\n"
            f"<b>Создал</b>: {game.owner.name}\n\n"
            f"{get_all_room_players(game)}\n"
            "⚙️ <b>правила</b> позволяют сделать игру более весёлой.\n"
            "- /rules настройки игровых правил комнаты\n"
            "- /join чтобы присоединиться к игре ✨\n"
            "- /start для начала веселья!🍰"
        )

    now = datetime.now()
    game_delta = get_str_timedelta(int((now - game.game_start).total_seconds()))
    turn_delta = get_str_timedelta(int((now - game.turn_start).total_seconds()))
    return (
        f"☕ <b>Игровая комната</b> {game.owner.name}:\n"
        f"🦝 <b>Сейчас ход</b> {game.player.name} "
        f"(прошло {turn_delta})\n\n"
        f"{get_room_players(game)}\n"
        # f"{get_room_rules(game)}\n"
        f"⏳ <b>Игра длится</b> {game_delta}\n"
    )


def get_error_message(exc: Exception) -> str:
    """Возвращает сообщение об ошибке."""
    if isinstance(exc, exceptions.NoGameInChatError):
        return NO_ROOM_MESSAGE

    if isinstance(exc, exceptions.LobbyClosedError):
        return (
            "🔒 К сожалению данная комната <b>закрыта</b>.\n"
            "Вы можете попросить владельца комнаты открыть"
            "комнату или дождаться окончания игра."
        )

    if isinstance(exc, exceptions.NotEnoughPlayersError):
        return NOT_ENOUGH_PLAYERS

    return f"👀 Что-то пошло не по плану...\n\n{exc}"


def end_game_message(game: MonoGame) -> str:
    """Сообщение об окончании игры.

    Отображает список победителей текущей комнаты и проигравших.
    Ну и полезные команды, если будет нужно создать новую игру.
    """
    if game.winner is None:
        res = "✨ <b>Игра завершена</b>!\n👑 Победителей нет\n"
    else:
        res = f"✨ <b>Игра завершена</b>!\n👑 Монополист: {game.winner.name}\n"
    res += "\n🪙 Банкроты:\n"
    for i, loser in enumerate(game.bankrupts):
        res += f"{i + 1}. {loser.name}\n"

    res += "\n🍰 /game - чтобы создать новую комнату!"
    return res


# Описание ячеек
# =============


def field_status(field: BaseField | BaseRentField) -> str:
    """Краткая информация о поле."""
    res = f"{field.type.symbol}<b>{field.name}</b>"
    if isinstance(field, BaseRentField):
        if field.owner is not None:
            res += f" {field.owner.name} {field.count_rent()}💸"
        else:
            res += f" цена {field.buy_cost}💸"
    return res
