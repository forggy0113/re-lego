from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
# 滑鼠移位置
def mousePressEvent(self, event):
    if event.button() == QtCore.Qt.MouseButton.LeftButton:
        self.is_moving = True
        # 滑鼠位置 - 窗口左上角座標相對於窗口位置。 計算相對座標
        self.mouse_position = event.globalPosition().toPoint() - self.pos()
        event.accept()
    
# 滑鼠移動位置
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
# 放大視窗
def max_win(self):
    if self.isMaximized():
        self.showNormal()
    else:
        self.showMaximized()
# 滑鼠點擊事件判斷縮放、移動
def border_mousePress(self, event):
    if event.button() == Qt.MouseButton.LeftButton:
        if self.is_in_resize_area(event.pos()):
            self.is_resizing = True
        else:
            self.is_dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.pos()
# 滑鼠移動事件判斷縮放、移動
def border_mouseMove(self, event):
    if self.is_dragging:
        self.move(event.globalPosition().toPoint() - self.drag_position)
    elif self.is_resizing:
        self.resize_window(event)
    else:
        self.update_cursor(event.pos())
# 滑鼠釋放事件判斷縮放、移動
def border_mouseRelease(self, event):
    if event.button() == Qt.MouseButton.LeftButton:
        self.is_dragging = False
        self.is_resizing = False
        self.setCursor(Qt.CursorShape.ArrowCursor)
# 靠近邊界時變更游標
def update_cursor(self, pos):
    if self.is_in_resize_area(pos):
        # 左邊位置 = 滑鼠水平座標 < 閥值 
        if pos.x() < self.resize_threshold:
            # 左上角 = 滑鼠垂直座標 < 閥值
            if pos.y() < self.resize_threshold:
                self.setCursor(Qt.CursorShape.SizeFDiagCursor) 
            # 左下角 = 滑鼠垂直座標 > 視窗高 - 閥值
            elif pos.y() > self.height() - self.resize_threshold:
                self.setCursor(Qt.CursorShape.SizeBDiagCursor)
            #左邊
            else:
                self.setCursor(Qt.CursorShape.SizeHorCursor)

        # 右邊位置 = 滑鼠水平座標 > 視窗寬 - 閥值         
        elif pos.x() > self.width() - self.resize_threshold:
            #  右上角 = 滑鼠垂直座標 < 閥值
            if pos.y() < self.resize_threshold:
                self.setCursor(Qt.CursorShape.SizeBDiagCursor)
            #  右下角 = 滑鼠垂直座標 > 視窗高 - 閥值
            elif pos.y() > self.height() - self.resize_threshold:
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            # 右邊
            else:
                self.setCursor(Qt.CursorShape.SizeHorCursor)
        # 頂端邊 = 滑鼠垂直座標 < 閥值
        elif pos.y() < self.resize_threshold:
            self.setCursor(Qt.CursorShape.SizeVerCursor) 
        # 底邊 = 滑鼠垂直座標 > 視窗高 - 閥值
        elif pos.y() > self.height() - self.resize_threshold:
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

def is_in_resize_area(self, pos):
    """ 判断鼠标是否在边缘或角落的缩放区域 """
    return (
        pos.x() < self.resize_threshold or
        pos.x() > self.width() - self.resize_threshold or
        pos.y() < self.resize_threshold or
        pos.y() > self.height() - self.resize_threshold
    )

def resize_window(self, event):
    # 獲取當前滑鼠位置
    mouse_pos = event.globalPosition().toPoint()
    # 獲取使用者螢幕大小，防止過度放大
    screen_geometry = QApplication.primaryScreen().availableGeometry()
    screen_width = screen_geometry.width()
    screen_height = screen_geometry.height()
    # setGemetry(x座標, y座標, width ,height)
    # 左邊位置 = 滑鼠水平座標 < 閥值
    if event.pos().x() < self.resize_threshold:
        # 左上角 = 滑鼠垂直座標 < 閥值
        if event.pos().y() < self.resize_threshold:
            width = self.width() - (mouse_pos.x() - self.x())
            height = self.height() - (mouse_pos.y() - self.y())
            self.setGeometry(self.x() + (mouse_pos.x() - self.x()), self.y() + (mouse_pos.y() - self.y()), width, height)
        # 左下角 = 滑鼠垂直座標 > 視窗高 - 閥值    
        elif event.pos().y() > self.height() - self.resize_threshold:
            width = self.width() - (mouse_pos.x() - self.x())
            height = mouse_pos.y() - self.y()
            self.setGeometry(self.x() + (mouse_pos.x() - self.x()), self.y(), width, height)
        # 左邊
        else: 
            width = self.width() - (mouse_pos.x() - self.x())
            self.setGeometry(self.x() + (mouse_pos.x() - self.x()), self.y(), width, self.height())
    # 右邊位置 = 滑鼠水平座標 > 視窗寬 - 閥值          
    elif event.pos().x() > self.width() - self.resize_threshold:
        # 右上角 = 滑鼠垂直座標 < 閥值
        if event.pos().y() < self.resize_threshold:
            width = mouse_pos.x() - self.x()
            height = self.height() - (mouse_pos.y() - self.y())
            self.setGeometry(self.x(), self.y() + (mouse_pos.y() - self.y()), width, height)
        # 左下角 = 滑鼠垂直座標 > 視窗高 - 閥值
        elif event.pos().y() > self.height() - self.resize_threshold:
            width = mouse_pos.x() - self.x()
            height = mouse_pos.y() - self.y()
            self.setGeometry(self.x(), self.y(), width, height)
        # 右邊
        else:  
            width = mouse_pos.x() - self.x()
            self.setGeometry(self.x(), self.y(), width, self.height())
    # 頂端邊 = 滑鼠垂直座標 < 閥值
    elif event.pos().y() < self.resize_threshold:
        height = self.height() - (mouse_pos.y() - self.y())
        self.setGeometry(self.x(), self.y() + (mouse_pos.y() - self.y()), self.width(), height)
    # 底邊 = 滑鼠垂直座標 > 視窗高 - 閥值
    elif event.pos().y() > self.height() - self.resize_threshold:
        height = mouse_pos.y() - self.y()
        self.setGeometry(self.x(), self.y(), self.width(), height)

    # 限制視窗不超過使用者螢幕
    max_width = min(self.width(), screen_width)
    max_height = min(self.height(), screen_height)

    self.setGeometry(self.x(), self.y(), max_width, max_height)