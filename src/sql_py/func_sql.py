from PyQt5.QtWidgets import QFileDialog, QMessageBox,QPushButton
from PyQt5 import QtWidgets,QtGui, QtCore
import sqlite3
import uuid
import pandas as pd
import os
import qrcode
from PIL import ImageDraw, ImageFont
from src.sql_py.encrypted import Encrypted
import time
class Stus:
    def __init__(self, db, ui,main_window):  # 只接受 db 和 ui 兩個參數
        self.db = db
        self.ui = ui
        self.main_window = main_window
        
    def add_stu(self):
        stu_uuid = str(uuid.uuid4())  # 生成唯一的學生 ID
        stu_qr_uuid =  Encrypted().encrypt(stu_uuid) # 加密uuid
        stu_name = self.ui.input_name.text()  # 讀取input_name
        stu_class = self.ui.input_class.text()  # 讀取 input_class
        stu_sex = self.ui.input_sex.currentText()  # 訪問下拉選單
        # 輸入帳號轉為整數，確保輸入有效
        try:
            if self.ui.input_seat_number.text():
                stu_seat_num = int(self.ui.input_seat_number.text())
            else: 0  # 默認座號為0
        except ValueError:
            stu_seat_num = 0  # 如果輸入無效，默認為0
            print("座位號無效，默認值 0")
        
        # 插入數據到數據庫
        try:
            self.db.cursor.execute('''
            INSERT INTO Students (stu_class, stu_sex, stu_seat_num, stu_name, stu_uuid,stu_qr_uuid, in_date) VALUES (?, ?, ?, ?, ?,?, datetime('now'))
            ''', (stu_class, stu_sex, stu_seat_num, stu_name, stu_uuid, stu_qr_uuid))
            self.db.conn.commit()
            QMessageBox.information(self.main_window, "成功","學生添加成功")
        except Exception as e:
            print(f"添加學生失敗: {e}")
            QMessageBox.information(self.main_window, "失敗","學生添加失敗")
        
    def add_csv(self):
        # 彈出視窗選擇檔案
        file_name, _ =  QFileDialog.getOpenFileName(self.main_window, "選擇csv文件",'', '(*.csv)')
        if file_name:
            try:
                df = pd.read_csv(file_name, encoding='utf-8-sig') # 讀取csv檔案
                required_columns = {'stu_class', 'stu_sex', 'stu_seat_num', 'stu_name'}
                if not required_columns.issubset(df.columns):
                    QMessageBox.information(self.main_window, "失敗", "csv文件缺少必要欄位值")
                    return
                # 如果stu_uuid不存在，則生成uuid
                if 'stu_uuid' not in df.columns:
                    df['stu_uuid'] = [str(uuid.uuid4()) for _ in range(len(df))]
                    df['stu_qr_uuid'] = [Encrypted().encrypt(uuid) for uuid in df['stu_uuid']]

                # 批量插入數據
                self.db.cursor.executemany('''
                                           INSERT INTO Students (stu_class, stu_sex, stu_seat_num, stu_name, stu_uuid, stu_qr_uuid, in_date)
                                           VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                                           ''', df[['stu_class', 'stu_sex', 'stu_seat_num', 'stu_name', 'stu_uuid','stu_qr_uuid']].values.tolist())
                self.db.conn.commit()
                QMessageBox.information(self.main_window, "成功","學生添加成功")
            except Exception as e:
                QMessageBox.information(self.main_window, "失敗","學生添加失敗")
                print(f"添加学生失敗: {e}")
    
    def clear_edit(self):
        # 清空输入框的内容
        self.ui.input_name.clear()  # 清空姓名输入框
        self.ui.input_class.clear()  # 清空輸入班級框
        self.ui.input_seat_number.clear()  # 清空座位号输入框
        self.ui.input_sex.setCurrentIndex(0)  # 重置性別下拉框到第一個選項
    

    def display_students(self):
        self.ui.table_stu.setRowCount(0)  # 清空現有行
        # 從資料庫獲取學生資料
        try:
            self.db.cursor.execute("SELECT stu_class, stu_sex, stu_seat_num, stu_name FROM Students")
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

        for row_index in range(self.ui.table_stu.rowCount()):
            qr_button = QPushButton("QRcode")
            modify_button = QPushButton("修改學生")
            delete_button = QPushButton("刪除學生")
            icon14 = QtGui.QIcon()
            icon14.addPixmap(QtGui.QPixmap("c:\\Users\\Ada\\Desktop\\github\\re-lego\\ui\\icon/qr_code.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
            qr_button.setIcon(icon14)
            qr_button.setIconSize(QtCore.QSize(35, 35))
            qr_button.setObjectName("btn_database_qrcode")
            qr_button.setStyleSheet("#btn_database_qrcode{\n"
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
            icon15.addPixmap(QtGui.QPixmap("c:\\Users\\Ada\\Desktop\\github\\re-lego\\ui\\icon/modify_data.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
            modify_button.setIcon(icon15)
            modify_button.setIconSize(QtCore.QSize(35, 35))
            modify_button.setObjectName("btn_database_modify_data")
            modify_button.setStyleSheet("#btn_database_modify_data{\n"
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
            icon16.addPixmap(QtGui.QPixmap("c:\\Users\\Ada\\Desktop\\github\\re-lego\\ui\\icon/delete.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
            delete_button.setIcon(icon16)
            delete_button.setIconSize(QtCore.QSize(35, 35))
            delete_button.setObjectName("btn_database_delect")
            delete_button.setStyleSheet("#btn_database_delect{\n"
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
            delete_button.clicked.connect(self.delect_student_row)
            qr_button.clicked.connect(self.stu_qrcode)
            
            self.ui.table_stu.setCellWidget(row_index, 5, qr_button)
            self.ui.table_stu.setCellWidget(row_index, 4, modify_button)
            self.ui.table_stu.setCellWidget(row_index, 6, delete_button)
         

    # 自動調整行高
        self.ui.table_stu.resizeRowsToContents()

    def delect_student_row(self):
        button = self.ui.table_stu.sender() # 獲取按鈕所在行的內容
        if button: # 檢查按鈕是否存在
            try:
                index = self.ui.table_stu.indexAt(button.pos())
                row = index.row()
                item = self.ui.table_stu.item(row, 3) # 得到對應學生姓名
                if row < 0: #無法確定按鈕所在行
                    raise ValueError(f"無法確定按鈕所在行")
                if  item is None or not item.text():
                    raise TypeError("無法獲取學生姓名，該行數據可能為空")
                stu_name = item.text()
                # 刪除學生名字所指資料行
                self.db.cursor.execute('''DELETE FROM Students WHERE stu_name=?''',(stu_name,))
                self.db.conn.commit()
                self.ui.table_stu.removeRow(row)
                self.display_students() # 顯示資料
                self.load_class() # 更新班級資料選單
                QMessageBox.information(self.main_window, "成功","學生資料刪除成功")
                
            except Exception as e:
                self.db.conn.rollback() # 資料庫回滾，恢復資料庫狀態，不受資料刪除失敗影響
                print(f"刪除資料行失敗:{e}")
                QMessageBox.information(self.main_window, "失敗",f"{stu_name}學生資料刪除失敗")
                
    def login_stu(self, uuid ):
        stu_uuid = self.db.cursor.execute('''SELECT stu_name, stu_class, stu_seat_num FROM Students WHERE stu_uuid=?''', (uuid,))
        if stu_uuid:
            stu_name, stu_class, stu_seat_num = stu_uuid.fetchone()
            QMessageBox.information(self.main_window, "成功",f"{stu_name}_{stu_class}_{stu_seat_num}學生登入成功")
            time.sleep(3)
            self.login_win.close()
        else:
            QMessageBox.information(self.main_window, "失敗","學生登入失敗")
            
    
            
    def stu_qrcode(self):
        button = self.ui.table_stu.sender()
        if button:
            try:
                index = self.ui.table_stu.indexAt(button.pos())
                row = index.row()
                item = self.ui.table_stu.item(row, 3)
                if row <0:
                    raise ValueError("無法確定按鈕所在行")
                if item is None or not item.text():
                    raise ValueError("無法獲取學生姓名，該行數據可能為空")
                stu_name = item.text()
                self.db.cursor.execute('''SELECT stu_qr_uuid, stu_class, stu_seat_num, stu_name FROM Students WHERE stu_name=?''', (stu_name,))
                stu_rows = self.db.cursor.fetchall()
                
                for uuid_row,class_row, seat_num_row, name_row  in stu_rows:
                    stu_uuid_row = uuid_row
                    stu_class_row = class_row
                    stu_seat_num_row = seat_num_row
                    stu_name_row = name_row
                    # 生成Qrcode
                    qr_image = qrcode.make(stu_uuid_row )
                    # 繪製qrcode
                    qr_image = qr_image.convert("RGB")
                    draw = ImageDraw.Draw(qr_image)
                    try:
                        font = ImageFont.truetype(r"C:\Users\Ada\Desktop\github\re-lego\ui\font\BpmfGenSenRounded-R.ttf", size=20) #顯示字體
                        print("使用自定義字體")
                    except IOError:
                        font = ImageFont.load_default() # 加載默認字體
                        print("使用默認字體")
                    # 字體位置定義
                    text = f"{stu_class_row}_{stu_seat_num_row}_{stu_name_row}"
                    text_bbox = draw.textbbox((0,0), text, font=font)
                    text_width = text_bbox[2] - text_bbox[0] # 右邊界 - 左邊界
                    text_height = text_bbox[3] - text_bbox[1] # 下邊界 - 上邊界
                    # qr位置定義
                    qr_width, qr_height = qr_image.size
                    text_x = (qr_width - text_width) // 2
                    text_y = (qr_height - text_height) -10 # 留底部空間
                    # 繪製文字
                    draw.text((text_x, text_y), text=text, fill='black',font=font)
                    # 儲存圖片名
                    qr_filename = f"{stu_class_row}_{stu_seat_num_row}_{stu_name_row}.png"
                    qr_image.save(qr_filename)
                    print(f"生成qrcode:{qr_filename}")
                    QMessageBox.information(self.main_window, "成功", f"成功生成{stu_name_row}學生qrcode")
            except Exception as e:
                print(f"生成{stu_name}學生qrcode失敗={e}")
                QMessageBox.information(self.main_window, "失敗", f"生成{stu_name_row}學生qrcode失敗")


    def load_class(self):
        # 從資料庫加載班級選單內容
        try:
            # 查詢資料庫中的所有班級（移除重複值）
            self.db.cursor.execute('''SELECT DISTINCT stu_class FROM Students''')
            class_data = self.db.cursor.fetchall()
            print(class_data)
            # 清空下拉選單
            self.ui.box_search_class.clear()
            # 添加「全部」選項
            self.ui.box_search_class.addItem("全部")  # 預設選項，顯示所有班級

            # 動態添加班級名稱
            for row in class_data:
                class_name = str(row[0]) if row[0] is not None else "未命名班級"
                self.ui.box_search_class.addItem(class_name)
                print(class_name)
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self.main_window, "錯誤", f"無法加載班級資料: {e}")

    def filter_display_students(self, rows):
        self.ui.table_stu.setRowCount(0)  # 清空現有行

        # 設置表格行數
        self.ui.table_stu.setRowCount(len(rows))

        for row_index, row in enumerate(rows):
            for column_index, item in enumerate(row):
                try:
                    qtablewidgetitem = QtWidgets.QTableWidgetItem(str(item))
                    self.ui.table_stu.setItem(row_index, column_index, qtablewidgetitem)
                except Exception as e:
                    print(f"設置表格項失敗: {e}")

            for row_index in range(self.ui.table_stu.rowCount()):
                qr_button = QPushButton("QRcode")
                modify_button = QPushButton("修改學生")
                delete_button = QPushButton("刪除學生")
                icon14 = QtGui.QIcon()
                icon14.addPixmap(QtGui.QPixmap("c:\\Users\\Ada\\Desktop\\github\\re-lego\\ui\\icon/qr_code.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
                qr_button.setIcon(icon14)
                qr_button.setIconSize(QtCore.QSize(35, 35))
                qr_button.setObjectName("btn_database_qrcode")
                qr_button.setStyleSheet("#btn_database_qrcode{\n"
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
                icon15.addPixmap(QtGui.QPixmap("c:\\Users\\Ada\\Desktop\\github\\re-lego\\ui\\icon/modify_data.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
                modify_button.setIcon(icon15)
                modify_button.setIconSize(QtCore.QSize(35, 35))
                modify_button.setObjectName("btn_database_modify_data")
                modify_button.setStyleSheet("#btn_database_modify_data{\n"
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
                icon16.addPixmap(QtGui.QPixmap("c:\\Users\\Ada\\Desktop\\github\\re-lego\\ui\\icon/delete.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
                delete_button.setIcon(icon16)
                delete_button.setIconSize(QtCore.QSize(35, 35))
                delete_button.setObjectName("btn_database_delect")
                delete_button.setStyleSheet("#btn_database_delect{\n"
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
                delete_button.clicked.connect(self.delect_student_row)
                qr_button.clicked.connect(self.stu_qrcode)
                
                self.ui.table_stu.setCellWidget(row_index, 5, qr_button)
                self.ui.table_stu.setCellWidget(row_index, 4, modify_button)
                self.ui.table_stu.setCellWidget(row_index, 6, delete_button)
        # 自動調整行高
        self.ui.table_stu.resizeRowsToContents()
        
    def filter_stu(self):
        """根據篩選條件查詢學生"""
        try:
            # 獲取篩選條件
            stu_class = self.ui.box_search_class.currentText()
            
            # 基本查詢語句，從學生資料中查詢指定欄位
            query = "SELECT stu_class, stu_sex, stu_seat_num, stu_name FROM Students WHERE 1=1"
            params = []

            # 根據條件動態構建查詢語句
            if stu_class != "全部" and stu_class != "":
                query += " AND stu_class=?"
                params.append(stu_class)

            # 執行查詢
            if len(params) > 0:
                self.db.cursor.execute(query, tuple(params))
            else:
                # 如果沒有篩選條件，查詢所有學生
                self.db.cursor.execute("SELECT stu_class, stu_sex, stu_seat_num, stu_name FROM Students")
            
            # 獲取查詢結果
            result = self.db.cursor.fetchall()

            # 顯示查詢結果
            self.filter_display_students(result)

        except Exception as e:
            print(f"查詢過程中出錯: {e}")




class Qrcode:
    def __init__(self, db_name, folder_path, main_window):
        self.db_name = db_name
        self.folder_path = folder_path
        main_window=main_window
    
    def all_qrcode(self):
        # 確保資料夾存在
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)
        # 連接資料庫
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        # 查詢所有uuid
        try:
            cursor.execute("select stu_qr_uuid, stu_class, stu_seat_num, stu_name from Students")
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
                font = ImageFont.truetype("ui\font\BpmfGenSenRounded-R.ttf", size=20)
                print("使用自定義字體")
            except IOError:
                # 加載默認字體
                font = ImageFont.load_default()
                print("使用默認字體")
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
