
# Mengirim pesan dengan cara biasa
async def send_message_normal(event, msg):
    try:
        await event.client.send_message(
            entity=msg.entity,
            message=msg.message,
            reply_to=msg.reply_to,
            silent=True,
            background=True
        )
        print("# Success | Message delivered to " + str(msg.entity))
    except:
        print("# Error | Unable to send the message")


# Mengirim media dengan cara biasa
async def send_media_normal(event, msg):
    try:
        await event.client.send_file(
            entity=msg.entity,
            file=msg.file,
            caption=msg.message,
            reply_to=msg.reply_to,
            silent=True,
            background=True
        )
        print("# Success | Files delivered to " + str(msg.entity))
    except:
        print("# Error | Unable to send the file")