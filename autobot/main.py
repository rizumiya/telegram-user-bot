from functions import database_helper as dbh, menu_function as mefuc, grab_link
from functions import send_message, turn_anon, download_media
from datas import storage, database
import config

from telethon import TelegramClient, events
from telethon.errors import FloodWaitError

import asyncio
import os
import re


# Inisialisasi User
api_id = config.API_ID
api_hash = config.API_HASH
session = config.SESSION
phone_no = config.PHONE_NUMBER

# Mendaftarkan client
client = TelegramClient(session, api_id, api_hash).start(phone_no)

# Ambil direktori saat ini
current_dir = os.path.dirname(os.path.abspath(__file__))

# Event Handler

# Menambahkan user jika belum terdaftar
@client.on(events.NewMessage(pattern="/add me"))
async def handle_add_user(event):
    user_id = event.sender_id
    sndmsg = config.SendMessage(user_id, None, None, False, None)

    if event.is_private and not event.via_bot_id:
        func = mefuc.DML_handle(user_id)
        result = func.addUserAndSetting()

        sndmsg.message = "You have been given admin rights." if result else "You are already an admin"
        await send_message.send_message_normal(event, sndmsg)


# Menambahkan task
@client.on(events.NewMessage(func=lambda event: event.message.text.startswith('/addtask')))
async def handle_add_task(event):
    user_id = event.sender_id
    sndmsg = config.SendMessage(user_id, None, None, False, None)
    func = mefuc.DML_handle(user_id)
    
    if func.checkUser():
        input_user = event.message.text.strip().split()
        if len(input_user) >= 7 and input_user[0] == '/addtask':
            conn_name, from_entity, use_this, old_live, min_id, limit, *from_user = input_user[1:]
            # Default nilai jika input user bermasalah
            from_user = from_user[0] if from_user else None
            use_this = 1 if use_this and use_this[0] == "yes" else 0
            limit = limit[0] if limit != 0 else 0

            task = config.NewTask(conn_name, old_live, from_entity, use_this, min_id, limit)
            task.from_user = from_user
            
            result = func.addNewTask(task)
            sndmsg.message = f"New task **{conn_name}** added" if result else f"Task **{conn_name}** already exists"
            await send_message.send_message_normal(event, sndmsg)


# Menampilkan daftar task
@client.on(events.NewMessage(pattern='/tasks'))
async def handle_tasks(event):
    user_id = event.sender_id
    sndmsg = config.SendMessage(user_id, None, None, False, None)
    func = mefuc.DML_handle(user_id)
    ["ut.id", "ut.use_this", "ut.old_live",
                          "ut.status", "dt.conn_name", 
                          "dt.task_from", "dt.task_from_user",
                          "dt.task_min_id", "dt.task_limit"]
    if func.checkUser():
        tasks = func.getCurrTasks()
        if not tasks:
            sndmsg.message = "**Current Task**\n\nNo Task"
        else:
            tasks = tasks[0]
            use_this = "yes" if tasks[1] == 1 else "no"
            sndmsg.message = (
                f"**Current Task**\n\n"
                f"Task Name : `{tasks[4]}`\n"
                f"From Entity : __{tasks[5]}__\n"
                f"Task Type : **{tasks[2]}**\n"
                f"Use This : **{use_this}**\n"
                f"Status : {tasks[3]}\n"
                f"- - - - - - - - - - - - - -\n"
                )
        await send_message.send_message_normal(event, sndmsg)


# Menambahkan target pesan
@client.on(events.NewMessage(func=lambda event: event.message.text.startswith('/addrecipient')))
async def handle_add_recipient(event):
    user_id = event.sender_id
    sndmsg = config.SendMessage(user_id, None, None, False, None)
    func = mefuc.DML_handle(user_id)

    if func.checkUser():
        input_user = event.message.text.strip().split()
        if len(input_user) >= 3 and input_user[0] == '/addrecipient':
            conn_name, to_user, *reply_to = input_user[1:]
            # Default nilai jika input user bermasalah
            reply_to = reply_to[0] if reply_to and reply_to[0] != 0 else None

            recipient = config.TaskRecipient(conn_name, to_user, reply_to)
            result = func.addNewRecipient(recipient)
            sndmsg.message = f"New recipient **{to_user}** for task **{conn_name}** added" if result else f"No task with name **{conn_name}**"
            await send_message.send_message_normal(event, sndmsg)


