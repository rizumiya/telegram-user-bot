from telethon import client
from handlers import client as cli, admin

client1 = cli.TeleClient()
client = client1.connect_acc(True)

with client as ttloli:
    ttloli.add_event_handler(admin.handle_add_user)
    ttloli.add_event_handler(admin.handle_tasks)
    ttloli.add_event_handler(admin.handle_add_task)
    ttloli.add_event_handler(admin.handle_add_recipient)
    ttloli.add_event_handler(admin.handle_add_filter)
    ttloli.add_event_handler(admin.handle_use)
    ttloli.add_event_handler(admin.handle_run)

    ttloli.run_until_disconnected()