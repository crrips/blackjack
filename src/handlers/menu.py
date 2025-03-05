from aiogram.dispatcher import FSMContext
from aiogram import types
from bot import dp
from app import conn_db

menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
menu.add(types.KeyboardButton('🎰Играть'), types.KeyboardButton('💰Баланс'), 
         types.KeyboardButton('📜Правила игры'), types.KeyboardButton('❓Помощь'))

@dp.message_handler(commands=['menu'])
async def main_menu(message: types.Message):
    await message.answer("Главное меню", reply_markup=menu)
    
    
@dp.message_handler(lambda message: message.text == "🎰Играть", state='*')
async def play(message: types.Message, state: FSMContext):
    from .play import play
    await play(message, state)
    pass


@dp.message_handler(lambda message: message.text == "💰Баланс")
async def balance(message: types.Message):
    conn = await conn_db()
    query = await conn.fetch('SELECT credits FROM users WHERE user_id=$1', message.from_user.id)
    await conn.close()
    
    balance = query[0]['credits']
    await message.answer(f"Ваш баланс: {balance}", reply_markup=menu)
    
    
@dp.message_handler(lambda message: message.text == "📜Правила игры")
async def rules(message: types.Message):
    from .rules import send_rules
    await send_rules(message)


@dp.message_handler(lambda message: message.text == "❓Помощь")
async def help(message: types.Message):
    from .help import send_help
    await send_help(message)