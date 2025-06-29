import uuid
from datetime import datetime, timedelta
from PyQt5.QtCore import QTimer

class User:
    """
    負責處理使用者註冊、登入、鎖定與切換介面等功能
    """

    def __init__(self, db, ui, main_window):
        """
        初始化 User 類別

        Args:
            db: 資料庫連線物件（含 cursor）
            ui: 登入/註冊介面的 UI 元件（PyQt5 對象）
            main_window: 登入主視窗（PyQt5 QMainWindow）
        """
        self.db = db
        self.ui = ui
        self.main_window = main_window
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_lock_time)
        self.lock_remaining_seconds = 0
        self.current_locked_user = None
        self.ui.txt_login.setText("")

    def Register_user(self):
        """
        註冊新使用者帳號，進行重複性與密碼檢查後寫入資料庫
        """
        user_account = self.ui.register_account.text()
        user_pwd = self.ui.register_password_1.text()
        user_check_pwd = self.ui.register_password_2.text()
        user_uuid = str(uuid.uuid4())

        if not user_account.strip() or not user_pwd.strip():
            self.ui.txt_login.setText("帳號密碼不得為空")
            return

        try:
            self.db.cursor.execute("SELECT user_account FROM Users WHERE user_account=?", (user_account,))
            if self.db.cursor.fetchone():
                self.ui.txt_login.setText("帳號不可用，請換另一個")
                return

            if user_pwd != user_check_pwd:
                self.ui.txt_login.setText("密碼不同")
                return

            self.db.cursor.execute('''
                INSERT INTO Users (user_account, user_password, user_uuid, create_date, user_failed_login, lock_date)
                VALUES (?, ?, ?, datetime('now'), 0, NULL)
            ''', (user_account, user_pwd, user_uuid))
            self.db.conn.commit()
            self.ui.txt_login.setText("註冊成功")

        except Exception as e:
            self.ui.txt_login.setText("註冊失敗")
            print(f"註冊失敗={e}")

    def check_login(self, account):
        """
        檢查帳號是否處於鎖定狀態

        Args:
            account (str): 欲檢查的帳號名稱

        Returns:
            bool: 若帳號鎖定中回傳 True，否則 False
        """
        self.db.cursor.execute("SELECT user_failed_login, lock_date FROM Users WHERE user_account=?", (account,))
        user_data = self.db.cursor.fetchone()

        if not user_data:
            return False

        _, lock_until = user_data

        if lock_until:
            lock_until_time = datetime.fromisoformat(lock_until)
            now_time = datetime.now()

            if now_time < lock_until_time:
                self.lock_remaining_seconds = (lock_until_time - now_time).seconds
                self.current_locked_user = account
                self.timer.start(1000)
                return True
            else:
                self.reset_failed_attempts(account)

        return False

    def login_user(self):
        """
        執行使用者登入流程，包含驗證、鎖定邏輯與成功後跳轉頁面
        """
        user_account = self.ui.Login_account.text()
        user_pwd = self.ui.Login_password.text()

        if self.check_login(user_account):
            return

        self.db.cursor.execute(
            "SELECT * FROM Users WHERE user_account=? AND user_password=?", 
            (user_account, user_pwd)
        )
        user = self.db.cursor.fetchone()

        if user:
            self.ui.txt_login.setText("登入成功")
            self.reset_failed_attempts(user_account)
            user_uuid = user[3]  # UUID 位於第4欄
            return self.switch_to_teacher_window(user_uuid)
        else:
            self.db.cursor.execute("SELECT user_failed_login FROM Users WHERE user_account=?", (user_account,))
            user_data = self.db.cursor.fetchone()

            if not user_data:
                self.ui.txt_login.setText("帳號或密碼錯誤")
                return

            user_failed_attempts = user_data[0] + 1

            if user_failed_attempts >= 3:
                lock_until = datetime.now() + timedelta(minutes=5)
                self.db.cursor.execute(
                    "UPDATE Users SET user_failed_login=?, lock_date=? WHERE user_account=?", 
                    (user_failed_attempts, lock_until.isoformat(), user_account)
                )
                self.lock_remaining_seconds = 5 * 60
                self.current_locked_user = user_account
                self.timer.start(1000)
                self.ui.txt_login.setText("密碼錯誤達三次，鎖定五分鐘")
            else:
                self.db.cursor.execute(
                    "UPDATE Users SET user_failed_login=? WHERE user_account=?", 
                    (user_failed_attempts, user_account)
                )
                self.ui.txt_login.setText("帳號或密碼錯誤")

            self.db.conn.commit()

    def reset_failed_attempts(self, account):
        """
        重置帳號的登入錯誤次數與解鎖

        Args:
            account (str): 使用者帳號名稱
        """
        self.db.cursor.execute(
            "UPDATE Users SET user_failed_login=0, lock_date=NULL WHERE user_account=?", 
            (account,)
        )
        self.db.conn.commit()

    def update_lock_time(self):
        """
        每秒更新鎖定倒數時間的 UI 顯示，時間到則自動解除鎖定
        """
        if self.lock_remaining_seconds > 0:
            minutes = self.lock_remaining_seconds // 60
            seconds = self.lock_remaining_seconds % 60
            self.ui.txt_login.setText(f"帳號鎖定中，請 {minutes} 分 {seconds} 秒後再試")
            self.lock_remaining_seconds -= 1
        else:
            self.timer.stop()
            self.ui.txt_login.setText("")
            self.reset_failed_attempts(self.current_locked_user)
            self.current_locked_user = None

    def clear_lock_status(self):
        """
        切換到註冊頁時清除鎖定倒數資訊
        """
        self.timer.stop()
        self.lock_remaining_seconds = 0
        self.current_locked_user = None
        self.ui.txt_login.setText("")

    def switch_to_teacher_window(self, user_uuid):
        """
        切換至教師主頁面並傳入該使用者 UUID

        Args:
            user_uuid (str): 登入成功者之 UUID

        Returns:
            Teacher_mode: 教師主介面實例
        """
        from module.qt_main import Teacher_mode  # 延遲導入以避免循環
        self.win = Teacher_mode(user_uuid=user_uuid)
        self.win.show()
        self.main_window.close()
        return self.win
