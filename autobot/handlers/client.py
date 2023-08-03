import config
import logging
from telethon import TelegramClient


class TeleClient:
    def __init__(self):
        self.api_id = config.API_ID
        self.api_hash = config.API_HASH
        self.phone_no = config.PHONE_NUMBER
        self.bot_token = config.BOT_TOKEN
        self.session = config.SESSION

    def send_message_to_user(self, user_id):
        sndmsg = config.SendMessage(user_id, None, None, False, None)
        return sndmsg

    def show_log(self):
        logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', 
                            level=logging.INFO)

    def connect_acc(self, log=False):
        if log:
            self.show_log()
        
        self.client = TelegramClient(
            self.session, 
            self.api_id, 
            self.api_hash
        )
        
        if self.bot_token:
            self.client.start(
                bot_token=self.bot_token
            )
        else:
            self.client.start(self.phone_no)

        return self.client