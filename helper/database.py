import sqlite3

def create_tables():
    conn = sqlite3.connect('ren_DB.db')
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id integer null
                    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS respondmessages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        client_id integer null,
                        client_msg_id integer null
                    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        userblacklist_id integer null,
                        userfilter_id integer null,
                        user_id integer
                    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS adminIns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        forum_id integer null,
                        topic_id integer null, 
                        forum_theme text null
                    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS linkJoins (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        link_tele text null
                    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS linkStickers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        link_sticker text null
                    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS userBlacklists (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        setting_id integer null,
                        blacklist_id text null
                    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS blacklists (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        blacklist_text text null
                    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS userFilters (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        setting_id integer null,
                        filter_id integer
                    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS filters (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filter_name text null
                    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS download_tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        link_value text null,
                        link_for text null,
                        replied integer null,
                        replied_msg_id integer null,
                        message_id integer null,
                        folder_path text null,
                        user_id integer null
                    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS forward_tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task_name text null,
                        from_id integer null,
                        to_id integer null,
                        reply_id integer null,
                        offset_id integer null,
                        user_id integer null
                    )''')


    queryFilter = """
    INSERT OR IGNORE INTO filters (id, filter_name)
    VALUES
        (1, 'file'),
        (2, 'foto'),
        (3, 'gif'),
        (4, 'sticker'),
        (5, 'url'),
        (6, 'video')
    """

    cursor.execute(queryFilter)

    queryForum = """
        INSERT OR IGNORE INTO adminIns (id, forum_id, topic_id, forum_theme)
        VALUES
            (1, 1901826075, 859, 'sharink'),
            (2, 1901826075, 61, 'sticker'),
            (3, 1901826075, 819, '2d'),
            (4, 1901826075, 14, 'cosplay'),
            (5, 1901826075, 15, 'hoyoverse'),
            (6, 1901826075, 21, 'real'),
            (7, 1901826075, 38, 'furry')
    """

    cursor.execute(queryForum)

    conn.commit()
    conn.close()


def insert_data(table_name, data):
    conn = sqlite3.connect('ren_DB.db')
    cursor = conn.cursor()
    
    placeholders = ', '.join(['?'] * (len(data) - 1))
    query = f"INSERT INTO {table_name} VALUES (NULL, {placeholders})"
    
    cursor.execute(query, data[1:])
    
    conn.commit()
    conn.close()


def select_data(table_name):
    conn = sqlite3.connect('ren_DB.db')
    cursor = conn.cursor()
    
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    conn.close()
    return rows


def update_data(table_name, field_value, condition, params):
    conn = sqlite3.connect('ren_DB.db')
    cursor = conn.cursor()

    query = f"UPDATE {table_name} SET {field_value} WHERE {condition}"
    cursor.execute(query, params)

    conn.commit()
    conn.close()


def delete_data(table_name, condition):
    conn = sqlite3.connect('ren_DB.db')
    cursor = conn.cursor()
    
    cursor.execute(f"DELETE FROM {table_name} WHERE {condition}")
    
    conn.commit()
    conn.close()


def is_table_empty(table_name):
    conn = sqlite3.connect('ren_DB.db')
    cursor = conn.cursor()
    
    query = f"SELECT COUNT(*) FROM {table_name}"
    cursor.execute(query) 
    row = cursor.fetchone()
    count = row[0]
    conn.close()
    return count == 0


def ifDataExist(table_name, attribute, value):
    conn = sqlite3.connect('ren_DB.db')
    cursor = conn.cursor()
    query = f"SELECT COUNT(*) FROM {table_name} WHERE {attribute} = ?"
    cursor.execute(query, (value,))
    row_count = cursor.fetchone()[0]
    conn.close()
    return row_count


def delete_data_by_id_range(start_id, end_id):
    conn = sqlite3.connect('ren_DB.db')
    cursor = conn.cursor()

    delete_query = "DELETE FROM linkStickers WHERE id BETWEEN ? AND ?"
    cursor.execute(delete_query, (start_id, end_id))

    conn.commit()
    conn.close()


def search_data(field, table_name, attribute, value):
    conn = sqlite3.connect('ren_DB.db')
    cursor = conn.cursor()

    query = f"SELECT {field} FROM {table_name} WHERE {attribute} = ?"
    cursor.execute(query, (value,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def export_all_tables_to_txt(database_file, file_path):
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()

    query = "SELECT name FROM sqlite_master WHERE type='table'"
    cursor.execute(query)

    tables = cursor.fetchall()

    with open(file_path, 'w') as file:
        for table in tables:
            table_name = table[0]
            file.write(f"Table: {table_name}\n")

            query = f"SELECT * FROM {table_name}"
            cursor.execute(query)

            rows = cursor.fetchall()
            for row in rows:
                line = '\t'.join(str(value) for value in row)
                file.write(line + '\n')

            file.write('\n')

    conn.close()
