import os

# Fungsi untuk mengunduh file

async def media_album_turn_anon(event, for_anon):
    if event.message.photo:
        # Inisialisasi daftar untuk menyimpan hasil unggahan file
        media_list = []

        # Loop melalui setiap file dalam album
        for file in event.messages:
            file_path = await event.client.download_media(file, file=for_anon)
            print("ini file nya : "+str(file_path))
            with open(file_path, 'rb') as file:
                media_photo = await event.client.upload_file(file=file)
                media_list.append(media_photo)
            os.remove(file_path)

            await event.client.delete_messages(event.chat_id, file)
        
        return media_list