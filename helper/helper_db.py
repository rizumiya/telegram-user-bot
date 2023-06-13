from helper import database

# Menambahkan link ke database
async def addLinktoDB(link, field, table, atribute):
    rows = database.search_data(field, table, atribute, link)
    if rows:
        print("- Link already existed")
        return None
    else:
        dataForum = (None, link)
        database.insert_data(table, dataForum)
        print("+ Link added to database")
        return True

# Menambahkan task untuk forward
async def addforwardTask(task_name, from_id, to_id, reply_id, offset_id, user_id):
    ifexist = database.ifDataExist('forward_tasks', 'task_name', task_name)
    if ifexist == 0:
        print("- Forward name already existed")
        return None
    else:
        dataForwardTask = (None, task_name, from_id, to_id, reply_id, offset_id, user_id)
        database.insert_data('forward_tasks', dataForwardTask)
        print("+ Forward task added")
        return True

# Mengambil daftar forward task
async def getCurrFwdTsk(event):
    user_id = event.sender_id
    fwdTsk = database.search_data(
        'forward_tasks.id, forward_tasks.task_name, forward_tasks.from_id, forward_tasks.to_id, forward_tasks.reply_id, forward_tasks.offset_id',
        '''
            forward_tasks 
            JOIN users ON forward_tasks.user_id = users.id
        ''',
        'forward_tasks.user_id',
        user_id
    )

    return fwdTsk

# Mengambil tujuan untuk forward mantab2
async def getRecipient(topic_about):
    rows = database.search_data('forum_id, topic_id', 'adminIns', 'forum_theme', topic_about)
    if rows:
        return rows
    else: 
        return None

# Tambah user yang bisa akses si mmccmntb
async def addingUser(event):
    user_id = event.sender_id
    dataUsers = (None, user_id)
    dataSettings = (None, None, None, user_id)

    row_count = database.ifDataExist('users', 'user_id', user_id)
    if row_count > 0:
        pass
    else:
        database.insert_data('users', dataUsers)
        database.insert_data('settings', dataSettings)

# Ambil user saat ini
async def getCurrUser(event):
    rows = database.search_data('user_id', 'users', 'user_id', event.sender_id)
    if rows:
        return rows[0][0]
    else: 
        return None

# Ambil settingan user saat ini
def getSettings(event):
    user_id = event.sender_id

    filters = database.search_data(
        'filters.id, filters.filter_name',
        '''
            filters 
            JOIN userFilters ON filters.id = userFilters.filter_id 
            JOIN settings ON settings.id = userFilters.setting_id
        ''',
        'settings.user_id',
        user_id
    )
    
    blacklists = database.search_data(
        'blacklists.id, blacklists.blacklist_text',
        '''
            blacklists 
            JOIN userBlacklists ON blacklists.id = userBlacklists.blacklist_id 
            JOIN settings ON settings.id = userBlacklists.setting_id
        ''',
        'settings.user_id',
        user_id
    )

    return filters, blacklists

# harusnya dipindah ke file lain karna gak ada hubungannya sama database
async def getStatus(event):
    filters, blacklists = getSettings(event)
    
    message = f'**Status**\n\nCurrent Filter:\n'
    if not filters:
        message += "No filters"
    else:
        for row in filters:
            message += row[1] + " | "
    message += f'\n\nCurrent Blacklist:\n- '
    if not blacklists:
        message += "No blacklists"
    else:
        for row in blacklists:
            message += "\n- " + row[1]
    
    return message