import os
from pprint import pprint

import requests
import telebot
from dotenv import load_dotenv

load_dotenv()
TG_APIKEY = os.getenv('TG_BOT_APIKEY')
DVMN_KEY = os.getenv('DVMN_API')
bot = telebot.TeleBot(TG_APIKEY)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        'Привет!'
    )


if __name__ == '__main__':
    url = 'https://dvmn.org/api/user_reviews/'
    headers = {
        'Authorization': f'Token {DVMN_KEY}',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    pprint(response.json())
    # bot.polling(none_stop=True)
