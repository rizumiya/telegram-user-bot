import os
import sqlite3


class Database:
    def __init__(self):
        self.SQLPATH = os.path.join(os.path.dirname(__file__), 'autobot.db')
        self.conn = sqlite3.connect(self.SQLPATH, uri=True)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            chat_id integer null,
                            phone_no text null,
                            username text null
                        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            id_user integer null,
                            use_caption integer null,
                            use_filter_text integer null,
                            use_filter_type text null,
                            delay integer null
                        )''')
        
        # Whitelist        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS wl_filters (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            id_user integer null
                        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS wl_filter_types (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            id_wl_filters integer null,
                            filter text null
                        )''')
        
        # Blacklist
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS bl_filters (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            id_user integer null,
                            text_type text null
                        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS bl_texts (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            id_bl_filters integer null,
                            text text null,
                            regex integer null
                        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS bl_filter_types (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            id_bl_filters integer null,
                            filter text null
                        )''')

        # Task
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            id_user integer null,
                            conn_name text null,
                            source text null,
                            use_this integer null,
                            reverse integer null,
                            min_id integer null,
                            limit_msg integer null,
                            from_user text null
                        )''')
        
        # Running task
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS running_tasks (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            id_user integer null,
                            conn_name text null,
                            source text null,
                            use_this integer null,
                            reverse integer null,
                            min_id integer null,
                            limit_msg integer null,
                            from_user text null,
                            to_entity text null,
                            reply_to integer null,
                            status text null
                        )''')
        
        # Task recipient
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS recipients (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            id_task integer null,
                            to_entity text null,
                            reply_to integer null
                        )''')
        
        # Forward links
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS fwd_links (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            id_user integer null,
                            source text null
                        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS links (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            id_user integer null,
                            link text null,
                            type text null
                        )''')
        
        # Link recipients
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS link_dests (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            id_user integer null,
                            type text null,
                            to_entity text null,
                            reply_to integer null
                        )''')
        
        self.conn.commit()
        self.dumpSQL()
        self.conn.close()

    # Add new data
    def create_data(self, table_name, fields, values):
        placeholders = ', '.join(['?' for _ in values])
        query = f"INSERT INTO {table_name} ({', '.join(fields)}) VALUES ({placeholders})"
        # print(query)
        self.conn.execute(query, values)
        self.conn.commit()
        self.dumpSQL()
        self.conn.close()

    # Read existed data
    def read_datas(self, table_name, fields=None, condition=None, values=None):
        query = f"SELECT {', '.join(fields) if fields else '*'} FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"
        if values:
            # print(query, values)
            self.cursor.execute(query, values)
        else:
            self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.dumpSQL()
        self.conn.close()
        return rows

    # Change value existed data
    def update_data(self, table_name, fields, values, condition=None, condition_values=None):
        set_values = ', '.join([f"{field} = ?" for field in fields])
        query = f"UPDATE {table_name} SET {set_values}"
        if condition:
            query += f" WHERE {condition}"
        if condition_values:
            self.conn.execute(query, values + condition_values)
        else:
            self.conn.execute(query, values)
        self.conn.commit()
        self.dumpSQL()
        self.conn.close()

    # Detele existed data
    def delete_data(self, table_name, condition=None, values=None):
        query = f"DELETE FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"
        if values:
            self.conn.execute(query, values)
        else:
            self.conn.execute(query)
        self.conn.commit()
        self.dumpSQL()
        self.conn.close()

    def dumpSQL(self):
        with open('db_autobot.txt', 'w') as f:
            for line in self.conn.iterdump():
                f.write('%s\n' % line)