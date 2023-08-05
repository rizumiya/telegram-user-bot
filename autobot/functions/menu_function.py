from . import database_helper as dbh
from . import forward_message as fwdtsk
from . import grab_link as grblnk

from datetime import datetime


class DML_handle:
    def __init__(self, user_id):
        self.user_id = user_id
    
    def get_id_user(self):
        db_user = dbh.DB_User(self.user_id)
        exists, userData = db_user.checkAndGetUser()
        return exists, userData[0]

    def checkUser(self):
        try:
            self.get_id_user()
            return True
        except:
            return False
    
    def addUserAndSetting(self):
        db_user = dbh.DB_User(self.user_id)
        result = db_user.add_user()
        if result:
            _, userData = self.get_id_user()
            db_sett = dbh.DB_Setting(userData[0])
            db_sett.add_setting()
            return True
        return False

    def addNewTask(self, task):
        _, userData = self.get_id_user()
        db_task = dbh.DB_Task(userData[0])
        db_task.var = task
        result = db_task.add_detailTask()
        if result:
            db_task.add_task()
            return True
        return False

    def getCurrTasks(self):
        _, userData = self.get_id_user()
        db_umum = dbh.DB_Umum()
        db_umum.fields = ["ut.id", "ut.use_this", "dt.old_live",
                          "ut.status", "dt.conn_name", 
                          "dt.task_from", "dt.task_from_user",
                          "dt.task_min_id", "dt.task_limit"]
        db_umum.table_name = (
            "user_tasks AS ut "
            "JOIN detailed_tasks AS dt ON dt.id = ut.id_detailtask "
            "JOIN users ON users.id = ut.id_user"
        )
        db_umum.condition = "ut.id_user=?"
        db_umum.values = [userData[0]]
        rows = db_umum.getDataFrom()
        return rows

    def addNewRecipient(self, recipient):
        _, userData = self.get_id_user()
        exists = self.getTaskFromConn_Name(recipient.conn_name)
        db_reci = dbh.DB_Recipient(userData[0])
        if exists:
            db_reci.add_recipient(recipient)
            return True
        return False

    def addNewFilter(self, filter_name, filter):
        db_filter = dbh.DB_Filter()
        if filter_name == "text":
            db_filter.setValues(filter.regex, filter.text)
            db_filter.addTextFilter()
            return True
        
        return False

    def getTaskFromConn_Name(self, conn_name):
        _, userData = self.get_id_user()
        db_task = dbh.DB_Task(userData[0])
        db_task.var.conn_name = conn_name
        exists, taskData = db_task.checkAndGetTask()
        if exists:
            return taskData[0]
        return False

    def updateTaskorFilter(self, kind, connName_filterno, conn_name):
        if kind == "task":
            _, userData = self.get_id_user()
            taskData = self.getTaskFromConn_Name(connName_filterno)
            db_task = dbh.DB_Task(userData[0])
            userTask = db_task.getUserTaskData(taskData[0])
            # Ubah use this pada task
            use_this = 0 if userTask[2] == 1 else 1
            db_task.var.conn_name = connName_filterno
            db_task.changeUseThis(use_this)
            return True
        elif kind == "filter":
            return True
        else:
            return False

    def changeRunVal(self):
        _, userData = self.get_id_user()
        db_umum = dbh.DB_Umum()
        db_umum.table_name = "settings"
        db_umum.fields = ["run_task"]
        db_umum.values = [1]
        db_umum.condition = f"id_user={userData[0]}"
        db_umum.changeDataFromId()

    def checkUseThisTrue(self, use_this, conn_name):
        if use_this == 1:
            taskData = self.getTaskFromConn_Name(conn_name)
            return taskData
        return None

    def get_recipient(self, con_name):
        _, userData = self.get_id_user()
        db_umum = dbh.DB_Umum()
        db_umum.fields = ["tr.id", "tr.task_to", "tr.task_reply"]
        db_umum.table_name = (
            "task_recipients AS tr "
            "JOIN user_tasks AS ut ON tr.id_task = ut.id "
            "JOIN detailed_tasks AS dt ON dt.id = ut.id_detailtask "
            "JOIN users ON users.id = ut.id_user"
        )
        db_umum.condition = "ut.id_user=? AND dt.conn_name=?"
        db_umum.values = [userData[0], con_name]
        rows = db_umum.getDataFrom()
        return rows


