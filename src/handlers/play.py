from aiogram.dispatcher import FSMContext
from .game import game_process
from bot import dp, PlayState
from .game_actions import *
from .game import card_sum
from aiogram import types
from pathlib import Path
from app import conn_db
from .menu import menu
import shutil

@dp.message_handler(commands=['play'], state='*')
async def play(message: types.Message, state: FSMContext):
    
    conn = await conn_db()
    query = await conn.fetch('SELECT credits FROM users WHERE user_id=$1', message.from_user.id)
    await conn.close()
    
    balance = query[0]['credits']
    
    bets = types.ReplyKeyboardMarkup(resize_keyboard=True)
    bets.add(
        types.KeyboardButton(str(0)),
        types.KeyboardButton(str(10)),
        types.KeyboardButton(str(50)),
        types.KeyboardButton(str(100)),
        types.KeyboardButton(str(200)),
        types.KeyboardButton(str(500)),
        types.KeyboardButton('Вернуться в меню')
    )
    
    await state.set_state(PlayState.bet)
    await message.answer(f"Ваш баланс: {balance}", reply_markup=bets)
    await message.answer("Выберите ставку или введите свою.")


@dp.message_handler(lambda message: message.text == "Вернуться в меню", state=PlayState.bet)
async def back_to_menu(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Главное меню", reply_markup=menu)


@dp.message_handler(lambda message: message.text.isdigit(), state=PlayState.bet)
async def bet(message: types.Message, state: FSMContext):
    bet_amount = int(message.text)
    
    conn = await conn_db()
    query = await conn.fetch('SELECT credits FROM users WHERE user_id=$1', message.from_user.id)
    balance = query[0]['credits']
    
    if bet_amount > balance:
        await message.answer("У вас недостаточно средств для этой ставки.")
    else:
        await conn.execute('UPDATE users SET credits = $1 WHERE user_id = $2', balance - bet_amount, message.from_user.id)
        await conn.execute('UPDATE users SET frozen_credits = $1 WHERE user_id = $2', bet_amount, message.from_user.id)
        await conn.close()
        
        await message.answer(f"Ставка принята: {bet_amount}. Игра началась...")
        await state.update_data(bet=bet_amount)
        await game(message, state)


@dp.message_handler(state=PlayState.bet)
async def game(message: types.Message, state: FSMContext):
    
    data = await state.get_data()
    bet = data['bet']
    
    await state.finish()
    
    conn = await conn_db()
    query = '''
        INSERT INTO game_sessions
            (player_id, bet)
                VALUES ($1, $2)
            RETURNING id;
    '''
    
    game_id = await conn.fetchval(query, message.from_user.id, bet)
    
    Path(f'src/game_{game_id}').mkdir(parents=True, exist_ok=True)
    
    await conn.close()
    
    await PlayState.game.set()
    await state.update_data(game_result='playing')
    await state.update_data(game_id=game_id)
    await game_process(message, state)
    
    
async def go_to_the_end(message: types.Message, state: FSMContext):
    game_data = await state.get_data()
    game_id = game_data['game_id']
    game_result = game_data['game_result']
    player_cards = game_data['player_cards']
    dealer_cards = game_data['dealer_cards']
    if game_result == 'playing':
        from .game import final_logic
        await final_logic(message, player_cards, dealer_cards, state)
        game_data = await state.get_data()
        game_result = game_data['game_result']
    await state.finish()
    await PlayState.end.set()
    await state.update_data(game_id=game_id)
    await state.update_data(game_result=game_result)
    await state.update_data(player_cards=player_cards)
    await state.update_data(dealer_cards=dealer_cards)
    await end(message, state)
    
    
@dp.message_handler(state=PlayState.game)
async def action(message: types.Message, state: FSMContext):
    if message.text == "🃏Взять карту":
        await hit(message, state)
    if message.text == "🛑Остановиться":
        await stand(message, state,)
    if message.text == "2️⃣Удвоить":
        await double(message, state)
    if message.text == "🪦Сдаться":
        await surrender(message, state)


@dp.message_handler(state=PlayState.end)
async def end(message: types.Message, state: FSMContext):
    
    data = await state.get_data()
    game_id = data['game_id']
    game_result = data['game_result']
    player_cards = data['player_cards']
    dealer_cards = data['dealer_cards']
    
    conn = await conn_db()
    
    if game_result == 'win':
        await conn.execute('UPDATE users SET credits = credits + frozen_credits * 2 WHERE user_id = $1', message.from_user.id,)
    elif game_result == 'draw':
        await conn.execute('UPDATE users SET credits = credits + frozen_credits WHERE user_id = $1', message.from_user.id,)
        
    await conn.execute('UPDATE users SET frozen_credits = 0 WHERE user_id = $1', message.from_user.id,)
    
    query = await conn.fetch('SELECT credits FROM users WHERE user_id=$1', message.from_user.id)
    balance = query[0]['credits']
    
    query = '''
        UPDATE game_sessions
            SET game_result = $1,
                status = 'finished',
                player_score = $2,
                dealer_score = $3,
                finished_at = NOW()
            WHERE id = $4;
    '''
    await conn.execute(query, game_result, card_sum(player_cards), card_sum(dealer_cards), game_id)
    
    await conn.close()
    
    game_result_text = {
        'win': "Поздравляем! Вы выиграли!",
        'lose': "Вы проиграли!",
        'draw': "Ничья!",
        'surrender': "Вы сдались!\nВам возвращена половина ставки."
    }
    
    END_TEXT = f"""
{game_result_text[game_result]}
Игра окончена!
Ваш новый баланс: {balance}
Хотите сыграть еще раз?
"""
    
    await message.answer(END_TEXT, reply_markup=menu)
    await state.finish()
    shutil.rmtree(f'src/game_{game_id}')