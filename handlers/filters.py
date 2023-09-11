from telethon import events

from . import tele_client
from functions import dml_func, nodml_func

client = tele_client.TeleClient()


# Show all filters (type) => photo, video, etc.
@events.register(events.NewMessage(pattern="/filters"))
async def handle_showall_filter(event):
    chat_id = event.sender_id
    sndmsg = client.send_message_to_user(chat_id)
    dml = dml_func.DMLHandle(chat_id)
    nodml = nodml_func.NoDMLFunctions(event)

    if dml.check_user():
        whitelists = dml.get_whitelist()
        if not whitelists:
            message = "**Whitelist Filter**\n\nNo Filter\n"
        else:
            message = "**Whitelist Filters**\n\n"
            for whitelist in whitelists:
                message += (
                    f"- {whitelist[2]}\n"
                )
        blacklists = dml.get_blacklist()
        if not blacklists:
            message += "\n**Blacklist Filter**\n\nNo Filter\n"
        else:
            message += "\n**Blacklist Filters**\n\n"
            for whitelist in blacklists:
                message += (
                    f"- {whitelist[2]}\n"
                )
        text_blacklists = dml.get_blacklist_text()
        if not text_blacklists:
            message += "\n**Blacklist Texts**\n\nNo Text\n"
        else:
            message += "\n**Blacklist Texts**\n\n"
            for text in text_blacklists:
                message += (
                    f"- {text[2]}\n"
                )

        sndmsg.message = message
        await nodml.send_message_normal(sndmsg)


# Add new whitelist (type) => photo, video, etc.
@events.register(events.NewMessage(pattern="/(addwhitelist|aw)"))
async def handle_add_whitelist(event):
    chat_id = event.sender_id
    sndmsg = client.send_message_to_user(chat_id)
    dml = dml_func.DMLHandle(chat_id)
    nodml = nodml_func.NoDMLFunctions(event)

    if dml.check_user():
        input_user = event.message.text.strip().split()
        if len(input_user) >= 2 and (input_user[0] == "/addwhitelist" or input_user[0] == "/aw"):
            filters = input_user[1:]

            filter_acc = []
            for filter in filters:
                dml.add_wl_filter(filter)
                blist_exist = dml.check_blacklist_filter(filter)
                if blist_exist:
                    message = f"Something is wrong, {filter} already existed in blacklist\n"
                else:
                    message = f"Filter with type "
                    filter_acc.append(filter)
            
            message += ', '.join(filter_acc)
            message += " added to whitelist" if len(filter_acc) != 0 else ""
        else:
            message = "Format error please refer to /help or /h"
        
        sndmsg.message = message
        await nodml.send_message_normal(sndmsg)


# Remove spesific whitelist / type
@events.register(events.NewMessage(pattern="/(delwhitelist|dw)"))
async def handle_delete_whitelist(event):
    chat_id = event.sender_id
    sndmsg = client.send_message_to_user(chat_id)
    dml = dml_func.DMLHandle(chat_id)
    nodml = nodml_func.NoDMLFunctions(event)

    if dml.check_user():
        input_user = event.message.text.strip().split()
        if len(input_user) >= 2 and (input_user[0] == "/delwhitelist" or input_user[0] == "/dw"):
            filters = input_user[1:]
            filter_acc = []

            for filter in filters:
                if dml.check_whitelist_filter(filter):
                    if dml.delete_whitelist_filter(filter):
                        filter_acc.append(filter)
            message = ', '.join(filter_acc) + ' removed from whitelist'
        else:
            message = "Format error please refer to /help or /h"

        sndmsg.message = message
        await nodml.send_message_normal(sndmsg)


# Add new blacklist (text) => "Hello World".
@events.register(events.NewMessage(pattern="/(addblacklist|ab)"))
async def handle_add_blacklist(event):
    chat_id = event.sender_id
    sndmsg = client.send_message_to_user(chat_id)
    dml = dml_func.DMLHandle(chat_id)
    nodml = nodml_func.NoDMLFunctions(event)

    if dml.check_user():
        input_user = event.message.text.strip().split()
        if len(input_user) >= 2 and (input_user[0] == "/addblacklist" or input_user[0] == "/ab"):
            filters = input_user[1:]
            argument = await nodml.get_text_petik(input_user)

            if filters[0].startswith('"'):
                dml.add_bl_filter(argument, "text")
                message = f'Text "{argument}" added to the blacklist'
            elif not filters[0].startswith('"'):
                filter_acc = []
                for filter in filters:
                    dml.add_bl_filter(filter, "type")
                    wlist_exist = dml.check_whitelist_filter(filter)
                    if wlist_exist:
                        message = f"Something is wrong, {filter} already existed in whitelist\n"
                    else:
                        message = f"Filter with type "
                        filter_acc.append(filter)
                message += ', '.join(filter_acc)
                message += " added to blacklist" if len(filter_acc) != 0 else ""
            else:
                message = "Format error please refer to /help or /h"
        else:
            message = "Format error please refer to /help or /h"
        
        sndmsg.message = message
        await nodml.send_message_normal(sndmsg)


# Remove spesific blacklist / type
@events.register(events.NewMessage(pattern="/(delblacklist|db)"))
async def handle_delete_blacklist(event):
    chat_id = event.sender_id
    sndmsg = client.send_message_to_user(chat_id)
    dml = dml_func.DMLHandle(chat_id)
    nodml = nodml_func.NoDMLFunctions(event)

    if dml.check_user():
        input_user = event.message.text.strip().split()
        if len(input_user) >= 2 and (input_user[0] == "/delblacklist" or input_user[0] == "/db"):
            filters = input_user[1:]
            filter_acc = []
            argument = await nodml.get_text_petik(input_user)

            if filters[0].startswith('"'):
                if dml.check_blacklist_text(argument):
                    if dml.delete_blacklist(argument, "text"):
                        message = f'Text "{argument}" removed from blacklist'
                else:
                    message = f'Text {argument} not found'
            elif not filters[0].startswith('"'):
                for filter in filters:
                    if dml.check_blacklist_filter(filter):
                        if dml.delete_blacklist(filter, "type"):
                            filter_acc.append(filter)
                message = ', '.join(filter_acc) + ' removed from blacklist'
            else:
                message = "Format error please refer to /help or /h"
        else:
            message = "Format error please refer to /help or /h"

        sndmsg.message = message
        await nodml.send_message_normal(sndmsg)


