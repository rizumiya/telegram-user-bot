import subprocess
import shutil
import asyncio
import os

async def download_from_supported_link(event, url, current_directory, toWho, reply_to):
    # Perintah untuk menjalankan gallery-dl dan mendownload konten dari Telegraph
    config_path = os.path.join(current_directory, '.venv', 'Include', 'gallery-dl', 'config.json')
    config = f'--config-ignore -c "{config_path}"'
    command = f'gallery-dl {config} --no-part "{url}"'

    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        media_list = []

        while True:
            line = process.stdout.readline().decode('utf-8')
            if not line:
                break

            output = line.strip()
            output = output[2:].replace('\\', '/')

            # Membagi nama folder dan nama file
            folder_name, file_name = os.path.split(output)
            folder_path = os.path.join(current_directory, folder_name)
            media_list = await upload_files(event, folder_path, file_name, toWho, reply_to, media_list)
            await asyncio.sleep(0.5)

        if media_list:
            message = f'[Source Link]({url})\n#AIO_Group'
            await event.client.send_file(toWho, file=media_list, caption=message, reply_to=reply_to, silent=True, background=True)
            media_list = []

        shutil.rmtree(folder_path)

    except Exception as e:
        print(str(e))


async def upload_files(event, folder_path, file_name, toWho, reply_to, media_list):
    file_path = os.path.join(folder_path, file_name)

    with open(file_path, 'rb') as file:
        media_photo = await event.client.upload_file(file=file)
        print("Uploaded")
        media_list.append(media_photo)
    os.remove(file_path)
    
    if len(media_list) % 10 == 0:
        # masih error jika didalam link terdapat media dengan jenis berbeda
        await event.client.send_file(toWho, file=media_list, reply_to=reply_to, silent=True, background=True)
        media_list = []
    
    return media_list


