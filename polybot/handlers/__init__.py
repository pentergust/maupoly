"""Инициализация всех роутеров.

Весь функционал бота был поделён на различные обработчики для
большей гибкости.
"""

from polybot.handlers import session, simple_commands, player, turn

# Список всех работающих роутеров
# Роутеры из этого списка будут включены в диспетчер бота
ROUTERS = (
    # Основная информация о пользователе
    # user.router,
    simple_commands.router,
    session.router,
    player.router,
    turn.router
)

__all__ = ("ROUTERS",)
