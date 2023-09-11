import ctypes.util
import os
from dotenv import load_dotenv

from datas import database as db
from typing import Union, Optional, List

env_path = "config.env"
load_dotenv(env_path)

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
API_SESSION = os.getenv("SESSION")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# lib = ctypes.util.find_library('libssl-1_1-x64.dll')
# ssl = ctypes.cdll.LoadLibrary(lib or r'C:\Windows\System32\libssl-1_1-x64.dll')

# First run
d_base = db.Database()
d_base.create_tables()


# Convert data type into integer if input value is number
class OrganizeType:
    @staticmethod
    def is_input_digit(value):
        if value is None:
            return None
        
        if isinstance(value, int):
            return value
        
        valuetype = int(value) if value.isdigit() else str(value)
        return valuetype


class UserAdmin(OrganizeType):
    def __init__(self, chat_id, phone_no="", username=""):
        self.chat_id = chat_id
        self.phone_no = phone_no
        self.username = username


class UserSetting(OrganizeType):
    def __init__(self):
        self.use_caption:int = 0
        self.use_filter_text:int = 0 # yes = 1, no = 0
        self.use_filter_type:str = "" # whitelist, blacklist, no
        self.delay:int = 1


class SendMessage(OrganizeType):
    def __init__(self, entity, message, reply_to, link_preview, file):
        self.entity = self.is_input_digit(entity)
        self.message = message
        self.reply_to = self.is_input_digit(reply_to)
        self.link_preview = link_preview
        self.file = file


class Task(OrganizeType):
    def __init__(self, conn_name, source, use_this, reverse, min_id, limit):
        self.ntid: Optional[int] = None
        self.conn_name: str = conn_name
        self.source: Union[int, str] = source
        self.use_this: int = use_this
        self.reverse: int = reverse
        self.min_id: int = min_id
        self.limit_msg: int = limit
        self.from_user: Union[int, str] = 0

    @property
    def source(self):
        return self._source
    
    @source.setter
    def source(self, value):
        self._source = self.is_input_digit(value)
        
    @property
    def from_user(self):
        return self._from_user
    
    @from_user.setter
    def from_user(self, value):
        self._from_user = self.is_input_digit(value)


class TaskRecipient(OrganizeType):
    def __init__ (self, conn_name, to_entity, reply_to):
        self.trid: Optional[int] = 0
        self.conn_name: str = conn_name
        self.to_entity: Union[int, str] = to_entity
        self.reply_to: Union[int, str] = reply_to
    
    @property
    def to_entity(self):
        return self._to_entity
    
    @to_entity.setter
    def to_entity(self, value):
        self._to_entity = self.is_input_digit(value)

    @property
    def reply_to(self):
        return self._reply_to
    
    @reply_to.setter
    def reply_to(self, value):
        self._reply_to = self.is_input_digit(value)
