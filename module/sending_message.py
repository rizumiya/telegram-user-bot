from telethon.tl.functions import messages
import os


async def sendingMessageTo(event, toWho, message, reply_to):
    request = messages.SendMessageRequest(
        peer=toWho,
        message=message,
        noforwards=True,
        reply_to_msg_id=reply_to,
        silent=True,
        background=True,
    )

    await event.client(request)


async def sendingMediaTo(event, toWho, message, reply_to):
    name = None
    if message.chat:
        name = message.chat.title
    elif message.sender:
        name = message.sender.first_name

    request = messages.SendMediaRequest(
        peer=toWho,
        media=message,
        message=f'Original source : '+ name,
        noforwards=True,
        reply_to_msg_id=reply_to,
        silent=True,
        background=True,
    )

    await event.client(request)
