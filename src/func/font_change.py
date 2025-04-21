from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtWidgets import QWidget

class Font:
    def __init__(self, parent, ui, init_font_size):
        self.is_font_1 = True # 初始化當前字體狀態
        self.parent = parent # 父窗口
        self.ui = ui # 當前窗口
        self.init_font_size = init_font_size
        # 定義字體
        self.font_id_1 = QFontDatabase.addApplicationFont("./ui/font/BpmfGenSenRounded-R.ttf")
        self.font_id_2 = QFontDatabase.addApplicationFont("./ui/font/FakePearl-Regular.ttf")
        if self.font_id_1 == -1:
            print("無法加載字體1")
        if self.font_id_2 == -1:
            print("無法加載字體2")
        # 獲取字體資料庫
        self.font_family_1 = QFontDatabase.applicationFontFamilies(self.font_id_1)
        self.font_family_2 = QFontDatabase.applicationFontFamilies(self.font_id_2)
        
    
    def font_all_change(self, font):
        for widget in self.parent.findChildren(QWidget): # 使用主窗口調用 findChildren，遍歷所有子窗口的 widget
            widget.setFont(font)
    
    def font_change_size_force(self, font_family):
        for widget in self.parent.findChildren(QWidget):
            original_font = widget.font()
            new_font = QFont(font_family)
            new_font.setPointSize(original_font.pointSize())
            widget.setFont(new_font)
        
    def font_change(self):
        # 切換字體邏輯
        try:
            if self.is_font_1:
                if self.font_family_2:
                    self.font = QFont(self.font_family_2[0], self.init_font_size)
                    self.font_all_change(self.font)
                    print(f"切換到字體{self.font_family_2[0]},大小")
                else:
                    print("無法加載字體 2")
            else:
                if self.font_family_1:
                    self.font = QFont(self.font_family_1[0], self.init_font_size)
                    self.font_all_change(self.font)
                    print(f"切換到字體{self.font_family_1[0]}")
                else:
                    print("無法加載字體 1")
        except Exception as e:
            print(f"無法加載字體錯誤: {e}")
        # 切換狀態：如果當前是font_1，則切換到font_2；如果當前是font_2，則切換到font_1
        self.is_font_1 = not self.is_font_1


    def font_size_change(self, value):
        # 設定字體大小跟隨滑動條變化
        self.init_font_size = value
        # 獲取當前字體家族類型
        font_family = self.font.family()
        if self.is_font_1:
            font_family = self.font_family_1[0] #使用family_1
        else:
            font_family = self.font_family_2[0] #使用family_2
        # 設定新字體大小
        if font_family:
            current_font_size = QFont(font_family, value)
            print(f"當前字體:{font_family}，字體大小:{value}")
            self.font_all_change(current_font_size)
            self.ui.txt_font_size.setFont(current_font_size)
            self.ui.txt_font_size.setText(f"字型大小：{value}")
    
