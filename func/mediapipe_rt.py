import cv2
import mediapipe as mp
import numpy as np
from typing import List, Tuple

class MediaPipeHandTracker:
    """
    MediaPipe 手部追蹤器

    方法：
        process_frame(frame, draw_landmarks=True, debug_info=True)
            參數：
                frame (np.ndarray): BGR 格式的影像
                draw_landmarks (bool): 是否在影像上繪製骨架連線
                debug_info (bool): 是否顯示關鍵點索引
            返回：
                Tuple[np.ndarray, List[List[Tuple[int,int]]]]: 標註後的影像，及每隻手的 21 個關鍵點座標列表
        close(): 關閉並釋放 MediaPipe 資源
    """
    def __init__(
        self,
        max_num_hands: int = 2,
        model_complexity=0,
        detection_confidence: float = 0.8,
        tracking_confidence: float = 0.8
    ):
        # 初始化 MediaPipe 手部模型與設定
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_num_hands,
            model_complexity=model_complexity,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )

    def process_frame(
            self,
            frame: np.ndarray,
            draw_landmarks: bool = True,
            debug_info: bool = True
        ) -> Tuple[np.ndarray,
                List[List[Tuple[int, int]]],
                List[str]]:
        """
        偵測並標註手部關鍵點

        參數
        ----
        frame : ndarray(H,W,3)  BGR 影像
        draw_landmarks : bool   是否畫骨架
        debug_info     : bool   是否畫索引

        返回
        ----
        (annotated_frame,
        hand_landmarks_list,   # list[21 個 (x,y)]
        handedness_list)       # list["Left"/"Right"] 與 landmarks 順序對齊
        """
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image_rgb)

        hand_landmarks_list: List[List[Tuple[int, int]]] = []
        handedness_list: List[str] = []
        h, w, _ = frame.shape

        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # ➊ 座標轉換
                landmarks = [(int(lm.x * w), int(lm.y * h))
                            for lm in hand_landmarks.landmark]
                hand_landmarks_list.append(landmarks)

                # ➋ 取 handedness (Left / Right)
                if results.multi_handedness and idx < len(results.multi_handedness):
                    handedness = results.multi_handedness[idx].classification[0].label
                else:
                    handedness = "Unknown"
                handedness_list.append(handedness)

                # ➌ 畫圖 & 除錯
                if draw_landmarks:
                    self.mp_drawing.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                    )
                if debug_info:
                    x0, y0 = landmarks[0]
                    cv2.putText(frame, f"{handedness} hand {idx}",
                                (x0, y0 - 20), cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, (255, 0, 0), 2)
                    for i, (x, y) in enumerate(landmarks):
                        cv2.circle(frame, (x, y), 3, (0, 255, 255), -1)
                        if i in [0, 4, 8, 12, 16, 20]:
                            cv2.putText(frame, f"{i}", (x + 5, y - 5),
                                        cv2.FONT_HERSHEY_PLAIN, 1,
                                        (0, 255, 0), 1)

        # 顯示手數
        cv2.putText(frame, f"hands: {len(hand_landmarks_list)}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 255, 0), 2)

        return frame, hand_landmarks_list, handedness_list


    def close(self) -> None:
        """
        釋放 MediaPipe Hands 資源
        """
        self.hands.close()
    def get_hand_tips(self, hand_landmarks):
        """
        從每隻手的 21 個座標點（MediaPipe 格式）中，取得所有手指指尖的座標。
        Args:
            hand_landmarks (list): 
                - 格式為 [ [ (x0, y0), (x1, y1), ..., (x20, y20) ], ... ]
                - 每隻手是 21 個(x, y)座標的列表。
        Returns:
            tips (list): 
                - 包含所有手指指尖的座標
                - 每隻手一筆五個指尖 [(thumb_tip, index_tip, middle_tip, ring_tip, pinky_tip)]
                - 額外將食指指尖(index_tip)的座標(int格式)單獨 append 進 tips
        """
        tips = []
        if hand_landmarks:
            for hand in hand_landmarks:
                # 取得每隻手的五個指尖 landmark
                tips.extend([hand[4], hand[8], hand[12], hand[16], hand[20]])
                # 額外將食指指尖的座標(int格式)加入
                tip = hand[8]
                tips.extend((int(tip[0]), int(tip[1])))
        return tips

    def is_hand_near(self, tips, target_pos, threshold=50):
        """
        判斷 tips 之中是否有某個點接近目標位置 target_pos。
        Args:
            tips (list): 
                - 指尖座標清單，每個元素為 (x, y)
            target_pos (tuple): 
                - 目標座標 (x, y)
            threshold (int, optional): 
                - 距離閾值，預設 50 像素內算接近
        Returns:
            (bool, tuple):
                - 若有指尖距離小於 threshold，回傳 True 和該點的 (x, y)
                - 否則回傳 False, None
        """
        for tip in tips:
            dx, dy = tip[0] - target_pos[0], tip[1] - target_pos[1]
            if dx * dx + dy * dy < threshold * threshold:
                return True, tip
        return False, None

    
    # def hand_in_bbox(self, hand_landmarks_list, bbox, landmark_idx=8, margin=0):
    #     """
    #     檢查有無任何一隻手的指定關鍵點（預設食指指尖）在 bbox 內
    #     Args:
    #         hand_landmarks_list: 來自 process_frame 的 21點座標list
    #         bbox: (x1, y1, x2, y2)
    #         landmark_idx: 要判斷的landmark索引（預設8=食指指尖）
    #         margin: 邊界容許誤差
    #     Returns:
    #         (bool, (x, y)): 是否有手指在bbox、該手指座標
    #     """
    #     x1, y1, x2, y2 = bbox
    #     for hand in hand_landmarks_list:
    #         x, y = hand[landmark_idx]
    #         if (x1 - margin) <= x <= (x2 + margin) and (y1 - margin) <= y <= (y2 + margin):
    #             return True, (x, y)
    #     return False, None

    # def is_object_grabbed(self, hand_landmarks_list, curr_bbox, init_bbox, threshold=20):
    #     """
    #     判斷手指在bbox，且物件已離開初始位置
    #     Returns:
    #         (bool, (x, y)): 是否抓取、手座標
    #     """
    #     grabbed, pos = self.hand_in_bbox(hand_landmarks_list, curr_bbox)
    #     if grabbed:
    #         # 算現在bbox中心與原始中心的距離
    #         curr_cx, curr_cy = (curr_bbox[0]+curr_bbox[2])//2, (curr_bbox[1]+curr_bbox[3])//2
    #         init_cx, init_cy = (init_bbox[0]+init_bbox[2])//2, (init_bbox[1]+init_bbox[3])//2
    #         dist = ((curr_cx - init_cx) ** 2 + (curr_cy - init_cy) ** 2) ** 0.5
    #         if dist > threshold:
    #             return True, pos
    #     return False, None
