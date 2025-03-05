from aiogram.dispatcher import FSMContext
from bot import dp, PlayState
from aiogram import types
import random
from app import conn_db


actions = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
actions.add(
    types.KeyboardButton('🃏Взять карту'),
    types.KeyboardButton('🛑Остановиться'),
    types.KeyboardButton('2️⃣Удвоить'),
    types.KeyboardButton('🪦Сдаться')
)


async def dealer_logic(dealer_cards, state):
    from .game import CARDS
    from .game import card_sum
    
    while card_sum(dealer_cards) < 17:
        dealer_cards.append(random.choice(list(CARDS.keys())))
        await state.update_data(dealer_cards=dealer_cards)


@dp.message_handler(commands=['hit'], state=PlayState.game)
async def hit(message: types.Message, state: FSMContext):
    
    from .game import CARDS, process_logic
    from .play import go_to_the_end
    
    data = await state.get_data()
    player_cards = data['player_cards']
    dealer_cards = data['dealer_cards']
    game_id = data['game_id']
    
    player_cards.append(random.choice(list(CARDS.keys())))
    
    conn = await conn_db()
    
    query = '''
        UPDATE game_sessions
            SET player_score = $1
        WHERE id = $2
    '''
    await conn.execute(query, sum([CARDS[card] for card in player_cards]), game_id)
    await conn.close()
    
    await state.update_data(player_cards=player_cards)
    
    if await process_logic(message, player_cards, dealer_cards, state):
        await go_to_the_end(message, state)
      

@dp.message_handler(commands=['stand'], state=PlayState.game)
async def stand(message: types.Message, state: FSMContext):
    data = await state.get_data()
    dealer_cards = data['dealer_cards']
    await dealer_logic(dealer_cards, state)
    from .play import go_to_the_end
    await go_to_the_end(message, state)


@dp.message_handler(commands=['double'], state=PlayState.game)
async def double(message: types.Message, state: FSMContext):
    
    conn = await conn_db()
    
    query = await conn.fetch('SELECT credits FROM users WHERE user_id=$1', message.from_user.id)
    balance = query[0]['credits']
    
    query = await conn.fetch('SELECT frozen_credits FROM users WHERE user_id = $1', message.from_user.id,)
    bet = query[0]['frozen_credits']
    
    if balance < bet:
        await conn.close()
        await message.answer("У вас недостаточно средств для удвоения ставки!")
    else:
        await conn.execute('UPDATE users SET frozen_credits = $1 WHERE user_id = $2', bet * 2, message.from_user.id)
        await conn.execute('UPDATE users SET credits = credits - $1 WHERE user_id = $2', bet, message.from_user.id)
        
        data = await state.get_data()
        game_id = data['game_id']
        
        await conn.execute('UPDATE game_sessions SET bet = $1 WHERE id = $2', bet * 2, game_id)
        
        await conn.close()
        
        await message.answer("Ставка удвоена и теперь равняется " + str(bet * 2) + "!\n"
                            + "Вам будет выдана еще одна карта.")
        
        await hit(message, state)


@dp.message_handler(commands=['surrender'], state=PlayState.game)
async def surrender(message: types.Message, state: FSMContext):
    
    from .play import go_to_the_end
    
    conn = await conn_db()
    
    query = await conn.fetch('SELECT frozen_credits FROM users WHERE user_id = $1', message.from_user.id,)
    half_bet = query[0]['frozen_credits'] // 2
    await conn.execute('UPDATE users SET credits = credits + $1 WHERE user_id = $2', half_bet, message.from_user.id)
    await conn.execute('UPDATE users SET frozen_credits = 0 WHERE user_id = $1', message.from_user.id)
    await conn.close()
    
    await state.update_data(game_result='surrender')
    await go_to_the_end(message, state)
    