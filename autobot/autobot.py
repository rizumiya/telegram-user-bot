from telethon import client
from handlers import client, admin

client = client.TeleClient()
client = client.connect_acc(True)

with client as ttloli:
    ttloli.add_event_handler(admin.handle_add_user)
    ttloli.add_event_handler(admin.handle_tasks)
    ttloli.add_event_handler(admin.handle_add_task)
    ttloli.add_event_handler(admin.handle_add_recipient)
    ttloli.add_event_handler(admin.handle_add_filter)

    ttloli.run_until_disconnected()