from aiogram import types
from bot import dp, bot
from app import conn_db
from .menu import menu

WELCOME_TEXT = """
🎰 Добро пожаловать в Блэкджек-бота!

Правила игры:
- Ваша цель — набрать 21 очко или как можно ближе к нему.
- Вы играете против дилера, который должен добирать карты, пока у него менее 17 очков.
- Вы можете взять карту (/hit), остановиться (/stand), удвоить ставку (/double) или сдаться (/surrender).

Ознакомиться со всеми командами можно по команде /help.

Чтобы начать игру, нажмите на кнопку "Играть" в меню или введите команду /play.
"""


@dp.message_handler(commands=['start'])
async def send_welcome(callback_query: types.CallbackQuery):
    
    user_id = callback_query.from_user.id
    user_username = callback_query.from_user.username
    user_first_name = callback_query.from_user.first_name
    user_last_name = callback_query.from_user.last_name
    user_language_code = callback_query.from_user.language_code
    
    conn = await conn_db()
    query = '''
        INSERT INTO users (user_id, username, first_name, last_name, language_code)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (user_id) DO NOTHING
    '''
    await conn.execute(query, user_id, user_username, user_first_name, user_last_name, user_language_code)
    await conn.close()
    
    await bot.send_message(user_id, WELCOME_TEXT, reply_markup=menu)
    
    
# @dp.message_handler(lambda message: message.text == "Меню")
# async def send_welcome(message: types.Message):
    
#     await bot.send_message(message.from_user.id, "Главное меню", reply_markup=main_menu)
    