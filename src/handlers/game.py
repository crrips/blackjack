from aiogram.dispatcher import FSMContext
from .game_actions import *
from aiogram import types
from bot import dp
import random
from PIL import Image
from app import conn_db


CARDS = {
    '2♠': 2, '3♠': 3, '4♠': 4, '5♠': 5, '6♠': 6, '7♠': 7, '8♠': 8, '9♠': 9, '10♠': 10, 'J♠': 10, 'Q♠': 10, 'K♠': 10, 'A♠': 11,
    '2♣': 2, '3♣': 3, '4♣': 4, '5♣': 5, '6♣': 6, '7♣': 7, '8♣': 8, '9♣': 9, '10♣': 10, 'J♣': 10, 'Q♣': 10, 'K♣': 10, 'A♣': 11,
    '2♦': 2, '3♦': 3, '4♦': 4, '5♦': 5, '6♦': 6, '7♦': 7, '8♦': 8, '9♦': 9, '10♦': 10, 'J♦': 10, 'Q♦': 10, 'K♦': 10, 'A♦': 11,
    '2♥': 2, '3♥': 3, '4♥': 4, '5♥': 5, '6♥': 6, '7♥': 7, '8♥': 8, '9♥': 9, '10♥': 10, 'J♥': 10, 'Q♥': 10, 'K♥': 10, 'A♥': 11
}


def define_assets_paths(cards):
    assets = []
    for card in cards:
        if card in CARDS.keys():
            suit = card[-1]
            if suit == '♠':
                suit = 'Spades'
            if suit == '♣':
                suit = 'Clubs'
            if suit == '♦':
                suit = 'Diamonds'
            if suit == '♥':
                suit = 'Hearts'
            assets.append(f"src/assets/{suit}/{card[:-1]}.png")
        if card == 'card_back':
            assets.append('src/assets/card_back.png')
    return assets


async def concat_images(state, cards, is_player):
    
    data = await state.get_data()
    game_id = data['game_id']
    
    images = [Image.open(photo) for photo in define_assets_paths(cards)]
    total_width = sum(image.width for image in images) + 2 * (len(images) - 1)
    max_height = max(image.height for image in images)
    new_image = Image.new('RGB', (total_width, max_height))
    x_offset = 0
    for image in images:
        new_image.paste(image, (x_offset, 0))
        x_offset += image.width + 2
    if is_player:
        path = f'src/game_{game_id}/concat_player.png'
    else:
        path = f'src/game_{game_id}/concat_dealer.png'
    new_image.save(path)
    return path


async def send_media_player(message, state, cards):
    path = await concat_images(state, cards, True)
    await message.answer_photo(open(path, 'rb'), caption=f"Сумма ваших карт: {card_sum(cards)}")
    
    
async def send_media_dealer(message, state, cards, is_first):
    if is_first:
        cards = [cards[0], 'card_back']
        path = await concat_images(state, cards, False)
        await message.answer_photo(open(path, 'rb'), caption=f"Сумма карт дилера: {CARDS[cards[0]]}")
    else:
        path = await concat_images(state, cards, False)
        await message.answer_photo(open(path, 'rb'), caption=f"Сумма карт дилера: {card_sum(cards)}")


def card_sum(cards):
    total = sum([CARDS[card] for card in cards])
    ace_count = sum(1 for card in cards if card in {'A♠', 'A♣', 'A♦', 'A♥'})
    if ace_count > 1:
        return total - 10 * (ace_count - 1)
    return sum([CARDS[card] for card in cards])


async def process_logic(message, player_cards, dealer_cards, state):
    if card_sum(player_cards) > 21:
        await send_media_player(message, state, player_cards)
        await send_media_dealer(message, state, dealer_cards, False)
        await state.update_data(game_result='lose')
        return True
    if card_sum(player_cards) < 21:
        await send_media_player(message, state, player_cards)
        await send_media_dealer(message, state, dealer_cards, True)
        await message.answer("Выберите действие", reply_markup=actions)
    return False


async def final_logic(message, player_cards, dealer_cards, state):
    data = await state.get_data()
    pc = data['player_cards']
    dc = data['dealer_cards']
    gr = data['game_result']
    # print(pc, dc, gr)
    if card_sum(player_cards) > card_sum(dealer_cards) and card_sum(player_cards) <= 21:
        await send_media_player(message, state, player_cards)
        await send_media_dealer(message, state, dealer_cards, False)
        await state.update_data(game_result='win')
        return True
    if card_sum(player_cards) < card_sum(dealer_cards) and card_sum(dealer_cards) <= 21:
        await send_media_player(message, state, player_cards)
        await send_media_dealer(message, state, dealer_cards, False)
        await state.update_data(game_result='lose')
        return True
    if card_sum(player_cards) == card_sum(dealer_cards) and card_sum(player_cards) <= 21:
        await send_media_player(message, state, player_cards)
        await send_media_dealer(message, state, dealer_cards, False)
        await state.update_data(game_result='draw')
        return True
    if card_sum(player_cards) > 21:
        await send_media_player(message, state, player_cards)
        await send_media_dealer(message, state, dealer_cards, False)
        await state.update_data(game_result='lose')
        return True
    if card_sum(dealer_cards) > 21:
        await send_media_player(message, state, player_cards)
        await send_media_dealer(message, state, dealer_cards, False)
        await state.update_data(game_result='win')
        return True
    return False


@dp.message_handler(commands=['begin_game'])
async def game_process(message: types.Message, state: FSMContext):
    
    data = await state.get_data()
    cards = data['cards']
  
    player_cards = [random.choice(list(cards.keys())), random.choice(list(cards.keys()))]
    for card in player_cards:
        cards.pop(card)
        
    dealer_cards = [random.choice(list(cards.keys())), random.choice(list(cards.keys()))]
    for card in dealer_cards:
        cards.pop(card)  
        
    data = await state.get_data()
    game_id = data['game_id']
    
    conn = await conn_db()
    query = '''
        UPDATE game_sessions
            SET player_score = $1,
                dealer_score = $2
            WHERE id = $3
    '''
    await conn.execute(query, card_sum(player_cards), card_sum(dealer_cards), game_id)
    await conn.close()
    
    await send_media_player(message, state, player_cards)
    await send_media_dealer(message, state, dealer_cards, True)
    
    await message.answer("Выберите действие", reply_markup=actions)
    await state.update_data(player_cards=player_cards, dealer_cards=dealer_cards)
    await state.update_data(cards=cards)
    