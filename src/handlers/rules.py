from aiogram import types
from bot import dp, bot

RULES_TEXT = """
📜 Правила игры
1. В игре используется колода из 52 карт.
2. Ваша цель — набрать 21 очко или как можно ближе к нему.
3. Вы играете против дилера, который должен добирать карты, пока у него менее 17 очков.
4. Вы можете взять карту (/hit), остановиться (/stand), удвоить ставку (/double) или сдаться (/surrender).
5. Если у вас больше 21 очка, вы проигрываете.
6. Если у дилера больше 21 очка, вы выигрываете.
7. Если у вас и у дилера одинаковое количество очков, объявляется ничья.

Удачной игры! 🃏
"""

@dp.message_handler(commands=['rules'])
async def send_rules(message: types.Message):
    cards_spritesheet = 'src/assets/cards_spritesheet.png'
    # await bot.send_photo(message.from_user.id, cards_spritesheet, caption=RULES_TEXT)
    with open(cards_spritesheet, 'rb') as photo:
        await message.answer_photo(photo, caption=RULES_TEXT)
    # await message.answer(RULES_TEXT)