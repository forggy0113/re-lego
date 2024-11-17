import sqlite3
import uuid
from teacher_mode_ui import Ui_MainWindow as teacher_mode
from PyQt6.QtWidgets import QFileDialog, QMessageBox,QMainWindow
from PyQt6 import QtWidgets
from PyQt6 import QtGui, QtCore
import pandas as pd
import os
import qrcode
from PIL import Image, ImageDraw, ImageFont

class CreateDatabase:
    # 創建資料庫
    def __init__(self, db_name='test_database.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        # 創建資料表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Students (
            stu_id TEXT PRIMARY KEY NOT NULL,
            stu_class TEXT NOT NULL,
            stu_sex TEXT NOT NULL,                 
            stu_seat_num INTEGER NOT NULL,
            stu_name TEXT NOT NULL,
            in_date TIMESTAMP
        )''')
        self.conn.commit()

class Stus:
    def __init__(self, db, ui):  # 只接受 db 和 ui 兩個參數
        self.db = db
        self.ui = ui
        
    def add_stu(self):
        stu_id = str(uuid.uuid4())  # 生成唯一的学生 ID
        stu_name = self.ui.input_name.text()  # 访问 input_name
        stu_class = self.ui.input_class.text()  # 访问 input_class
        
        # 将输入的座位号转换为整数，确保输入有效
        try:
            stu_seat_num = int(self.ui.input_seat_number.text()) if self.ui.input_seat_number.text() else 0  # 默认座位号为 0
        except ValueError:
            stu_seat_num = 0  # 如果輸入無效，默認為0
            print("座位號無效，默認值 0。")
        
        stu_sex = self.ui.input_sex.currentText()  # 訪問下拉選單
        
        # 插入數據到數據庫
        try:
            self.db.cursor.execute('''
            INSERT INTO Students (stu_class, stu_sex, stu_seat_num, stu_name, stu_id, in_date) VALUES (?, ?, ?, ?, ?, datetime('now'))
            ''', (stu_class, stu_sex, stu_seat_num, stu_name, stu_id))
            self.db.conn.commit()
        except Exception as e:
            print(f"添加学生失败: {e}")

    def display_students(self):
        self.ui.table_stu.setRowCount(0)  # 清空现有行

        # 從資料庫獲取學生資料
        try:
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