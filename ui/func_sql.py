import sqlite3
import uuid
from teacher_mode_ui import Ui_MainWindow as teacher_mode
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import QtWidgets

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
            
            button1 = QtWidgets.QPushButton(f"Button 1-{row_index + 1}")
            button2 = QtWidgets.QPushButton(f"Button 2-{row_index + 1}")
            button3 = QtWidgets.QPushButton(f"Button 3-{row_index + 1}")
            layout.addWidget(button1)
            layout.addWidget(button2)
            layout.addWidget(button3)
            
            layout.setSpacing(10)
            layout.setContentsMargins(0, 0, 0, 0)
            self.ui.table_stu.setCellWidget(row_index, 5, button_widget)

    # 自动調整行高
        self.ui.table_stu.resizeRowsToContents()


    def clear_edit(self):
        # 清空输入框的内容
        self.ui.input_name.clear()  # 清空姓名输入框
        self.ui.input_class.clear()  # 清空班级输入框
        self.ui.input_seat_number.clear()  # 清空座位号输入框
        self.ui.input_sex.setCurrentIndex(0)  # 重置性别下拉框到第一个选项