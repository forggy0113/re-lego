import sys
import cv2
import os
import pandas as pd
from ui.Ui_face import Ui_MainWindow as FaceUiMainWindow
from ui.Ui_login_resigert import Ui_MainWindow as LoginUiMainWindow
from ui.Ui_teacher_mode import Ui_MainWindow as teacher_mode
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QFontDatabase, QFont
from PyQt5 import  QtCore
from src.sql_py.login_sql import *
from src.sql_py.func_sql import Stus, Qrcode
from src.sql_py.create_sql import CreateDatabase
from ui.func.win_move_zoom import border_mouseMove, border_mousePress, border_mouseRelease, is_in_resize_area, resize_window, update_cursor, max_win
from ui.func.win_move_zoom import mouseMoveEvent, mousePressEvent, mouseReleaseEvent
from src.sql_py.encrypted import Encrypted

class Login_Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = LoginUiMainWindow()
        self.db = CreateDatabase()
        self.User = Users(db=self.db, ui=self.ui, main_window=self)
        self.ui.setupUi(self)
        self.initstack()
        # 設置窗口屬性 frameless 無邊框窗口
        self.setWindowFlag(Qt.FramelessWindowHint)
        # 自定義外觀窗口 背景為透明
        self.setAttribute(Qt.WA_TranslucentBackground)
        # 標示窗口是否拖動 (無邊框設計)
        self.is_moving = False
        # 儲存滑鼠位置
        self.mouse_position = None
        self.mouseMoveEvent = lambda event: mouseMoveEvent(self, event)
        self.mousePressEvent = lambda event: mousePressEvent(self, event)
        self.mouseReleaseEvent = lambda event: mouseReleaseEvent(self, event)
        # 設定滑鼠點擊切換頁面方式
        self.ui.toolButton.clicked.connect(lambda: self.close())
        # stackedWidget_2為多頁面 
        self.ui.Login_button.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(0))
        self.ui.btn_find_password.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(1))
        self.ui.Register_button.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(2))
        
        self.ui.register_correct.clicked.connect(self.register_user)
        self.ui.Login_correct.clicked.connect(self.login_user)
        
    def register_user(self):
        self.User.register_user()

    def login_user(self):
        self.User.login_user()

    def initstack(self):
        self.ui.stackedWidget.setCurrentIndex(1)
        
class InterfaceWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = FaceUiMainWindow()
        self.ui.setupUi(self)
        self.create_db = CreateDatabase(db_name='test_database.db')
        self.stu_manager = Stus(self.create_db, self.ui, main_window=self)
        ### 視窗設定 ###
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.is_moving = False
        self.mouse_position = None
        self.mouseMoveEvent = lambda event: mouseMoveEvent(self, event)
        self.mousePressEvent = lambda event: mousePressEvent(self, event)
        self.mouseReleaseEvent = lambda event: mouseReleaseEvent(self, event)

        ### 切換至教師登入介面 ###  
        self.ui.teacher.clicked.connect(self.open_to_login)
        self.show()
    
        ### 切換字體 ###
        init_font_size = 25
        self.font_id_1 = QFontDatabase.addApplicationFont("ui/font/BpmfGenSenRounded-R.ttf")
        self.font_id_2 = QFontDatabase.addApplicationFont("ui/font/FakePearl-Regular.ttf")
        self.font_family_1 = QFontDatabase.applicationFontFamilies(self.font_id_1)
        self.font_family_2 = QFontDatabase.applicationFontFamilies(self.font_id_2)
        
        if self.font_family_1:
            self.current_font = QFont(self.font_family_1[0], init_font_size)
            self.set_all_fonts(self.current_font)
            print(f"初始字體: {self.font_family_1[0]}")
            
        self.is_font_1 = True
        self.ui.slider_font_size.setRange(10, 27)
        self.ui.slider_font_size.setValue(init_font_size)
        self.ui.language.clicked.connect(self.change_font)
        self.ui.slider_font_size.valueChanged.connect(self.change_font_size)
        self.ui.txt_font_size.setText(f"字形大小:{init_font_size}")

        ### 影片讀取 ###
        self.cap = cv2.VideoCapture(0)
        self.video_label = self.ui.pic
        self.detector = cv2.QRCodeDetector()
        self.timer = QTimer()
        self.timer.timeout.connect(self.updata_frame)
        self.timer.start(30)

    def open_to_login(self):
        self.login_window = Login_Window()
        self.login_window.show()

    def set_all_fonts(self, font):
        for widget in self.findChildren(QWidget):
            widget.setFont(font)
    
    # 切換字形
    def change_font(self):
        init_font_size = self.ui.txt.font().pointSize() # 獲取當前文本框字型大小
        if self.is_font_1:
            if self.font_family_2:
                new_font = QFont(self.font_family_2[0], init_font_size)
                self.set_all_fonts(new_font)
                print(f"切換到新字體:{self.font_family_2[0]}")
            else:
                print("無法加載新字體")
        else:
            if self.font_family_1:
                original_font = QFont(self.font_family_1[0], init_font_size)
                self.set_all_fonts(original_font)
                print(f"切回原字體:{self.font_family_1[0]}")
            else:
                print("無法加載原字體")
        self.is_font_1 = not self.is_font_1

    # 切換字型大小
    def change_font_size(self, value):
        font_family = self.font_family_1 if self.is_font_1 else self.font_family_2
        if font_family:
            current_font = QFont(font_family[0], value)
            print(f"當前字體: {font_family[0]}, 大小: {value}")
            self.ui.txt.setFont(current_font)
            self.ui.txt_font_size.setFont(current_font)
            self.ui.txt_font_size.setText(f"字形大小: {value}")

    def updata_frame(self):
        ret, frame = self.cap.read()
        if ret:
            decoder_text, pts, _ = self.detector.detectAndDecode(frame)
            if decoder_text:
                self.draw_qrcode_box(frame, pts, decoder_text)
                # print(f"Qrcode內容:{decoder_text}")
                self.login_student(decoder_text)
            image_with_cerent = self.draw_cercent(frame)
            self.display_image(image_with_cerent)
    
    
    def login_student(self, decoder_text):
        decrypted_data = Encrypted().decrypt(decoder_text)
        # print(f"解密後: {decrypted_data}")
        if decrypted_data:
            self.stu_manager.login_stu(decrypted_data)

    def draw_qrcode_box(self, frame, pts, decoder_text):
        if pts is not None:
            pts = pts[0].astype(int).reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], isClosed=True, color=(0, 0, 255), thickness=2)
            cv2.putText(frame, decoder_text, (pts[0][0][0], pts[0][0][1]-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    def draw_cercent(self, image):
        height, width, _ = image.shape
        center_x, center_y = width // 2, height // 2
        cv2.line(image, (0, center_y), (width, center_y), (255, 255, 255), 2)
        cv2.line(image, (center_x, 0), (center_x, height), (255, 255, 255), 2)
        return image

    def display_image(self, image):
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qimg))

    def closeEvent(self):
        self.cap.release()

