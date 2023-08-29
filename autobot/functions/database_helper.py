from datas import database as db
import config as cfg


class DB_Umum:
    def __init__(self):
        self.table_name: str = ""
        self.fields: str = None
        self.values: str = None
        self.condition: str = None
        self.condition_values: str = None
    
    def insertNewData(self):
        dbase = db.Database()
        dbase.create_data(
            table_name = self.table_name,   # "users"
            fields = self.fields,           # None / "username=? AND password=? ORDER BY name ASC"
            values = self.values,           # None / ("username", "password")
        )

    def changeDataFromId(self):
        dbase = db.Database()
        dbase.update_data(
            table_name = self.table_name,   # "users"
            fields = self.fields,           # None / ["first_name", "phone_no"]
            values = self.values,           # None / ("username", "password")
            condition = self.condition,     # None / "username=? AND password=? ORDER BY name ASC"
            condition_values = self.condition_values # None / (username, password)
        )

    def dropDataFromId(self):
        dbase = db.Database()
        dbase.delete_data(
            table_name = self.table_name,   # "users"
            condition = "id=?",             # None / "username=? AND password=? ORDER BY name ASC"
            values = self.values,           # None / ("username", "password")
        )

    def getDataFrom(self):
        dbase = db.Database()
        rows = dbase.read_datas(
            table_name = self.table_name,   # "users"
            fields = self.fields,           # None / ("username", "password")
            condition = self.condition,     # None / "username=? AND password=? ORDER BY name ASC"
            values = self.values            # None / ("username", "password")
        )
        return rows


class DB_User(DB_Umum):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
    
    def checkAndGetUser(self):
        dbase = db.Database()
        user_data = dbase.read_datas(
            table_name = "users",
            condition = "user_id=?",
            values = [self.user_id]
        )
        if user_data:
            # jika user sudah ada
            return True, user_data
        # jika user belum ada
        return False, None

    def add_user(self):
        exists, _ = self.checkAndGetUser()
        if not exists:
            self.table_name = "users"
            self.fields = ["user_id"]
            self.values = [self.user_id]
            self.insertNewData()
            return True
        return False


class DB_Setting(DB_Umum):
    def __init__(self, id_user):
        super().__init__()
        self.id_user = id_user

    def checkAndGetSetting(self):
        dbase = db.Database()
        user_setting = dbase.read_datas(
            table_name = "settings",
            condition = "id_user=?",
            values = (self.id_user)
        )
        if user_setting:
            # jika user setting sudah ada
            return user_setting
        # jika user setting belum ada
        return None
    
    def add_setting(self):
        self.table_name = "settings"
        self.fields = ["id_user", "run_task"]
        self.values = (self.id_user, 0)
        self.insertNewData()
        return True


class DB_Task(DB_Umum):
    def __init__(self, id_user):
        super().__init__()
        self.id_user = id_user
        self.var: cfg.NewTask = None
        self.var = cfg.NewTask(conn_name="", old_live="", from_entity="", use_this=0, min_id=0, limit=0)

    def checkAndGetTask(self):
        dbase = db.Database()
        detail_tasks = dbase.read_datas(
            table_name = "detailed_tasks",
            condition = "conn_name=?",
            values = [self.var.conn_name]
        )
        if detail_tasks:
            # jika task sudah ada
            return True, detail_tasks
        # jika task belum ada
        return False, None

    def add_detailTask(self):
        exists, _ = self.checkAndGetTask()
        if not exists:
            self.table_name = "detailed_tasks"
            self.fields = ["conn_name", "old_live", "task_from", "task_from_user", "task_min_id", "task_limit"]
            self.values = (
                self.var.conn_name, 
                self.var.old_live,
                self.var._from_entity,
                self.var._from_user,
                self.var.min_id,
                self.var.limit
            )
            self.insertNewData()
            return True
        return False
    
    def add_task(self):
        _, taskData = self.checkAndGetTask()
        id_detailtask = taskData[0][0]
        self.table_name = "user_tasks"
        self.fields = ["id_detailtask", "use_this", "status", "id_user"]
        self.values = (id_detailtask, self.var.use_this, "Incomplete", self.id_user)
        self.insertNewData()
    
    def getUserTaskData(self, id_detailtask):
        self.table_name = "user_tasks"
        self.condition = "id_detailtask=?"
        self.values = [id_detailtask]
        datas = self.getDataFrom()
        return datas[0]
    
    def changeUseThis(self, use_this):
        _, taskData = self.checkAndGetTask()
        self.table_name = "user_tasks"
        self.fields = ["use_this"]
        self.values = [use_this]
        self.condition = "id_detailtask=?"
        self.condition_values = [taskData[0][0]]
        self.changeDataFromId()

    def changeMinID(self, min_id):
        _, taskData = self.checkAndGetTask()
        self.table_name = "detailed_tasks"
        if taskData[0][6] > 0:
            self.fields = ["task_min_id", "task_limit"]
            self.values = [min_id, taskData[0][6] - 1]
        else:
            self.fields = ["task_min_id"]
            self.values = [min_id]
        self.condition = "id=?"
        self.condition_values = [taskData[0][0]]
        self.changeDataFromId()

class DB_Recipient(DB_Umum):
    def __init__(self, id_user):
        super().__init__()
        self.id_user = id_user
        self.var: cfg.TaskRecipient = None
        self.var = cfg.TaskRecipient(conn_name="", to_user="", reply_to=0)
        
    def add_recipient(self, recipient):
        self.var = recipient
        db_task = DB_Task(self.id_user)
        db_task.var.conn_name = self.var.conn_name
        _, taskData = db_task.checkAndGetTask()
        id_detailtask = taskData[0][0]
        self.table_name = "task_recipients"
        self.fields = ["id_task", "task_to", "task_reply"]
        self.values = (id_detailtask, self.var.to_user, self.var.reply_to)
        self.insertNewData()



class DB_Filter(DB_Umum):
    def __init__(self):
        super().__init__()
    
    def addTextFilter(self):
        self.table_name = "text_filters"
        self.fields = ["regex", "text"]
        self.insertNewData()

    def setValues(self, regex, text):
        self.values = [regex, text]


