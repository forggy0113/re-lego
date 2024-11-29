import sqlite3
import uuid
from PyQt6.QtWidgets import QMessageBox, QMainWindow
from PyQt6 import QtWidgets, QtGui, QtCore
from datetime import datetime, timedelta
from main_teacher import teacher_window

# # 初始化Users
class Users:
    # 初始化資料表所需參數
    def __init__(self ,db, ui,main_window):
        self.db = db
        self.ui = ui
        self.main_window = main_window
        
    # 註冊
    def register_user(self):
        user_account = self.ui.register_account.text()
        user_pwd = self.ui.register_password_1.text()
        user_check_pwd = self.ui.register_password_2.text()
        user_uuid = str(uuid.uuid4())
        # 搜索
        self.ui.stackedWidget.setCurrentIndex(1)
        # 註冊時帳號密碼不能為空白
        if  not user_account.strip() or not user_pwd.strip(): #判斷去掉空白後是否為空
                self.ui.stackedWidget.setCurrentIndex(7)
        else:
            try:
                self.db.cursor.execute('''SELECT user_account from Users where user_account=?''',(user_account,))
                user_data = self.db.cursor.fetchone()
                if not user_data: #判斷此帳號不存在，則可以註冊
                    if user_pwd != user_check_pwd: # 判斷驗證密碼和所輸入密碼是否相同
                        self.ui.stackedWidget.setCurrentIndex(3)
                    else: # 註冊成功
                        self.db.cursor.execute('''INSERT INTO Users (user_account, user_password, user_uuid, in_date) VALUES (?, ?, ?, datetime('now'))''',
                        (user_account, user_pwd, user_uuid))
                        self.db.conn.commit()
                        self.ui.stackedWidget.setCurrentIndex(0)
                else: # 帳號已存在不可註冊
                    self.ui.stackedWidget.setCurrentIndex(2)
            except Exception as e:
                    self.ui.stackedWidget.setCurrentIndex(4)
                    print(f"註冊失敗={e}")
                    
    
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
            
        # 搜尋帳號密碼並回傳
        self.db.cursor.execute("SELECT * FROM Users WHERE user_account = ? AND user_password = ?", (user_account, user_pwd))
        user = self.db.cursor.fetchone()

        if user: # 登入成功
            self.ui.stackedWidget.setCurrentIndex(5)
            self.reset_failed_attempts(user_account)
            self.win = teacher_window()
            self.win.show()
            self.main_window.close()
        else:
            self.record_failed_attempt(user_account)
    
    # 將錯誤次數、鎖定時間歸0
    def reset_failed_attempts(self, user_account): 
        self.db.cursor.execute("UPDATE Users SET user_failed_attempts = 0, lock_until = NULL WHERE user_account = ?", (user_account,))
        self.db.conn.commit()
        
    # 鎖定條件
    def record_failed_attempt(self, user_account):
        # 查詢用戶失敗次數
        self.db.cursor.execute("SELECT user_failed_attempts FROM Users WHERE user_account = ?", (user_account,))
        user = self.db.cursor.fetchone()
        # 
        if user:
            failed_attempts = user[0] + 1
            print(f"次數{failed_attempts}")
            # 如果密碼錯誤達3次，則鎖定五分鐘
            if failed_attempts >= 3:
                lock_until = datetime.now() + timedelta(minutes=1)
                self.db.cursor.execute("UPDATE Users SET user_failed_attempts = ?, lock_until = ? WHERE user_account = ?",
                                    (failed_attempts, lock_until.isoformat(),user_account))
                self.ui.stackedWidget.setCurrentIndex(8)
            else: # 錯誤未達3次，則累加錯誤次數至user_failed_attempts
                self.db.cursor.execute("UPDATE Users SET user_failed_attempts = ? WHERE user_account = ?", (failed_attempts,user_account))
                self.ui.stackedWidget.setCurrentIndex(6) # 帳號密碼錯誤
        else:
            self.ui.stackedWidget.setCurrentIndex(6) # 帳號密碼錯誤

        self.db.conn.commit()

        
    
