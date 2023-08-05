import os
import sqlite3

class Database:
    def __init__(self):
        self.SQLPATH = os.path.join(os.path.dirname(__file__), 'autobot.db')
        self.conn = sqlite3.connect(self.SQLPATH)
        self.cursor = self.conn.cursor()

    def create_tables(self):        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id integer null
                        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            id_user integer null,
                            run_task integer null
                        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS user_tasks (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            id_detailtask integer null,
                            use_this integer null,
                            status text null,
                            id_user integer null
                        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS detailed_tasks (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            conn_name text null,
                            old_live text null,
                            task_from text null,
                            task_from_user text null,
                            task_min_id integer null,
                            task_limit integer null
                        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS has_textfilters (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            id_detailtask integer null,
                            id_textfilter integer null
                        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS text_filters (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            regex integer null,
                            text text null
                        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS has_filtertypes (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            id_detailtask integer null,
                            id_filtertype integer null
                        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS filter_types (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            type text null
                        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS task_recipients (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            id_task int null,
                            task_to text null,
                            task_reply text null
                        )''')
        
        # self.queryFilter = """
        # INSERT OR IGNORE INTO filter_types (id, type)
        # VALUES
        #     (1, 'file'),
        #     (2, 'foto'),
        #     (3, 'gif'),
        #     (4, 'sticker'),
        #     (5, 'url'),
        #     (6, 'video'),
        #     (7, 'all')
        # """

        # self.cursor.execute(self.queryFilter)

        self.conn.commit()
        self.dumpSQL()
        self.conn.close()

    def create_data(self, table_name, fields, values):
        placeholders = ', '.join(['?' for _ in values])
        query = f"INSERT INTO {table_name} ({', '.join(fields)}) VALUES ({placeholders})"
        self.conn.execute(query, values)
        self.conn.commit()
        self.dumpSQL()
        self.conn.close()

    def read_datas(self, table_name, fields=None, condition=None, values=None):
        query = f"SELECT {', '.join(fields) if fields else '*'} FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"
        if values:
            # print(query)
            self.cursor.execute(query, values)
        else:
            self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.dumpSQL()
        self.conn.close()
        return rows

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


# db = Database("path/to/your/database.db")
# db.create_tables()

# # Contoh penggunaan metode CRUD
# db.create_data("logins", ["username", "password", "status"], ["john", "password", "admin"])
# logins = db.read_datas("logins")
# print(logins)

# db.create_data("subjects", ["sub_name", "sub_totalQuestion", "sub_choices", "sub_answer", "id_login"],
#                  ["Math", 20, 4, "A", 1])
# subjects = db.read_datas("subjects")
# print(subjects)

# db.create_data("settings", ["id_login", "cameraNo", "def_subject", "showAnswer", "autoSave"],
#                  [1, 1, "Math", 1, 0])
# settings = db.read_datas("settings")
# print(settings)

# # Contoh penggunaan join query
# query = """
#     SELECT logins.username, subjects.sub_name
#     FROM logins
#     JOIN subjects ON logins.login_id = subjects.id_login
# """
# results = db.read_datas(None, None, query)
# print(results)

# db = Database("path/to/your/database.db")
# db.create_tables()

# # Contoh penggunaan metode create_record
# db.create_record("logins", ["username", "password", "status"], ["john", "password", "admin"])

# # Contoh penggunaan metode read_records
# logins = db.read_records("logins")
# print(logins)

# # Contoh penggunaan metode update_record
# db.update_record("logins", ["password"], ["new_password"], "username = ?", ["john"])

# # Contoh penggunaan metode delete_record
# db.delete_record("logins", "username = ?", ["john"])

# db.close_connection()
