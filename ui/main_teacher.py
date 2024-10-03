import sys
from teacher_mode_ui import Ui_MainWindow as teacher_mode
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QStackedWidget, QWidget
from PyQt6 import QtWidgets
from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import QImage, QPixmap


class teacher_window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = teacher_mode()
        self.ui.setupUi(self)

        ### 無邊框 ###
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.m_flag = False
        self.resizeing = False
        self.border_width = 1
        ### 窗口控制 ###
        self.ui.close_button.clicked.connect(self.close_window)
        self.ui.min_button.clicked.connect(self.min_window)
        self.ui.max_button.clicked.connect(self.max_window)

        ### 菜单栏初始化 ###
        self.ui.side_menu_2.hide()
        self.ui.stackedWidget.setCurrentIndex(3)
        self.ui.home_button.setChecked(True)

        self.ui.database_button.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.database_2_button.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.analytics_button.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.analytics_2_button.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))    
        self.ui.setting_button.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(2))
        self.ui.setting_2_button.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(2))
        self.ui.home_button.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(3))
        self.ui.home_2_button.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(3))
        self.ui.release_button.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(4))
        self.ui.release_2_button.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(4))


    ### 窗口關閉 縮小 放大_method ###
    def close_window(self):
        self.close()
    def min_window(self):
        self.showMinimized()
    def max_window(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    ### 無邊框移動 ###
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            # 判斷滑鼠是否在邊界
            if self.is_on_border(event.pos()):
                self.resizeing = True
                self.m_Position = event.globalPosition().toPoint()
            else:
                # 判斷是否移動
                self.m_flag = True
                self.m_Position = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def mouseMoveEvent(self, mouse_event):
        if self.resizeing:
            # 改變大小
            self.resize_window(mouse_event.globalPosition().toPoint())
        elif self.m_flag and mouse_event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.move(mouse_event.globalPosition().toPoint() - self.m_Position)
            mouse_event.accept()
        else:
            self.update_cursor(mouse_event.pos())  # 修正：update_cursor

    ## 無邊框移動_離開長按左鍵，結束觸發 ##
    def mouseReleaseEvent(self, event):  # 修正：添加 event 参数
        self.m_flag = False
        self.resizeing = False
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
    
    def is_on_border(self, pos):
        return (pos.x() >= self.width() - self.border_width or pos.y() >= self.height() - self.border_width)

    def resize_window(self, global_pos):
        diff = global_pos - self.m_Position
        new_width = max(self.minimumWidth(), self.width() + diff.x())
        new_height = max(self.minimumHeight(), self.height() + diff.y())
        self.resize(new_width, new_height)
        self.m_Position = global_pos

    def update_cursor(self, pos):  # 修正：update_cursor
        if self.is_on_border(pos):
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.SizeFDiagCursor))
        else:
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor)) 


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = teacher_window()
    win.show()
    sys.exit(app.exec())
