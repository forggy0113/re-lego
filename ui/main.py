import sys
from face_ui import Ui_MainWindow as FaceUiMainWindow
from login_resigert_ui import Ui_MainWindow as LoginUiMainWindow
from PyQt6.QtWidgets import QApplication, QMainWindow,QWidget
from PyQt6 import QtWidgets
from PyQt6.QtCore import QTimer 
from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import QImage, QPixmap
import cv2

class Login_Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = LoginUiMainWindow()  
        self.ui.setupUi(self)
        # 設置窗口屬性 frameless 無邊框窗口
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        # 自定義外觀窗口 背景為透明
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        # 標示窗口是否拖動 (無邊框設計)
        self.is_moving = False
        # 儲存滑鼠位置
        self.mouse_position = None

        # 設定滑鼠點擊切換頁面方式
        self.ui.toolButton.clicked.connect(self.close_window)
        # stackedWidget_2為多頁面 
        # setCurrentIndex 為頁面索引至哪裡
        self.ui.Login_button.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(0))
        self.ui.password_button.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(1))
        self.ui.Register_button.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(2))
        self.ui.Login_correct.clicked.connect(self.Login)

        self.show()
    # 登入帳號密碼
    def Login(self):
        account = self.ui.Login_account.text()
        password = self.ui.Login_password.text()
        if account == "ada" and password == "012567":
            self.win = InterfaceWindow()
            self.close()

        else:
            print("wrong")

    def close_window(self):
        self.close()
    # 實現無邊框窗口移動方式
    # 按下滑鼠左鍵，觸發窗口是否移動
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.is_moving = True
            # 滑鼠位置 - 窗口左上角座標。 計算相對座標
            self.mouse_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    # 移動位置
    def mouseMoveEvent(self, event):
        if self.is_moving:
            # 計算新窗口位置
            self.move(event.globalPosition().toPoint() - self.mouse_position)
            event.accept()
    # 離開長按左鍵，結束觸發
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.is_moving = False
            event.accept()

class InterfaceWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = FaceUiMainWindow()
        self.ui.setupUi(self)
        ###視窗設定###
        # self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        # self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        ### 切換至教師登入介面 ###  
        self.ui.teacher.clicked.connect(self.open_to_login)  # 連結到switch_to_login method
        self.show()
    
        ### 切換字體 ###
        # 設定字體類型
        self.font_id_1 = QtGui.QFontDatabase.addApplicationFont("font/BpmfGenSenRounded-R.ttf")
        self.font_id_2 = QtGui.QFontDatabase.addApplicationFont("font/FakePearl-Regular.ttf")
        self.font_family_1 = QtGui.QFontDatabase.applicationFontFamilies(self.font_id_1)
        self.font_family_2 = QtGui.QFontDatabase.applicationFontFamilies(self.font_id_2)
        # 設置初始字體
        if self.font_family_1:
            self.current_font = QtGui.QFont(self.font_family_1[0], 25)
            self.set_all_fonts(self.current_font)
            print(f"初始字體: {self.font_family_1[0]}")
        # 初始化字體狀態
        self.is_font_1 = True
        # 點擊按鈕切換字體
        self.ui.language.clicked.connect(self.change_font)

        ### 影片讀取 ###
        # 影片捕捉對象 (0 表示攝影機)
        self.cap = cv2.VideoCapture(0)
        self.video_label = self.ui.pic
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
        if self.is_font_1:
            if self.font_family_2:
                new_font = QtGui.QFont(self.font_family_2[0], 25)
                self.set_all_fonts(new_font)
                print(f"切換到新字體:{self.font_family_2[0]}")
            else:
                print("無法加載新字體")
        else:
            if self.font_family_1:
                orginal_font = QtGui.QFont(self.font_family_1[0],25)
                self.set_all_fonts(orginal_font)
                print(f"切回原字體:{self.font_family_1[0]}")
            else:
                print("無法加載原字體")
        self.is_font_1 = not self.is_font_1

    ### 影片讀取_part1 ###
    def updata_frame(self):
        ret, frame = self.cap.read()

        if ret:
            # 轉換顏色，opencv BGR 轉為 RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            h, w, ch = rgb_frame.shape
            # 計算每一行圖像所占像素(像素點*通道)
            bytes_per_line = ch * w
            qimg = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

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
