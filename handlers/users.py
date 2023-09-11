from telethon import events

import config as cfg
from functions import dml_func, nodml_func
from . import tele_client

client = tele_client.TeleClient()


# Show detailed help sections
async def section_help(section):
    if section == "task":
        message = (
            "**Task**\n\n"
            "**List of available commands** : \n"
            "Create a new task\n> `/addtask 1 2 3 4 5 6 7`\n> `/at 1 2 3 4 5 6 7`\n"
            "Show all existed tasks\n> `/tasks`\n"
            "Delete spesific task\n> `/deletetask 1`\n> `/dt 1`\n"
            "\n**Notes** : (1 - 7 = user input)\n"
            "1 : Task name [text]\n"
            "2 : Source [chat id | number]\n"
            "3 : Use this task [`yes` / `no`]\n"
            "4 : Reverse [**oldest** post to **latest** post | `1` / `0`]\n"
            "5 : Start from post [message id | number]\n"
            "6 : Limit message [number]\n"
            "7 : From who [**optional** | chat id | number]\n"
            "\n**Usage example** :\n"
            "`/addtask test1 123451 yes 1 0 10 4436283`\n"
            "`/at test1 123451 yes 1 0 10`\n"
            "`/tasks`\n"
            "`/deletetask test1`\n"
            "`/dt test1`\n"
            "\n#help #task"
        )
    elif section == "recipient":
        message = (
            "**Recipient**\n\n"
        )
    else:
        message = f"No section found with keyword {section}"
        
    return message


# Checking and adding current user to users table
@events.register(events.NewMessage(pattern="/add me"))
async def handle_add_user(event):
    chat_id = event.sender_id
    sndmsg = client.send_message_to_user(chat_id)
    dml = dml_func.DMLHandle(chat_id)
    nodml = nodml_func.NoDMLFunctions(event)

    if event.is_private and not event.via_bot_id:
        input_user = event.message.text.strip().split()
        phone_no = None
        if len (input_user) > 2 and input_user[0] == "/add":
            _, *number = input_user[1:]
            if number: 
                phone_no = number[0] 
                await nodml.add_to_contact(phone_no)
            else:
                phone_no = None

        user_data = cfg.UserAdmin(chat_id, phone_no)
        result = dml.add_new_admin(user_data)
        message = "You have been given admin rights." if result else "You are already an admin"

        sndmsg.message = message
        await nodml.send_message_normal(sndmsg)


# Change user setting
@events.register(events.NewMessage(pattern="/(settings|s)"))
async def handle_change_setting(event):
    chat_id = event.sender_id
    sndmsg = client.send_message_to_user(chat_id)
    dml = dml_func.DMLHandle(chat_id)
    nodml = nodml_func.NoDMLFunctions(event)

    if dml.check_user():
        input_user = event.message.text.strip().split()
        if len(input_user) == 5 and (input_user[0] == "/setting" or input_user[0] == "/s"):
            caption, text, ftypes, delay = input_user[1:]

            if ftypes.lower() != "blacklist" and ftypes.lower() != "whitelist":
                ftypes = "No"

            sett_data = cfg.UserSetting()
            sett_data.use_caption = caption
            sett_data.use_filter_text = text
            sett_data.use_filter_type = ftypes
            sett_data.delay = delay

            dml.update_setting(sett_data)
            sndmsg.message = "Setting updated"
        else:
            sndmsg.message = await nodml.show_settings()

        await nodml.send_message_normal(sndmsg)


# Help user to get id
@events.register(events.NewMessage(pattern="/id"))
async def handle_get_id(event):
    chat_id = event.sender_id
    sndmsg = client.send_message_to_user(chat_id)
    dml = dml_func.DMLHandle(chat_id)
    nodml = nodml_func.NoDMLFunctions(event)
    
    if dml.check_user() and event.is_reply:
        reply_msg = await event.get_reply_message()
        sender = await nodml.get_sender_id(reply_msg)

        message = "**Message Data**\n\n"
        message += (
            f"**Sender**\n{sender['username']}"
            f"Chat ID : `{sender['chat_id']}`\n"
            f"User ID : `{sender['user_id']}`\n"
            f"Message ID : `{sender['message_id']}`\n" # ID pesan di chatnya bukan di channelnya
        )

        try:
            forwarded = await nodml.get_forwarded_id(reply_msg)
            message += (
                f"\n**Forwarded from**\n{forwarded['username']}"
                f"ID : `{forwarded['id']}`\n"
                f"Name : `{forwarded['name']}`\n"
                f"{forwarded['message_id']}\n" # ID pesan di chatnya bukan di channelnya
            )
        except:
            message += (
                f"\n**Forwarded from**\nPrivate Chat\n"
            )

        sndmsg.message = message
        await nodml.send_message_normal(sndmsg)
    

# Show help message
@events.register(events.NewMessage(pattern="/(help|h)"))
async def handle_show_help(event):
    chat_id = event.sender_id
    sndmsg = client.send_message_to_user(chat_id)
    dml = dml_func.DMLHandle(chat_id)
    nodml = nodml_func.NoDMLFunctions(event)

    if dml.check_user():
        input_user = event.message.text.strip().split()
        if len(input_user) == 1 and (input_user[0] == "/help" or input_user[0] == "/h"):
            message = "**Help**\n\n"
            message += (
                "**Sections**:\n"
                "- `Task`\n"
                "- `Recipient`\n"
                "- `Filter`\n"
                "- `Setting`\n"
                "\n"
                "To learn more about any of these sections, \n"
                "simply send `/help [section name]`.\n"
            )
        elif len(input_user) > 1 and (input_user[0] == "/help" or input_user[0] == "/h"):
            section_str = input_user[1]

            section = section_str.lower()
            message = await section_help(section)

        sndmsg.message = message
        await nodml.send_message_normal(sndmsg)


