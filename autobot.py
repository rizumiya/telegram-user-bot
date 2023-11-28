from handlers import tele_client as tcli, users, tasks, filters, recipients


tclient = tcli.TeleClient()
client = tclient.connect_account(True)    

# Always active until it stopped
with client as client_me:
    client_me.add_event_handler(users.handle_add_user)
    client_me.add_event_handler(users.handle_change_setting)
    client_me.add_event_handler(users.handle_show_help)
    client_me.add_event_handler(users.handle_get_id)
    client_me.add_event_handler(tasks.handle_showall_task)
    client_me.add_event_handler(tasks.handle_add_task)
    client_me.add_event_handler(tasks.handle_delete_task)
    client_me.add_event_handler(tasks.handle_run_task)
    client_me.add_event_handler(filters.handle_showall_filter)
    client_me.add_event_handler(filters.handle_add_whitelist)
    client_me.add_event_handler(filters.handle_delete_whitelist)
    client_me.add_event_handler(filters.handle_add_blacklist)
    client_me.add_event_handler(filters.handle_delete_blacklist)
    client_me.add_event_handler(recipients.handle_add_recipient)
    client_me.add_event_handler(recipients.handle_get_recipient)
    client_me.add_event_handler(recipients.handle_delete_recipient)

    client_me.run_until_disconnected()
