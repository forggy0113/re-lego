import sqlite3

class CreateDataBase:
    def __init__(self, db_name='data.db'):
        self.conn = sqlite3.connect(db_name) # 連接數據庫
        self.cursor = self.conn.cursor() # 創建游標
        self.create_table()
    
    def create_table(self):
        # 創建學生資料表
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS Students(
                                stu_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                stu_class TEXT NOT NULL,
                                stu_sex TEXT NOT NULL,
                                stu_seat_num INTEGER NOT NULL,
                                stu_name TEXT NOT NULL,
                                stu_uuid TEXT NOT NULL,
                                stu_qr_uuid TEXT,
                                in_date TIMESTAMP NOT NULL)''')
        # 創建教師資料表
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS Users(
                                user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                user_account TEXT NOT NULL,
                                user_password TEXT NOT NULL,
                                user_uuid TEXT NOT NULL,
                                user_failed_login INTEGER Default 0,
                                lock_date TIMESTAMP Default NULL,
                                Login_time TIMESTAMP,
                                Logout_time TIMESTAMP,
                                create_date TIMESTAMP)''')
        # 創建權限資料表
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS Permissions(
                                permission_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                action TEXT NOT NULL)''')
        # 創建使用者權限資料表
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS User_permissions(
                                permission_id INTEGER,
                                uuid TEXT,
                                PRIMARY KEY (uuid, permission_id),
                                FOREIGN KEY (uuid) REFERENCES Users(user_id),
                                FOREIGN KEY (permission_id) REFERENCES Permissions(permission_id))''')
        # 創建模型資料表
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS Model(
                                model_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                model_name TEXT NOT NULL,
                                model_path TEXT NOT NULL,
                                model_parameter TEXT NOT NULL,
                                model_date TIMESTAMP NOT NULL)''')
        # 創建腳本資料表
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS Script(
                                script_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                script_name TEXT NOT NULL,
                                script_brick_path TEXT NOT NULL,
                                script_date TIMESTAMP NOT NULL)''')
        # 創建學生練習資料表
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS Practice(
                                practice_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                stu_uuid INTEGER NOT NULL,
                                model_id INTEGER NOT NULL,
                                script_id INTEGER NOT NULL,
                                score INTEGER NOT NULL,
                                practice_start_date TIMESTAMP NOT NULL,
                                practice_end_date TIMESTAMP NOT NULL,
                                FOREIGN KEY (stu_uuid) REFERENCES Students(stu_uuid),
                                FOREIGN KEY (model_id) REFERENCES Model(model_id),
                                FOREIGN KEY (script_id) REFERENCES Script(script_id))''')
        
        
        self.conn.commit() # 提交數據庫


if __name__ == '__main__':
    CreateDataBase()
    print("數據庫創建成功")