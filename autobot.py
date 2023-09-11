from handlers import tele_client as tcli, users, tasks, filters, recipients

import os
import subprocess

tclient = tcli.TeleClient()
client = tclient.connect_account(True)

# Ganti 'nama_file' dengan nama file yang sesuai
file_name = os.path.join(os.path.dirname(__file__), 'autobot.db')

# Jalankan perintah chmod dari Python
try:
    subprocess.run(['chmod', 'g+w', file_name], check=True)
    print(f'Izin file {file_name} berhasil diubah.')
except subprocess.CalledProcessError as e:
    print(f'Gagal mengubah izin file {file_name}. Error: {e}')
    

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