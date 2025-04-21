from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from func.mouse_move import *

# 隱藏視窗標題欄
def win_no_title_bar(self):
    self.setWindowFlags(Qt.FramelessWindowHint) # 隱藏視窗標題欄
    self.setAttribute(Qt.WA_TranslucentBackground) # 設定背景透明
    return self

# 自適應螢幕大小，全螢幕
def win_full(self):
    screen_height = QApplication.desktop().screenGeometry().height() # 取得螢幕高度
    screen_width = QApplication.desktop().screenGeometry().width() # 取得螢幕寬度
    self.resize(screen_width, screen_height) # 設定視窗大小
    return self

# 視窗移動
def win_move(self):
    self.is_moving = False # 視窗移動狀態
    self.mouse_Position = None # 記錄滑鼠位置
    self.mouseMoveEvent = lambda event: mouseMoveEvent(self, event) # 滑鼠移動事件
    self.mousePressEvent = lambda event: mousePressEvent(self, event) # 滑鼠按下事件
    self.mouseReleaseEvent = lambda event: mouseReleaseEvent(self, event) # 滑鼠釋放事件
    return self

# 視窗縮放
def win_resize(self):
    # 初始化拖動和縮放相關的屬性
    self.is_dragging = False
    self.is_resizing = False
    self.drag_position = None
    self.resize_threshold = 20
    self.setMouseTracking(True)
    self.mouseMoveEvent = lambda event: border_mouseMove(self, event)
    self.mousePressEvent = lambda event: border_mousePress(self, event)
    self.mouseReleaseEvent = lambda event: border_mouseRelease(self, event)
    self.is_in_resize_area = lambda pos: is_in_resize_area(self, pos)
    self.update_cursor = lambda pos: update_cursor(self, pos)
    self.resize_window = lambda pos: resize_window(self, pos)
    


    