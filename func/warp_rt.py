# warp_rt.py
import os
import cv2
import numpy as np
import pygame
from typing import Optional, Dict, Tuple
from PIL import Image
from func.pygame_rt import *  # draw_guidance_with_center 等工具
# from pygame_rt import *

class WarpProcessor:
    """
    ArUco 校正與影像透視變換模組
    """
    # --------------------------------------------------
    def __init__(self, screen_width: int, screen_height: int,
                 button_centers, button_radius: int):
        """
        Args:
            screen_width   (int): 投影畫面寬度 (px)
            screen_height  (int): 投影畫面高度 (px)
            button_centers (list[tuple[int,int]]): 互動圓形按鈕中心座標 [(cx,cy), ...]
            button_radius  (int): 按鈕半徑 (px)
        """
        # 投影區域尺寸
        self.SCREEN_WIDTH  = screen_width
        self.SCREEN_HEIGHT = screen_height

        # ArUco & UI 參數
        self.MARKER_SIZE  = 60
        self.EDGE_SIZE    = 80
        self.EDGE_MARGIN  = 10

        # 圓形按鈕
        self.button_centers = button_centers or []
        self.button_radius  = button_radius
        self.button_progress = [0.0] * len(button_centers)  # 充能百分比


        # 透視校正狀態
        self.M: Optional[np.ndarray] = None
        self.calibrated: bool = False

        # 目標畫面四角對應座標 (id 0→左上, 1→右上, 2→左下, 3→右下)
        self.ID_TO_CORNER: Dict[int, Tuple[float, float]] = {
            0: (0.0, 0.0),
            1: (self.SCREEN_WIDTH, 0.0),
            2: (0.0, self.SCREEN_HEIGHT),
            3: (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        }

        # ArUco 字典
        self.ARUCO_IDS  = [0, 1, 2, 3]
        self.ARUCO_DICT = cv2.aruco.getPredefinedDictionary(
            cv2.aruco.DICT_4X4_50
        )

        # 投影引導狀態 (由主程式每幀更新)
        self.proj_draw_info = {
            'cuni_draw_pos'   : None,
            'cuni_draw_radius': None,
            'cint_draw_pos'   : None,
            'cint_draw_radius': None
        }

        # 動畫相關
        self.current_animation_frames = []  # list[pygame.Surface]
        self.current_animation_idx    = 0
        self.current_animation_path   = None

    # --------------------------------------------------
    def update_button_progress(self, progress):
        """主執行緒每幀呼叫，用 list[float 0~1] 更新充能進度"""
        self.button_progress = progress.copy()
    # ====== 第二螢幕投影迴圈 ===============================================
    def generate_marker_images(self):
        """產生四張 ArUco marker 的 Pygame Surface"""
        markers = []
        for marker_id in self.ARUCO_IDS:
            img = cv2.aruco.generateImageMarker(
                self.ARUCO_DICT, marker_id, self.MARKER_SIZE
            )
            rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            surf = pygame.surfarray.make_surface(rgb.swapaxes(0, 1))
            markers.append(surf)
        return markers

    def show_aruco_on_second_screen(
        self,
        stop_event,
        stu_name: str,
        start_time: float,
        text_settings: dict
    ):
        """
        在第二螢幕持續顯示：
          • 四角 ArUco + 白框
          • 圓形按鈕
          • StepGuide 引導圈/箭頭
          • 動畫
        """
        os.environ["SDL_VIDEO_WINDOW_POS"] = "1920,0"  # 讓視窗出現在右屏最左上
        import time
        pygame.init()
        # 初始化字體模組 & 字體
        pygame.font.init()
        # 如果有指定字體檔，就用 Font；否則 fallback 到 SysFont
        font_path = text_settings.get("font_path")
        font_size = text_settings["font_size"]
        if font_path:
            font = pygame.font.Font(font_path, font_size)
        else:
            font = pygame.font.SysFont(None, font_size)
        screen = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.NOFRAME
        )
        pygame.display.set_caption("ArUco 投影")

        markers   = self.generate_marker_images()
        positions = [
            (self.EDGE_MARGIN, self.EDGE_MARGIN),
            (self.SCREEN_WIDTH - self.EDGE_SIZE + self.EDGE_MARGIN, self.EDGE_MARGIN),
            (self.EDGE_MARGIN,
             self.SCREEN_HEIGHT - self.EDGE_SIZE + self.EDGE_MARGIN),
            (self.SCREEN_WIDTH - self.EDGE_SIZE + self.EDGE_MARGIN,
             self.SCREEN_HEIGHT - self.EDGE_SIZE + self.EDGE_MARGIN)
        ]

        clock = pygame.time.Clock()
        while not stop_event.is_set():
            pygame.event.pump()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    stop_event.set()

            screen.fill((0, 0, 0))

            # ---- 四角白框 ---------------------------------
            pygame.draw.rect(screen, (255, 255, 255),
                             (0, 0, self.EDGE_SIZE, self.EDGE_SIZE))
            pygame.draw.rect(screen, (255, 255, 255),
                             (self.SCREEN_WIDTH - self.EDGE_SIZE, 0,
                              self.EDGE_SIZE, self.EDGE_SIZE))
            pygame.draw.rect(screen, (255, 255, 255),
                             (0, self.SCREEN_HEIGHT - self.EDGE_SIZE,
                              self.EDGE_SIZE, self.EDGE_SIZE))
            pygame.draw.rect(screen, (255, 255, 255),
                             (self.SCREEN_WIDTH - self.EDGE_SIZE,
                              self.SCREEN_HEIGHT - self.EDGE_SIZE,
                              self.EDGE_SIZE, self.EDGE_SIZE))

            # ---- ArUco 圖片 --------------------------------
            for surf, pos in zip(markers, positions):
                screen.blit(surf, pos)

            # ---- StepGuide 引導圈 / 箭頭 --------------------
            info = self.proj_draw_info
            if (info['cuni_draw_pos'] and info['cint_draw_pos']):
                draw_guidance_with_center(
                    screen,
                    info['cuni_draw_pos'], info['cuni_draw_radius'],
                    info['cint_draw_pos'], info['cint_draw_radius']
                )

            # ---- 圓形按鈕 ----------------------------------
            for i, (cx, cy) in enumerate(self.button_centers):
                # ① 外框
                pygame.draw.circle(
                    screen, (0, 255, 255), (cx, cy),
                    self.button_radius, width=4
                )
                # ② 充能填充：self.button_progress[i] 取值 0.0~1.0
                prog = self.button_progress[i] if i < len(self.button_progress) else 0.0
                if prog > 0:
                    inner_r = int(self.button_radius * prog)
                    pygame.draw.circle(screen, (0, 255, 255), (cx, cy), inner_r)

            # ---- 動畫 --------------------------------------
            if self.current_animation_frames:
                if self.current_animation_idx >= len(self.current_animation_frames):
                    self.current_animation_idx = 0
                frame = self.current_animation_frames[self.current_animation_idx]
                x = (self.SCREEN_WIDTH - frame.get_width()) // 2
                screen.blit(frame, (x, 10))
                self.current_animation_idx = (
                    self.current_animation_idx + 1) % len(self.current_animation_frames)

            # ---- 3. 顯示文字資訊 ----
            # 遊玩時間 (mm:ss)
            elapsed = time.time() - start_time
            mins = int(elapsed // 60)
            secs = int(elapsed % 60)
            tm_str = f"{mins:02d}:{secs:02d}"
            surf_time = font.render(tm_str, True, text_settings["color"])
            screen.blit(surf_time, text_settings["pos"]["play_time"])

            # 當前步驟 ID
            sid = self.proj_draw_info.get("step_id")
            if sid is not None:
                surf_sid = font.render(str(sid), True, text_settings["color"])
                rect_sid = surf_sid.get_rect()
                rect_sid.midtop = text_settings["pos"]["step_id"]
                screen.blit(surf_sid, rect_sid)

            # 學生名稱
            surf_name = font.render(stu_name, True, text_settings["color"])
            rect_name = surf_name.get_rect()
            rect_name.topright = text_settings["pos"]["stu_name"]
            screen.blit(surf_name, rect_name)

            pygame.display.flip()
            clock.tick(30)

        pygame.quit()

    # --------------------------------------------------
    # ====== 校正、透視、同步、動畫 =========================================
    def calibrate_once(self, frame: np.ndarray) -> bool:
        """
        偵測四顆 ArUco → 計算透視矩陣 M
        """
        corners, ids, _ = cv2.aruco.detectMarkers(frame, self.ARUCO_DICT)
        if ids is None or len(ids) < 4:
            return False

        # 收集 src_pts：id → 對應頂點
        src_pts: Dict[int, Tuple[float, float]] = {}
        for id_arr, corner in zip(ids, corners):
            _id = int(id_arr[0])
            pts = corner[0]  # 0:LU 1:RU 2:RD 3:LD
            if _id == 0:
                src_pts[0] = tuple(pts[0])  # 左上 (LU)
            elif _id == 1:
                src_pts[1] = tuple(pts[1])  # 右上 (RU)
            elif _id == 2:
                src_pts[2] = tuple(pts[3])  # 左下 (LD)
            elif _id == 3:
                src_pts[3] = tuple(pts[2])  # 右下 (RD)

        if len(src_pts) != 4:
            return False

        src = np.array([src_pts[i] for i in self.ARUCO_IDS], dtype=np.float32)
        dst = np.array([self.ID_TO_CORNER[i] for i in self.ARUCO_IDS],
                       dtype=np.float32)

        self.M = cv2.getPerspectiveTransform(src, dst)
        self.calibrated = True
        return True

    def warp_frame(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """根據 M 對原始畫面做透視轉換"""
        if not self.calibrated or self.M is None:
            return None
        warped = cv2.warpPerspective(
            frame, self.M, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        )
        return warped

    def update_proj_draw_info(self, draw_info: dict):
        """主程式每幀同步最新引導圈 / 箭頭資訊"""
        self.proj_draw_info = draw_info

    def update_animation(self, anim_path: str):
        """載入 GIF 幀並存為 Pygame Surface list"""
        if anim_path == self.current_animation_path:
            return
        self.current_animation_path = anim_path

        if anim_path is None or not os.path.exists(anim_path):
            self.current_animation_frames = []
            self.current_animation_idx = 0
            return

        frames = []
        try:
            im = Image.open(anim_path)
            while True:
                frame_rgba = im.convert("RGBA")
                mode, size = frame_rgba.mode, frame_rgba.size
                data = frame_rgba.tobytes()
                surf = pygame.image.fromstring(data, size, mode)
                frames.append(surf)
                im.seek(im.tell() + 1)
        except EOFError:
            pass

        self.current_animation_frames = frames
        self.current_animation_idx = 0
