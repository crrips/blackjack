from aiogram import types
from bot import dp

HELP_TEXT = """
💬 Команды бота:
/play — начать игру
/help — помощь по командам
/rules — правила игры
/hit — взять карту
/stand — остановиться
/double — удвоить ставку
/surrender — сдаться

Удачной игры! 🃏
"""

@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    await message.answer(HELP_TEXT)