import sys
from PyQt5.QtWidgets import QApplication
from module.qt_main import Main

if __name__ == '__main__':


    app = QApplication(sys.argv)
    window = Main()          # 你的主視窗（原本就會呼叫 win_full 等函式）

    # === 把視窗放到第二顆螢幕（如果有）=============================
    screens = app.screens()           # 依 OS 回傳所有螢幕，index 0 一般是主要
    if len(screens) > 1:
        second = screens[1]           # 第二顆螢幕（投影機）
        geo = second.geometry()       # QRect：含 x/y/寬/高
        window.setGeometry(geo)       # 把主視窗填滿那顆螢幕
        window.showFullScreen()       # 無邊框全螢幕（你已經有 win_full，可擇一）
    else:
        window.showFullScreen()       # 只有一顆螢幕就照原本方式顯示
    # ============================================================

    sys.exit(app.exec_())
