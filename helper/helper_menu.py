from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator
import re

async def getJoinLink(link):
    regex_list = [
        r"https?://t\.me/addlist/[a-zA-Z\d_-]+",
        r"https?://t\.me/joinchat/[a-zA-Z\d_-]+",
        r"https?://t\.me/\+[a-zA-Z\d_-]+",
        r"https?://t\.me/(?!(addstickers/))[a-zA-Z\d_-]+"
    ]

    for regex in regex_list:
        match = re.search(regex, link)
        if match:
            join_link = match.group()
            # Periksa akhiran link
            if not join_link.endswith("_bot") and not join_link.endswith("bot"):
                return join_link

    return None


async def getSticker(link):
    match = None
    regex = r"https?://t\.me/addstickers/[^\]\)\s]+"

    match = re.match(regex, link)
    if match:
        sticker_link = match.group()
        return sticker_link

    return match


async def extract_link(string):
    # Regex untuk mengekstraksi link dari website yang ditentukan
    telegraph_regex = r"https?://telegra\.ph/[\w%-]+"
    pixiv_regex = r"https?://www.pixiv.net/(?:en/)?artworks/\d+"
    vk_regex = r"https?://(m\.)?vk\.com/[\w\d-]+"
    hentai_regex = r"https?://hentai-cosplays\.com/image/[\w%-]+"

    match = re.search(f"({telegraph_regex}|{pixiv_regex}|{vk_regex}|{hentai_regex})", string)
    if match:
        return match.group(1)
    else:
        return None


async def showHelp(event):
    user_id = event.message.peer_id.user_id
    cmd1 = [
        ('/start', 'Register your account'),
        ('/help', 'Show this message'),
        ('/status', 'Show your current settings'),
        ('/forward', 'Start forwarding messages'),
    ]
    cmdsett = [
        ('/addblacklist text', 'Add words or phrases that should be excluded while forwarding messages'),
        ('/resetblacklist text', 'Reset your current blacklist to None'),
        ('/filterlist', 'Show list of available filters'),
        ('/addfilter filter', 'Allow you to specify type of messages that will be forwarded'),
        ('/resetfilter filter', 'Reset your current filter to None'),
    ]
    
    message = (
        "**Help**\n\n"
        "**Usage**\n"
        "- In order to get images, simply **send the link** to me\n"
        "- If you want to convert an image file into media, just **send the image file** to me\n"
        "- Use the `/forward from_id to_id` command to forward messages. If the 'to_id' is not provided, "
        "the messages will be forwarded back to you\n\n"
        "**Supported Website**\n"
        "`Telegraph`, `Pixiv`, more will be added in the future\n\n"
        "**List of available commands**\n\n"
    )
    
    for cmd in cmd1:
        message += f"`{cmd[0]}` - {cmd[1]}\n"
        
    message += "\n**Forward settings**\n\n"
    
    for cmd in cmdsett:
        message += f"`{cmd[0]}`\n{cmd[1]}\n"
        
    message += (
        "**\nUsage Example**\n"
        "/addfilter image\n"
        "/addfilter gif\n"
        "/addblacklist si anjing coklat\n"
        "/forward 123456 654321\n\n"
        "**Explanation**\n"
        "Only images and GIFs will be forwarded. If an image has the caption 'si anjing coklat', "
        "the message will be skipped and not forwarded. The messages will be forwarded from the source ID "
        "123456 to the destination ID 654321\n\n"
        "Created by __@Rizumiya__"
    )
    
    await event.client.send_message(user_id, message, parse_mode='markdown')