from . import db_helper as dbh

class DMLHandle:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.db_umum = dbh.DB_Umum()
        self.db_user = dbh.DB_User(self.chat_id)
        self.db_sett = dbh.DB_Setting(self.chat_id)
        self.db_task = dbh.DB_Task(self.chat_id)
        self.db_fltr = dbh.DB_Filter(self.chat_id)
        self.db_reci = dbh.DB_Recipient(self.chat_id)
        
    # Check if user is existed in database
    def get_id_user(self):
        exists, user_data = self.db_user.get_user()
        # Return True/False, and first data found
        return exists, user_data[0]

    # Check if user is already admin
    def check_user(self):
        try:
            self.get_id_user()
            return True
        except:
            return False
    
    # Add admin previllage to user
    def add_new_admin(self, user_data):
        user = user_data
        values = [user.chat_id, user.phone_no, user.username]
        if self.check_user():
            # If existed return false
            return False
        else:
            # Add current user to user table
            self.db_user.add_user(values)
            self.add_new_setting()
            self.add_new_whitelist()
            self.add_new_blacklist()
        return True
    
    # Add setting to new admin
    def add_new_setting(self):
        _, user = self.get_id_user()
        values = [user[0], 0, 0, "none", 1]
        self.db_sett.add_settings(values)
        
    # Update admin setting 
    def update_setting(self, sett_data):
        _, user = self.get_id_user()
        values = [
            sett_data.use_caption, 
            sett_data.use_filter_text, 
            sett_data.use_filter_type, 
            sett_data.delay
        ]
        c_values = [user[0]]
        self.db_sett.update_settings(values=values, condition_value=c_values)

    # Get settings
    def get_setting(self):
        _, user = self.get_id_user()
        return self.db_sett.get_settings(user[0])

    # Check and get task provided by conn_name
    def get_task(self, name):
        _, user = self.get_id_user()
        task_data = self.db_task.get_tasks(id_user=user[0], conn_name=name)
        if task_data:
            return task_data
        else:
            return None

    # Add new task
    def add_new_task(self, task):
        _, user = self.get_id_user()
        values = [user[0], task.conn_name, task.source,
                  task.use_this, task.reverse, task.min_id,
                  task.limit_msg, task.from_user]
        task = self.get_task(task.conn_name)
        if not task:
            self.db_task.add_tasks(values)
            return True
        else:
            return False

    # Delete existed task
    def delete_task(self, name):
        _, user = self.get_id_user()
        task = self.get_task(name)
        if task:
            self.db_task.delete_tasks(id_user=user[0], conn_name=name)
            self.db_reci.delete_recipients(task[0][0])
            return True
        else:
            return False

    # WHITELIST
    # Add new filter to admin
    def add_new_whitelist(self):
        _, user = self.get_id_user()
        self.db_fltr.create_whitelist(user[0])
    
    # Get whitelists
    def get_whitelist(self):
        whitelists = self.check_whitelist_filter(None)
        if whitelists:
            return whitelists
        else:
            return None
    
    # Check if whitelist filter is existed in database
    def get_id_whitelist(self):
        _, user = self.get_id_user()
        whitelist = self.db_fltr.get_whitelist(user[0])
        return whitelist[0]
    
    # Add new whitelist filter
    def add_wl_filter(self, filter_type):
        blist_exist = self.check_blacklist_filter(filter_type)
        wlist_exist = self.check_whitelist_filter(filter_type)
        if not blist_exist and not wlist_exist:
            wlist = self.get_id_whitelist()
            values = [wlist[0], filter_type]
            self.db_fltr.add_whitelist_filters(values)

    # Check filter is existed
    def check_whitelist_filter(self, filter_type):
        _, user = self.get_id_user()
        exist = self.db_fltr.get_whitelist_filters(id_user=user[0], filter=filter_type)
        return exist

    # Delete whitelist filter
    def delete_whitelist_filter(self, filter_type):
        list_exist = self.check_whitelist_filter(filter_type)
        if list_exist:
            wlist = self.get_id_whitelist()
            self.db_fltr.delete_whitelist_filters(id_wl_filters=wlist[0], filter=filter_type)
            return True
        return False

    # BLACKLIST
    # Add new filter to admin
    def add_new_blacklist(self):
        _, user = self.get_id_user()
        self.db_fltr.create_blacklist(user[0], "text")
        self.db_fltr.create_blacklist(user[0], "type")
    
    # Get blacklists
    def get_blacklist(self):
        blacklists = self.check_blacklist_filter(None)
        if blacklists:
            return blacklists
        else:
            return None
    
    # Check if blacklist filter is existed in database
    def get_id_blacklist(self, btype):
        _, user = self.get_id_user()
        blacklist = self.db_fltr.get_blacklist(user[0], btype)
        return blacklist[0]
    
    # Add new blacklist filter to text and type table
    def add_bl_filter(self, filter_type, btype):
        blist_exist = self.check_blacklist_filter(filter_type)
        wlist_exist = self.check_whitelist_filter(filter_type)
        if not blist_exist and not wlist_exist:
            blist = self.get_id_blacklist(btype)
            if btype == "text":
                values = [blist[0], filter_type, 0]
                tb_nm = "bl_texts"  
            else:
                values = [blist[0], filter_type]
                tb_nm = "bl_filter_types"
            self.db_fltr.add_blacklist_filters(tb_nm, values)

    # Check if blacklist with filter ... is existed
    def check_blacklist_filter(self, filter_type):
        _, user = self.get_id_user()
        exist = self.db_fltr.get_blacklist_filters(id_user=user[0], filter=filter_type)
        return exist

    # Delete blacklist filter
    def delete_blacklist(self, filter_type, btype):
        list_exist = self.check_blacklist_filter(filter_type)
        btextlist = self.check_blacklist_text(filter_type)
        if list_exist or btextlist:
            blist = self.get_id_blacklist(btype)
            tb_nm = "bl_texts" if btype == "text" else "bl_filter_types"
            values = [blist[0], filter_type]
            self.db_fltr.delete_blacklists(values=values, table_name=tb_nm)
            return True
        return False

    # Get blacklists
    def get_blacklist_text(self):
        bl_text = self.check_blacklist_text(None)
        if bl_text:
            return bl_text
        else:
            return None
    
    # Check if blacklist with text ... is existed
    def check_blacklist_text(self, text):
        _, user = self.get_id_user()
        exist = self.db_fltr.get_blacklist_texts(id_user=user[0], text=text)
        return exist
    
    # Add new recipient for the task
    def add_new_recipient(self, id_task, reci):
        values = [id_task, reci.to_entity, reci.reply_to]
        self.db_reci.add_recipients(values)

    # Delete recipient with for task
    def delete_recipient(self, id_task):
        self.db_reci.delete_recipients(id_task)

    # Get all recipients for task
    def get_recipient(self, id_task):
        return self.db_reci.get_recipients(id_task)
    
    # Delete spesific recipient
    def delete_spesific_recipient(self, entity):
        self.db_reci.delete_spesific_recipients(entity)

    # Running task
    # Get running_task data
    def get_running_task(self):
        _, user = self.get_id_user()
        running_task = self.db_task.get_running_tasks(id_user=user[0], status="running")
        return running_task

    # Create new running task
    def create_runningtask(self, task, reci):
        _, user = self.get_id_user()
        self.db_task.add_running_task(user[0], task, reci)

    # Delete running task where status = running
    def delete_runningtask(self):
        _, user = self.get_id_user()
        self.db_task.delete_runningtasks(user[0])

