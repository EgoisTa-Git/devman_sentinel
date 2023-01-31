import logging
from datetime import datetime
from time import sleep

import requests
import telegram
from environs import Env

logger = logging.getLogger(__file__)


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def send_review_status(tg_bot, review, chat_id):
    new_attempt = review.get('new_attempts')[0]
    correction_required = new_attempt.get('is_negative')
    lesson_title = new_attempt.get('lesson_title')
    lesson_url = new_attempt.get('lesson_url')
    comment = '✔Вы познали мудрость богов, можно приступать к следующему уроку!'
    if correction_required:
        comment = '✘Седовласый мудрец молвит: "Всё хорошо, но переделать!"'
    message = 'У Вас проверили работу:\n"{}"\n\n*{}*\n\n[Ссылка на работу]({})'\
        .format(lesson_title, comment, lesson_url)
    tg_bot.send_message(
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
    logging.basicConfig(
        level=logging.WARNING,
        format='%(process)d %(filename)s %(levelname)s %(message)s',
    )
    logger.setLevel(logging.ERROR)
    logger.addHandler(TelegramLogsHandler(bot, tg_chat_id))
    while True:
        try:
            response = requests.get(
                url=long_polling_url,
                headers=headers,
                params=params,
            )
            response.raise_for_status()
        except requests.exceptions.ReadTimeout:
            logger.warning('Истекло время ожидания ответа от сервера')
            continue
        except requests.exceptions.HTTPError:
            logger.warning('Сервер не отвечает')
            continue
        except requests.ConnectionError:
            sleep(3)
            continue
        founded_review = response.json()
        status = founded_review.get('status')
        if status == 'found':
            params['timestamp'] = founded_review.get('last_attempt_timestamp')
            send_review_status(bot, founded_review, tg_chat_id)
        elif status == 'timeout':
            params['timestamp'] = founded_review.get('timestamp_to_request')
