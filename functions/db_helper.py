from datas import database as db


class DB_Umum:
    def __init__(self):
        self.table_name: str = ""
        self.fields: str = None
        self.values:str = None
        self.condition: str = None
        self.condition_value: str = None

    def create_new_data(self):
        dbase = db.Database()
        dbase.create_data(
            self.table_name, 
            self.fields, 
            self.values
        )

    def read_data(self):
        dbase = db.Database()
        rows = dbase.read_datas(
            self.table_name,
            self.fields,
            self.condition,
            self.values
        )
        return rows
    
    def update_data(self):
        dbase = db.Database()
        dbase.update_data(
            self.table_name,
            self.fields, 
            self.values,
            self.condition,
            self.condition_value
        )
    
    def delete_data(self):
        dbase = db.Database()
        dbase.delete_data(
            self.table_name,
            self.condition, 
            self.values
        )


class DB_User(DB_Umum):
    def __init__(self, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.table_name = "users"

    # Check and get user datas
    def get_user(self):
        self.fields = None
        self.condition = "chat_id=?"
        self.values = [self.chat_id]
        user_data = self.read_data()
        if user_data:
            # If user already existed
            return True, user_data
        else:
            # If user not exists
            return False, None
    
    # Add new user to table users
    def add_user(self, values): # input values as array/list
        self.fields = ["chat_id", "phone_no", "username"]
        self.values = values
        self.create_new_data()

    
class DB_Setting(DB_Umum):
    def __init__(self, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.table_name = "settings"
    
    # Add new settings to user
    def add_settings(self, values):
        self.fields = ["id_user", "use_caption", 
                       "use_filter_text", "use_filter_type", "delay"]
        self.values = values
        self.create_new_data()

    # Get setting values
    def get_settings(self, chat_id):
        self.fields = None
        self.condition = "id_user=?"
        self.values = [chat_id]
        user_setting = self.read_data()
        if user_setting:
            return user_setting[0]
        else:
            return False

    # Update admin settings
    def update_settings(self, **kwargs):
        self.fields = ["use_caption", 
                   "use_filter_text", "use_filter_type", "delay"]
        self.values = kwargs['values']
        self.condition = "id_user=?"
        self.condition_value = kwargs['condition_value']
        self.update_data()
    

class DB_Task(DB_Umum):
    def __init__(self, chat_id):
        super().__init__()
        self.chat_id = chat_id
    
    # Add new task to table
    def add_tasks(self, values):
        self.table_name = "tasks"
        self.fields = ["id_user","conn_name", "source", 
                       "use_this", "reverse", "min_id", 
                       "limit_msg", "from_user"]
        self.values = values
        self.create_new_data()
    
    # Get data task by name
    def get_tasks(self, **kwargs):
        self.table_name = (
            "tasks "
            "JOIN users ON users.id=tasks.id_user"
        )
        self.fields = None
        self.condition = "id_user=? AND conn_name=?" if kwargs["conn_name"] else "id_user=?"
        self.values = [kwargs['id_user'], kwargs['conn_name']] if kwargs["conn_name"] else [kwargs['id_user']]
        task_data = self.read_data()
        if task_data:
            return task_data
        else:
            return None

    # Delete data task by name
    def delete_tasks(self, **kwargs):
        self.table_name = "tasks"
        self.condition = "id_user=? AND conn_name=?"
        self.values = [kwargs['id_user'], kwargs['conn_name']]
        self.delete_data()
    
    # Add new running_tasks data
    def add_running_task(self, id_user, task, reci):
        self.table_name = "running_tasks"
        self.fields = [
            "id_user", "conn_name", "source", "use_this", "reverse",
            "min_id", "limit_msg", "from_user", "to_entity", "reply_to", "status"
            ]
        self.values = [
            id_user, task.conn_name, task.source, task.use_this, task.reverse, 
            task.min_id, task.limit_msg, task.from_user, reci.to_entity, reci.reply_to, "running"
            ]
        self.create_new_data()
 
    # Get data of running task by status
    def get_running_tasks(self, **kwargs):
        self.table_name = (
            "running_tasks AS rt "
            "JOIN users ON users.id=rt.id_user"
        )
        self.fields = None
        self.condition = "rt.id_user=? AND rt.status=?" if kwargs["status"] else "rt.id_user=?"
        self.values = [kwargs['id_user'], kwargs['status']] if kwargs["status"] else [kwargs['id_user']]
        task_data = self.read_data()
        if task_data:
            return task_data
        else:
            return None
    
    # Delete running task
    def delete_runningtasks(self, id_user):
        self.table_name = "running_tasks"
        self.condition = "id_user=? AND status=?"
        self.values = [id_user, "running"]
        self.delete_data()


class DB_Filter(DB_Umum):
    def __init__(self, chat_id):
        super().__init__()
        self.chat_id = chat_id
    
    # WHITELIST
    # Run this once per user
    def create_whitelist(self, chat_id):
        self.table_name = "wl_filters"
        self.fields = ['id_user']
        self.values = [chat_id]
        self.create_new_data()
    
    # Get whitelist data
    def get_whitelist(self, id_user):
        self.table_name = (
            "wl_filters AS wf JOIN users ON users.id=wf.id_user"
        )
        self.fields = None
        self.condition = "id_user=?"
        self.values = [id_user]
        whitelist = self.read_data()
        return whitelist

    # Add new filter to database
    def add_whitelist_filters(self, values):
        self.table_name = "wl_filter_types"
        self.fields = ["id_wl_filters", "filter"]
        self.values = values
        self.create_new_data()
    
    # Get whitelist through name or get all whitelists
    def get_whitelist_filters(self, **kwargs):
        self.table_name = (
            "wl_filter_types AS wft "
            "JOIN wl_filters AS wf ON wf.id=wft.id_wl_filters "
            "JOIN users ON users.id=wf.id_user"
        )
        self.fields = None
        self.condition = "wf.id_user=? AND wft.filter=?" if kwargs['filter'] else "wf.id_user=?"
        self.values = [kwargs['id_user'], kwargs['filter']] if kwargs['filter'] else [kwargs['id_user']]
        filters = self.read_data()
        if filters:
            return filters
        else:
            return None
    
    # Remove whitelist filter from whitelist
    def delete_whitelist_filters(self, **kwargs):
        self.table_name = "wl_filter_types"
        self.condition = "id_wl_filters=? AND filter=?"
        self.values = [kwargs['id_wl_filters'], kwargs['filter']]
        self.delete_data()

    # BLACKLIST
    # Run this once per user
    def create_blacklist(self, chat_id, value):
        self.table_name = "bl_filters"
        self.fields = ['id_user', 'text_type']
        self.values = [chat_id, value]
        self.create_new_data()
    
    # Get blacklist data by text or type
    def get_blacklist(self, id_user, btype):
        self.table_name = (
            "bl_filters AS bf JOIN users ON users.id=bf.id_user"
        )
        self.fields = None
        self.condition = "id_user=? AND text_type=?"
        self.values = [id_user, btype]
        blacklist = self.read_data()
        return blacklist

    # Add new filter to database
    def add_blacklist_filters(self, table_name, values):
        self.table_name = table_name
        if table_name == "bl_texts":
            self.fields = ["id_bl_filters", "text", "regex"]
        else:
            self.fields = ["id_bl_filters", "filter"]
        self.values = values
        self.create_new_data()
    
    # Get blacklist through name or get all blacklists
    def get_blacklist_filters(self, **kwargs):
        self.table_name = (
            "bl_filter_types AS bft "
            "JOIN bl_filters AS bf ON bf.id=bft.id_bl_filters "
            "JOIN users ON users.id=bf.id_user"
        )
        self.fields = None
        self.condition = "bf.id_user=? AND bft.filter=?" if kwargs['filter'] else "bf.id_user=?"
        self.values = [kwargs['id_user'], kwargs['filter']] if kwargs['filter'] else [kwargs['id_user']]
        filters = self.read_data()
        if filters:
            return filters
        else:
            return None
    
    # Remove blacklist text or filter from blacklist
    def delete_blacklists(self, **kwargs):
        self.table_name = kwargs['table_name']
        if self.table_name == "bl_texts":
            self.condition = "id_bl_filters=? AND text=?"
        else:
            self.condition = "id_bl_filters=? AND filter=?"
        self.values = kwargs['values']
        self.delete_data()

    # Get blacklist text
    def get_blacklist_texts(self, **kwargs):
        self.table_name = (
            "bl_texts AS bt "
            "JOIN bl_filters AS bf ON bf.id=bt.id_bl_filters "
            "JOIN users ON users.id=bf.id_user"
        )
        self.fields = None
        self.condition = "bf.id_user=? AND bt.text LIKE ?" if kwargs['text'] else "bf.id_user=?"
        self.values = [kwargs['id_user'], f'%{kwargs["text"]}%'] if kwargs['text'] else [kwargs['id_user']]
        filters = self.read_data()
        if filters:
            return filters
        else:
            return None


class DB_Recipient(DB_Umum):
    def __init__(self, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.table_name = "recipients"
    
    # Add new recipients
    def add_recipients(self, values):
        self.fields = ["id_task", "to_entity", "reply_to"]
        self.values = values
        self.create_new_data()

    # Delete all recipient by task
    def delete_recipients(self, id_task):
        self.condition = "id_task=?"
        self.values = [id_task]
        self.delete_data()

    # Get all recipient by task
    def get_recipients(self, id_task):
        self.fields = None
        self.condition = "id_task=?"
        self.values = [id_task]
        reci = self.read_data()
        return reci

    # Delete spesific recipient
    def delete_spesific_recipients(self, entity):
        self.condition = "to_entity=?"
        self.values = [entity]
        self.delete_data()


# class DB_Link(DB_Umum):
#     def __init__(self, chat_id):
#         self.chat_id = chat_id

#     def get_links(self, link):
#         self.table_name = "links"
#         self.fields = None
#         self.condition = "link=?"
#         link_exist = self.read_data()
#         if link_exist:
#             return link_exist
#         else:
#             return None