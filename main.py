from datetime import datetime
from time import sleep

import requests
import telegram
from environs import Env


def send_review_status(reply, chat_id):
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
        chat_id=chat_id,
        text=message,
        parse_mode=telegram.ParseMode.MARKDOWN,
    )


if __name__ == '__main__':
    env = Env()
    env.read_env()
    dvmn_api_key = env('DVMN_API_KEY')
    tg_bot_api_key = env('TG_BOT_APIKEY')
    tg_chat_id = env('TG_CHAT_ID')
    long_polling_url = 'https://dvmn.org/api/long_polling/'
    headers = {'Authorization': f'Token {dvmn_api_key}'}
    params = {'timestamp': datetime.timestamp(datetime.now())}
    bot = telegram.Bot(token=tg_bot_api_key)
    connection = True
    while True:
        try:
            response = requests.get(
                url=long_polling_url,
                headers=headers,
                params=params,
            )
            response.raise_for_status()
        except requests.exceptions.ReadTimeout:
            if connection:
                bot.send_message(
                    chat_id=tg_chat_id,
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
            send_review_status(response.json(), tg_chat_id)
        elif status == 'timeout':
            params['timestamp'] = response.json().get('timestamp_to_request')
