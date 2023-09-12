from handlers import tele_client as tcli, users, tasks, filters, recipients


tclient = tcli.TeleClient()
client = tclient.connect_account(True)    

# Always active until it stopped
with client as ttloli:
    ttloli.add_event_handler(users.handle_add_user)
    ttloli.add_event_handler(users.handle_change_setting)
    ttloli.add_event_handler(users.handle_show_help)
    ttloli.add_event_handler(users.handle_get_id)
    ttloli.add_event_handler(tasks.handle_showall_task)
    ttloli.add_event_handler(tasks.handle_add_task)
    ttloli.add_event_handler(tasks.handle_delete_task)
    ttloli.add_event_handler(tasks.handle_run_task)
    ttloli.add_event_handler(filters.handle_showall_filter)
    ttloli.add_event_handler(filters.handle_add_whitelist)
    ttloli.add_event_handler(filters.handle_delete_whitelist)
    ttloli.add_event_handler(filters.handle_add_blacklist)
    ttloli.add_event_handler(filters.handle_delete_blacklist)
    ttloli.add_event_handler(recipients.handle_add_recipient)
    ttloli.add_event_handler(recipients.handle_get_recipient)
    ttloli.add_event_handler(recipients.handle_delete_recipient)

    ttloli.run_until_disconnected()