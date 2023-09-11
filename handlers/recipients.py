from telethon import events

from functions import dml_func, nodml_func
from . import tele_client
import config as cfg

client = tele_client.TeleClient()


# Add new recipient for task
@events.register(events.NewMessage(pattern="/(addrecipient|ar)"))
async def handle_add_recipient(event):
    chat_id = event.sender_id
    sndmsg = client.send_message_to_user(chat_id)
    dml = dml_func.DMLHandle(chat_id)
    nodml = nodml_func.NoDMLFunctions(event)

    if dml.check_user():
        input_user = event.message.text.strip().split()
        if len(input_user) >= 3 and len(input_user) < 5 and (input_user[0] == "/addrecipient" or input_user[0] == "/ar"):
            conn_name, to_entity, *reply_to = input_user[1:]
            task_exists = dml.get_task(conn_name)
            
            reply_to = reply_to[0] if reply_to and reply_to[0] != 0 else None
            rec = cfg.TaskRecipient(conn_name, to_entity, reply_to)

            try:
                to_entity = await event.client.get_entity(rec.to_entity)
            except:
                to_entity = None

            if task_exists and to_entity:
                dml.add_new_recipient(task_exists[0][0], rec)

                try:
                    name = to_entity.first_name  
                except:
                    name = to_entity.title

                message = f"New recipient **{name}** for task **{conn_name}** added"
            elif not task_exists:
                message = f"No task with name **{conn_name}** found"
            else:
                message = "Error! I'm not inside the group or the channel"
        else:
            message = "Format error please refer to /help or /h"

        sndmsg.message = message
        await nodml.send_message_normal(sndmsg)


# Get all recipient for task
@events.register(events.NewMessage(pattern="/(recipients|re)"))
async def handle_get_recipient(event):
    chat_id = event.sender_id
    sndmsg = client.send_message_to_user(chat_id)
    dml = dml_func.DMLHandle(chat_id)
    nodml = nodml_func.NoDMLFunctions(event)

    if dml.check_user():
        input_user = event.message.text.strip().split()
        if len(input_user) == 2 and (input_user[0] == "/recipients" or input_user[0] == "/re"):
            conn_name = input_user[1]
            task_exists = dml.get_task(conn_name)

            if task_exists:
                recis = dml.get_recipient(task_exists[0][0])
                message = f"**Recipients for task {conn_name}**\n\n"
                if message:
                    for reci in recis:
                        reply_to = f"reply to id **{reci[3]}**\n" if reci[3] else "\n"
                        message += f"- **{reci[2]}** {reply_to}"
                else:
                    message = f"**No recipient for task {conn_name}**\n\n"
            else:
                message = f"No task with name {conn_name}"
        else:
            message = "Format error please refer to /help or /h"
            
        sndmsg.message = message
        await nodml.send_message_normal(sndmsg)


# Remove recipient from task
@events.register(events.NewMessage(pattern="/(deleterecipient|dr)"))
async def handle_delete_recipient(event):
    chat_id = event.sender_id
    sndmsg = client.send_message_to_user(chat_id)
    dml = dml_func.DMLHandle(chat_id)
    nodml = nodml_func.NoDMLFunctions(event)

    if dml.check_user():
        input_user = event.message.text.strip().split()
        if len(input_user) == 2 and (input_user[0] == "/deleterecipient" or input_user[0] == "/dr"):
            conn_name = input_user[1]
            task_exists = dml.get_task(conn_name)

            if task_exists:
                dml.delete_recipient(task_exists[0][0])
                message = f"**All** recipients for task **{conn_name}** deleted"
            else:
                message = f"No task with name {conn_name}"
        else:
            message = "Format error please refer to /help or /h"
            
        sndmsg.message = message
        await nodml.send_message_normal(sndmsg)

    

