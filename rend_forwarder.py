
# @client.on(events.NewMessage(pattern='/filterlist'))
# async def handle_filterlist(event):
#     if event.is_private:
#         filtertype = ['file', 'foto', 'gif', 'sticker', 'url', 'video']
        
#         message = "**Available Filter Type**\n\n"
        
#         for type in filtertype:
#             message += f"`{type}`\n"
        
#         message += "\n**Usage Example**: `/filter image`"
#         user_id = event.sender_id

#         await client.send_message(user_id, message, parse_mode='markdown')


# @client.on(events.NewMessage(pattern='/addblacklist (.*)'))
# async def handle_addblacklist(event):
#     if event.is_private:
#         user_id = event.sender_id
#         blacklist_value = event.pattern_match.group(1)
        
#         try:
#             id_blacklist = insert_blacklist(blacklist_value)
#             id_setting = search_data('id', 'settings', 'user_id', user_id)

#             insert_user_blacklist(id_setting[0][0], id_blacklist[0][0])
#             await send_response_message(client, user_id, f"'{blacklist_value}' added.")
#             message = await getStatus(event)
#             await send_response_message(client, user_id, message)
#         except Exception as e:
#             await send_response_message(client, user_id, f"Failed to add '{blacklist_value}', check your blacklist list. {e}")

# =============================================================================================================

from telethon import TelegramClient, events, types
from telethon.tl.functions import messages

import logging
import os
import re

from module import downloading_media, forwarding_message, sending_message, turning_anon
from helper import helper_menu, helper_db, database
import autogram_userbot.config as config

api_id = config.API_ID
api_hash = config.API_HASH
session_name = config.SESSION
phone_number = config.PHONE_NUMBER

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',level=logging.INFO)

current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.join(os.path.dirname(current_directory), 'AIOMediaBot')

# Membuat koneksi dengan Telegram
client = TelegramClient(session_name, api_id, api_hash).start(phone_number)


# Mendaftarkan user ke dalam database jika belum ada
@client.on(events.NewMessage(pattern='/start me'))
async def handle_start(event):
    if event.is_private:
        user_id = event.sender_id

        await client.send_message(user_id, 'Send `/help` to see commands list and how to use them.', parse_mode='markdown')
        await helper_db.addingUser(event)


# Export database jadi txt
@client.on(events.NewMessage(pattern='/backup'))
async def handle_start(event):
    if await checkUserValidity(event):
        file_path = os.path.join(parent_directory, 'export_db.txt')
        database.export_all_tables_to_txt('ren_DB.db', file_path)
        print("# Database exported")


# Menampilkan pesan bantuan cara penggunaan, dll
@client.on(events.NewMessage(pattern='/help'))
async def handle_help(event):
    if await checkUserValidity(event):
        await helper_menu.showHelp(event)
    

# Menampilkan pengaturan yang dimiliki user saat ini
@client.on(events.NewMessage(pattern='/setting'))
async def handle_setting(event):
    if await checkUserValidity(event):
        message = await helper_db.getStatus(event)
        user_id = event.sender_id

        await client.send_message(user_id, message, parse_mode='markdown')


# Memulai forward konten
@client.on(events.NewMessage(func=lambda event: event.is_private and event.message.text.startswith('/run')))
async def handle_runforward(event):
    if await checkUserValidity(event):
        text = event.message.text.strip().split()
        if len(text) >= 2 and text[0] == '/run':
            kata1 = text[1]
            if kata1.isdigit():
                kata1 = int(kata1)
            else:
                kata1 = str(kata1)
            print("# Start forwarding media from id : " + str(kata1))
            await mediaForwarder(event, kata1, int(1901826075), 15)



