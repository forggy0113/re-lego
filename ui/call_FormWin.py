import sys
from PyQt6.QtWidgets import QApplication, QWidget
from sign_in_ui import Ui_Form  # 變更匯入py檔，顯示主畫面

class MyApp:
    def __init__(self):
        # 創建應用程序對象
        self.app = QApplication(sys.argv)
        # 設置主窗口
        self.main_window = QWidget()
        self.main_window.setObjectName("mainWindow")
        self.ui = Ui_Form()
        self.ui.setupUi(self.main_window)
        self.main_window.setStyleSheet("background-color: #FCFAED;")

    def run(self):
        self.main_window.show()
        sys.exit(self.app.exec())

if __name__ == "__main__":
    app = MyApp()
    app.run()



