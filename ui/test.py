import sys
from PyQt6.QtWidgets import QMainWindow, QApplication, QLineEdit
from password_ui import Ui_MainWindow  # 確保這裡的匯入是正確的

class MyMainWin:
    def __init__(self):
        # 創建應用程序對象
        self.app = QApplication(sys.argv)
        # 設定主窗口
        self.main_window = QMainWindow()
        self.main_window.setObjectName("mainWindow")
        # 設置用戶介面
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.main_window)
        # 變更背景色
        self.main_window.setStyleSheet(
            """
            QMainWindow {
                background-color: #FCFAED;
            }
            QLineEdit {
                background-color: white;
            }
            """
        )

    def run_main(self):
        # 顯示介面並啟動應用程序事件循環
        self.main_window.show()
        sys.exit(self.app.exec())

if __name__ == "__main__":
    main = MyMainWin()
    main.run_main()
