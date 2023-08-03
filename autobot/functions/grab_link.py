from telethon.errors import FloodWaitError
from telethon.tl.functions import messages
from telethon import types

from . import database_helper as dbhlp
from . import send_message as sndmsg
from . import menu_function as mnfunc

import asyncio
import re


# Regex untuk mendapatkan link join
async def getJoinLink(link):
    regex_list = [
        r"https?://t\.me/addlist/[a-zA-Z\d_-]+",
        r"https?://t\.me/joinchat/[a-zA-Z\d_-]+",
        r"https?://t\.me/\+[a-zA-Z\d_-]+",
        r"https?://t\.me/(?!(addstickers/|proxy/))[a-zA-Z\d_-]+"
    ]

    for regex in regex_list:
        match = re.search(regex, link)
        if match:
            join_link = match.group()
            # Periksa akhiran link
            if not join_link.endswith("_bot") and not join_link.endswith("bot"):
                return join_link

    return None


# Regex untuk mendapatkan link sticker
async def getSticker(link):
    match = None
    regex = r"https?://t\.me/addstickers/[^\]\)\s]+"

    match = re.match(regex, link)
    if match:
        sticker_link = match.group()
        return sticker_link

    return match


# Mencari dan menyimpan link ke database
def addLinktoDB(link, link_type):
    tabel_name = 'links'
    attribute = 'url'
    id1 = dbhlp.find_data(tabel_name, 'id', 1)
    id = 1 if id1 else None
    linkNotExist = dbhlp.find_data(tabel_name, attribute, link)
    if linkNotExist:
        data = (id, link, link_type)
        dbhlp.add_data(tabel_name, data)
        return True
    return False


# Proses link dan menambahkan ke database
async def prosesTeleLink(event, grabby):
    # Cek apakah link merupakan link join telegram
    valid_tele_link = await getJoinLink(grabby.message)
    if valid_tele_link:
        # Cek dan simpan link ke table
        if addLinktoDB(valid_tele_link, 'invite'):
            await sndmsg.send_message_normal(event, grabby)


# Prosesl link sticker dan menambahkan ke database
async def prosesStickerLink(event, grabby):
    # Cek apakah link merupakan link sticker
    valid_sticker_link = await getSticker(grabby.message)
    if valid_sticker_link:
        # Cek dan simpan link ke table
        if addLinktoDB(valid_sticker_link, 'sticker'):
            await sndmsg.send_message_normal(event, grabby)


# Ambil sticker link dari sticker
async def getStickerLinkBySticker(event, message, grabby):
    print(grabby.message)
    if message.sticker is not None:
        for attr in message.sticker.attributes:
            if isinstance(attr, types.DocumentAttributeSticker):
                pack = await event.client(messages.GetStickerSetRequest(attr.stickerset, 0))
                grabby.message = "https://t.me/addstickers/" + pack.set.short_name
                await prosesStickerLink(event, grabby)


# Menambahkan task grablink baru
def addNewGrabLink(type_name, task_name, use_this, user_id):
    if dbhlp.find_data('detailed_tasks', 'conn_name', task_name):
        # Jika nama koneksi belum ada, tambahkan ke database
        dataGrabLink = (None, task_name, type_name, None, None, None, None, None, None, 'incomplete')
        dbhlp.add_data('detailed_tasks', dataGrabLink)
        
        # Mengambil id
        id_grabLink = dbhlp.getIdFromTable('detailed_tasks', 'conn_name', task_name)
        id_user = dbhlp.getIdFromTable('users', 'user_id', user_id)
        
        # Menambahkan task ke user_tasks
        dataTask = (None, task_name, use_this, 0, id_grabLink, id_user)
        dbhlp.add_data('user_tasks', dataTask)


# Memulai mengambil link dari chat tertentu
async def runGrabLinkTask(event, grabby):
    chat_id = mnfunc.is_input_digit(grabby.from_entity)
    from_user = mnfunc.is_input_digit(grabby.from_user)
    grabby.entity = mnfunc.is_input_digit(grabby.entity)
    chat_id = 'me' if chat_id == 1642531797 else chat_id
    link_pattern = r'(http(s)?:\/\/[^\]\)\s]+)'
    try:
        async for message in event.client.iter_messages(chat_id, reverse=True, from_user=from_user):
            try:
                text = message.text
                links = re.findall(link_pattern, text)
                for link in links:
                    grabby.message = link[0]
                    await prosesTeleLink(event, grabby)
                    await prosesStickerLink(event, grabby)

                await getStickerLinkBySticker(event, message, grabby)
            except FloodWaitError as e:
                # Handle the FloodWaitError
                print("FloodWaitError occurred. Sleeping for {} seconds.".format(e.seconds))
                await asyncio.sleep(e.seconds)
                continue
            except: 
                print("# No text/link to proccess")
        
        print("# Done, no more link from " + str(chat_id))
    except:
        print("# Error | Invalid entity")