class NoDML:
    def __init__(self, user_id):
        self.user_id = user_id

    async def runTask(self, event, tasks):
        dml = DML_handle(self.user_id)

        if tasks:
            old_live_value = tasks.old_live
            bool_reverse = True if old_live_value == "old" else False
            limit_msg = tasks.limit if tasks.limit != 0 else 0
            offset_msg = tasks.min_id if tasks.min_id != 0 else 0
            recipients = dml.get_recipient(tasks.conn_name)
            album_id = None
            media_album = []

            from_entity = int(tasks.from_entity)
            # print(bool_reverse, limit_msg, offset_msg, recipients, from_entity)
            print("# Start forwarding media from id : " + str(tasks.from_entity)) 
            for recipient in recipients:
                send_to = int(recipient[1])
                reply_to = int(recipient[2]) if recipient[2] != None else None
                async for message in event.client.iter_messages(from_entity,reverse=bool_reverse,min_id=offset_msg):
                    if message.photo:
                        print(event.grouped_id)
                        if message.grouped_id != None:
                            # print(message.stringify())
                            album_id = event.grouped_id
                            media_album.append(message.photo)
                        elif message.grouped_id != album_id:
                            await event.client.send_file(send_to, file=media_album, reply_to=reply_to)
                            media_album = []
                            album_id = event.grouped_id
                            if message.grouped_id != None:
                                media_album.append(message.photo)
                            else:
                                await event.client.send_file(send_to, file=message.photo, reply_to=reply_to)
                        else:
                            if media_album:
                                await event.client.send_file(send_to, file=media_album, reply_to=reply_to)
                                media_album = []
                            await event.client.send_file(send_to, file=message.photo, reply_to=reply_to)

            print("Selesai..")
                # if message.video:
                #     print(event.grouped_id)
                #     if message.grouped_id != None:
                #         print(message.stringify())
                #         album_id = event.grouped_id
                #         media_album.append(message.video)
                #     elif message.grouped_id != album_id:
                #         await event.client.send_file(to_entity, file=media_album, reply_to=reply_to)
                #         media_album = []
                #         album_id = event.grouped_id
                #         if message.grouped_id != None:
                #             media_album.append(message.video)
                #         else:
                #             await event.client.send_file(to_entity, file=message.video, reply_to=reply_to)
                #     else:
                #         if media_album:
                #             await event.client.send_file(to_entity, file=media_album, reply_to=reply_to)
                #             media_album = []
                #         await event.client.send_file(to_entity, file=message.video, reply_to=reply_to)
                # print(tasks)
        











# def updateTaskorFilter(kind, connName_filterno, conn_name):
#     db_umum = dbhlp.DB_Umum()
#     if kind == "task":
#         db_umum.field =  "dt.id, ut.use_this"
#         db_umum.table_name = (
#             "user_tasks AS ut"
#             "JOIN detailed_tasks AS dt"
#             "ON ut.id_detailtask = dt.id"
#             )
#         db_umum.condition = "dt.conn_name=?"
#         db_umum.value = connName_filterno
#         rows = db_umum.get_data_from_table()
#         print(rows)
#         if rows:
#             use_this = rows[0][1]
#             id = rows[0][0]
#             use_this = 1 if use_this == 0 else 0
#             db_umum.table_name = "user_tasks"
#             db_umum.fieldval = f"use_this=?"
#             db_umum.condition = "id_detailtask=?"
#             db_umum.params = (use_this, id)
#             db_umum.change_value()
#             return True
#     elif kind == "filter":
#         print("test")
#         return True
#     return False






















# # Mengecek user saat ini dan yang terdaftar
# async def checkUserValidity(event):
#     sender_id = event.sender_id
#     user_id = await dbhlp.getCurrUser(sender_id)
#     if event.is_private and user_id and not event.via_bot_id:
#         return user_id
    
#     return False


# # Mencari dan menambahkan user sebagai admin ke database
# def check_user(user_id):
#     table_name = 'users'
#     attribute = 'user_id'
#     if dbhlp.find_data(table_name, attribute, user_id):
#         data = (None, user_id)
#         dbhlp.add_data(table_name, data)
#         id_user = dbhlp.getIdFromTable(table_name, attribute, user_id)
#         dataSetting = (None, id_user, 0)
#         dbhlp.add_data('settings', dataSetting)
#         return True
#     return False


# # Mendapatkan task user saat ini
# def getCurrUserTask(user_id):
#     listofData = dbhlp.getTaskFromUser(user_id)
    
#     message = f'\n\n**Current Tasks**\n '
#     if not listofData:
#         message += "\nNo Task"
#     else:
#         for row in listofData:
#             message += "\nTask Name: `" + row[4] + "`"
#             message += "\nTask Type : `" + row[5] + "`"
#             usethis = 'Yes' if row[3] == 1 else 'No'
#             message += "\nUse This : **" + usethis + "**"
#             message += "\nStatus : **" + row[12] + "**"
#             specified = 'Yes' if row[1] == 1 else 'No'
#             message += "\nSpecified : **" + specified + "**"
#             message += "\n **- - - - - - - - - - - - - - - -**"
    
