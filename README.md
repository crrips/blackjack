# Blackjack Telegram Bot

This Telegram bot lets you play the classic card game Blackjack directly in the bot.

## 🚀 Launch

Firstly, create a .env file and set the values
```
TOKEN = ""
DB_NAME = ""
DB_USER = ""
DB_PASSWORD = ""
DB_HOST = ""
DB_PORT = 
```

To start the bot using Docker and docker-compose, run:

```
docker-compose up --build
```

## 💬 Bot Commands

/play — start a game

/help — get command help

/rules — view game rules

/hit — draw a card

/stand — stop drawing cards

/double — double the bet

/surrender — surrender

## 📜 Game Rules

Blackjack is a card game with the goal of getting a total card value as close to 21 as possible without exceeding it.

Basic Rules:

An Ace counts as 1 or 11 points.

Kings, Queens, and Jacks count as 10 points.

Other cards are worth their face value.

The player starts with two cards and can draw more (/hit) or stop (/stand).

The bet can be doubled (/double), receiving one more card.

The player can surrender (/surrender), losing half the bet.

If the total exceeds 21, the player loses.

## 🛠️ Development

* Bot: Python and the aiogram library
* Data: PostgreSQL
* Deployment: Docker
* Photo editing and generation: The Pillow library

## 📩 Feedback

If you have any suggestions or find any issues, feel free to contact me.