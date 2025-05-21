import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.ui.Ui_main import Ui_MainWindow as Main_Window
from src.ui.Ui_login_resigert import Ui_MainWindow as Login_Resigert_Window
from src.ui.Ui_teacher_mode import Ui_MainWindow as Teacher_Mode_Window
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QFont
from src.func.window_change import *
from src.func.font_change import Font
from src.func.camera import Camera
from src.sql.create_sql import CreateDataBase
from src.sql.user_login import User
from sql.student import Stus
from src.sql.encrypted import Encrypted

# 學生登入介面
class Main(QMainWindow):
    def __init__(self):
        super().__init__() # 為衍生類別建構函數，調用父類QMainWindow
        self.ui = Main_Window()
        self.ui.setupUi(self) # 設定主視窗
        self.db = CreateDataBase()
        self.camera = Camera(db = self.db, ui=self.ui, main_window=self)
        self.on_login_success = None  # 外部 controller 用來註冊 callback
        """螢幕調整方式"""
        win_move(self)
        win_full(self) # 設定全螢幕
        win_no_title_bar(self) # 隱藏視窗標題欄 
        """ 初始化字體和設定字體大小"""
        init_font_size = 20 # 初始化字體大小
        self.Font = Font(self, self.ui, init_font_size) # 初始化字體
        init_font = QFont(self.Font.font_family_1[0], init_font_size)
        self.Font.font_all_change(init_font)
        self.ui.txt_font_size.setText(f"字型大小：{init_font_size}") # 顯示字體大小提示
        self.ui.btn_close.clicked.connect(self.close) # 關閉視窗
        self.ui.btn_teacher.clicked.connect(self.show_teacher_login) # 顯示教師登入介面
        self.ui.btn_translate.clicked.connect(lambda: self.Font.font_change()) # 切換字體
        
        # 滑動條調整字體大小
        self.ui.slide_font_size.setRange(10, 27)
        self.ui.slide_font_size.setValue(init_font_size)
        self.ui.slide_font_size.valueChanged.connect(lambda: self.Font.font_size_change(self.ui.slide_font_size.value()))
        self.stu_camera()
    
    def show_teacher_login(self): # 顯示教師登入介面
        self.teacher_login = Teacher_login()
        self.teacher_login.show()
    
    def stu_camera(self):
        self.camera.stu_login_video()
        self.camera.timer.timeout.connect(self.check_login_result)
    
    def check_login_result(self):
        """
        檢查攝影機是否成功解碼 QRCode 並登入學生。

        調用方式：
            此函數通常由 QTimer（如每 30ms）定期觸發，用於輪詢檢查 login_student() 是否成功回傳資料。

        調用依賴：
            - self.camera.login_student()：會回傳 (student_data, True) 若登入成功；失敗則回傳 None 或 (None, False)
            - self.on_login_success：一個外部註冊的 callback（如控制器 AppController），用來處理登入後的流程（例如啟動遊戲）

        Returns:
            None  # 無回傳值，但登入成功後會觸發視窗切換與 callback
        """
        # 嘗試從 camera 取得登入結果
        result = self.camera.login_student()
        if result: # 取得結果
            student_data, success = result

            if success and student_data:
                # 停止 QRCode 掃描與攝影機
                self.camera.timer.stop()
                self.camera.release_camera()

                # 通知 controller 或主流程登入成功
                if self.on_login_success:
                    self.hide()  # 隱藏登入畫面
                    self.on_login_success(student_data)
    
    def reset(self):
        """
        遊戲結束後重新顯示登入畫面並清除上次登入狀態
        """
        print("回到學生登入介面，準備下一位學生")
        self.camera.logged_in = False
        self.camera.decoder_text = None
        self.camera.student_data = None           # ✅ 清除學生資料
        self.camera.release_camera()              # ✅ 安全釋放上一輪攝影機
        self.show()
        self.stu_camera()