# Menambahkan channel untuk di forward
@client.on(events.NewMessage(func=lambda event: event.is_private and event.message.text.startswith('/addforward')))
async def handle_addforward(event):
    user_id = await checkUserValidity(event)
    if user_id:
        text = event.message.text.strip().split()
        if len(text) >= 6 and text[0] == '/addforward':
            task_name, from_id, to_id, reply_id, offset_id = text[1:6]
            checkFwdTsk = await helper_db.addforwardTask(task_name, from_id, to_id, reply_id, offset_id, user_id)
            if checkFwdTsk:
                message = 'Send `/run` [forward_name] to start forwarding contents'
                await client.send_message(user_id, message, parse_mode='markdown')
                await getFwdTsk(event)


# Menghandle pesan untuk mengambil link dari id tertentu
@client.on(events.NewMessage(func=lambda event: event.is_private and event.message.text.startswith('/scraplink')))
async def handle_scraplink(event):
    if await checkUserValidity(event):
        text = event.message.text.strip().split()
        if len(text) >= 2 and text[0] == '/scraplink':
            kata1 = text[1]
            if kata1.isdigit():
                kata1 = int(kata1)
            else:
                kata1 = str(kata1)
            print("# Start processing links from id : " + str(kata1))
            await scrapingLink(event, kata1)


# Handle Forward dan lainnya
@client.on(events.NewMessage)
async def handle_new_message(event):
    link_pattern = r'(http(s)?:\/\/[^\]\)\s]+)'
    # Cek jika pengirim adalah user lain dan bukan bot
    if await checkUserValidity(event):
        # Panggil fungsi ambil sticker link
        await getStickerLinkBySticker(event)

        # Menghandle pesan yang berasal dari terusan
        if event.fwd_from and not event.grouped_id:

            original_message = await client.get_messages(event.chat_id, ids=event.message.id)
            await client.send_message(event.sender_id, original_message)
            await getStickerLinkBySticker(event)

            await event.client.delete_messages(event.sender_id, event.message)
            
        # Cek jika pesan adalah sebuah text
        if event.message.text:
            text = event.message.text
            links = re.findall(link_pattern, text)
            for link in links:
                await prosesTeleLink(event, link[0])
                await prosesStickerLink(event, link[0])

    # jika pengirim berasal dari grup aio
    if event.is_channel and event.peer_id.channel_id == 1901826075:
        if event.message.text:
            reply_to = event.reply_to.reply_to_msg_id if event.reply_to else None
            text = event.message.text
            links = re.findall(link_pattern, text)
            for link in links:
                await prosesDownloadLink(event, link[0], reply_to)

    # Cek jika pengirim berada dalam channel / supergrup / grup yang bukan aio
    if event.is_channel or event.is_group and event.chat.id != 1901826075:
        text = event.message.text
        links = re.findall(link_pattern, text)
        for link in links:
            await prosesTeleLink(event, link[0])
            await prosesStickerLink(event, link[0])

# Function

# Tampilkan seluruh task pada user saat ini
async def getFwdTsk(event):
    fwdTsks = await helper_db.getCurrFwdTsk(event)
    message = f'**Forward Task**\n\nCurrent Task:\n'
    if not fwdTsks:
        message += "No forward task"
    else:
        for row in fwdTsks:
            message += "Task name: " + fwdTsks[row][1] + " \n"
            message += "From id: " + fwdTsks[row][2] + " \n"
            message += "To id: " + fwdTsks[row][3] + " \n"
            message += "Reply id: " + fwdTsks[row][4] + " \n"
            message += "Offset: " + fwdTsks[row][5] + " \n\n"
    
    return message


# Ambil sticker link dari sticker
async def getStickerLinkBySticker(event):
    if event.message.sticker is not None:
        for attr in event.message.sticker.attributes:
            if isinstance(attr, types.DocumentAttributeSticker):
                pack = await client(messages.GetStickerSetRequest(attr.stickerset, 0))
                shareStickerLink = "https://t.me/addstickers/" + pack.set.short_name
                await prosesStickerLink(event, shareStickerLink)   