# Menambahkan filter
@client.on(events.NewMessage(func=lambda event: event.message.text.startswith('/addfilter')))
async def handle_add_filter(event):
    user_id = event.sender_id
    sndmsg = config.SendMessage(user_id, None, None, False, None)
    func = mefuc.DML_handle(user_id)
    formattext = False

    if func.checkUser():
        input_user = event.message.text.strip().split()
        if len(input_user) >= 3 and input_user[0] == '/addfilter':
            filter_name, regext, *text_list  = input_user[1:]

            if filter_name == "text":
                regext = 1 if regext == "yes" else 0
                texts = ' '.join(text_list) if text_list else "."
                fltr = config.Filter(filter_type=filter_name, regex=regext, text=texts)
                formattext = True
            else:
                sndmsg.message = f"Choose only text / type"

            if formattext:
                result = func.addNewFilter(filter_name, fltr)
                sndmsg.message = f"New filter added" if result else f"Filter already exists"
            
            await send_message.send_message_normal(event, sndmsg)


# Mengubah use this task
@client.on(events.NewMessage(func=lambda event: event.message.text.startswith('/use')))
async def handle_use(event):
    user_id = event.sender_id
    sndmsg = config.SendMessage(user_id, None, None, False, None)
    func = mefuc.DML_handle(user_id)

    if func.checkUser():
        input_user = event.message.text.strip().split()
        if len(input_user) >= 3 and input_user[0] == '/use':
            kind, connName_filterno, *conn_name = input_user[1:]
            conn_name = conn_name[0] if conn_name else None

            result = func.updateTaskorFilter(kind, connName_filterno, conn_name)
            sndmsg.message = f"{kind} Updated" if result else f"Error, cannot use {kind}"
            await send_message.send_message_normal(event, sndmsg)


# Menjalankan seluruh task
@client.on(events.NewMessage(func=lambda event: event.message.text.startswith('/run')))
async def handle_run(event):
    user_id = event.sender_id
    sndmsg = config.SendMessage(user_id, None, None, False, None)
    func = mefuc.DML_handle(user_id)
    func2 = mefuc.NoDML(user_id)
    
    if func.checkUser():
        input_user = event.message.text.strip().split()
        if len(input_user) >= 1 and input_user[0] == '/run':
            task_name = input_user[1] if input_user else None
            runtask = func.getTaskFromConn_Name(task_name)
            print(runtask)

            tasks = config.NewTask(runtask[1], runtask[2], runtask[3], 1, runtask[5], runtask[6])
            tasks.from_user = runtask[3]

            func2.runTask(tasks)
            func.changeRunVal()


async def run_task_user(event):
    print("a")















# # Menampilkan list task saat ini untuk user saat ini
# @client.on(events.NewMessage(func=lambda event: event.message.text.startswith('/run')))
# async def handle_runTask(event):
#     if await menu_function.checkUserValidity(event):
#         user_id = event.sender_id
#         msg = default_simple_message(user_id)

#         texts = event.message.text.strip().split()
#         if len(texts) >= 1 and texts[0] == '/run':
#             try:
#                 task_name = texts[1]
#             except:
#                 task_name = None
#             tasksList = menu_function.getAutorunTask(task_name, user_id)
#             menu_function.turnOnOffRun(user_id)
#             if tasksList: 
#                 # Memulai proses running task
#                 for task in tasksList:
#                     if task[5] != 'forward live' or task[5] != 'grab link live':
#                         tsk = new_task(task)
#                         await runTask(event, tsk, task[5])
#                     else:
#                         tsk = new_task(task)

#             else:
#                 msg.message = "No task to run\n`/run` only run task with **Specified : Yes** and **Use This : Yes**"
#                 await send_message.send_message_normal(event, msg)






            
                

# # Menampilkan daftar task
# @client.on(events.NewMessage(pattern='/tasks'))
# async def handle_backup(event):
#     user_id = event.sender_id
#     sndmsg = config.SendMessage(user_id, None, None, False, None)

#     if mefuc.checkCurrentUser(user_id):
#         db_task = dbhlp.DB_Task()
#         db_task.user_id = user_id
#         tasks = db_task.getTaskFromUser()
#         print(tasks)
#         if not tasks:
#             sndmsg.message = "**Current Task**\n\nNo Task"
#         else:
#             tasks = tasks[0]
#             use_this = "yes" if tasks[2] == 1 else "no"
#             sndmsg.message = (
#                 f"**Current Task**\n\n"
#                 f"Task Name : `{tasks[4]}`\n"
#                 f"Use This : **{use_this}**\n"
#                 f"Status : {tasks[3]}\n"
#                 f"- - - - - - - - - - - - - -\n"
#                 )
#         await send_message.send_message_normal(event, sndmsg)
        










