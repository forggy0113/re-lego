import numpy as np
import torch
from typing import List, Tuple
from models.experimental import attempt_load
from utils.datasets import letterbox
from utils.general import non_max_suppression, scale_coords

class YoloV7Detector:
    """
    YOLOv7 物件偵測器

    方法：
        detect(img)
            參數：
                img (np.ndarray): BGR 影像
            返回：
                List[Tuple[Tuple[int,int,int,int], str]]: 每個偵測框與標籤文字
    """
    def __init__(
        self,
        model_path: str = "yolov7.pt",
        class_path: str = "classes.txt",
        device: str = 'cuda'
    ):
        # 選擇運算裝置，載入模型
        self.device = torch.device(device if torch.cuda.is_available() else 'cpu')
        self.model = attempt_load(model_path, map_location=self.device)
        self.model.eval()
        # 讀取類別名稱
        with open(class_path, 'r', encoding='utf-8') as f:
            self.class_names = [line.strip() for line in f]

    def detect(
        self,
        img: np.ndarray
    ) -> List[Tuple[Tuple[int,int,int,int], str]]:
        """
        在影像上執行偵測

        參數：
            img: BGR 影像
        返回：
            detections: list of ((x1,y1,x2,y2), "class conf")
        """
        img0 = img.copy()
        # 圖片預處理：resize + BGR->RGB + transpose
        img_proc = letterbox(img0, new_shape=640)[0]
        img_proc = img_proc[:, :, ::-1].transpose(2, 0, 1)
        img_proc = np.ascontiguousarray(img_proc)

        tensor = torch.from_numpy(img_proc).to(self.device).float() / 255.0
        tensor = tensor.unsqueeze(0)

        with torch.no_grad():
            pred = self.model(tensor, augment=False)[0]
            pred = non_max_suppression(pred, 0.8, 0.8)

        detections = []
        for det in pred:
            if len(det):
                # 反 scale 回原始影像尺寸
                det[:, :4] = scale_coords(
                    tensor.shape[2:], det[:, :4], img0.shape
                ).round()
                for *xyxy, conf, cls in det:
                    x1, y1, x2, y2 = map(int, xyxy)
                    label = f"{self.class_names[int(cls)]} {conf:.2f}"
                    detections.append(((x1, y1, x2, y2), label))
        return detections