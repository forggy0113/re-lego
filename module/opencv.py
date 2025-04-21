import os
import cv2
import time
from multiprocessing.managers import BaseManager

# 定義與主程式相同的 Manager 類別
class QueueManager(BaseManager):
    pass

# 註冊共享的 Queue，不需要 callable 參數（因為只是連線）
QueueManager.register('get_queue')

# 從環境變數中讀取連線資訊
address = os.environ.get('QUEUE_ADDRESS', 'localhost')
port = int(os.environ.get('QUEUE_PORT', '50000'))
authkey = os.environ.get('QUEUE_AUTHKEY', 'abc').encode()

# 連線到 Manager 服務器
manager = QueueManager(address=(address, port), authkey=authkey)
manager.connect()

# 取得共享的 Queue
shared_queue = manager.get_queue()

# 設定緩衝區大小
buffer_size = 10

# 啟動相機讀取
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("無法開啟相機！")
    exit(1)

while True:
    ret, frame = cap.read()
    if not ret:
        print("無法讀取影像，結束程序。")
        break

    # 當 Queue 已滿時，移除最舊的影像
    while shared_queue.qsize() >= buffer_size:
        shared_queue.get()
    shared_queue.put(frame)  # 放入最新讀取的影像

    time.sleep(0.01)  # 調整讀取頻率

cap.release()