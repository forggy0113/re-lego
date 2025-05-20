from PyQt5.QtWidgets import QFileDialog, QMessageBox,QPushButton
from PyQt5 import QtWidgets,QtGui, QtCore
import uuid
import pandas as pd
import os
import qrcode
from PIL import ImageDraw, ImageFont

class Stus:
    def __init__(self, db, ui,main_window, encrypted, folder_path, teacher_uuid):  # 只接受 db 和 ui 兩個參數
        self.db = db
        self.ui = ui
        self.main_window = main_window
        self.encrypted = encrypted
        self.folder_path = folder_path
        self.teacher_uuid = teacher_uuid

    def add_stu(self):
        """添加學生"""
        stu_uuid = str(uuid.uuid4())  # 生成唯一的學生 ID
        stu_qr_uuid =  self.encrypted.encrypt(stu_uuid) # 加密uuid
        stu_name = self.ui.input_name.text()  # 讀取input_name
        stu_class = self.ui.input_class.text()  # 讀取 input_class
        stu_sex = self.ui.input_sex.currentText()  # 訪問下拉選單
        # 輸入帳號轉為整數，確保輸入有效
        try:
            if self.ui.input_seat_number.text():
                stu_seat_num = int(self.ui.input_seat_number.text())
            else: 
                stu_seat_num = 0  # 默認座號為0
        except ValueError:
            stu_seat_num = 0  # 如果輸入無效，默認為0
            print("座位號無效，默認值 0")
        
        # 插入數據到數據庫
        try:
            self.db.cursor.execute('''
            INSERT INTO Students (stu_class, stu_sex, stu_seat_num, stu_name, stu_uuid, stu_qr_uuid, in_date) VALUES (?, ?, ?, ?, ?,?, datetime('now'))
            ''', (stu_class, stu_sex, stu_seat_num, stu_name, stu_uuid, stu_qr_uuid))
            self.db.cursor.execute('''INSERT INTO Teacher_Student (user_uuid, stu_uuid) VALUES (?,?)''',
                                   (self.teacher_uuid, stu_uuid))
            self.db.conn.commit()
            QMessageBox.information(self.main_window, "成功","學生添加成功")
        except Exception as e:
            print(f"添加學生失敗: {e}")
            QMessageBox.information(self.main_window, "失敗","學生添加失敗")
        
    def add_csv(self):
        """添加學生_批量"""
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
                    df['stu_qr_uuid'] = [self.encrypted.encrypt(uuid) for uuid in df['stu_uuid']]
                # 建立與老師的關聯關係
                relations = [(self.teacher_uuid, uid) for uid in df['stu_uuid']]
                # 批量插入數據
                self.db.cursor.executemany('''
                                           INSERT INTO Students (stu_class, stu_sex, stu_seat_num, stu_name, stu_uuid, stu_qr_uuid, in_date)
                                           VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                                           ''', df[['stu_class', 'stu_sex', 'stu_seat_num', 'stu_name', 'stu_uuid', 'stu_qr_uuid']].values.tolist())
                self.db.cursor.executemany('''INSERT INTO Teacher_Student (user_uuid, stu_uuid) VALUES (?,?)'''
                                           , relations)
                self.db.conn.commit()
                QMessageBox.information(self.main_window, "成功","學生添加成功")
            except Exception as e:
                QMessageBox.information(self.main_window, "失敗","學生添加失敗")
                print(f"添加学生失敗: {e}")
    
    def clear_edit(self):
        # 清空輸入框的內容
        self.ui.input_name.clear()  # 清空姓名输入框
        self.ui.input_class.clear()  # 清空輸入班級框
        self.ui.input_seat_number.clear()  # 清空座位号输入框
        self.ui.input_sex.setCurrentIndex(0)  # 重置性別下拉框到第一個選項
    

    def display_students(self):
        """
        顯示目前登入老師所屬學生資料。
        包含 stu_class, stu_sex, stu_seat_num, stu_name, stu_uuid, stu_id。
        呼叫 render_table() 顯示。
        """
        try:
            self.db.cursor.execute('''
                SELECT s.stu_class, s.stu_sex, s.stu_seat_num, s.stu_name, s.stu_uuid, s.stu_id
                FROM Students AS s
                JOIN Teacher_Student AS ts ON s.stu_uuid = ts.stu_uuid
                WHERE ts.user_uuid = ?
            ''', (self.teacher_uuid,))
            rows = self.db.cursor.fetchall()
            self.render_table(rows)
        except Exception as e:
            print(f"獲取學生資料失敗: {e}")
            QMessageBox.critical(self.main_window, "錯誤", f"學生資料載入失敗\n{e}")

    def filter_stu(self):
        """根據班級篩選目前老師的學生"""
        try:
            # 取得下拉選單中的班級條件
            stu_class = self.ui.box_search_class.currentText()

            # 建立基本查詢語句（JOIN 以限制學生必須屬於該老師）
            query = '''
                SELECT s.stu_class, s.stu_sex, s.stu_seat_num, s.stu_name, s.stu_uuid, stu_id
                FROM Students s
                JOIN Teacher_Student ts ON s.stu_uuid = ts.stu_uuid
                WHERE ts.user_uuid = ?
            '''
            params = [self.teacher_uuid]

            # 如果班級不是「全部」，加入條件
            if stu_class != "全部" and stu_class != "":
                query += " AND s.stu_class = ?"
                params.append(stu_class)

            # 執行查詢
            self.db.cursor.execute(query, tuple(params))
            rows = self.db.cursor.fetchall()

            # 顯示結果
            self.render_table(rows)

        except Exception as e:
            print(f"查詢過程中出錯: {e}")
            QMessageBox.critical(self.main_window, "錯誤", f"學生查詢失敗\n{e}")

    def delect_student_row(self):
        """刪除指定學生與其教師關聯資料"""
        button = self.ui.table_stu.sender()  # 獲取按鈕來源
        stu_name = "未知學生"  # 🔧 預設錯誤處理名稱
        if button:
            try:
                index = self.ui.table_stu.indexAt(button.pos())
                row = index.row()

                if row < 0:
                    raise ValueError("無法確定按鈕所在行")

                uuid_item = self.ui.table_stu.item(row, 6)  # 第 6 欄是 stu_uuid
                if uuid_item is None or not uuid_item.text():
                    raise ValueError("無法取得學生 UUID，該行資料可能為空")

                stu_uuid = uuid_item.text()

                # 查詢學生姓名（用於提示訊息）
                self.db.cursor.execute("SELECT stu_name FROM Students WHERE stu_uuid = ?", (stu_uuid,))
                result = self.db.cursor.fetchone()
                stu_name = result[0] if result else "未知學生"

                # 刪除 Teacher_Student 關聯資料
                self.db.cursor.execute("DELETE FROM Teacher_Student WHERE stu_uuid = ?", (stu_uuid,))
                # 刪除學生本體資料
                self.db.cursor.execute("DELETE FROM Students WHERE stu_uuid = ?", (stu_uuid,))
                self.db.conn.commit()

                # 更新 UI
                self.ui.table_stu.removeRow(row)
                self.display_students()
                self.load_class()

                QMessageBox.information(self.main_window, "成功", f"{stu_name} 資料已成功刪除")

            except Exception as e:
                self.db.conn.rollback()
                print(f"刪除學生失敗：{e}")
                QMessageBox.critical(self.main_window, "錯誤", f"{stu_name} 資料刪除失敗\n{e}")

        
            
    def stu_qrcode(self):
        """生成單一學生的 QRCode，使用 UUID 作為查詢依據"""
        button = self.ui.table_stu.sender()
        if button:
            try:
                index = self.ui.table_stu.indexAt(button.pos())
                row = index.row()
                if row < 0:
                    raise ValueError("無法確定按鈕所在行")

                # 從第 6 欄取得 UUID
                uuid_item = self.ui.table_stu.item(row, 6)
                if uuid_item is None or not uuid_item.text():
                    raise ValueError("找不到學生 UUID，無法生成 QRCode")

                stu_uuid = uuid_item.text()

                # 查詢學生資料
                self.db.cursor.execute('''
                    SELECT stu_qr_uuid, stu_class, stu_seat_num, stu_name
                    FROM Students
                    WHERE stu_uuid = ?
                ''', (stu_uuid,))
                result = self.db.cursor.fetchone()

                if not result:
                    raise ValueError("查無此學生資料")

                stu_qr_uuid, stu_class, stu_seat_num, stu_name = result

                # 生成 QRCode 圖像
                qr_image = qrcode.make(stu_qr_uuid)
                qr_image = qr_image.convert("RGB")
                draw = ImageDraw.Draw(qr_image)

                # 加入底部文字
                try:
                    font = ImageFont.truetype(r"C:\Users\Admin\Documents\re-lego\src\ui\font\BpmfGenSenRounded-R.ttf", size=20)
                    print("✅ 使用自定義字體")
                except IOError:
                    font = ImageFont.load_default()
                    print("⚠️ 使用預設字體")

                text = f"{stu_class}_{stu_seat_num}_{stu_name}"
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]

                qr_width, qr_height = qr_image.size
                text_x = (qr_width - text_width) // 2
                text_y = qr_height - text_height - 10
                draw.text((text_x, text_y), text, fill='black', font=font)

                # 儲存圖像
                qr_filename = f"{stu_uuid}_{stu_class}_{stu_seat_num}_{stu_name}.png"
                qr_image.save(qr_filename)

                print(f"✅ 生成 QRCode：{qr_filename}")
                QMessageBox.information(self.main_window, "成功", f"成功生成 {stu_name} 的 QRCode")

            except Exception as e:
                print(f"❌ 生成學生 QRCode 失敗：{e}")
                QMessageBox.critical(self.main_window, "錯誤", f"QRCode 生成失敗：\n{e}")


    def load_class(self):
        """根據目前登入的老師 UUID，載入對應學生的班級選單"""
        try:
            # 查詢該老師對應學生的班級（去除重複值）
            self.db.cursor.execute('''
                SELECT DISTINCT s.stu_class
                FROM Students s
                JOIN Teacher_Student ts ON s.stu_uuid = ts.stu_uuid
                WHERE ts.user_uuid = ?
            ''', (self.teacher_uuid,))
            class_data = self.db.cursor.fetchall()

            # 清空下拉選單
            self.ui.box_search_class.clear()
            self.ui.box_search_class.addItem("全部")  # 預設選項：顯示所有班級

            # 加入查到的班級名稱
            for row in class_data:
                class_name = str(row[0]) if row[0] else "未命名班級"
                self.ui.box_search_class.addItem(class_name)
        except Exception as e:
            print(f"⚠️ 載入班級失敗: {e}")
            QMessageBox.critical(self.main_window, "錯誤", f"無法載入班級資料：{e}")
    
    """下載範例csv檔 """
    def create_download_csv(self):
        df = pd.DataFrame(columns=['stu_class', 'stu_sex', 'stu_seat_num', 'stu_name'])
        file_name = 'example.csv'
        df.to_csv(file_name, index=False, encoding='utf-8-sig')

        if os.path.exists(file_name):
            print(f"可供下載: {file_name}")
            QMessageBox.information(self.main_window,"成功", "下載範本成功")  
            return file_name
        else:
            print("Csv檔不存在，無法下載")
            QMessageBox.information(self.main_window,"失敗", "下載範本失敗")  
            return None
    
    def all_qrcode(self):
        """批量生成目前老師所屬學生 QRCode（使用 stu_id 命名，支援中文顯示）"""
        try:
            if not os.path.exists(self.folder_path):
                os.makedirs(self.folder_path)

            # 查詢學生資料
            self.db.cursor.execute('''
                SELECT s.stu_qr_uuid, s.stu_class, s.stu_seat_num, s.stu_name, s.stu_id
                FROM Students s
                JOIN Teacher_Student ts ON s.stu_uuid = ts.stu_uuid
                WHERE ts.user_uuid = ?
            ''', (self.teacher_uuid,))
            rows = self.db.cursor.fetchall()

            if not rows:
                QMessageBox.information(self.main_window, "提示", "尚未有學生可產生 QRCode")
                return

            # 載入中文字體（使用絕對路徑）
            # base_dir = os.path.dirname(os.path.abspath(__file__))
            font_path = os.path.join("src", "ui", "font", "BpmfGenSenRounded-R.ttf")

            for qr_uuid, stu_class, stu_seat_num, stu_name, stu_id in rows:
                # 生成 QRCode
                qr = qrcode.make(qr_uuid)
                qr_image = qr.convert("RGB")
                draw = ImageDraw.Draw(qr_image)

                # 載入字體
                try:
                    font = ImageFont.truetype(font_path, size=20)
                except IOError:
                    font = ImageFont.load_default()
                    print("⚠️ 字體載入失敗，使用預設字體")

                # 顯示於圖片上的文字
                label_text = f"{stu_class}_{stu_seat_num}_{stu_name}"
                text_bbox = draw.textbbox((0, 0), label_text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                qr_width, qr_height = qr_image.size
                text_x = (qr_width - text_width) // 2
                text_y = qr_height - text_height - 10
                draw.text((text_x, text_y), label_text, fill='black', font=font)

                # 使用 stu_id 當作檔名前綴
                qr_filename = os.path.join(
                    self.folder_path,
                    f"{stu_id}_{stu_class}_{stu_seat_num}.png"
                )
                qr_image.save(qr_filename)
                print(f"✅ 已儲存 QRCode：{qr_filename}")

            QMessageBox.information(self.main_window, "成功", "所有學生 QR Code 已成功生成")

        except Exception as e:
            print(f"❌ QRCode 批次產生錯誤：{e}")
            QMessageBox.critical(self.main_window, "錯誤", f"QRCode 產生失敗：\n{e}")


    def render_table(self, rows):
        """
        顯示學生資料表格與操作按鈕。

        Args:
            rows (List[Tuple]): 每筆資料格式為
            (stu_class, stu_sex, stu_seat_num, stu_name, stu_uuid, stu_id)
        """
        self.ui.table_stu.setRowCount(0)
        self.ui.table_stu.setRowCount(len(rows))
        self.ui.table_stu.setColumnCount(8)  # 顯示0~5, 隱藏6,7

        for row_index, row in enumerate(rows):
            # 顯示欄位：0~3 = 基本資料
            for col_index in range(4):
                item = QtWidgets.QTableWidgetItem(str(row[col_index]))
                self.ui.table_stu.setItem(row_index, col_index, item)

            # === QR Code 按鈕 ===
            qr_button = QPushButton("QRcode")
            qr_button.setIcon(QtGui.QIcon(".src/ui/icon/qr_code.png"))
            qr_button.setIconSize(QtCore.QSize(35, 35))
            qr_button.setObjectName("btn_database_qrcode")
            qr_button.setStyleSheet("""
                #btn_database_qrcode {
                    border: none; border-radius: 6px;
                    background-color: #EEEEEE;
                }
                #btn_database_qrcode:hover {
                    background-color: #B7B7B7;
                }
            """)
            qr_button.clicked.connect(self.stu_qrcode)
            self.ui.table_stu.setCellWidget(row_index, 4, qr_button)

            # === 刪除按鈕 ===
            delete_button = QPushButton("刪除學生")
            delete_button.setIcon(QtGui.QIcon(".src/ui/icon/delete.png"))
            delete_button.setIconSize(QtCore.QSize(35, 35))
            delete_button.setObjectName("btn_database_delect")
            delete_button.setStyleSheet("""
                #btn_database_delect {
                    border: none; border-radius: 6px;
                    background-color: #ffeb9a;
                }
                #btn_database_delect:hover {
                    background-color: #FFCD00;
                }
            """)
            delete_button.clicked.connect(self.delect_student_row)
            self.ui.table_stu.setCellWidget(row_index, 5, delete_button)

            # === 隱藏欄：stu_uuid 第 6 欄 ===
            uuid_item = QtWidgets.QTableWidgetItem(str(row[4]))
            self.ui.table_stu.setItem(row_index, 6, uuid_item)

            # === 隱藏欄：stu_id 第 7 欄 ===
            id_item = QtWidgets.QTableWidgetItem(str(row[5]))
            self.ui.table_stu.setItem(row_index, 7, id_item)

        # 隱藏 UUID 與 stu_id 欄位
        self.ui.table_stu.setColumnHidden(6, True)
        self.ui.table_stu.setColumnHidden(7, True)
        self.ui.table_stu.resizeRowsToContents()
