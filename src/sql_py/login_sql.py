import uuid
from datetime import datetime, timedelta
from ui_main import teacher_window

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

    def login_user(self):
        user_account = self.ui.Login_account.text()
        user_pwd = self.ui.Login_password.text()

        self.db.cursor.execute("SELECT user_failed_attempts, lock_until FROM Users WHERE user_account = ?", (user_account,))
        user_data = self.db.cursor.fetchone()

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

# class Stus:
#     def __init__(self, db, ui, main_window):
#         self.db = db
#         self.ui = ui
#         self.main_window = main_window

#     def add_stu(self):
#         stu_uuid = str(uuid.uuid4())
#         stu_name = self.ui.input_name.text()
#         stu_class = self.ui.input_class.text()
#         stu_sex = self.ui.input_sex.currentText()

#         try:
#             stu_seat_num = int(self.ui.input_seat_number.text()) if self.ui.input_seat_number.text() else 0
#         except ValueError:
#             stu_seat_num = 0

#         try:
#             self.db.cursor.execute(
#                 '''INSERT INTO Students (stu_class, stu_sex, stu_seat_num, stu_name, stu_id, in_date) VALUES (?, ?, ?, ?, ?, datetime('now'))''',
#                 (stu_class, stu_sex, stu_seat_num, stu_name, stu_uuid)
#             )
#             self.db.conn.commit()
#             QMessageBox.information(self.main_window, '成功', '添加學生成功')
#         except Exception as e:
#             QMessageBox.information(self.main_window, '失敗', '添加學生失敗')
#             print(f"添加學生失敗: {e}")

#     def display_students(self):
#         self.ui.table_stu.setRowCount(0)
#         try:
#             self.db.cursor.execute("SELECT stu_class, stu_sex, stu_seat_num, stu_name, stu_id FROM Students")
#             rows = self.db.cursor.fetchall()
#         except Exception as e:
#             print(f"獲取學生資料失敗: {e}")
#             return

#         self.ui.table_stu.setRowCount(len(rows))

#         for row_index, row in enumerate(rows):
#             for column_index, item in enumerate(row):
#                 try:
#                     self.ui.table_stu.setItem(row_index, column_index, QTableWidgetItem(str(item)))
#                 except Exception as e:
#                     print(f"設置表格項失敗: {e}")

#         for row_index in range(len(rows)):
#             button_widget = QWidget()
#             layout = QHBoxLayout(button_widget)

#             button1 = QPushButton()
#             button2 = QPushButton()
#             button3 = QPushButton()
#             layout.addWidget(button1)
#             layout.addWidget(button2)
#             layout.addWidget(button3)

#             button1.setIcon(QtGui.QIcon("path_to_icon_1"))
#             button2.setIcon(QtGui.QIcon("path_to_icon_2"))
#             button3.setIcon(QtGui.QIcon("path_to_icon_3"))

#             self.ui.table_stu.setCellWidget(row_index, 5, button_widget)

#         self.ui.table_stu.resizeRowsToContents()

#     def clear_edit(self):
#         self.ui.input_name.clear()
#         self.ui.input_class.clear()
#         self.ui.input_seat_number.clear()
#         self.ui.input_sex.setCurrentIndex(0)

# class MainWindow(QMainWindow):
#     def __init__(self):
#         super(MainWindow, self).__init__()

# class Qrcode:
#     def __init__(self, db_name, folder_path):
#         self.db_name = db_name
#         self.folder_path = folder_path

#     def all_qrcode(self):
#         if not os.path.exists(self.folder_path):
#             os.makedirs(self.folder_path)

#         conn = sqlite3.connect(self.db_name)
#         conn.cursor()
#         # Your database logic here
#         conn.close()
