"""Простые вспомогательные команды для бота."""

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger

from polybot.messages import HELP_MESSAGE

router = Router(name="simple commands")


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


# Обработчики
# ===========


@router.message(Command("help"))
async def get_help(message: Message, bot: Bot) -> None:
    """Помогает пользователю начать работать с ботом."""
    if message.chat.type == "private":
        return await message.answer(HELP_MESSAGE)

    try:
        await message.delete()
    except Exception as e:
        logger.warning("Unable to delete message: {}", e)
        await message.answer(
            "👀 Пожалуйста выдайте мне права удалять сообщения в чате."
        )

    try:
        await bot.send_message(message.from_user.id, HELP_MESSAGE)
        await message.answer("✨ Помощь отправлена в личные сообщения.")
    except Exception as e:
        logger.warning("Unable to send private message: {}", e)
        await message.answer("👀 Я не могу написать вам первым.")


@router.message(Command("status"))
async def get_bot_status(message: Message) -> None:
    """Полезная информация о боте."""
    await message.answer(STATUS_MESSAGE)
