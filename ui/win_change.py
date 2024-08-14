import sys
from login_resigert_ui import Ui_MainWindow
from win_main import InterfaceWindow
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import QtCore,QtGui

class Login_Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # 設置無邊框窗口
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)  
        # 設定透明背景
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)  
        
        self.is_moving = False #判斷是否拖動窗口
        self.mouse_position = None # 儲存滑鼠起始位置
        
        # 定義按鈕意義
        self.ui.toolButton.clicked.connect(self.close_window)  # 關閉窗口
        self.ui.Login_button.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(0))
        self.ui.password_button.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(1))
        self.ui.Register_button.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(2))
        self.ui.Login_correct.clicked.connect(self.Login)

        self.show()
    
    def Login(self):
        account = self.ui.Login_account.text()
        password = self.ui.Login_password.text()
        if account == "ada" and password =="012567":
            self.win = InterfaceWindow()
            self.close()
        else:
            print("wrong")

    def close_window(self):
        self.close()
    # 按下滑鼠
    def mousePressEvent(self, event):
        # 當左鍵按下時
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.is_moving = True
            # 紀錄當前滑鼠位置(全局座標)-左上角的座標偏移量 = 新視窗位置
            self.mouse_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    # 移動滑鼠
    def mouseMoveEvent(self, event):
        if self.is_moving:
            self.move(event.globalPosition().toPoint() - self.mouse_position)
            event.accept()
    # 釋放滑鼠
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.is_moving = False
            event.accept()
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Login_Window()
    sys.exit(app.exec())
