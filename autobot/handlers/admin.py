from telethon import events

import config
from functions import menu_function as mefuc, send_message as send_msg
from . import client


# Mendaftarkan user sebagai admin
@events.register(events.NewMessage(pattern="/add me"))
async def handle_add_user(event):
    user_id = event.sender_id
    sndmsg = client.TeleClient.send_message_to_user(client.TeleClient, user_id)

    if event.is_private and not event.via_bot_id:
        func = mefuc.DML_handle(user_id)
        result = func.addUserAndSetting()

        sndmsg.message = "You have been given admin rights." if result else "You are already an admin"
        await send_msg.send_message_normal(event, sndmsg)


# Menampilkan daftar task
@events.register(events.NewMessage(pattern='/tasks'))
async def handle_tasks(event):
    user_id = event.sender_id
    sndmsg = client.TeleClient.send_message_to_user(client.TeleClient, user_id)
    func = mefuc.DML_handle(user_id)
    
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
        await send_msg.send_message_normal(event, sndmsg)


# Menambahkan task baru
@events.register(events.NewMessage(func=lambda event: event.message.text.startswith('/addtask')))
async def handle_add_task(event):
    user_id = event.sender_id
    sndmsg = client.TeleClient.send_message_to_user(client.TeleClient, user_id)
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
            await send_msg.send_message_normal(event, sndmsg)


# Menambahkan target pesan
@events.register(events.NewMessage(func=lambda event: event.message.text.startswith('/addrecipient')))
async def handle_add_recipient(event):
    user_id = event.sender_id
    sndmsg = client.TeleClient.send_message_to_user(client.TeleClient, user_id)
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
            await send_msg.send_message_normal(event, sndmsg)


# Menambahkan filter
@events.register(events.NewMessage(func=lambda event: event.message.text.startswith('/addfilter')))
async def handle_add_filter(event):
    user_id = event.sender_id
    sndmsg = client.TeleClient.send_message_to_user(client.TeleClient, user_id)
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
            
            await send_msg.send_message_normal(event, sndmsg)