class Stus:
    def __init__(self, db, ui, main_window):  # 只接受 db 和 ui 兩個參數
        self.db = db
        self.ui = ui
        self.main_window = main_window
    
    def add_stu(self): # 輸入單一筆資料
        stu_uuid = str(uuid.uuid4())  # 生成唯一的学生 ID
        stu_name = self.ui.input_name.text()  # 讀取input_name
        stu_class = self.ui.input_class.text()  # 讀取input_class
        stu_sex = self.ui.input_sex.currentText()  # 訪問下拉選單
        # 為確保輸入有效，將座位輸入格式轉為int
        try:  
            if self.ui.input_seat_number.text():
                stu_seat_num = int(self.ui.input_seat_number.text())
            else: 0  # 默認座號為0
        except ValueError:
            stu_seat_num = 0  # 如果輸入無效，默認為0
            print("座位號無效，默認值 0。")
        
        # 插入數據到數據庫
        try:
            self.db.cursor.execute('''
            INSERT INTO Students (stu_class, stu_sex, stu_seat_num, stu_name, stu_id, in_date) VALUES (?, ?, ?, ?, ?, datetime('now'))
            ''', (stu_class, stu_sex, stu_seat_num, stu_name, stu_uuid))
            self.db.conn.commit()
            QMessageBox.information(self.main_window, '成功', '添加學生成功')
        except Exception as e:
            QMessageBox.information(self.main_window, '失敗', '添加學生失敗')
            print(f"添加学生失敗: {e}")

    def display_students(self):
        self.ui.table_stu.setRowCount(0)  # 清空現有行
        try: # 從資料庫獲取學生資料
            self.db.cursor.execute("SELECT stu_class, stu_sex, stu_seat_num, stu_name, stu_id FROM Students")
            rows = self.db.cursor.fetchall()
        except Exception as e:
            print(f"獲取學生資料失敗: {e}")
            return
        # 設置表格行數
        self.ui.table_stu.setRowCount(len(rows))

        for row_index, row in enumerate(rows):
            for column_index, item in enumerate(row):
                try:
                    qtablewidgetitem = QtWidgets.QTableWidgetItem(str(item))
                    self.ui.table_stu.setItem(row_index, column_index, qtablewidgetitem)
                except Exception as e:
                    print(f"設置表格項失敗: {e}")

        # 添加按紐到最后一列
        for row_index in range(len(rows)):
            button_widget = QtWidgets.QWidget()
            layout = QtWidgets.QHBoxLayout(button_widget)
            
            button1 = QtWidgets.QPushButton()
            button2 = QtWidgets.QPushButton()
            button3 = QtWidgets.QPushButton()
            layout.addWidget(button1)
            layout.addWidget(button2)
            layout.addWidget(button3)
            icon14 = QtGui.QIcon()
            icon14.addPixmap(QtGui.QPixmap("c:\\Users\\Ada\\Desktop\\github\\re-lego\\ui\\icon_0925/qr_code.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
            button1.setIcon(icon14)
            button1.setIconSize(QtCore.QSize(35, 35))
            button1.setObjectName("btn_database_qrcode")
            button1.setStyleSheet("#btn_database_qrcode{\n"
"border:none;\n"
"border-radius :6px;\n"
"background-color:#EEEEEE;\n"
"}\n"
"\n"
"#btn_database_qrcode:hover{\n"
"border:none;\n"
"border-radius :6px;\n"
"background-color:#B7B7B7;\n"
"}\n"
"\n"
"#btn_database_qrcode:check{\n"
"border:none;\n"
"border-radius :6px;\n"
"background-color:#B7B7B7;\n"
"}")
            icon15 = QtGui.QIcon()
            icon15.addPixmap(QtGui.QPixmap("c:\\Users\\Ada\\Desktop\\github\\re-lego\\ui\\icon_0925/modify_data.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
            button2.setIcon(icon15)
            button2.setIconSize(QtCore.QSize(35, 35))
            button2.setObjectName("btn_database_modify_data")
            button2.setStyleSheet("#btn_database_modify_data{\n"
"border:none;\n"
"border-radius :6px;\n"
"background-color:#FFCF9D;\n"
"}\n"
"\n"
"#btn_database_modify_data:hover{\n"
"border:none;\n"
"border-radius :6px;\n"
"background-color: #DE8F5F;\n"
"}\n"
"\n"
"#btn_database_modify_data:check{\n"
"border:none;\n"
"border-radius :6px;\n"
"background-color:#DE8F5F;\n"
"}")
            icon16 = QtGui.QIcon()
            icon16.addPixmap(QtGui.QPixmap("c:\\Users\\Ada\\Desktop\\github\\re-lego\\ui\\icon_0925/delete.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
            button3.setIcon(icon16)
            button3.setIconSize(QtCore.QSize(35, 35))
            button3.setObjectName("btn_database_delect")
            button3.setStyleSheet("#btn_database_delect{\n"
"border:none;\n"
"border-radius :6px;\n"
"background-color: #ffeb9a;\n"
"}\n"
"\n"
"#btn_database_delect:hover{\n"
"border:none;\n"
"border-radius :6px;\n"
"background-color:#FFCD00;\n"
"}\n"
"\n"
"#btn_database_delect:check{\n"
"border:none;\n"
"border-radius :6px;\n"
"background-color: #FFCD00;\n"
"}")
            layout.setSpacing(10)
            layout.setContentsMargins(2, 2, 2, 2)
            self.ui.table_stu.setCellWidget(row_index, 5, button_widget)

    # 自动調整行高
        self.ui.table_stu.resizeRowsToContents()


    def clear_edit(self):
        # 清空输入框的内容
        self.ui.input_name.clear()  # 清空姓名输入框
        self.ui.input_class.clear()  # 清空班级输入框
        self.ui.input_seat_number.clear()  # 清空座位号输入框
        self.ui.input_sex.setCurrentIndex(0)  # 重置性別下拉框到第一個選項

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # 创建Qrcode实例并传入主窗口作为父窗口
        self.qrcode = Qrcode(parent=self)

class Qrcode:
    def __init__(self, db_name, folder_path):
        self.db_name = db_name
        self.folder_path = folder_path
    def all_qrcode(self):
        # 確保資料夾存在
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)
        # 連接資料庫
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        # 查詢所有uuid
        try:
            cursor.execute("select stu_id, stu_class, stu_seat_num, stu_name from Students")
            rows = cursor.fetchall()
        except Exception as e:
            print(f"獲取uuid失敗:{e}")
            return
        for uuid_row,stu_class_row, stu_seat_num_row, stu_name_row  in rows:
            uuid_str =uuid_row #取得uuid字串
            class_str = stu_class_row
            seat_num_str = stu_seat_num_row 
            name_str = stu_name_row
            # 生成qrcode
            qr = qrcode.make(uuid_str)
            qr_image = qr.convert("RGB")
            # 繪製qrcode
            draw = ImageDraw.Draw(qr_image)
            try:
                font = ImageFont.truetype("font\BpmfGenSenRounded-R.ttf", size=20)
            except IOError:
                # 加載默認字體
                font = ImageFont.load_default()
            text = f"{class_str}_{seat_num_str}_{name_str}"
            text_bbox = draw.textbbox((0,0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0] # 右邊界 - 左邊界
            text_height = text_bbox[3] - text_bbox[1] # 下邊界 - 上邊界
            
            qr_width, qr_height = qr_image.size
            text_x = (qr_width - text_width) //2
            text_y = (qr_height-text_height)-10 # 留底部空間
            # 繪製文字
            draw.text((text_x, text_y), text, fill='black', font=font)
            # 圖片名
            qr_filename = os.path.join(self.folder_path,f"{class_str}_{seat_num_str}_{name_str}.png")
            qr_image.save(qr_filename)
            print(f"生成qrcode:{qr_filename}")
        QMessageBox.information(None, '成功', '學生QRcode已生成')
    
        conn.close()



def import_csv_to_db(self, file_name):
    try:
        db_path = 'test_database.db'
        table_path = 'Students'
        df = pd.read_csv(file_name, encoding='utf-8-sig')
        if 'stu_id' not in df.columns:
            df['stu_id'] = [str(uuid.uuid4()) for _ in range(len(df))]

        conn = sqlite3.connect(db_path)
        df.to_sql(table_path, conn, if_exists='append', index=False)
        
        conn.close()
        QMessageBox.information(self, '成功', 'csv文件已成功導入數據庫')
        
    except Exception as e:
        QMessageBox.critical(self, '錯誤', f"導入失敗:{str(e)}")