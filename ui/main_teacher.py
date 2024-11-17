import sys
from teacher_mode_ui import Ui_MainWindow as teacher_mode
from PyQt6.QtWidgets import  QMainWindow,QFileDialog,QMessageBox
from PyQt6 import QtWidgets,QtCore
from func_sql import CreateDatabase, Stus, Qrcode, import_csv_to_db
import sqlite3
import pandas as pd
import uuid
import os
from PyQt6.QtSql import QSqlTableModel
from func.win_move_zoom import border_mouseMove, border_mousePress,border_mouseRelease,is_in_resize_area,resize_window,update_cursor,max_win



class teacher_window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = teacher_mode()
        self.ui.setupUi(self)
        ### 初始化資料庫 ###
        self.create_db = CreateDatabase()
        # 只回傳 db 和 ui
        self.stu_manager = Stus(self.create_db, self.ui)
        db_name = 'test_database.db'
        folder_path = 'qrcode'
        self.qrcode_test = Qrcode(db_name, folder_path)

        ## 連接保存和刪除按鈕
        self.ui.btn_save.clicked.connect(self.add_stu_data)
        self.ui.btn_trash.clicked.connect(self.clear_stu_data)
        self.update_student_display()

        ### menu init ###
        self.ui.side_menu_2.hide()
        self.ui.stack_change_page.setCurrentIndex(3)
        self.ui.home_button.setChecked(True)
        ### sild_menu change page ###
        self.ui.database_button.clicked.connect(lambda: self.ui.stack_change_page.setCurrentIndex(0))
        self.ui.database_2_button.clicked.connect(lambda: self.ui.stack_change_page.setCurrentIndex(0))
        self.ui.analytics_button.clicked.connect(lambda: self.ui.stack_change_page.setCurrentIndex(1))
        self.ui.analytics_2_button.clicked.connect(lambda: self.ui.stack_change_page.setCurrentIndex(1))    
        self.ui.setting_button.clicked.connect(lambda: self.ui.stack_change_page.setCurrentIndex(2))
        self.ui.setting_2_button.clicked.connect(lambda: self.ui.stack_change_page.setCurrentIndex(2))
        self.ui.home_button.clicked.connect(lambda: self.ui.stack_change_page.setCurrentIndex(3))
        self.ui.home_2_button.clicked.connect(lambda: self.ui.stack_change_page.setCurrentIndex(3))
        self.ui.release_button.clicked.connect(lambda: self.ui.stack_change_page.setCurrentIndex(4))
        self.ui.release_2_button.clicked.connect(lambda: self.ui.stack_change_page.setCurrentIndex(4))
        ### 新增學生資料切換頁面 ###
        self.ui.btn_create_data.clicked.connect(lambda: self.ui.stack_create_data.setCurrentIndex(0))
        self.ui.btn_create_file.clicked.connect(lambda: self.ui.stack_create_data.setCurrentIndex(1))
        
        ## 新增下載example.csv檔功能
        self.ui.btn_download_file.clicked.connect(self.create_download_csv)
        self.ui.btn_import_csvfile.clicked.connect(self.open_file_dialog)
        self.ui.btn_import_qrcode.clicked.connect(self.qrcode_test.all_qrcode)
        
        ### 無邊框 ###
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True) 
        # 初始化拖動和縮放相關的屬性
        self.is_dragging = False
        self.is_resizing = False
        self.drag_position = None
        self.resize_threshold = 20
        ### 窗口按鈕控制 ###
        self.ui.close_button.clicked.connect(lambda: self.close())
        self.ui.min_button.clicked.connect(lambda: self.showMinimized())
        self.ui.max_button.clicked.connect(lambda: max_win(self))
    def mousePressEvent(self, event): # 重寫調用 mousePressEvent 正確附蓋掉原本存在的mousePressEvent
        border_mousePress(self, event)
    def mouseMoveEvent(self, event): # 重寫調用 mouseMoveEvent
        border_mouseMove(self, event)   
    def mouseReleaseEvent(self, event): # 重寫調用mouseReleaseEvent
        border_mouseRelease(self, event)
    def is_in_resize_area(self, pos):   #判斷滑鼠是否在邊緣或角落的縮放區域
        return is_in_resize_area(self, pos)
    def update_cursor(self, pos): # 更新滑鼠游標
        update_cursor(self, pos)
    def resize_window(self, pos): # 縮放窗口
        resize_window(self, pos)
        
    def open_file_dialog(self):
        # 彈出一個文件夾讓用戶選擇檔案
        file_name, _ = QFileDialog.getOpenFileName(self, "選擇csv文件", '', '(*.csv)') 
        if file_name:
            self.import_csv_to_db(file_name)
            
    def import_csv_to_db(self, file_name):
        import_csv_to_db(self, file_name)
            

    def refresh_table_view(self):
        # 創建並設置 QSqlTableModel 來顯示數據
        model = QSqlTableModel()
        model.setTable("Students")
        model.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)
        model.select()
        
        # 將模型設置給 QTableView 控件
        self.tableView.setModel(model)

    ### 下載範例csv檔 ###
    def create_download_csv(self):
        df = pd.DataFrame(columns=['stu_class','stu_sex','stu_seat_num','stu_name'])
        file_name = 'example.csv'
        df.to_csv(file_name, index=False, encoding='utf-8-sig')
        
        if os.path.exists(file_name):
            print(f"可供下載:{file_name}")
            return file_name
        else:
            print("Csv檔不存在，無法下載")
            return None

    ### 引用 UI 中的 table_stu ###
    def add_stu_data(self):
        self.stu_manager.add_stu()
        self.stu_manager.clear_edit()
        self.update_student_display()

    def update_student_display(self):
        self.stu_manager.display_students()
    def clear_stu_data(self):
        self.stu_manager.clear_edit()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = teacher_window()
    win.show()
    sys.exit(app.exec())
