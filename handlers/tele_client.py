import config as cfg
import logging

from telethon import TelegramClient


class TeleClient:
    def __init__(self):
        self.api_id = cfg.API_ID
        self.api_hash = cfg.API_HASH
        self.phone_no = cfg.PHONE_NUMBER
        self.bot_token = cfg.BOT_TOKEN
        self.session = cfg.API_SESSION
        self.client = None

    # Send message to user / admin
    def send_message_to_user(self, chat_id):
        sndmsg = cfg.SendMessage(chat_id, None, None, False, None)
        return sndmsg
    
    def show_log(self):
        logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.INFO)

    def connect_account(self, log=False):
        if log:
            self.show_log()

        self.client = TelegramClient(self.session, self.api_id, self.api_hash)

        if self.bot_token:
            self.client.start(
                bot_token=self.bot_token
            )
        else:
            self.client.start(self.phone_no)

        return self.client
