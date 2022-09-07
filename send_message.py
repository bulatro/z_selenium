import requests
from config import token, chat_id


TOKEN = token


def send_msg(text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    params = {
        'chat_id': chat_id,
        'parse_mode': 'HTML',
        'text': text
    }
    res = requests.get(url, params=params)
