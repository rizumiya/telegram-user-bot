from . import database_helper as dbhlp


# Menambahkan task grablink baru
def addNewForward(task_name, type_name, use_this, user_id):
    if dbhlp.find_data('detailed_tasks', 'conn_name', task_name):
        # Jika nama koneksi belum ada, tambahkan ke database
        dataGrabLink = (None, task_name, type_name, None, None, None, None, None, None, 'incomplete')
        dbhlp.add_data('detailed_tasks', dataGrabLink)
        
        # Mengambil id
        id_grabLink = dbhlp.getIdFromTable('detailed_tasks', 'conn_name', task_name)
        id_user = dbhlp.getIdFromTable('users', 'user_id', user_id)
        
        # Menambahkan task ke user_tasks
        dataTask = (None, task_name, use_this, 0, id_grabLink, id_user)
        dbhlp.add_data('user_tasks', dataTask)
