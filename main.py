import requests
import telegram_auth
import time
from parsing import parse_page, users_id_list


TOKEN = telegram_auth.token
URL = 'https://api.telegram.org/bot'


# def get_updates(offset=0):
#     result = requests.get(f'{URL}{TOKEN}/getUpdates?offset={offset}').json()
#     print(result)
#     return result['result']


def run():
    # update_id = get_updates()[-1]['update_id']
    while True:
        parse_page()
        time.sleep(60 * 60 * 1)
        # messages = get_updates(update_id)
        # for message in messages:
        #     if message['message']['text'] == "/start":
        #         if message['message']['chat']['id'] not in users_id_list:
        #             users_id_list.append(message['message']['chat']['id'])
        #             print(users_id_list)
        #     if update_id < message['update_id']:
        #         update_id = message['update_id']
                # if message['message']['text'] == "/start":
                #     parse_page()


if __name__ == '__main__':
    run()