class teacher_window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = teacher_mode()
        self.ui.setupUi(self)
        
        ### 初始化資料庫 ###
        self.create_db = CreateDatabase(db_name='test_database.db')
        self.create_qr = Qrcode(db_name='test_database.db', folder_path='qrcode', main_window=self)
        self.stu_manager = Stus(self.create_db, self.ui, main_window=self)
        
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
        self.ui.btn_import_csvfile.clicked.connect(self.add_csv_data)
        self.update_student_display()
        self.ui.btn_import_qrcode.clicked.connect(self.create_qrcode)

        ## 加載班級 and 篩選學生
        self.load_class()
        self.ui.btn_filter.clicked.connect(self.search_stu)

        ### 無邊框 ###
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
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

    def mousePressEvent(self, event):  # 重寫調用 mousePressEvent 正確覆蓋掉原本存在的 mousePressEvent
        border_mousePress(self, event)

    def mouseMoveEvent(self, event):  # 重寫調用 mouseMoveEvent
        border_mouseMove(self, event)

    def mouseReleaseEvent(self, event):  # 重寫調用 mouseReleaseEvent
        border_mouseRelease(self, event)

    def is_in_resize_area(self, pos):  # 判斷滑鼠是否在邊緣或角落的縮放區域
        return is_in_resize_area(self, pos)

    def update_cursor(self, pos):  # 更新滑鼠游標
        update_cursor(self, pos)

    def resize_window(self, pos):  # 縮放窗口
        resize_window(self, pos)

    def search_stu(self):
        self.stu_manager.filter_stu()

    def load_class(self):
        self.stu_manager.load_class()

    def create_qrcode(self):
        self.create_qr.all_qrcode()

    ### 下載範例csv檔 ###
    def create_download_csv(self):
        df = pd.DataFrame(columns=['stu_class', 'stu_sex', 'stu_seat_num', 'stu_name'])
        file_name = 'example.csv'
        df.to_csv(file_name, index=False, encoding='utf-8-sig')

        if os.path.exists(file_name):
            print(f"可供下載: {file_name}")
            return file_name
        else:
            print("Csv檔不存在，無法下載")
            return None

    ### 引用 UI 中的 table_stu ###
    def add_stu_data(self):
        self.stu_manager.add_stu()
        self.stu_manager.clear_edit()
        self.stu_manager.display_students()
        self.stu_manager.load_class()

    def add_csv_data(self):
        self.stu_manager.add_csv()
        self.stu_manager.load_class()
        self.stu_manager.display_students()

    def update_student_display(self):
        self.stu_manager.display_students()

    def clear_stu_data(self):
        self.stu_manager.clear_edit()

    def delect_stu_row(self):
        self.stu_manager.delect_student_row()

class teacher_window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = teacher_mode()
        self.ui.setupUi(self)
        
        ### 初始化資料庫 ###
        self.create_db = CreateDatabase(db_name='test_database.db')
        self.create_qr = Qrcode(db_name='test_database.db', folder_path='qrcode', main_window=self)
        self.stu_manager = Stus(self.create_db, self.ui, main_window=self)
        
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
        self.ui.btn_import_csvfile.clicked.connect(self.add_csv_data)
        self.update_student_display()
        self.ui.btn_import_qrcode.clicked.connect(self.create_qrcode)

        ## 加載班級 and 篩選學生
        self.load_class()
        self.ui.btn_filter.clicked.connect(self.search_stu)

        ### 無邊框 ###
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
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

    def mousePressEvent(self, event):  # 重寫調用 mousePressEvent 正確覆蓋掉原本存在的 mousePressEvent
        border_mousePress(self, event)

    def mouseMoveEvent(self, event):  # 重寫調用 mouseMoveEvent
        border_mouseMove(self, event)

    def mouseReleaseEvent(self, event):  # 重寫調用 mouseReleaseEvent
        border_mouseRelease(self, event)

    def is_in_resize_area(self, pos):  # 判斷滑鼠是否在邊緣或角落的縮放區域
        return is_in_resize_area(self, pos)

    def update_cursor(self, pos):  # 更新滑鼠游標
        update_cursor(self, pos)

    def resize_window(self, pos):  # 縮放窗口
        resize_window(self, pos)

    def search_stu(self):
        self.stu_manager.filter_stu()

    def load_class(self):
        self.stu_manager.load_class()

    def create_qrcode(self):
        self.create_qr.all_qrcode()

    ### 下載範例csv檔 ###
    def create_download_csv(self):
        df = pd.DataFrame(columns=['stu_class', 'stu_sex', 'stu_seat_num', 'stu_name'])
        file_name = 'example.csv'
        df.to_csv(file_name, index=False, encoding='utf-8-sig')

        if os.path.exists(file_name):
            print(f"可供下載: {file_name}")
            return file_name
        else:
            print("Csv檔不存在，無法下載")
            return None

    ### 引用 UI 中的 table_stu ###
    def add_stu_data(self):
        self.stu_manager.add_stu()
        self.stu_manager.clear_edit()
        self.stu_manager.display_students()
        self.stu_manager.load_class()

    def add_csv_data(self):
        self.stu_manager.add_csv()
        self.stu_manager.load_class()
        self.stu_manager.display_students()

    def update_student_display(self):
        self.stu_manager.display_students()

    def clear_stu_data(self):
        self.stu_manager.clear_edit()

    def delect_stu_row(self):
        self.stu_manager.delect_student_row()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = InterfaceWindow()
    win.show()
    sys.exit(app.exec_())
