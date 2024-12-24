import cv2
from models.experimental import attempt_load
import torch
from utils.general import non_max_suppression, scale_coords
from utils.datasets import letterbox
import numpy as np
import time

def load_class(name_path):
    with open(name_path, 'r') as f:
        return [line.strip() for line in f]

def main():
    class_name_path = r'C:\Users\Ada\Desktop\yolov7_opencv\class_lego.txt'
    class_names = load_class(class_name_path)

    # 指定模型權重路徑
    weights_path = r'C:\Users\Ada\Desktop\yolov7_opencv\yolov7-main\best.pt'
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    if 'cuda':
        print('cuda可用')
    else:
        print('cuda不可用')
    # 加載模型
    model = attempt_load(weights_path, map_location=device)
    model.eval()  # 設置為推理模式

    print('模型加載完成')

    # 開啟攝影機
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("無法開啟攝影機")
        exit()
    # 開啟攝影機並設定解析度
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # 設定攝影機寬度
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)  # 設定攝影機高度
    # 確認影像解析度
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"攝影機解析度：{width}x{height}")

    frame_count = 0  # 計數幀數
    start_time = time.time()
    fps = 0  # Initialize fps before the loop

    while True:
        ret, frame = cap.read()  # 讀取攝影機內容
        if not ret:
            print("無法讀取幀，攝影機可能已關閉")
            break
        frame_count += 1  # 每讀取一幀就增加1
        # 圖片預處理
        img = letterbox(frame, new_shape=(640, 640))[0]  # 調整大小並保持比例
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        img = np.ascontiguousarray(img, dtype=np.float32) / 255.0  # 標準化到[0,1]
        img = torch.from_numpy(img).to(device).unsqueeze(0)  # 加載到gpu上跑，並且添加一個維度
        # 推論
        with torch.no_grad():
            predictions, _ = model(img)  # 模型推論
            results = non_max_suppression(predictions, conf_thres=0.70, iou_thres=0.80)  # 後處理
        classes = []
        coordinates = []
        # 5. 繪製檢測結果
        for det in results:  # 每個檢測結果
            if len(det):
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], frame.shape).round()
                # 調整框大小到原圖
                for *xyxy, conf, cls in det:  # 每個框的坐標、信心分數和類別
                    label = f"{class_names[int(cls)]} {conf:.2f}"
                    cv2.rectangle(frame, (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3])), (0, 255, 0), 2)
                    cv2.putText(frame, label, (int(xyxy[0]), int(xyxy[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    x_center = (xyxy[0] + xyxy[2]) / 2  # 計算物體中心 x 座標
                    y_center = (xyxy[1] + xyxy[3]) / 2  # 計算物體中心 y 座標
                    coordinates.append((x_center.item(), y_center.item()))
                    classes.append(class_names[int(cls)])  # 儲存類別

        # 計算每秒鐘的幾幀
        elapsed_time = time.time() - start_time
        if elapsed_time >= 1.0:  # 每秒鐘更新一次
            fps = frame_count  # 幀數即為FPS
            frame_count = 0  # 重置幀數計數器
            start_time = time.time()  # 重置時間計算

        # 在OpenCV視窗中顯示FPS
        cv2.putText(frame, f"FPS: {fps:.2f}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # 顯示結果
        cv2.imshow('YOLOv7 Detection', frame)

        # 按下 'q' 退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 釋放資源
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
