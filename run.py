from module.qt_main import Main
from main import run_game  # ✅ 或 alias run_game = main
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QGuiApplication
import sys
def handle_login_success(student_data):
    print(f"✅ 登入成功: {student_data}")
    play_time = run_game(student_data, db = window.db)
    print(f"🎮 遊戲結束，遊玩時間：{play_time:.2f} 秒")
    window.reset()  # 回到登入畫面

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main()
    window.on_login_success = handle_login_success

    # 顯示在第二螢幕（如果有）
    screens = QGuiApplication.screens()
    if len(screens) > 1:
        second_screen = screens[1]
        geo = second_screen.geometry()
        window.setGeometry(geo)
        window.showFullScreen()
    else:
        window.showFullScreen()
        print("⚠️ 找不到第二螢幕，顯示在主螢幕")

    sys.exit(app.exec_())
