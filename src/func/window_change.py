from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt



# 滑鼠按下事件
def mousePressEvent(self, event):
    if event.button() == Qt.LeftButton:
        self.is_moving = True
        # 計算相對座標
        self.mouse_position = event.globalPos() - self.pos()
        event.accept()

# 滑鼠移動事件
def mouseMoveEvent(self, event):
    if self.is_moving:
        # 計算新窗口位置
        self.move(event.globalPos() - self.mouse_position)
        event.accept()

# 滑鼠釋放事件
def mouseReleaseEvent(self, event):
    if event.button() == Qt.LeftButton:
        self.is_moving = False
        event.accept()

# 放大視窗
def max_win(self):
    if self.isMaximized():
        self.showNormal()
    else:
        self.showMaximized()

# 邊框滑鼠按下事件
def border_mousePress(self, event):
    if event.button() == Qt.LeftButton:
        if self.is_in_resize_area(event.pos()):
            self.is_resizing = True
        else:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.pos()

# 邊框滑鼠移動事件
def border_mouseMove(self, event):
    if self.is_dragging:
        self.move(event.globalPos() - self.drag_position)
    elif self.is_resizing:
        self.resize_window(event)
    else:
        self.update_cursor(event.pos())

# 邊框滑鼠釋放事件
def border_mouseRelease(self, event):
    if event.button() == Qt.LeftButton:
        self.is_dragging = False
        self.is_resizing = False
        self.setCursor(Qt.ArrowCursor)

# 更新游標形狀
def update_cursor(self, pos):
    if self.is_in_resize_area(pos):
        if pos.x() < self.resize_threshold:
            if pos.y() < self.resize_threshold:
                self.setCursor(Qt.SizeFDiagCursor)
            elif pos.y() > self.height() - self.resize_threshold:
                self.setCursor(Qt.SizeBDiagCursor)
            else:
                self.setCursor(Qt.SizeHorCursor)
        elif pos.x() > self.width() - self.resize_threshold:
            if pos.y() < self.resize_threshold:
                self.setCursor(Qt.SizeBDiagCursor)
            elif pos.y() > self.height() - self.resize_threshold:
                self.setCursor(Qt.SizeFDiagCursor)
            else:
                self.setCursor(Qt.SizeHorCursor)
        elif pos.y() < self.resize_threshold:
            self.setCursor(Qt.SizeVerCursor)
        elif pos.y() > self.height() - self.resize_threshold:
            self.setCursor(Qt.SizeVerCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

# 判斷是否在邊框範圍
def is_in_resize_area(self, pos):
    return (
        pos.x() < self.resize_threshold or
        pos.x() > self.width() - self.resize_threshold or
        pos.y() < self.resize_threshold or
        pos.y() > self.height() - self.resize_threshold
    )

# 調整視窗大小
def resize_window(self, event):
    mouse_pos = event.globalPos()
    screen_geometry = QApplication.primaryScreen().availableGeometry()
    screen_width = screen_geometry.width()
    screen_height = screen_geometry.height()

    if event.pos().x() < self.resize_threshold:
        if event.pos().y() < self.resize_threshold:
            width = self.width() - (mouse_pos.x() - self.x())
            height = self.height() - (mouse_pos.y() - self.y())
            self.setGeometry(self.x() + (mouse_pos.x() - self.x()), self.y() + (mouse_pos.y() - self.y()), width, height)
        elif event.pos().y() > self.height() - self.resize_threshold:
            width = self.width() - (mouse_pos.x() - self.x())
            height = mouse_pos.y() - self.y()
            self.setGeometry(self.x() + (mouse_pos.x() - self.x()), self.y(), width, height)
        else:
            width = self.width() - (mouse_pos.x() - self.x())
            self.setGeometry(self.x() + (mouse_pos.x() - self.x()), self.y(), width, self.height())
    elif event.pos().x() > self.width() - self.resize_threshold:
        if event.pos().y() < self.resize_threshold:
            width = mouse_pos.x() - self.x()
            height = self.height() - (mouse_pos.y() - self.y())
            self.setGeometry(self.x(), self.y() + (mouse_pos.y() - self.y()), width, height)
        elif event.pos().y() > self.height() - self.resize_threshold:
            width = mouse_pos.x() - self.x()
            height = mouse_pos.y() - self.y()
            self.setGeometry(self.x(), self.y(), width, height)
        else:
            width = mouse_pos.x() - self.x()
            self.setGeometry(self.x(), self.y(), width, self.height())
    elif event.pos().y() < self.resize_threshold:
        height = self.height() - (mouse_pos.y() - self.y())
        self.setGeometry(self.x(), self.y() + (mouse_pos.y() - self.y()), self.width(), height)
    elif event.pos().y() > self.height() - self.resize_threshold:
        height = mouse_pos.y() - self.y()
        self.setGeometry(self.x(), self.y(), self.width(), height)

    max_width = min(self.width(), screen_width)
    max_height = min(self.height(), screen_height)

    self.setGeometry(self.x(), self.y(), max_width, max_height)

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
    


    