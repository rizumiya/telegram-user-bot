import ctypes.util
import os
from dotenv import load_dotenv

from datas import database as db
from typing import Union, Optional, List

env_path = "./config.env"
load_dotenv(env_path)

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
BOT_TOKEN = os.getenv("BOT_TOKEN")


lib = ctypes.util.find_library('libssl-1_1-x64.dll')
ssl = ctypes.cdll.LoadLibrary(lib or r'C:\Windows\System32\libssl-1_1-x64.dll')


# Membuat database
dbase = db.Database()
dbase.create_tables()


# Mengubah tipe data menjadi integer untuk nilai berupa angka
class OrganizeType:
    @staticmethod
    def is_input_digit(value):
        if value is None:
            return None
        
        if isinstance(value, int):
            return value
        
        valuetype = int(value) if value.isdigit() else str(value)
        return valuetype


class SendMessage(OrganizeType):
    def __init__(self, entity, message, reply_to, link_preview, file):
        self.entity = self.is_input_digit(entity)
        self.message = message
        self.reply_to = self.is_input_digit(reply_to)
        self.link_preview = link_preview
        self.file = file


class NewTask(OrganizeType):
    def __init__(self, conn_name, old_live, from_entity, use_this, min_id, limit):
        self.ntid: Optional[int] = None
        self.conn_name: str = conn_name
        self.old_live: str = old_live
        self.use_this: int = use_this
        self._from_entity: Union[int, str] = from_entity
        self._from_user: Union[int, str] = 0
        self.min_id: int = min_id
        self.limit: int = limit

    @property
    def from_entity(self):
        return self._from_entity
    
    @from_entity.setter
    def from_entity(self, value):
        self._from_entity = self.is_input_digit(value)
    
    @property
    def from_user(self):
        return self._from_user
    
    @from_user.setter
    def from_user(self, value):
        self._from_user = self.is_input_digit(value)


class TaskRecipient(OrganizeType):
    def __init__(self, conn_name, to_user, reply_to):
        self.trid: Optional[int] = 0
        self.conn_name: str = conn_name
        self.to_user: Union[int, str] = to_user
        self.reply_to: Union[int, str] = reply_to

    @property
    def to_user(self):
        return self._to_user
    
    @to_user.setter
    def to_user(self, value):
        self._to_user = self.is_input_digit(value)
    
    @property
    def reply_to(self):
        return self._reply_to
    
    @reply_to.setter
    def reply_to(self, value):
        self._reply_to = self.is_input_digit(value)


class Filter:
    def __init__(self, filter_type="",filter_types=None, regex=0, text=""):
        self.filter_type: str = filter_type
        self.filter_types: List[str] = filter_types
        self.regex: int = regex
        self.text: str = text



# class TrackMessages:
#     def __init__(self):
#         self.entity: Union[int, str] = ""
#         self.message: str = ""
#         self.reply_to: Optional[Union[int, str]] = None
#         self.link_preview: bool = False
#         self.file: str = ""

        



# class NewTask:
#     def __init__(self):
#         self.tid: str = ""
#         self.conn_name: str = ""
#         self.from_entity: Union[int, str] = ""
#         self.from_user: Union[int, str] = ""
#         self.entity: Union[int, str] = ""
#         self.reply_to: Optional[Union[int, str]] = None
#         self.message: str = ""
#         self.min_id: int = 0
#         self.limit: int = 0
#         self.status: str = ""
#         self.link_preview: bool = True
