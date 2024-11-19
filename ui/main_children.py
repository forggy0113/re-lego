import sys
from face_ui import Ui_MainWindow as FaceUiMainWindow
from login_resigert_ui import Ui_MainWindow as LoginUiMainWindow
from main_teacher import teacher_window
from PyQt6.QtWidgets import QApplication, QMainWindow,QWidget
from PyQt6 import QtWidgets
from PyQt6.QtCore import QTimer 
from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import QImage, QPixmap
import cv2
from func.win_move_zoom import mouseMoveEvent, mousePressEvent, mouseReleaseEvent
from create_sql import *

class Login_Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = LoginUiMainWindow()  
        self.ui.setupUi(self)
        self.initstack()
        # 設置窗口屬性 frameless 無邊框窗口
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        # 自定義外觀窗口 背景為透明
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        # 標示窗口是否拖動 (無邊框設計)
        self.is_moving = False
        # 儲存滑鼠位置
        self.mouse_position = None
        self.mouseMoveEvent = lambda event:mouseMoveEvent(self, event)
        self.mousePressEvent = lambda event:mousePressEvent(self, event)
        self.mouseReleaseEvent = lambda event:mouseReleaseEvent(self, event)
        # 設定滑鼠點擊切換頁面方式
        self.ui.toolButton.clicked.connect(lambda: self.close())
        # stackedWidget_2為多頁面 
        # setCurrentIndex 為頁面索引至哪裡
        self.ui.Login_button.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(0))
        self.ui.btn_find_password.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(1))
        self.ui.Register_button.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(2))
        
        self.db = CreateDatabase()
        self.User = Users(db=self.db, ui=self.ui, main_window=self)
        
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
        ###視窗設定###
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.mouseMoveEvent = lambda event:mouseMoveEvent(self, event)
        self.mousePressEvent = lambda event:mousePressEvent(self, event)
        self.mouseReleaseEvent = lambda event:mouseReleaseEvent(self, event)

        ### 切換至教師登入介面 ###  
        self.ui.teacher.clicked.connect(self.open_to_login)  # 連結到switch_to_login method
        self.show()
    
        ### 切換字體 ###
        # 設定字體類型
        init_font_size = 25
        self.font_id_1 = QtGui.QFontDatabase.addApplicationFont("font/BpmfGenSenRounded-R.ttf")
        self.font_id_2 = QtGui.QFontDatabase.addApplicationFont("font/FakePearl-Regular.ttf")
        self.font_family_1 = QtGui.QFontDatabase.applicationFontFamilies(self.font_id_1)
        self.font_family_2 = QtGui.QFontDatabase.applicationFontFamilies(self.font_id_2)
        # 設置初始字體
        if self.font_family_1:
            self.current_font = QtGui.QFont(self.font_family_1[0], init_font_size)
            self.set_all_fonts(self.current_font)
            print(f"初始字體: {self.font_family_1[0]}")
        # 初始化字體狀態
        self.is_font_1 = True
        # 默認調整字型大小為25
        self.ui.slider_font_size.setRange(10,32)
        self.ui.slider_font_size.setValue(init_font_size)
        # 點擊按鈕切換字體
        self.ui.language.clicked.connect(self.change_font)
        self.ui.slider_font_size.valueChanged.connect(self.change_font_size)
        self.ui.txt_font_size.setText(f"字形大小:{init_font_size}")

        ### 影片讀取 ###
        # 影片捕捉對象 (0 表示攝影機)
        self.cap = cv2.VideoCapture(0)
        self.video_label = self.ui.pic
        self.detector = cv2.QRCodeDetector()
        # 設置定時器，每30毫秒刷新畫面
        self.timer = QTimer()
        self.timer.timeout.connect(self.updata_frame)
        self.timer.start(30)

    ### 切換至教師登入介面_part1 ###        
    def open_to_login(self):
        self.login_window = Login_Window()  # 實例化login介面
        self.login_window.show()  # 顯示 Login_Window 界面
        

    ### 切換字體_part1 ###
    def set_all_fonts(self, font):
        # 跑遍全部字體
        for widget in self.findChildren(QWidget):
            widget.setFont(font)

    ### 切換字體_part2 ###
    def change_font(self):
        init_font_size = 25
        if self.is_font_1:
            if self.font_family_2:
                new_font = QtGui.QFont(self.font_family_2[0], init_font_size)
                self.set_all_fonts(new_font)
                print(f"切換到新字體:{self.font_family_2[0]}")
            else:
                print("無法加載新字體")
        else:
            if self.font_family_1:
                orginal_font = QtGui.QFont(self.font_family_1[0], init_font_size)
                self.set_all_fonts(orginal_font)
                print(f"切回原字體:{self.font_family_1[0]}")
            else:
                print("無法加載原字體")
        self.is_font_1 = not self.is_font_1
    #改變字體大小
    def change_font_size(self, value):
        if self.is_font_1:
            font_family = self.font_family_1
        else:
            font_family = self.font_family_2
        
        if font_family:
            current_font = QtGui.QFont(font_family[0], value)
            print(f"當前字體: {font_family[0]}, 大小: {value}")
            self.ui.txt.setFont(current_font)
            
            # 僅更新 txt_font_size 的顯示文本，不改變其字體大小
            self.ui.txt_font_size.setText(f"字形大小: {value}")


    ### 影片讀取_part1 ###
    def updata_frame(self):
        ret, frame = self.cap.read()
        if ret:
            decoder_text, pts, _ = self.detector.detectAndDecode(frame)
            if decoder_text:
                self.draw_qrcode_box(frame, pts, decoder_text)
                print(f"Qrcode內容:{decoder_text}")
            
            image_with_cerent = self.draw_cercent(frame)
            self.display_image(image_with_cerent)
        
    def draw_qrcode_box(self, frame, pts, decoder_text):
        if pts is not None:
            # pts 是 QRCode 外框的四個頂點座標
            pts = pts[0].astype(int).reshape((-1,1,2))
            # 繪製外框
            cv2.polylines(frame, [pts], isClosed=True, color=(0,0,255), thickness=2)
            # 顯示內容在QRCode外框上方
            cv2.putText(frame, decoder_text, (pts[0][0][0], pts[0][0][1]-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),2)
    
    # 繪製十字線
    def draw_cercent(self, image):
        height, width, _ = image.shape
        center_x, center_y = width//2, height//2
        # 繪製水平線
        cv2.line(image, (0, center_y), (width, center_y), (255,255,255),2)
        # 繪製垂直線
        cv2.line(image, (center_x,0), (center_x, height), (255,255,255),2)
        return image

    # 顯示影像
    def display_image(self, image):
        # BGR轉RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h,w,ch = rgb_image.shape
        # 計算每一行圖像所占像素(像素點*通道)
        bytes_pre_line = ch*w
        qimg = QImage(rgb_image.data, w, h, bytes_pre_line, QImage.Format.Format_RGB888)
        # 在 QLabel 上顯示圖片
        self.video_label.setPixmap(QPixmap.fromImage(qimg))
    
    ### 影片讀取_part2 ###
    def closeEvent(self, event):
        # 釋放攝影機資源
        self.cap.release()



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = InterfaceWindow()
    win.show()
    sys.exit(app.exec())