import os
from dotenv import load_dotenv


load_dotenv()

token = os.environ.get("TOKEN")
chat_id = os.environ.get("CHAT_ID")
host = os.environ.get("DB_SETTINGS_HOST")
port = os.environ.get("DB_SETTINGS_PORT")
database = os.environ.get("DB_SETTINGS_DATABASE")
user = os.environ.get("DB_SETTINGS_USER")
password = os.environ.get("DB_SETTINGS_PASSWORD")