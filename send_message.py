import requests
from config import token


TOKEN = token
URL = 'https://api.telegram.org/bot'
users_id_list = [-1001342407725]


def send_msg(text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    params = {
        'chat_id': users_id_list[0],
        'parse_mode': 'HTML',
        'text': text
    }
    res = requests.get(url, params=params)
