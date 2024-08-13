import sys
from face_ui import Ui_MainWindow
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import QtCore, QtGui

class InterfaceWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)  # 设置无边框窗口
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)  # 设置背景透明

        # 初始化变量
        self.m_flag = False
        self.resizing = False
        self.border_width = 5  # 调整窗口大小的边框宽度

        # 连接按钮与各自的功能
        self.ui.toolButton_3.clicked.connect(self.minimize_window)  # 最小化窗口
        self.ui.toolButton_2.clicked.connect(self.restore_or_maximize_window)  # 最大化/还原窗口
        self.ui.toolButton.clicked.connect(self.close_window)  # 关闭窗口

        self.show()
    
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
    
    def minimize_window(self):
        self.showMinimized()

    def restore_or_maximize_window(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    
    def close_window(self):
        self.close()

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
