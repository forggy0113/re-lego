import cv2
import pygame
import torch
from models.experimental import attempt_load
from utils.general import non_max_suppression, scale_coords
from utils.datasets import letterbox
import numpy as np
import time
import sys
from PIL import Image, ImageSequence


class GifDisplay:
    def __init__(self, gif_path, screen, fps):
        self.gif_path = gif_path
        self.screen = screen
        self.image = Image.open(gif_path)
        self.frames = []

        for frame in ImageSequence.Iterator(self.image):
            mode = frame.mode
            if mode == "P":  # 轉換調色盤模式為 RGBA
                frame = frame.convert("RGBA")
            pygame_image = pygame.image.fromstring(frame.tobytes(), frame.size, "RGBA")
            self.frames.append(pygame_image)

        self.clock = pygame.time.Clock()
        self.fps = fps  # 設定gif播放速動 (每秒幀數)
        self.running = True
        self.frame_index = 0

    def display_gif(self):
        """顯示 GIF 畫面 (左上角)"""
        frame = self.frames[self.frame_index]
        self.screen.fill((0, 0, 0))  # 清除畫面
        self.screen.blit(frame, (1600, 0))  # 右上角顯示(x座標, y座標)
        pygame.display.update()  # 更新畫面
        # 更新到下一幀
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.clock.tick(self.fps)  # 控制播放速度
    

class YOLO_Display:
    def __init__(self, screen, width=1600, height=900):
        self.screen = screen
        self.width = width
        self.height = height
        self.circle_radius = 20  # 圓形半徑設為20
        self.class_colors = {
            'support-11': (255, 255, 255),
            'bearing': (255, 204, 255),
            'hold': (255, 204, 153),
            'wheel': (102, 102, 153),
            'motor': (255, 255, 102),
            'long': (102, 255, 51),
            'screw': (0, 102, 255),
            'fixed': (51, 102, 0)
        }
    def draw_detection(self, coordinates, classes , y_offse=180):
        """繪製檢測結果"""
        for (x, y), cls in zip(coordinates, classes):  # coordinates=座標
            y += y_offse # 調整y座標，使y=180開始
            x = min(max(x, self.circle_radius), self.width - self.circle_radius)
            y = min(max(y, self.circle_radius), self.height - self.circle_radius)
            color = self.class_colors.get(cls, (255, 255, 255))
            pygame.draw.circle(self.screen, color, (int(x), int(y)), self.circle_radius)
        pygame.display.flip()  # 更新整個待顯示的介面到屏幕上

    def handle_pygame_events(self):
        # 處理Pygame事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def load_class(self, name_path):
        # 讀取類別名稱
        with open(name_path, 'r') as f:
            return [line.strip() for line in f]
    
    def load_model(self, weights_path, device):
        # 載入模型
        if torch.cuda.is_available():
            print('CUDA 可用')
        else:
            print('CUDA 不可用')
        model = attempt_load(weights_path, map_location=device)
        model.eval()  # 設置為推理模式
        print('模型加載完成')
        return model

def camera():
    """初始化攝影機並回傳攝影機對象"""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("無法開啟攝影機")
        exit()
    
    # 設定解析度
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1600)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 900)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"攝影機解析度：{width}x{height}")
    
    return cap  # 回傳攝影機對象

def main():
    """初始化 pygame"""
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    pygame.display.set_caption("Pygame Display")
    screen.fill((0, 0, 0))  # 填充黑色背景
    visualizer = YOLO_Display(screen)  # 創建yolov7視覺化
    """模型參數"""
    class_name_path = './pygame/class_lego.txt'
    weights_path = './pygame/best.pt'
    gif_path = './pygame/animation/step_1.gif'
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    class_names = visualizer.load_class(class_name_path)
    model = visualizer.load_model(weights_path, device)
    
    """初始化GIF"""
    gif = GifDisplay(gif_path, screen, fps=20)
    """初始化攝影機"""
    cap = camera()
    """ 初始化計數器 """
    frame_count = 0  # 計數幀數
    start_time = time.time()
    fps = 0  # Initialize fps before the loop
    """開始攝影機影像檢測"""
    while True:
        """處理GIF事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gif.running = False
        gif.display_gif()

        # 開始讀取攝影機影像
        ret, frame = cap.read()  # 讀取攝影機內容
        if not ret:
            print("無法讀取幀，攝影機可能已關閉")
            break
        frame_count += 1  # 每讀取一幀就增加1
        # 圖片預處理
        img = letterbox(frame, new_shape=(640,640))[0]  # 調整大小並保持比例
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        img = np.ascontiguousarray(img, dtype=np.float32) / 255.0  # 標準化到[0,1]
        img = torch.from_numpy(img).to(device).unsqueeze(0)  # 加載到gpu上跑，並且添加一個維度

        # 推論
        with torch.no_grad():
            predictions, _ = model(img)  # 模型推論
            results = non_max_suppression(predictions, conf_thres=0.70, iou_thres=0.80)  # 後處理

        classes = []
        coordinates = []
        # 繪製檢測結果
        for det in results:
            if len(det):
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], frame.shape).round()
                for *xyxy, conf, cls in det:  # 每個框的坐標、信心分數和類別
                    # 調整y座標，使y=180開始
                    # xyxy[1] += y_offset # 左上角 y 座標 + 180
                    # xyxy[3] += y_offset # 右下角 y 座標 + 180
                    label = f"{class_names[int(cls)]} {conf:.2f}"
                    # 只顯示在裁剪範圍內的結果
                    cv2.rectangle(frame, (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3])), (0, 255, 0), 2)
                    cv2.putText(frame, label, (int(xyxy[0]), int(xyxy[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    x_center = (xyxy[0] + xyxy[2]) / 2  # 計算物體中心 x 座標
                    y_center = (xyxy[1] + xyxy[3]) / 2  # 計算物體中心 y 座標
                    coordinates.append((x_center.item(), y_center.item()))
                    classes.append(class_names[int(cls)])  # 儲存類別
        print(f"classes={classes}")
        visualizer.draw_detection(coordinates, classes)

        # 只顯示攝影機影像區域的偵測框
        cv2.imshow('YOLOv7 Detection', frame)

        visualizer.handle_pygame_events()

        # 計算 FPS
        elapsed_time = time.time() - start_time
        if elapsed_time >= 1.0:
            fps = frame_count
            frame_count = 0
            start_time = time.time()

        cv2.putText(frame, f"FPS: {fps:.2f}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()