# Membaca pesan sambil ambil linknya
async def scrapingLink(event, from_entity):
    from_entity = 'me' if from_entity == 1642531797 else from_entity
    link_pattern = r'(http(s)?:\/\/[^\]\)\s]+)'
    async for message in event.client.iter_messages(from_entity, reverse=True, from_user='me'):
        try:
            text = message.text
            links = re.findall(link_pattern, text)
            for link in links:
                await prosesTeleLink(event, link[0])
                await prosesStickerLink(event, link[0])

            await getStickerLinkBySticker(event)
        except: 
            print("# No text/link to proccess")
        
    print("# Done, no more link from " + str(from_entity))


# Meneruskan pesan media
async def mediaForwarder(event, from_entity, to_entity, reply_to):
    media_album = []
    album_id = None
    async for message in event.client.iter_messages(from_entity, reverse=True):
        if message.photo:
            print(event.grouped_id)
            if message.grouped_id != None:
                print(message.stringify())
                album_id = event.grouped_id
                media_album.append(message.photo)
            elif message.grouped_id != album_id:
                await event.client.send_file(to_entity, file=media_album, reply_to=reply_to)
                media_album = []
                album_id = event.grouped_id
                if message.grouped_id != None:
                    media_album.append(message.photo)
                else:
                    await event.client.send_file(to_entity, file=message.photo, reply_to=reply_to)
            else:
                if media_album:
                    await event.client.send_file(to_entity, file=media_album, reply_to=reply_to)
                    media_album = []
                await event.client.send_file(to_entity, file=message.photo, reply_to=reply_to)
        if message.video:
            print(event.grouped_id)
            if message.grouped_id != None:
                print(message.stringify())
                album_id = event.grouped_id
                media_album.append(message.video)
            elif message.grouped_id != album_id:
                await event.client.send_file(to_entity, file=media_album, reply_to=reply_to)
                media_album = []
                album_id = event.grouped_id
                if message.grouped_id != None:
                    media_album.append(message.video)
                else:
                    await event.client.send_file(to_entity, file=message.video, reply_to=reply_to)
            else:
                if media_album:
                    await event.client.send_file(to_entity, file=media_album, reply_to=reply_to)
                    media_album = []
                await event.client.send_file(to_entity, file=message.video, reply_to=reply_to)


# Cek user saat ini
async def checkUserValidity(event):
    user_id = await helper_db.getCurrUser(event)
    if event.is_private and user_id and not event.via_bot_id:
        return user_id
    
    return False


# Proses link dan download media jika link valid
async def prosesDownloadLink(event, link, reply_to):
    # Cek apakah link merupakan supported download link
    valid_download_link = await helper_menu.extract_link(link)
    if valid_download_link:
        # Mulai download media
        await downloading_media.download_from_supported_link(event, valid_download_link, parent_directory, 1901826075, reply_to)

        await event.client.delete_messages(1901826075, event.message)


# Proses link dan menambahkan ke database
async def prosesTeleLink(event, link):
    # Cek apakah link merupakan link join telegram
    valid_tele_link = await helper_menu.getJoinLink(link)
    if valid_tele_link:
        # Cek dan simpan link ke table
        tele_link_status = await helper_db.addLinktoDB(valid_tele_link, 'link_tele', 'linkJoins', 'link_tele')
        if tele_link_status:
            # Kirim link ke forum topic #sharink
            recipients = await helper_db.getRecipient('sharink')
            for receipient in recipients:
                await sending_message.sendingMessageTo(event, receipient[0], valid_tele_link, receipient[1])


# Prosesl link sticker dan menambahkan ke database
async def prosesStickerLink(event, link):
    # Cek apakah link merupakan link sticker
    valid_sticker_link = await helper_menu.getSticker(link)
    if valid_sticker_link:
        # Cek dan simpan link ke table
        sticker_link_status = await helper_db.addLinktoDB(valid_sticker_link, 'link_sticker', 'linkStickers', 'link_sticker')
        if sticker_link_status:
            # Kirim link ke forum topic #sticker
            recipients = await helper_db.getRecipient('sticker')
            for receipient in recipients:
                await sending_message.sendingMessageTo(event, receipient[0], valid_sticker_link, receipient[1])


# Menjalankan client
client.run_until_disconnected()
