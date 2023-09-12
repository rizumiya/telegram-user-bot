import streamlit as st
import asyncio
import os
from dotenv import load_dotenv

from handlers import tele_client as tcli, users, tasks, filters, recipients
from telethon import TelegramClient

st.set_page_config(page_title='UserAutoBot WebUI', page_icon=':guardsman:')

hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


class WebUI:
    def __init__(self):
        env_path = "config.env"
        load_dotenv(env_path)
        self.api_id = None
        self.api_hash = None
        self.bot_token = None
        self.phone_number = None

        # Inisialisasi event loop
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        

    def show_widgets(self):
        st.title("Telegram Auto Forwarder")
        self.input_api_id = st.text_input("API ID*", self.api_id, type='password')
        self.input_api_hash = st.text_input("API HASH*", self.api_hash, type='password')
        self.input_bot_token = st.text_input("Bot Token", self.bot_token)
        self.input_phone_number = st.text_input("Phone Number*", self.phone_number)

        # Tombol untuk menghubungkan ke API
        if st.button("Simpan"):
            # Periksa apakah inputan kosong
            if not self.api_id or not self.api_hash or not self.phone_number:
                st.warning("Harap isi semua input bertanda *")
            else:
                try:
                    with open("config.env", "w") as env_file:
                        env_file.write(f"API_ID={self.api_id}\n")
                        env_file.write(f"API_HASH={self.api_hash}\n")
                        env_file.write(f"SESSION=newuser\n")
                        env_file.write(f"PHONE_NUMBER={self.phone_number}\n")
                        env_file.write(f"BOT_TOKEN={self.bot_token}\n")
                    # Inisialisasi klien Telethon
                    self.connect_telegram()
                except Exception as e:
                    # Tangani kesalahan jika gagal terhubung
                    st.error(f"Gagal terhubung ke API. Kesalahan: {str(e)}")
    

    def connect_telegram(self):

        tclient = tcli.TeleClient()
        tclient.loop = self.loop
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


    def check_env(self):
        API_ID = os.getenv("API_ID")
        API_HASH = os.getenv("API_HASH")
        API_SESSION = os.getenv("SESSION")
        PHONE_NUMBER = os.getenv("PHONE_NUMBER")
        BOT_TOKEN = os.getenv("BOT_TOKEN")
        if API_ID and API_HASH and (BOT_TOKEN or PHONE_NUMBER) and API_SESSION:
            self.api_id = API_ID
            self.api_hash = API_HASH
            self.bot_token = BOT_TOKEN
            self.phone_number = PHONE_NUMBER
        return False


if __name__ == '__main__':
    app = WebUI()
    app.check_env()
    app.show_widgets()
