import sqlite3
import uuid
from PyQt6.QtWidgets import QMessageBox, QMainWindow
from PyQt6 import QtWidgets, QtGui, QtCore
from datetime import datetime, timedelta
from main_teacher import teacher_window
# from main_children import Login_Window

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

# # 初始化Users
class Users:
    # 初始化資料表所需參數
    def __init__(self ,db, ui,main_window):
        self.db = db
        self.ui = ui
        self.main_window = main_window

    def register_user(self):
        user_account = self.ui.register_account.text()
        user_pwd = self.ui.register_password_1.text()
        user_check_pwd = self.ui.register_password_2.text()
        user_uuid = str(uuid.uuid4())
        self.db.cursor.execute('''SELECT user_account from Users where user_account=?''',(user_account,))
        user_data = self.db.cursor.fetchone()
        # 如果是非帳號的
        if  not user_data:
            try:
                if user_pwd != user_check_pwd:
                    self.ui.stackedWidget.setCurrentIndex(3)
                else:
                    self.db.cursor.execute('''INSERT INTO Users (user_account, user_password, user_uuid, in_date) VALUES (?, ?, ?, datetime('now'))''',
                       (user_account, user_pwd, user_uuid))
                    self.db.conn.commit()
                    self.ui.stackedWidget.setCurrentIndex(0)  
            except Exception as e:
                self.ui.stackedWidget.setCurrentIndex(4)
        else:
            self.ui.stackedWidget.setCurrentIndex(2)
                

    
    def login_user(self):
        user_account = self.ui.Login_account.text()
        user_pwd = self.ui.Login_password.text()
        
        # 判斷帳戶是否被鎖定中
        self.db.cursor.execute("SELECT user_failed_attempts, lock_until FROM Users WHERE user_account = ?", (user_account,))
        user_data = self.db.cursor.fetchone()
        # 如果帳戶被鎖定，檢查鎖定時間是否已經過期
        if user_data:
            user_failed_attempts, lock_until = user_data
            if lock_until:
                lock_until_time = datetime.fromisoformat(lock_until)
                # 如果當前時間超過了鎖定時間，則重置失敗次數並解除鎖定
                if datetime.now() > lock_until_time:
                    self.reset_failed_attempts(user_account)
                else:
                    remaining_time = (lock_until_time - datetime.now()).seconds
                    self.ui.label_lock.setText(f"錯誤，帳號被鎖定請{remaining_time//60}分{remaining_time%60}秒後再試")
                return
                # 如果帳戶被鎖定，檢查鎖定時間是否已經過期
                
        self.db.cursor.execute("SELECT * FROM Users WHERE user_account = ? AND user_password = ?", (user_account, user_pwd))
        user = self.db.cursor.fetchone()

        if user:
            self.ui.stackedWidget.setCurrentIndex(5)
            self.reset_failed_attempts(user_account)
            self.win = teacher_window()
            self.win.show()
            self.main_window.close()
        else:
            self.record_failed_attempt(user_account)
  
    def reset_failed_attempts(self, user_account):
        self.db.cursor.execute("UPDATE Users SET user_failed_attempts = 0, lock_until = NULL WHERE user_account = ?", (user_account,))
        self.db.conn.commit()
    
    def record_failed_attempt(self, user_account):
        self.db.cursor.execute("SELECT user_failed_attempts FROM Users WHERE user_account = ?", (user_account,))
        user = self.db.cursor.fetchone()

        if user:
            failed_attempts = user[0] + 1
            print(f"次數{failed_attempts}")
            if failed_attempts >= 3:
                lock_until = datetime.now() + timedelta(minutes=1)
                self.db.cursor.execute("UPDATE Users SET user_failed_attempts = ?, lock_until = ? WHERE user_account = ?",
                                    (failed_attempts, lock_until.isoformat(),user_account))
                self.ui.stackedWidget.setCurrentIndex(8)
            else:
                self.db.cursor.execute("UPDATE users SET user_failed_attempts = ? WHERE user_account = ?", (failed_attempts,user_account))
                self.ui.stackedWidget.setCurrentIndex(7)
        else:
            self.ui.stackedWidget.setCurrentIndex(6)

        self.db.conn.commit()

        
    
        