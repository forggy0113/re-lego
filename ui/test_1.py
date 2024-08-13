import sys
from face_ui import Ui_MainWindow  # 导入你的 UI 文件
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import QtCore, QtGui

class InterfaceWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)  # 設置無邊框窗口
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)  # 設置背景透明

        # 連接按鈕與各自功能
        self.ui.toolButton_3.clicked.connect(self.minimize_window)  # 最小化窗口
        self.ui.toolButton_2.clicked.connect(self.restore_or_maximize_window)  # 最大化/還原窗口
        self.ui.toolButton.clicked.connect(self.close_window)  # 關閉窗口

        self.m_flag = False  # 初始化 m_flag，可拖一窗口

        self.show()
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.m_flag = True
            self.m_Position = event.globalPosition().toPoint() - self.pos()  # 得到鼠標相對窗口位置
            event.accept()
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.OpenHandCursor))  # 更改鼠標光標為手的形狀
    
    def mouseMoveEvent(self, mouse_event):
        if self.m_flag and mouse_event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.move(mouse_event.globalPosition().toPoint() - self.m_Position)  # 移动窗口位置
            mouse_event.accept()

    def mouseReleaseEvent(self, mouse_event):
        self.m_flag = False
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))  # 還原鼠標光標為箭頭
    
    def minimize_window(self):
        self.showMinimized()  # 最小化窗口

    def restore_or_maximize_window(self):  # 最大化或還原窗口
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    
    def close_window(self):
        self.close()  # 關閉窗口

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = InterfaceWindow()
    sys.exit(app.exec())
