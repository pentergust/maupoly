
"""Все использованные сообщения в боте, доступные в общем доступе.

Разные обработчики могут получить доступ к данным сообщениям.
"""

from datetime import datetime

from polybot.config import config
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

# Рассказывает об авторстве проекта и новостном канале
STATUS_MESSAGE = (
    "🌟 <b>Информация о боте</b>:\n\n"
    "<b>polybot</b> - Telegram бот с открытым исходным кодом, позволяющий "
    "пользователям играть в Монополию с друзьями в групповых чатах.\n"
    "Исходный код проекта доступен в "
    "<a href='https://codeberg.org/salormoont/polybot'>Codeberg</a>.\n"
    "🍓 Мы будем очень рады если вы внесёте свой вклад в развитие бота.\n\n"
    "Узнать о всех новостях проекта вы можете в Telegram канале "
    "<a href='https://t.me/mili_qlaster'>Salorhard</a>."
)


# Игровые комнаты ------------------------------------------------------

# Если в данном чате ещё не создано ни одной комнаты
NO_ROOM_MESSAGE = (
    "👀 В данном чате <b>нет игровой комнаты</b>.\n"
    "Вы можете <b>создайте новую</b> при помощи команды /game."
)

# Когда недостаточно игроков для продолжения игры
NOT_ENOUGH_PLAYERS = (
    f"🍰 <b>Недостаточно игроков</b> (минимум {config.min_players}) для "
    "игры.\n"
    "Если игра <b>не началась</b> воспользуйтесь командой "
    "/join чтобы зайти в комнату.\n"
    "Или создайте новую комнату при помощи /start."
)

def get_closed_room_message(game: MonoGame) -> str:
    """Когда пользователь пытается подключиться в закрытую комнату."""
    return (
        "🔒 К сожалению данная комната <b>закрыта</b>.\n"
        f"Вы можете попросить {game.start_player.mention_html()} открыть"
        "комнату или дождаться когда завершится игра."
    )


# Вспомогательные функции
# =======================

def plural_form(n: int, v: tuple[str, str, str]) -> str:
    """Возвращает склонённое значение в зависимости от числа.

    Возвращает склонённое слово: "для одного", "для двух",
    "для пяти" значений.
    """
    return v[2 if (4 < n % 100 < 20) else (2, 0, 1, 1, 1, 2)[min(n % 10, 5)]] # noqa: PLR2004

def get_str_timedelta(seconds: int) -> str:
    """Возвращает строковое представление времени из количества секунд."""
    m, s = divmod(seconds, 60)
    if m == 0:
        return f"{s} {plural_form(m, ('секунду', 'секунды', 'секунд'))}"
    if s == 0:
        return f"{m} {plural_form(m, ('минуту', 'минуты', 'минут'))}"
    return (
        f"{m} {plural_form(m, ('минуту', "минуты", 'минут'))} и "
        f"{s} {plural_form(m, ('секунду', "секунды", 'секунд'))}"
    )


# Комната
# =======


# def get_room_rules(game: MonoGame) -> str:
#     """Получает включенные игровые правила для текущей комнаты."""
#     rule_list = ""
#     active_rules = 0
#     for rule in RULES:
#         status = getattr(game.rules, rule.key, False)
#         if status:
#             active_rules += 1
#             rule_list += f"\n- {rule.name}"

#     if active_rules == 0:
#         return ""
#     return f"🔥 Выбранные правила {active_rules}:{rule_list}"

def get_all_room_players(game: MonoGame) -> str:
    """Собирает список участников игры без описания карт и текущего игрока."""
    if len(game.players) == 0:
        return "✨ В комнате пока никого нету.\n"
    players_list = f"✨ всего игроков {len(game.players)}:\n"
    for player in game.players:
        players_list += f"- {player.user.mention_html()}\n"
    return players_list

def get_room_players(game: MonoGame) -> str:
    """Собирает список игроков для текущей комнаты."""
    players_list = f"✨ Игроки ({len(game.players)}):\n"
    for i, player in enumerate(game.players):
        if i == game.current_player:
            players_list += f"- <b>{player.user.mention_html()}</b>\n"
        else:
            players_list += f"- {player.user.mention_html()}\n"
    return players_list


def get_new_game_message(game: MonoGame) -> str:
    """Сообщение о начале новой игры в комнате."""
    return (
        "🌳 Да начнётся <b>Новая игра!</b>!\n"
        f"🍓 И первым у нас ходит {game.player.user.mention_html()}\n\n"
        f"{get_room_players(game)}\n"
        # f"{get_room_rules(game)}"
    )


def get_room_status(game: MonoGame) -> str:
    """Отображает статус текущей комнаты."""
    if not game.started:
        return (
            f"☕ Новая <b>Игровая комната</b>!\n"
            f"<b>Создал</b>: {game.start_player.mention_html()}\n\n"
            f"{get_all_room_players(game)}\n"
            "⚙️ <b>правила</b> позволяют сделать игру более весёлой.\n"
            "- /join чтобы присоединиться к игре\n"
            "- /start для начала веселья!🍰"
        )

    now = datetime.now()
    game_delta = get_str_timedelta(int((now - game.game_start).total_seconds()))
    turn_delta = get_str_timedelta(int((now - game.turn_start).total_seconds()))
    return (
        f"☕ <b>Игровая комната</b> {game.start_player.first_name}:\n"
        f"🦝 <b>Сейчас ход</b> {game.player.user.first_name} "
        f"(прошло {turn_delta})\n\n"
        f"{get_room_players(game)}\n"
        # f"{get_room_rules(game)}\n"
        f"⏳ <b>Игра длится</b> {game_delta}\n"
    )

def end_game_message(game: MonoGame) -> str:
    """Сообщение об окончании игры."""
    res = (
        "✨ <b>Игра завершена</b>!\n"
        f"👑 Монополист: {game.winner.user.mention_html()}\n"
    )

    res += "\n🪙 Банкроты:\n"
    for i, loser in enumerate(game.losers):
        res += f"{i+1}. {loser.user.mention_html()}\n"

    return res

