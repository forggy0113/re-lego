import sys
from face_ui import Ui_MainWindow as FaceUiMainWindow
from login_resigert_ui import Ui_MainWindow as LoginUiMainWindow
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import QtCore, QtGui

class Login_Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = LoginUiMainWindow()  # 使用 login_resigert_ui 中的 UI 类
        self.ui.setupUi(self)
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.is_moving = False
        self.mouse_position = None

        self.ui.toolButton.clicked.connect(self.close_window)
        self.ui.Login_button.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(0))
        self.ui.password_button.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(1))
        self.ui.Register_button.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(2))
        self.ui.Login_correct.clicked.connect(self.Login)

        self.show()

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

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.is_moving = True
            self.mouse_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_moving:
            self.move(event.globalPosition().toPoint() - self.mouse_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.is_moving = False
            event.accept()

class InterfaceWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = FaceUiMainWindow()  # 使用 face_ui 中的 UI 类
        self.ui.setupUi(self)
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.m_flag = False
        self.resizing = False
        self.border_width = 1

        self.ui.min_window.clicked.connect(self.minimize_window)
        self.ui.open_window.clicked.connect(self.restore_or_maximize_window)
        self.ui.close_window.clicked.connect(self.close_window)
        self.ui.user.clicked.connect(self.switch_to_login)  # 连接到 switch_to_login 方法
        
        self.show()

    def switch_to_login(self):
        self.login_window = Login_Window()  # 实例化 Login_Window
        self.login_window.show()  # 显示 Login_Window 界面
        self.close()  # 关闭当前的 InterfaceWindow

    def minimize_window(self):
        self.showMinimized()

    def restore_or_maximize_window(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def close_window(self):
        self.close()

    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            if self.is_on_border(event.pos()):
                self.resizing = True
                self.m_Position = event.globalPosition().toPoint()
            else:
                self.m_flag = True
                self.m_Position = event.globalPosition().toPoint() - self.pos()
            event.accept()
    
    def mouseMoveEvent(self, mouse_event):
        if self.resizing:
            self.resize_window(mouse_event.globalPosition().toPoint())
        elif self.m_flag and mouse_event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.move(mouse_event.globalPosition().toPoint() - self.m_Position)
            mouse_event.accept()
        else:
            self.update_cursor(mouse_event.pos())

    def mouseReleaseEvent(self, mouse_event):
        self.m_flag = False
        self.resizing = False
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))

    def is_on_border(self, pos):
        """判断鼠标是否在窗口边缘"""
        return (pos.x() >= self.width() - self.border_width or
                pos.y() >= self.height() - self.border_width)

    def resize_window(self, global_pos):
        """根据鼠标移动调整窗口大小"""
        diff = global_pos - self.m_Position
        new_width = max(self.minimumWidth(), self.width() + diff.x())
        new_height = max(self.minimumHeight(), self.height() + diff.y())
        self.resize(new_width, new_height)
        self.m_Position = global_pos

    def update_cursor(self, pos):
        """更新鼠标指针样式"""
        if self.is_on_border(pos):
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.SizeFDiagCursor))
        else:
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = InterfaceWindow()
    sys.exit(app.exec())
