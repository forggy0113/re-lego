import sys
from font_ui import Ui_MainWindow
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import QtGui

class FontWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 加載兩種字體
        self.font_id_1 = QtGui.QFontDatabase.addApplicationFont("BpmfGenSenRounded-R.ttf")
        self.font_family_1 = QtGui.QFontDatabase.applicationFontFamilies(self.font_id_1)

        self.font_id_2 = QtGui.QFontDatabase.addApplicationFont("FakePearl-Regular.ttf")
        self.font_family_2 = QtGui.QFontDatabase.applicationFontFamilies(self.font_id_2)

        # 設置初始字體
        if self.font_family_1:
            self.current_font = QtGui.QFont(self.font_family_1[0], 18)
            self.ui.label.setFont(self.current_font)
            print(f"初始字體: {self.font_family_1[0]}")

        # 初始化字體狀態
        self.is_font1 = True

        # 綁定按鈕點擊事件來切換字體
        self.ui.pushButton.clicked.connect(self.change_font)

    def change_font(self):
        # 切換字體
        if self.is_font1:
            if self.font_family_2:
                new_font = QtGui.QFont(self.font_family_2[0], 18)
                self.ui.label.setFont(new_font)
                print(f"切換到新字體: {self.font_family_2[0]}")
            else:
                print("無法加載新字體。")
        else:
            if self.font_family_1:
                original_font = QtGui.QFont(self.font_family_1[0], 18)
                self.ui.label.setFont(original_font)
                print(f"切換回原始字體: {self.font_family_1[0]}")
            else:
                print("無法加載原始字體。")

        # 切換字體狀態
        self.is_font1 = not self.is_font1

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = FontWindow()
    win.show()
    sys.exit(app.exec())