#     return message


# # Mengecek input task yang diberikan dan menambahkannya ke database
# def checkNewTask(task_type, task_behav, task_name, use_this, user_id):
#     if task_type == 'grablink':
#         if task_behav == 'old':
#             type_name = 'grab link old'
#         else:
#             type_name = 'grab link live'
#         grblnk.addNewGrabLink(type_name, task_name, use_this, user_id)

#     elif task_type == 'forward':
#         if task_behav == 'old':
#             type_name = 'forward old'
#         else:  
#             type_name = 'forward old'
#         fwdtsk.addNewForward(task_name, type_name, use_this, user_id)

#     else:
#         print("# Error | Unrecognized task type.")
#     # Menampilkan daftar task saat ini


# # Mengubah tipe data menjadi integer untuk nilai berupa angka
# def is_input_digit(value):
#     if value is None:
#         return None
    
#     valuetype = int(value) if value.isdigit() else str(value)
#     return valuetype


# # Mengubah nilai use this
# def editUseTaskValue(conn_name, user_id):
#     user_id = dbhlp.getIdFromTable('users', 'user_id', user_id)
#     if not dbhlp.find_data('user_tasks', 'conn_name', conn_name):
#         useThisVal = dbhlp.getDataFromTable('use_this', 'user_tasks', 'conn_name', conn_name)
#         useThisVal = 1 if useThisVal[0][0] == 0 else 0
#         dbhlp.editValueFromTable(
#             'user_tasks', 
#             'use_this=?', 
#             'conn_name=? AND user_id=?', 
#             (useThisVal, conn_name, user_id)
#             )
#         return True
#     return False


# # Memberi detail grab task
# def specifyTask(tsk):
#     conn_name = tsk.conn_name
#     task_chat = tsk.from_entity 
#     task_from_user = tsk.from_user 
#     task_to = tsk.entity 
#     task_reply_to = tsk.reply_to 
#     task_min_id = tsk.min_id 
#     task_limit = tsk.limit 

#     if not dbhlp.find_data('detailed_tasks', 'conn_name', conn_name):
#         field_value = "task_chat=?, task_from_user=?, task_to=?, task_reply_to=?, task_min_id=?, task_limit=?"
#         detail_id = dbhlp.getIdFromTable('detailed_tasks', 'conn_name', conn_name)
#         params = (task_chat, task_from_user, task_to, task_reply_to, task_min_id, task_limit, detail_id)
#         dbhlp.editValueFromTable('detailed_tasks', field_value, "id=?", params)
#         dbhlp.editValueFromTable('user_tasks', "specified=?", "detailtask_id=?", (1, detail_id))
#         return True
#     return False


# # Mengambil task yang use_this = True dan specified = True, atau task dengan nama tertentu
# def getAutorunTask(task_name, user_id):
#     taskslist = dbhlp.getTaskFromUser(user_id)
#     autorunTask = []
#     if task_name:
#         for task in taskslist:
#             if task[4] == task_name:
#                 autorunTask.append(task)
#                 return autorunTask
#     else:
#         for task in taskslist:
#             if task[1] == 1 and task[3] == 1:
#                 autorunTask.append(task)
#         return autorunTask


# # Membuat data pesan baru di table pesan
# def newMessage(from_entity, from_user, msg_id):
#     if dbhlp.find_data('messages', 'in_chat', from_entity):
#         id1 = dbhlp.find_data('messages', 'id', 1)
#         id = 1 if id1 else None
#         now = datetime.now()
#         tanggal = now.date()
#         data = (id, msg_id, from_entity, from_user, tanggal)
#         dbhlp.add_data('messages', data)


# # Ambil data run setting
# def turnOnOffRun(user_id):

#     dataSetting = checkRunTask(user_id)

#     # Jika run = False / 0 maka ubah agar menjadi True
#     if dataSetting[0] == 0:
#         dbhlp.editValueFromTable('settings', 
#                                 'run_task=?', 
#                                 'id=?', 
#                                 (1, dataSetting[1]))
        
#     # Jika run = True / 1 maka ubah agar menjadi False
#     else:
#         dbhlp.editValueFromTable('settings', 
#                                 'run_task=?', 
#                                 'id=?', 
#                                 (0, dataSetting[1]))


# def checkRunTask(user_id):
#     # Ambil nilai dari table setting
#     dataSetting = dbhlp.getDataFromTable(
#         'settings.run_task, settings.id', 
#         'settings JOIN users ON users.id = settings.user_id', 
#         'users.user_id', 
#         user_id)
    
#     return dataSetting[0]

