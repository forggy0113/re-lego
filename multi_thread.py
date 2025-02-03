import multiprocessing as mp
import time
from ui_main import *  # 確保這裡能夠正確導入 Login_Window
from src.sql_py.func_sql import Stus

# Event object used to signal threads to start
start_event = mp.Event()

def pyqt_thread():
    print("First thread (pyqt_thread) is running")
    app = QApplication(sys.argv)
    win = InterfaceWindow()
    win.show()
    sys.exit(app.exec_())
    start_event.set()
    print("First thread (pyqt_thread) has finished work")

def pygame_thread():
    start_event.wait()
    print("Second thread (pygame_thread) is running")
    print("Second thread (pygame_thread) has finished work")

def cv_thread():
    start_event.wait()
    print("Third thread (cv_thread) is running")
    print("Third thread (cv_thread) has finished work")

def call_model_thread():
    start_event.wait()
    print("Fourth thread (call_model_thread) is running")
    print("Fourth thread (call_model_thread) has finished work")

# Example usage
is_logged_in = True  # 這個變數目前沒有在程式中使用，可以考慮如何在程式邏輯中利用它

# Create threads
thread1 = mp.Process(target=pyqt_thread)
thread2 = mp.Process(target=pygame_thread)
thread3 = mp.Process(target=cv_thread)
thread4 = mp.Process(target=call_model_thread)

# Start and join threads
thread1.start()
thread1.join()  # 等待 thread1 完成並設置事件

# Start other threads after thread1 has completed
thread2.start()
thread3.start()
thread4.start()

thread2.join()
thread3.join()
thread4.join()

print("All threads have finished")
