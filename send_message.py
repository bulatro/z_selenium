import requests
import telegram_auth

TOKEN = telegram_auth.token
URL = 'https://api.telegram.org/bot'

users_id_list = [448732321]

def send_message(chat_id, text):
    requests.get(f'{URL}{TOKEN}/sendMessage?chat_id={chat_id}&text={text}')
