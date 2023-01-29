from datetime import datetime
from time import sleep

import requests
import telegram
from environs import Env

env = Env()
env.read_env()
DVMN_API_KEY = env('DVMN_API_KEY')
TG_BOT_APIKEY = env('TG_BOT_APIKEY')
TG_CHAT_ID = env('TG_CHAT_ID')
LONG_POLLING_URL = 'https://dvmn.org/api/long_polling/'


def reply_on_found(reply):
    new_attempt = reply.get('new_attempts')[0]
    correction_required = new_attempt.get('is_negative')
    lesson_title = new_attempt.get('lesson_title')
    lesson_url = new_attempt.get('lesson_url')
    comment = '✔Вы познали мудрость богов, можно приступать к следующему уроку!'
    if correction_required:
        comment = '✘Седовласый мудрец молвит: "Всё хорошо, но переделать!"'
    message = 'У Вас проверили работу:\n"{}"\n\n*{}*\n\n[Ссылка на работу]({})'\
        .format(lesson_title, comment, lesson_url)
    bot.send_message(
        chat_id=TG_CHAT_ID,
        text=message,
        parse_mode=telegram.ParseMode.MARKDOWN,
    )


if __name__ == '__main__':
    headers = {'Authorization': f'Token {DVMN_API_KEY}'}
    params = {'timestamp': datetime.timestamp(datetime.now())}
    bot = telegram.Bot(token=TG_BOT_APIKEY)
    connection = True
    while True:
        try:
            response = requests.get(
                url=LONG_POLLING_URL,
                headers=headers,
                params=params,
            )
            response.raise_for_status()
        except requests.exceptions.ReadTimeout:
            if connection:
                bot.send_message(
                    chat_id=TG_CHAT_ID,
                    text='Сервер не отвечает. Повторный запрос...',
                )
                connection = False
            continue
        except requests.ConnectionError:
            if connection:
                print('Соединение потеряно. Переподключение...')
                connection = False
            sleep(3)
            continue
        connection = True
        status = response.json().get('status')
        if status == 'found':
            params['timestamp'] = response.json().get('last_attempt_timestamp')
            reply_on_found(response.json())
        elif status == 'timeout':
            params['timestamp'] = response.json().get('timestamp_to_request')
