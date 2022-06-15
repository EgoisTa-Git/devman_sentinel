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


def get_user_reviews(url):
    headers = {
        'Authorization': f'Token {DVMN_KEY}',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


if __name__ == '__main__':
    url_review = 'https://dvmn.org/api/user_reviews/'
    bot.polling(none_stop=True)
