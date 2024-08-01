# my_window.py
from PyQt6.QtWidgets import QMainWindow
from signin_inference_ui import Ui_MainWindow

class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
