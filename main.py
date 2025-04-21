import os
import subprocess
import multiprocessing
from multiprocessing.managers import BaseManager
from queue import Queue

# 定義一個回傳 Queue 的函式
def get_shared_queue():
    return Queue()

# 定義一個 Manager 類別，用來共享 Queue
class QueueManager(BaseManager):
    pass

if __name__ == "__main__":
    # 註冊共享的 Queue
    QueueManager.register('get_queue', callable=get_shared_queue)
    
    # 啟動 Manager 服務器，設定地址、port 與驗證金鑰
    manager = QueueManager(address=('', 50000), authkey=b'abc')
    manager.start()
    
    # 從 Manager 中取得共享的 Queue
    shared_queue = manager.get_queue()
    
    # 將 Manager 的連線資訊透過環境變數傳遞給子程序
    os.environ['QUEUE_ADDRESS'] = 'localhost'
    os.environ['QUEUE_PORT'] = '50000'
    os.environ['QUEUE_AUTHKEY'] = 'abc'

    # 先執行 PyQt 程式（假設檔名為 pyqt_main.py），等待其結束
    subprocess.run(["python", "pyqt_main.py"])

    # 定義透過 subprocess 執行各功能的子程序函式
    def run_pygame():
        subprocess.run(["python", "pygame.py"])

    def run_opencv():
        subprocess.run(["python", "opencv.py"])

    def run_call_model():
        subprocess.run(["python", "call_model.py"])

    def run_docker_command():
        subprocess.run(["bash", "-c", "your_docker_command_here"])

    # 使用 multiprocessing 啟動其他子程序
    processes = [
        multiprocessing.Process(target=run_pygame),
        multiprocessing.Process(target=run_opencv),
        multiprocessing.Process(target=run_call_model),
        multiprocessing.Process(target=run_docker_command)
    ]

    for p in processes:
        p.start()

    for p in processes:
        p.join()

    # 結束 Manager 服務器
    manager.shutdown()
