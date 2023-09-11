import os
import streamlit as st
from dotenv import load_dotenv

# Set page title and favicon
st.set_page_config(page_title='UserAutoBot WebUI', page_icon=':guardsman:')

# Hide the default Streamlit hamburger menu
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


class TelegramAutoForwarderApp:
    def __init__(self):
        # Memuat variabel-variabel dari file .env jika ada
        env_path = "config.env"
        load_dotenv(env_path)

    def run(self):
        # Judul aplikasi
        st.title("Telegram Auto Forwarder")

        # Input teks
        api_id = st.text_input("API ID*", "")
        api_hash = st.text_area("API HASH*", "")
        st.text("Pilih salah satu dari metode di bawah, atau bisa isi keduanya")
        bot_token = st.text_input("Bot Token", "")
        phone_number = st.text_input("Phone Number", "")

        # Tombol Submit
        if st.button("Submit"):
            # Menyimpan nilai-nilai ke file .env
            if api_id and api_hash or (bot_token or phone_number):
                with open("config.env", "w") as env_file:
                    env_file.write(f"API_ID={api_id}\n")
                    env_file.write(f"API_HASH={api_hash}\n")
                    env_file.write(f"SESSION=newuser\n")
                    env_file.write(f"PHONE_NUMBER={phone_number}\n")
                    env_file.write(f"BOT_TOKEN={bot_token}\n")

                st.success("Data berhasil disimpan")
                return True
            else:
                st.warning("Mohon isi semua yang bertanda *")
                return False
            
    def check_env(self):
        API_ID = os.getenv("API_ID")
        API_HASH = os.getenv("API_HASH")
        API_SESSION = os.getenv("SESSION")
        PHONE_NUMBER = os.getenv("PHONE_NUMBER")
        BOT_TOKEN = os.getenv("BOT_TOKEN")
        if API_ID and API_HASH and (BOT_TOKEN or PHONE_NUMBER) and API_SESSION:
            self.run()
            os.system(f"python autobot.py")
            return True
        return False


if __name__ == '__main__':
    app = TelegramAutoForwarderApp()
    if not app.check_env():
        app.run()