# # Menghentikan koneksi
# @client.on(events.NewMessage(pattern='/stop'))
# async def handle_stopndisconn(event):
#     if await menu_function.checkUserValidity(event):
#         menu_function.turnOnOffRun(event.sender_id)
#         file_path = os.path.join(storage.getCurrDir(), 'export_db.txt')
#         database.export_all_tables_to_txt('autobot.db', file_path)
#         print("# Database exported")


# # Menggunakan task untuk autorun
# @client.on(events.NewMessage(func=lambda event: event.message.text.startswith('/use')))
# async def handle_usetasks(event):
#     if await menu_function.checkUserValidity(event):
#         user_id = event.sender_id
#         msg = default_simple_message(user_id)

#         text = event.message.text.strip().split()
#         if len(text) >= 2 and text[0] == '/use':
#             conn_name = text[1]
#             if menu_function.editUseTaskValue(conn_name, event.sender_id):
#                 msg.message = f"Success, **{conn_name}** updated"
#             else:
#                 msg.message = f"No task with name **{conn_name}** found"
#             await send_message.send_message_normal(event, msg)


# # Mengambil link dari entity yang di inputkan dan mengirimkannya ke target tertentu
# @client.on(events.NewMessage(func=lambda event: event.message.text.startswith('/addtask')))
# async def handle_addgrablinktask(event):
#     if await menu_function.checkUserValidity(event):
#         user_id = event.sender_id
#         msg = default_simple_message(user_id)

#         text = event.message.text.strip().split()
#         if len(text) >= 4 and text[0] == '/addtask':
#             task_type, task_behav, task_name, *use_this = text[1:]
#             use_this = 1 if use_this and use_this[0] == 'yes' else 0
#             menu_function.checkNewTask(task_type, task_behav, task_name, use_this, user_id)

#             # Mengirim pesan list task saat ini
#             msg.message = (
#                 f"New task created : **{task_name}**\n"
#                 "Now send me `/specify task_name from_chat to_chat reply_to offset limit *from_user`\n"
#                 "Send `/tasks` to see current tasks list"
#                 )
#             await send_message.send_message_normal(event, msg)


# # Mengedit detail task yang sudah dibuat
# @client.on(events.NewMessage(func=lambda event: event.message.text.startswith('/specify')))
# async def handle_grablink(event):
#     if await menu_function.checkUserValidity(event):
#         texts = event.message.text.strip().split()
#         if len(texts) >= 4 and texts[0] == '/specify':
#             conn_name, task_chat, task_to, task_reply_to, task_min_id, task_limit, *task_from_user = texts[1:]
#             task_from_user = task_from_user[0] if task_from_user else task_chat
#             task_reply_to = task_reply_to[0] if task_reply_to != "0" else None
#             task_limit = task_limit[0] if task_limit != "0" else None
            
#             # /grablink nama from to reply min_id limit user
#             tsk = config.NewTask()
#             tsk.conn_name = conn_name
#             tsk.from_entity = menu_function.is_input_digit(task_chat)
#             tsk.from_user = menu_function.is_input_digit(task_from_user)
#             tsk.entity = menu_function.is_input_digit(task_to)
#             tsk.reply_to = menu_function.is_input_digit(task_reply_to)
#             tsk.min_id = menu_function.is_input_digit(task_min_id)
#             tsk.limit = menu_function.is_input_digit(task_limit)

#             if menu_function.specifyTask(tsk):
#                 tsk.message = (
#                     f"**{conn_name}** updated\n"
#                     f"Send `/run {conn_name}` to run **this** task or \n"
#                     "Send `/run` to run **all specified** task with **Use This = Yes**\n"
#                     "To change __Use This__ value, simply send `/use [task name]`"
#                 )
#                 tsk.entity = event.sender_id
#                 await send_message.send_message_normal(event, tsk)




# # Menjalankan task
# async def runTask(event, tsk, type_name):
#     try:
#         min_id = database_helper.getDataFromTable('task_min_id', 'detailed_tasks', 'conn_name', tsk.conn_name)
#         tsk.min_id = min_id[0][0]
#         messages = await client.get_messages(tsk.from_entity, limit=1)
#         last_message_id = messages[0].id

