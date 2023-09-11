from telethon import events

import config as cfg
from . import tele_client
from functions import dml_func, nodml_func

client = tele_client.TeleClient()


# Add new task
@events.register(events.NewMessage(pattern="/(addtask|at)"))
async def handle_add_task(event):
    chat_id = event.sender_id
    sndmsg = client.send_message_to_user(chat_id)
    dml = dml_func.DMLHandle(chat_id)
    nodml = nodml_func.NoDMLFunctions(event)

    if dml.check_user():
        input_user = event.message.text.strip().split()
        if len(input_user) >= 7 and (input_user[0] == "/addtask" or input_user[0] == "/at"):
            conn_name, source, use_this_str, reverse, min_id, limit, *from_entity = input_user[1:]
            # try:
            from_user = from_entity[0] if from_entity else None
            use_this = 1 if use_this_str.lower() == "yes" else 0
            limit = int(limit) if limit != 0 else None

            new_task = cfg.Task(conn_name, source, use_this, reverse, min_id, limit)
            new_task.from_user = from_user

            try:
                if new_task.source.startswith("-"):
                    new_task.source = int(new_task.source)
            except:
                new_task.source = new_task.source

            source_entity = await event.client.get_entity(new_task.source)

            if source_entity:
                message = f"New task **{conn_name}** added" if dml.add_new_task(new_task) else f"Task **{conn_name}** already exists"
            else:
                message = "Invalid source"
            # except:
            #     message = "Format error please refer to /help or /h"
        else:
            message = "Format error please refer to /help or /h"

        sndmsg.message = message
        await nodml.send_message_normal(sndmsg)


# Delete existed task
@events.register(events.NewMessage(pattern="/(deletetask|dt)"))
async def handle_delete_task(event):
    chat_id = event.sender_id
    sndmsg = client.send_message_to_user(chat_id)
    dml = dml_func.DMLHandle(chat_id)
    nodml = nodml_func.NoDMLFunctions(event)

    if dml.check_user():
        input_user = event.message.text.strip().split()
        if len(input_user) == 2 and (input_user[0] == "/deletetask" or input_user[0] == "/dt"):
            conn_name = input_user[1]
            
            message = f"Task **{conn_name}** and all its recipients deleted" if dml.delete_task(conn_name) else f"Task **{conn_name}** not found"
        else:
            message = "Format error please refer to /help or /h"

        sndmsg.message = message
        await nodml.send_message_normal(sndmsg)


# Show all tasks
@events.register(events.NewMessage(pattern="/tasks"))
async def handle_showall_task(event):
    chat_id = event.sender_id
    sndmsg = client.send_message_to_user(chat_id)
    dml = dml_func.DMLHandle(chat_id)
    nodml = nodml_func.NoDMLFunctions(event)

    if dml.check_user():
        tasks = dml.get_task(None)
        if not tasks:
            message = "**Current Task**\n\nNo Task"
        else:
            message = f"**Current Tasks**\n\n"
            for task in tasks:
                use_this = "yes" if task[4] == 1 else "no"
                reverse = "yes" if task[5] == 1 else "no"
                message += (
                    f"Task Name : `{task[2]}`\n"
                    f"Source : `{task[3]}`\n"
                    f"Use this : **{use_this}**\n"
                    f"Reverse : **{reverse}**\n"
                    f"Min ID : __{task[6]}__\n"
                    f"Limit : **{task[7]}**\n"
                    f"From user : {task[8]}\n"
                    f"- - - - - - - - - - - - - - -\n"
                )
            
        sndmsg.message = message
        await nodml.send_message_normal(sndmsg)


# Run task
@events.register(events.NewMessage(pattern="/run"))
async def handle_run_task(event):
    chat_id = event.sender_id
    sndmsg = client.send_message_to_user(chat_id)
    dml = dml_func.DMLHandle(chat_id)
    nodml = nodml_func.NoDMLFunctions(event)

    if dml.check_user():
        input_user = event.message.text.strip().split()
        if len(input_user) == 2 and input_user[0] == "/run":
            conn_name = input_user[1]
            task_detail = dml.get_task(conn_name)
            if task_detail:
                message = f"Stopping task {conn_name}.."
                await nodml.run_spesific_task(task_detail[0], 0)
            else:
                message = f"No task with name {conn_name}"
        elif len(input_user) == 1 and input_user[0] == "/run":
            message = "Running all task.."
        else:
            message = "Format error please refer to /help or /h"
        
        sndmsg.message = message
        await nodml.send_message_normal(sndmsg)


# Add task for link
@events.register(events.NewMessage(pattern="/fwdlink"))
async def handle_forward_link(event):
    print("forward link")


