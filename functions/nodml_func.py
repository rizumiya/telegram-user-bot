from telethon.tl.types import InputPhoneContact, PeerChannel, PeerUser
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.errors import FloodWaitError

from . import dml_func
import config as cfg

import asyncio
import re


class NoDMLFunctions:
    def __init__(self, event):
        self.event = event
        self.client = self.event.client
        self.dml = dml_func.DMLHandle(self.event.sender_id)
        
        self.media_album = []
        self.album_id = None
        self.send_to = None
        self.reply_to = None
        self.caption = None

    # Sending message to user
    async def send_message_normal(self, msg):
        try:
            await self.client.send_message(
                entity=msg.entity,
                message=msg.message,
                reply_to=msg.reply_to,
                silent=True,
                background=True
            )
            print("# Success | Message delivered to " + str(msg.entity))
        except:
            print("# Error | Unable to send the message")

    # User
    # Save user contact
    async def add_to_contact(self, phone_no):
        await self.client(ImportContactsRequest(
            contacts=[InputPhoneContact(
                client_id=0,
                phone=phone_no,
                first_name='new',
                last_name='user'
                )]
        ))


    # Show current setting
    async def show_settings(self):
        sett = self.dml.get_setting()
        cap = "On" if sett[2] == 1 else "Off"
        tf = "On" if sett[3] == 1 else "Off"
        message = (
            "**Current Setting**\n\n"
            f"Show Caption : **{cap}**\n"
            f"Blacklist Text : **{tf}**\n"
            f"Active Filter : **{sett[4]}**\n"
            f"Delay : **{sett[5]}** seconds\n"
            "-----------------------\n"
            )
        return message


    # Get message information from replied message (sender)
    async def get_sender_id(self, message):
        sender_id = message.sender_id
        sender_entity = await self.client.get_entity(int(sender_id))
        user_username = sender_entity.username if sender_entity.username else None
        show_username = f"`@{user_username}`\n" if user_username else ""

        sender = {
            "username" : show_username,
            "chat_id" : message.chat_id,
            "user_id" : sender_id,
            "message_id" : message.id
        }

        return sender


    # Get message information from replied message (forwarded)
    async def get_forwarded_id(self, message):
        if message.forward:
            data = message.forward
            if isinstance(data.from_id, PeerChannel):
                from_id = data.from_id.channel_id
                from_id = "-100" + str(from_id)
            elif isinstance(data.from_id, PeerUser):
                from_id = data.from_id.user_id
            
            entity = await self.client.get_entity(int(from_id))
            username = entity.username if entity.username else None
            show_username = f"`@{username}`\n" if username else ""
            try:
                name = entity.title 
            except:
                name = entity.first_name
            message_id = data.channel_post if data.channel_post else None
            show_message_id = f"Message ID : `{message_id}`\n" if message_id else ""
            forwarded = {
                "username" : show_username,
                "id" : from_id,
                "name" : name,
                "message_id" : show_message_id
            }
            return forwarded
        return None

    # Filter
    # Get text between apostrophe
    async def get_text_petik(self, input_user):
        text = ""
        for i in range(1, len(input_user)):
            text += input_user[i] + " "
        text = text.strip()

        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]

        return text

    # Task
    # Regex sticker
    async def reg_get_sticker(self, link):
        match = None
        regex = r"https?://t\.me/addstickers/[^\]\)\s]+"
        
        match = re.match(regex, link)
        if match:
            sticker_link = match.group()
            return sticker_link
        
        return match


    # Regex join link
    async def reg_get_joinlink(self, link):
        regex_list = [
            r"https?://t\.me/addlist/[a-zA-Z\d_-]+",
            r"https?://t\.me/joinchat/[a-zA-Z\d_-]+",
            r"https?://t\.me/\+[a-zA-Z\d_-]+",
            r"https?://t\.me/(?!(addstickers/|proxy/))[a-zA-Z\d_-]+"
        ]

        for regex in regex_list:
            match = re.search(regex, link)
            if match:
                join_link = match.group()
                # Periksa akhiran link
                if not join_link.endswith("_bot") and not join_link.endswith("bot"):
                    return join_link

        return None


    # Append all to datas into array
    async def asign_to_array(self, datas):
        if datas:
            arr = []
            for data in datas:
                arr.append(data[2])
            return arr
        return None


    # Gett setting, filters, recipient
    async def get_all_requirements(self, task):
        settings = self.dml.get_setting()
        whitelists = self.dml.get_whitelist()
        blacklists = self.dml.get_blacklist()
        text_bls = self.dml.get_blacklist_text()
        recipans = self.dml.get_recipient(task[0])

        whites = await self.asign_to_array(whitelists)
        blacks = await self.asign_to_array(blacklists)
        texts = await self.asign_to_array(text_bls)
        recs = []
        for recipan in recipans:
            recs.append({
                "to_entity": recipan[2],
                "reply_to": recipan[3]
            })
        
        return settings, whites, blacks, texts, recs


    # Running existed task by name
    async def run_spesific_task(self, task, i):
        _,_,_,_,recs = await self.get_all_requirements(task)

        bool_reverse = True if task[5] == 1 else False
        limit_msg = task[7] if task[7] != 0 else 0
        offset_msg = task[6] if task[6] != 0 else 0

        try:
            if task[3].startswith("-") or task[3].isdigit():
                source = int(task[3])
        except:
            source = task[3]

        # Perlu pengecekan jika running_task bukan task detail yang dikirim kan
        run_task = self.dml.get_running_task()

        if i < len(recs) and run_task:
            i += 1
            run_task = run_task[0]

            try:
                if run_task[9].startswith("-") or run_task[9].isdigit():
                    self.send_to = int(run_task[9])
            except:
                self.send_to = run_task[9]

            self.reply_to = run_task[10] if run_task[10] != None else None

            await self.run_iter_message(
                task,
                limit_msg,
                entity=source,
                reverse=bool_reverse,
                min_id=offset_msg
            )
            
            # Delete running task
            self.dml.delete_runningtask()
            # Delete recipient from task
            # self.dml.delete_spesific_recipient(self.send_to)
            return await self.run_spesific_task(task, i)
        elif i < len(recs) and not run_task:
            new_r_task = cfg.Task(task[2], task[3], task[4], task[5], task[6], task[7])
            new_r_task.from_user = task[8]
            new_r_reci = cfg.TaskRecipient(task[2], recs[i]['to_entity'], recs[i]['reply_to'])

            self.dml.create_runningtask(new_r_task, new_r_reci)
            return await self.run_spesific_task(task, i)


    # Only for whitelist
    async def get_filters(self, message, lists):
        for item in lists:
            if item not in ["file", "photo", "document", "web_preview", "audio", "video", "video_note", "gif", "sticker", "contact"]:
                continue

            item_value = getattr(message, item, None)
            if item_value:
                await self.send_message(item_value, message)
                self.sent += 1


    # Proses filtering pesan
    async def run_iter_message(self, task, limit_msg, **kwargs):
        setts, wls, bls, bts, recs = await self.get_all_requirements(task)

        self.caption = setts[2]  # Gunakan caption
        s_bl_text = setts[3]  # Gunakan blacklist text
        s_filter_on = setts[4]  # Gunakan filter ["blacklist" / "whitelist"]
        s_delay = setts[5]  # Delay pengiriman

        self.sent = 0
        max_iter = limit_msg

        # If use blacklist text = True, assign list of blacklist to exclude_strings
        exclude_strings = bts if s_bl_text and bts else None
        filter_type = s_filter_on if s_filter_on in ["blacklist", "whitelist"] else None

        async for message in self.client.iter_messages(**kwargs):
            try:
                await asyncio.sleep(int(s_delay))
                should_exclude = False

                if exclude_strings:
                    for exclude_string in exclude_strings:
                        if exclude_string in message.message:
                            should_exclude = True
                            break
                
                if not should_exclude and message.media:
                    # Logika filtering
                    if filter_type:
                        if filter_type == "whitelist":
                            if wls:
                                await self.get_filters(message, wls)
                    else:
                        # Jika filter tidak digunakan, kirim pesan
                        await self.send_message(message, message)
                        self.sent += 1

                    if max_iter > 0 and self.sent >= max_iter:
                        if self.media_album:
                            await self.send_iter_message()
                            self.media_album = []
                        break
            except FloodWaitError as e:
                # Handle the FloodWaitError
                print("FloodWaitError occurred. Sleeping for {} seconds.".format(e.seconds))
                await asyncio.sleep(e.seconds)
                continue
            except: 
                print("# No text/link to proccess")

    # Only to send an album
    async def send_iter_message(self):
        await self.client.send_file(self.send_to, file=self.media_album, reply_to=self.reply_to)
    
    # check if message an album or not
    async def send_message(self, file, message):
        if message.grouped_id != None:
            if message.grouped_id != self.album_id and self.media_album:
                await self.send_iter_message()
                self.media_album = []
            self.album_id = message.grouped_id
            self.media_album.append(file)
        elif message.grouped_id != self.album_id:
            await self.send_iter_message()
            self.media_album = []
            self.album_id = message.grouped_id
            if message.grouped_id != None:
                self.media_album.append(file)
            else:
                await self.client.send_file(self.send_to, file, reply_to=self.reply_to)
        else:
            if self.media_album:
                await self.send_iter_message()
                self.media_album = []
            await self.client.send_file(self.send_to, file, reply_to=self.reply_to)

