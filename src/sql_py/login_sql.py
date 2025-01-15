import uuid
from datetime import datetime, timedelta
from ui_main import teacher_window
from src.sql_py.encrypted import Encrypted

# 初始化 Users
class Users:
    def __init__(self, db, ui, main_window):
        self.db = db
        self.ui = ui
        self.main_window = main_window

    # 註冊
    def register_user(self):
        user_account = self.ui.register_account.text()
        user_pwd = self.ui.register_password_1.text()
        user_check_pwd = self.ui.register_password_2.text()
        user_uuid = str(uuid.uuid4())
        user_uuid = Encrypted().encrypt(user_uuid)
        self.ui.stackedWidget.setCurrentIndex(1)

        if not user_account.strip() or not user_pwd.strip():
            self.ui.stackedWidget.setCurrentIndex(7)
        else:
            try:
                self.db.cursor.execute('''SELECT user_account FROM Users WHERE user_account=?''', (user_account,))
                user_data = self.db.cursor.fetchone()

                if not user_data:
                    if user_pwd != user_check_pwd:
                        self.ui.stackedWidget.setCurrentIndex(3)
                    else:
                        self.db.cursor.execute(
                            '''INSERT INTO Users (user_account, user_password, user_uuid, in_date) VALUES (?, ?, ?, datetime('now'))''',
                            (user_account, user_pwd, user_uuid)
                        )
                        self.db.conn.commit()
                        self.ui.stackedWidget.setCurrentIndex(0)
                else:
                    self.ui.stackedWidget.setCurrentIndex(2)
            except Exception as e:
                self.ui.stackedWidget.setCurrentIndex(4)
                print(f"註冊失敗: {e}")
    # 登入帳號
    def login_user(self):
        user_account = self.ui.Login_account.text()
        user_pwd = self.ui.Login_password.text()

        self.db.cursor.execute("SELECT user_failed_attempts, lock_until FROM Users WHERE user_account = ?", (user_account,))
        user_data = self.db.cursor.fetchone()
        # 鎖定判斷計時
        if user_data:
            user_failed_attempts, lock_until = user_data
            if lock_until:
                lock_until_time = datetime.fromisoformat(lock_until)
                if datetime.now() > lock_until_time:
                    self.reset_failed_attempts(user_account)
                else:
                    remaining_time = (lock_until_time - datetime.now()).seconds
                    self.ui.label_lock.setText(f"錯誤，帳號被鎖定請{remaining_time // 60}分{remaining_time % 60}秒後再試")
                    return

        self.db.cursor.execute("SELECT * FROM Users WHERE user_account = ? AND user_password = ?", (user_account, user_pwd))
        user = self.db.cursor.fetchone()
        # 登入成功
        if user:
            self.ui.stackedWidget.setCurrentIndex(5)
            self.reset_failed_attempts(user_account)
            print(bool(user))
            self.win = teacher_window()
            self.win.show()
            self.main_window.close()
        else:
            self.record_failed_attempt(user_account)
            print(bool(user))
            
    # 重置失敗次數
    def reset_failed_attempts(self, user_account):
        self.db.cursor.execute("UPDATE Users SET user_failed_attempts = 0, lock_until = NULL WHERE user_account = ?", (user_account,))
        self.db.conn.commit()

    def record_failed_attempt(self, user_account):
        self.db.cursor.execute("SELECT user_failed_attempts FROM Users WHERE user_account = ?", (user_account,))
        user = self.db.cursor.fetchone()

        if user:
            failed_attempts = user[0] + 1
            if failed_attempts >= 3:
                lock_until = datetime.now() + timedelta(minutes=1)
                self.db.cursor.execute(
                    "UPDATE Users SET user_failed_attempts = ?, lock_until = ? WHERE user_account = ?",
                    (failed_attempts, lock_until.isoformat(), user_account)
                )
                self.ui.stackedWidget.setCurrentIndex(8)
            else:
                self.db.cursor.execute("UPDATE Users SET user_failed_attempts = ? WHERE user_account = ?", (failed_attempts, user_account))
                self.ui.stackedWidget.setCurrentIndex(6)
        else:
            self.ui.stackedWidget.setCurrentIndex(6)

        self.db.conn.commit()
