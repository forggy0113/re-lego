from PyQt6 import QtCore, QtGui, QtWidgets
import sys

from PyQt6 import QtCore, QtGui, QtWidgets
import sys

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        
        # Get screen size
        screen = QtGui.QGuiApplication.primaryScreen().geometry()
        screen_w = screen.width()
        screen_h = screen.height()
        
        # # Set Form properties
        # Form.resize(690, 456)
        # Form_w = Form.width()
        # Form_h = Form.height()
        print(screen_w, screen_h)
        # Calculate center position
        new_x = int((screen_w) * 0.6)
        new_y = int((screen_h) * 0.6)
        #Form.move(new_x, new_y)
        Form.setFixedSize(new_x, new_y)
        # Add a push button
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(100, 50, 75, 23))
        self.pushButton.setObjectName("pushButton")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.pushButton.setText(_translate("Form", "PushButton"))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
