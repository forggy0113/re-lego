import sys
from face_ui import Ui_MainWindow as FaceUiMainWindow
from login_resigert_ui import Ui_MainWindow as LoginUiMainWindow
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import QtCore, QtGui

# 登入介面設計
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

# 首頁介面設計
class InterfaceWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = FaceUiMainWindow()
        self.ui.setupUi(self)
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.m_flag = False
        self.resizing = False
        self.border_width = 1
        # 滑鼠點擊觸發動作
        self.ui.min_window.clicked.connect(self.minimize_window)
        self.ui.open_window.clicked.connect(self.restore_or_maximize_window)
        self.ui.close_window.clicked.connect(self.close_window)
        self.ui.user.clicked.connect(self.switch_to_login)  # 連結到switch_to_login method
        
        self.show()

    def switch_to_login(self):
        self.login_window = Login_Window()  # 實例化login介面
        self.login_window.show()  # 顯示 Login_Window 界面
        self.close()  # 關閉目前的 InterfaceWindow

    # 實現窗口最小化功能
    def minimize_window(self):
        self.showMinimized()
    # 實現窗口最大化功能
    def restore_or_maximize_window(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    # 實現關閉窗口
    def close_window(self):
        self.close()

    # 實現無邊框窗口移動、放大縮小功能
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            # 如果滑鼠在邊界上
            if self.is_on_border(event.pos()):
                self.resizing = True
                # 紀錄當前位置，以利後續調整窗口大小
                self.m_Position = event.globalPosition().toPoint()
            else:
                # 按下滑鼠左鍵，觸發窗口是否移動
                self.m_flag = True
                self.m_Position = event.globalPosition().toPoint() - self.pos()
            event.accept()

    # 移動位置
    def mouseMoveEvent(self, mouse_event):
        if self.resizing:
            # 改變大小
            self.resize_window(mouse_event.globalPosition().toPoint())
        elif self.m_flag and mouse_event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.move(mouse_event.globalPosition().toPoint() - self.m_Position)
            mouse_event.accept()
        else:
            self.update_cursor(mouse_event.pos())

    # 離開長按左鍵，結束觸發
    def mouseReleaseEvent(self, mouse_event):
        self.m_flag = False
        self.resizing = False
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))

    def is_on_border(self, pos):
        """判斷滑鼠是否在窗口邊緣"""
        return (pos.x() >= self.width() - self.border_width or
                pos.y() >= self.height() - self.border_width)

    def resize_window(self, global_pos):
        """根據滑鼠移動調整窗口大小"""
        diff = global_pos - self.m_Position
        new_width = max(self.minimumWidth(), self.width() + diff.x())
        new_height = max(self.minimumHeight(), self.height() + diff.y())
        self.resize(new_width, new_height)
        self.m_Position = global_pos

    def update_cursor(self, pos):
        """更新滑鼠指針樣式"""
        if self.is_on_border(pos):
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.SizeFDiagCursor))
        else:
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = InterfaceWindow()
    sys.exit(app.exec())