#         async for message in event.client.iter_messages(tsk.from_entity, reverse=True, from_user=tsk.from_user, min_id=tsk.min_id, limit=tsk.limit, offset_id=0, max_id=0):
#             try:
#                 print(message.id)
#                 print(last_message_id)
#                 run = menu_function.checkRunTask(event.sender_id)
#                 if run[0] == 1:
#                     if type_name == 'grab link old':
#                         await runGrabLink(event, message, tsk)
#                     if message.id == last_message_id:
#                         tsk.message = f'Task **{tsk.conn_name}** completed'
#                         await send_message.send_message_normal(event, tsk)
#                         database_helper.editValueFromTable('detailed_tasks', 
#                                     'task_status=?', 
#                                     'conn_name=?', 
#                                     ('completed', tsk.conn_name))

#                 # Jika koneksi terhenti, hentikan pengambilan pesan 
#                 if not client.is_connected():
#                     break
#             except FloodWaitError as e:
#                 # Handle the FloodWaitError
#                 print("FloodWaitError occurred. Sleeping for {} seconds.".format(e.seconds))
#                 await asyncio.sleep(e.seconds)
#                 continue
#             except Exception as e: 
#                 print(f"# Error | No content to proccess : {e}")
#         print(f"# Done forwarding content from {tsk.from_entity}")
#     except Exception as e:
#         print(f"# Error | Invalid entity : {e}")


# # Menjalankan grablink
# async def runGrabLink(event, message, tsk):
#     text = message.text
#     tsk.min_id = message.id
#     link_pattern = r'(http(s)?:\/\/[^\]\)\s]+)'
#     database_helper.editValueFromTable('detailed_tasks', 
#                                     'task_min_id=?', 
#                                     'conn_name=?', 
#                                     (tsk.min_id, tsk.conn_name))
    
#     links = re.findall(link_pattern, text)

#     for link in links:
#         await prosesTeleLink(event, link[0], tsk)
        
#         if not client.is_connected():
#             break
#         # await prosesStickerLink(event, link[0], tsk)

#     # await getStickerLinkBySticker(event)


# # Proses link dan menambahkan ke database
# async def prosesTeleLink(event, link, tsk):
#     # Cek apakah link merupakan link join telegram
#     valid_tele_link = await grab_link.getJoinLink(link)
#     if valid_tele_link:
#         # Cek dan simpan link ke table
#         if grab_link.addLinktoDB(link, 'link join'):
#             # Kirim link ke forum topic #sharink
#             tsk.message = valid_tele_link
#             await send_message.send_message_normal(event, tsk)


# # Prosesl link sticker dan menambahkan ke database
# async def prosesStickerLink(event, link):
#     # Cek apakah link merupakan link sticker
#     valid_sticker_link = await grab_link.getSticker(link)
#     if valid_sticker_link:
#         # Cek dan simpan link ke table
#         sticker_link_status = await database_helper.addLinktoDB(valid_sticker_link, 'link_sticker', 'linkStickers', 'link_sticker')
#         if sticker_link_status:
#             # Kirim link ke forum topic #sticker
#             recipients = await helper_db.getRecipient('sticker')
#             for receipient in recipients:
#                 await sending_message.sendingMessageTo(event, receipient[0], valid_sticker_link, receipient[1])

# # # Ambil sticker link dari sticker
# # async def getStickerLinkBySticker(event):
# #     if event.message.sticker is not None:
# #         for attr in event.message.sticker.attributes:
# #             if isinstance(attr, types.DocumentAttributeSticker):
# #                 pack = await client(messages.GetStickerSetRequest(attr.stickerset, 0))
# #                 shareStickerLink = "https://t.me/addstickers/" + pack.set.short_name
# #                 await prosesStickerLink(event, shareStickerLink) 


# def new_task(task):
#     tsk = config.NewTask()
#     tsk.from_entity = menu_function.is_input_digit(task[6])
#     tsk.entity = menu_function.is_input_digit(task[7])
#     tsk.from_user = menu_function.is_input_digit(task[8])
#     tsk.from_user = 'me' if task[8] == 1642531797 else tsk.from_user
#     tsk.reply_to = menu_function.is_input_digit(task[9])

#     tsk.conn_name = task[4]
#     tsk.message = ""
#     tsk.min_id = task[10] 
#     tsk.limit = task[11] 
#     tsk.status = task[12] 
#     tsk.link_preview = False
#     return tsk


# Menjalankan client
client.run_until_disconnected()