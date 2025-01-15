import sqlite3

class CreateDatabase:
    def __init__(self, db_name='test_database.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()
    
    def create_table(self):
    # 學生資料表
        self.cursor.execute('''
                        CREATE TABLE IF NOT EXISTS Students(
                            stu_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
                            stu_class TEXT NOT NULL,
                            stu_sex TEXT NOT NULL,
                            stu_seat_num INTEGER NOT NULL,
                            stu_name TEXT NOT NULL,
                            stu_uuid TEXT NOT NULL,
                            stu_qr_uuid TEXT NOT NULL,
                            in_date TIMESTAMP)''')

    # 老師/家長資料表
        self.cursor.execute('''
                        CREATE TABLE IF NOT EXISTS Users(
                            user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                            user_account TEXT NOT NULL,
                            user_password TEXT NOT NULL,
                            user_uuid TEXT NOT NULL,
                            user_failed_attempts INTEGER DEFAULT 0,
                            lock_until TEXT DEFAULT NULL,
                            in_date TIMESTAMP)''')

    # 權限動作資料表
        self.cursor.execute('''
                        CREATE TABLE IF NOT EXISTS permissions(
                            permission_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                            action TEXT NOT NULL)''')

    # 使用者權限分配
        self.cursor.execute('''
                        CREATE TABLE IF NOT EXISTS user_permissions(
                            permission_id INTEGER,
                            uuid TEXT,
                            FOREIGN KEY (uuid) REFERENCES Users (user_uuid),
                            FOREIGN KEY (permission_id) REFERENCES permissions (permission_id),
                            PRIMARY KEY (uuid, permission_id))''')

    # 提交至sqlite
        self.conn.commit()