# 教師登入介面
class Teacher_login(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Login_Resigert_Window()
        self.ui.setupUi(self)
        self.DataBase = CreateDataBase()
        self.User_login = User(db=self.DataBase, ui=self.ui, main_window=self)
        
        self.ui.register_correct.clicked.connect(lambda: self.User_login.Register_user())
        self.ui.Login_correct.clicked.connect(lambda: self.User_login.login_user())
        
        win_move(self) # 設定視窗移動
        win_no_title_bar(self) # 隱藏視窗標題欄
        self.ui.toolButton.clicked.connect(self.close) # 關閉視窗
        ### 切換頁面至登入、忘記密碼、註冊 ###
        self.ui.Login_button.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(0))
        self.ui.btn_find_password.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(1))
        self.ui.Register_button.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(2))
        ### 變更字體
        self.Font = Font(self, self.ui, init_font_size=10)
        font = QFont(self.Font.font_family_2[0])
        self.Font.font_change_size_force(font)
        
class Teacher_mode(QMainWindow):
    def __init__(self, user_uuid):
        super().__init__()
        self.ui = Teacher_Mode_Window()
        self.ui.setupUi(self)
        win_no_title_bar(self) # 隱藏視窗標題欄
        win_resize(self) # 設定視窗縮放
        
        self.Encrypted = Encrypted(private_key_path= "./src/sql/private.pem", public_key_path = "./src/sql/public.pem")
        # self.Encrypted.generate_keys()
        
        self.db = CreateDataBase()
        ### 變更字體
        self.Font = Font(self, self.ui, init_font_size=10)
        font = QFont(self.Font.font_family_2[0])
        self.Font.font_change_size_force(font)
        
        self.ui.close_button.clicked.connect(self.close) # 關閉視窗
        self.ui.min_button.clicked.connect(self.showMinimized) # 最小化視窗
        self.ui.max_button.clicked.connect(lambda: max_win(self)) # 放大視窗
        ### 切換菜單頁面 ###
        self.ui.database_2_button.clicked.connect(lambda: self.ui.stack_change_page.setCurrentIndex(0))
        self.ui.analytics_2_button.clicked.connect(lambda: self.ui.stack_change_page.setCurrentIndex(1))
        self.ui.setting_2_button.clicked.connect(lambda: self.ui.stack_change_page.setCurrentIndex(2))
        self.ui.home_2_button.clicked.connect(lambda: self.ui.stack_change_page.setCurrentIndex(3))
        self.ui.release_2_button.clicked.connect(lambda: self.ui.stack_change_page.setCurrentIndex(4))
        ### 切換新增學生頁面 ###
        self.ui.btn_create_data.clicked.connect(lambda: self.ui.stack_create_data.setCurrentIndex(0))
        self.ui.btn_create_file.clicked.connect(lambda: self.ui.stack_create_data.setCurrentIndex(1))
        
        """ 學生資料管理功能 """
        self.stu_manager = Stus(self.db, self.ui, main_window=self, encrypted=self.Encrypted, folder_path='./qrcode', teacher_uuid=user_uuid)
        ## 連接保存和刪除按鈕
        self.ui.btn_save.clicked.connect(self.add_stu_data)
        self.ui.btn_trash.clicked.connect(lambda: self.stu_manager.clear_edit())
        # self.update_student_display()
        self.ui.btn_download_file.clicked.connect(lambda: self.stu_manager.create_download_csv())
        self.ui.btn_import_csvfile.clicked.connect(self.add_csv_data)
        self.ui.btn_import_qrcode.clicked.connect(lambda: self.stu_manager.all_qrcode())
        self.ui.btn_filter.clicked.connect(lambda: self.stu_manager.filter_stu())
        # 初次載入資料
        self.update_student_display()
    def add_stu_data(self):
        self.stu_manager.add_stu()
        self.stu_manager.clear_edit()
        self.stu_manager.display_students()
        self.stu_manager.load_class()
        
    def update_student_display(self):
        self.stu_manager.display_students()
    
    def add_csv_data(self):
        self.stu_manager.add_csv()
        self.stu_manager.load_class()
        self.stu_manager.display_students()

    
