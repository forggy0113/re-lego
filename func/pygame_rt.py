# pygame_rt.py

import pygame
import math
import cv2
import numpy as np
import os

# class PygameDraw:
#     """
#     在 Pygame Surface 上繪製圓圈與箭頭指引
#     """
#     def __init__(self):
#         # 由外部傳入的 cuni 與 cint bbox (格式: [x1, y1, x2, y2])
#         self.locked_cuni = None
#         self.locked_cint = None
#         self.contact_flags = {}  # 如需記錄接觸狀態，可在此使用

#     def draw_guidance(self, screen: pygame.Surface):
#         """
#         畫出紅圈與箭頭（箭頭指向圓邊緣）
#         Args:
#             screen (pygame.Surface): Pygame 畫布
#         """
#         if not (self.locked_cuni and self.locked_cint):
#             return

#         # 計算 cuni 中心與半徑
#         x1, y1, x2, y2 = self.locked_cuni
#         cx1 = (x1 + x2) // 2
#         cy1 = (y1 + y2) // 2
#         r1 = int(math.hypot(x2 - x1, y2 - y1) / 2)
#         pygame.draw.circle(screen, (255, 0, 0), (cx1, cy1), r1, 3)

#         # 計算 cint 中心與半徑
#         x3, y3, x4, y4 = self.locked_cint
#         cx2 = (x3 + x4) // 2
#         cy2 = (y3 + y4) // 2
#         r2 = int(math.hypot(x4 - x3, y4 - y3) / 2)
#         pygame.draw.circle(screen, (0, 255, 0), (cx2, cy2), r2, 3)

#         # 主箭線起訖點：從 cuni 圓邊往 cint 圓邊
#         dx, dy = cx2 - cx1, cy2 - cy1
#         length = math.hypot(dx, dy)
#         ux, uy = dx / length, dy / length
#         start = (int(cx1 + ux * r1), int(cy1 + uy * r1))
#         end   = (int(cx2 - ux * r2), int(cy2 - uy * r2))
#         pygame.draw.line(screen, (255, 255, 0), start, end, 3)

#         # 畫箭頭分叉
#         arrow_len = 15
#         arrow_ang = math.radians(30)
#         for sign in (-1, 1):
#             ang = math.atan2(dy, dx) + sign * arrow_ang
#             ax = end[0] - arrow_len * math.cos(ang)
#             ay = end[1] - arrow_len * math.sin(ang)
#             pygame.draw.line(screen, (255, 255, 0), end, (int(ax), int(ay)), 3)
# ============================================================
# 🔊  音效播放工具
# ============================================================
_audio_mixer_ready: bool = False   # lazy‑init 旗標

def _init_mixer():
    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"⚠️ mixer init fail: {e}")

def _ensure_mixer() -> bool:
    """確保 pygame.mixer 已初始化；失敗時回傳 False。"""
    global _audio_mixer_ready
    if _audio_mixer_ready:
        return True
    try:
        pygame.mixer.init()
        _audio_mixer_ready = True
        return True
    except Exception as e:
        print(f"⚠️  pygame.mixer init failed: {e}")
        return False

def _play_sound(path: str):
    _init_mixer()
    if not path or not os.path.exists(path):
        print(f"🎵 skip (file not found): {path}")
        return
    try:
        pygame.mixer.Sound(path).play()
    except Exception as e:
        print(f"⚠️ play sound fail: {e}")

# ---- 對外 API ------------------------------------------------

def play_init_sound(path: str = "init.mp3"):  _play_sound(path)
def play_step_sound(path: str):               _play_sound(path)
def play_end_sound(path: str = "end.mp3"):    _play_sound(path)
def play_error_sound(path: str = "audio/fail.mp3"): _play_sound(path)

def draw_guidance_np_center(
    img: np.ndarray,
    cuni_draw_pos: tuple,
    cuni_draw_radius: int,
    cint_draw_pos: tuple,
    cint_draw_radius: int,
    color_cuni=(0, 0, 255),
    color_cint=(0, 255, 0),
    color_arrow=(0, 255, 255),
    thickness=2
) -> np.ndarray:
    """
    在 OpenCV numpy 影像上以「圓心＋半徑」方式畫兩個節點圓圈與箭頭指引。
    
    Args:
        img (np.ndarray): BGR 影像
        cuni_draw_pos (tuple): cuni 圓心 (x, y)
        cuni_draw_radius (int): cuni 圓半徑
        cint_draw_pos (tuple): cint 圓心 (x, y)
        cint_draw_radius (int): cint 圓半徑
        color_cuni (tuple): cuni 圓顏色 (B, G, R)
        color_cint (tuple): cint 圓顏色 (B, G, R)
        color_arrow (tuple): 箭頭顏色 (B, G, R)
        thickness (int): 線條粗細
    Returns:
        np.ndarray: 繪製完畢的 BGR 影像
    """
    output = img.copy()
    if cuni_draw_pos is None or cint_draw_pos is None:
        return output

    # 畫圓
    cv2.circle(output, cuni_draw_pos, cuni_draw_radius, color_cuni, thickness)
    cv2.circle(output, cint_draw_pos, cint_draw_radius, color_cint, thickness)

    # 算箭頭起訖點
    dx, dy = cint_draw_pos[0] - cuni_draw_pos[0], cint_draw_pos[1] - cuni_draw_pos[1]
    length = np.hypot(dx, dy)
    if length == 0:
        return output
    ux, uy = dx / length, dy / length
    start = (int(cuni_draw_pos[0] + ux * cuni_draw_radius), int(cuni_draw_pos[1] + uy * cuni_draw_radius))
    end   = (int(cint_draw_pos[0] - ux * cint_draw_radius), int(cint_draw_pos[1] - uy * cint_draw_radius))
    cv2.line(output, start, end, color_arrow, thickness)

    # 畫箭頭分叉
    arrow_length = 20
    arrow_angle = np.radians(30)
    for sign in (-1, 1):
        ang = np.arctan2(dy, dx) + sign * arrow_angle
        ax = int(end[0] - arrow_length * np.cos(ang))
        ay = int(end[1] - arrow_length * np.sin(ang))
        cv2.line(output, end, (ax, ay), color_arrow, thickness)

    return output

def draw_guidance_np(
    frame: np.ndarray,
    cuni_bbox: list,
    cint_bbox: list
) -> np.ndarray:
    """
    在 OpenCV numpy 影像上畫紅圈與箭頭指引
    Args:
        frame (np.ndarray): BGR 格式的影像陣列
        cuni_bbox (list): [x1, y1, x2, y2] for 起點物件 bounding box
        cint_bbox (list): [x1, y1, x2, y2] for 目標物件 bounding box
    Returns:
        np.ndarray: 繪製完畢的 BGR 影像
    """
    output = frame.copy()
    # 若任一框不存在，就直接回傳原圖
    if cuni_bbox is None or cint_bbox is None:
        return output

    # 計算兩個圓的中心與半徑
    x1, y1, x2, y2 = cuni_bbox
    cx1, cy1 = (x1 + x2) // 2, (y1 + y2) // 2
    r1 = int(math.hypot(x2 - x1, y2 - y1) / 2)
    cv2.circle(output, (cx1, cy1), r1, (0, 0, 255), 2)

    x3, y3, x4, y4 = cint_bbox
    cx2, cy2 = (x3 + x4) // 2, (y3 + y4) // 2
    r2 = int(math.hypot(x4 - x3, y4 - y3) / 2)
    cv2.circle(output, (cx2, cy2), r2, (0, 255, 0), 2)

    # 箭頭起訖點：從 cuni 圓邊指向 cint 圓邊
    dx, dy = cx2 - cx1, cy2 - cy1
    length = math.hypot(dx, dy)
    if length == 0:
        return output
    ux, uy = dx / length, dy / length
    start_pt = (int(cx1 + ux * r1), int(cy1 + uy * r1))
    end_pt   = (int(cx2 - ux * r2), int(cy2 - uy * r2))
    cv2.line(output, start_pt, end_pt, (0, 255, 255), 2)

    # 畫箭頭分叉
    arrow_len = 15
    arrow_ang = math.radians(30)
    for sign in (-1, 1):
        ang = math.atan2(dy, dx) + sign * arrow_ang
        ax = int(end_pt[0] - arrow_len * math.cos(ang))
        ay = int(end_pt[1] - arrow_len * math.sin(ang))
        cv2.line(output, end_pt, (ax, ay), (0, 255, 255), 2)

    return output



def draw_stepguide_overlay(
    screen,
    locked_cuni,
    locked_cint,
    color_cuni=(255, 0, 0),
    color_cint=(0, 255, 0),
    color_arrow=(255, 255, 0),
    circle_thickness=5,
    arrow_thickness=5,
    arrow_length=20,
    arrow_angle_deg=30
):
    """
    在 Pygame Surface 上繪製節點圓圈與箭頭引導（不回傳任何內容，直接修改畫面）

    參數說明：
    - screen: Pygame 的畫布 (Surface)，要在上面畫圖
    - locked_cuni: list [x1, y1, x2, y2]，cuni 節點的 bounding box 左上和右下座標
    - locked_cint: list [x1, y1, x2, y2]，cint 節點的 bounding box 左上和右下座標
    - color_cuni/color_cint/color_arrow: 顏色設定 (RGB)
    - circle_thickness, arrow_thickness: 線條粗細
    - arrow_length: 箭頭分叉長度
    - arrow_angle_deg: 箭頭分叉角度（度）

    回傳：無（in-place 畫到 screen 上）
    """

    if locked_cuni is None or locked_cint is None:
        # 只要有一邊沒找到，就不畫
        return

    # 1. 由 bounding box 取得中心點與半徑
    # bounding box = [x1, y1, x2, y2]，分別為左上角和右下角的座標
    def get_center_radius(box):
        x1, y1, x2, y2 = box
        cx = (x1 + x2) // 2      # 中心 x 座標 = 左右平均
        cy = (y1 + y2) // 2      # 中心 y 座標 = 上下平均
        r = int(math.hypot(x2 - x1, y2 - y1) / 2)  # 半徑 = 對角線長度除以2
        return cx, cy, r

    cx1, cy1, r1 = get_center_radius(locked_cuni)  # cuni 節點中心/半徑
    cx2, cy2, r2 = get_center_radius(locked_cint)  # cint 節點中心/半徑

    # 2. 畫兩個圓圈
    pygame.draw.circle(screen, color_cuni, (cx1, cy1), r1, circle_thickness)
    pygame.draw.circle(screen, color_cint, (cx2, cy2), r2, circle_thickness)

    # 3. 算箭頭起點、終點（都在圓的邊緣，不是圓心）
    dx, dy = cx2 - cx1, cy2 - cy1
    length = math.hypot(dx, dy)
    if length == 0:
        # 兩圓中心重疊就不畫
        return
    # 單位向量
    ux, uy = dx / length, dy / length
    start_pt = (int(cx1 + ux * r1), int(cy1 + uy * r1))  # 從 cuni 圓邊緣出發
    end_pt   = (int(cx2 - ux * r2), int(cy2 - uy * r2))  # 到 cint 圓邊緣結束

    # 4. 畫主箭幹
    pygame.draw.line(screen, color_arrow, start_pt, end_pt, arrow_thickness)

    # 5. 算並畫箭頭分叉（兩個小斜線）
    arrow_angle = math.radians(arrow_angle_deg)  # 轉為弧度
    for sign in (-1, 1):
        ang = math.atan2(dy, dx) + sign * arrow_angle  # 箭頭角度（左右分叉）
        ax = int(end_pt[0] - arrow_length * math.cos(ang))  # 箭頭端點x
        ay = int(end_pt[1] - arrow_length * math.sin(ang))  # 箭頭端點y
        pygame.draw.line(screen, color_arrow, end_pt, (ax, ay), arrow_thickness)

def draw_guidance_with_center(
    screen,
    cuni_draw_pos: tuple,
    cuni_draw_radius: int,
    cint_draw_pos: tuple,
    cint_draw_radius: int,
    color_cuni=(255,0,0),
    color_cint=(0,255,0),
    color_arrow=(255,255,0),
    thickness=4
):
    if cuni_draw_pos is None or cint_draw_pos is None:
        return
    pygame.draw.circle(screen, color_cuni, cuni_draw_pos, cuni_draw_radius, thickness)
    pygame.draw.circle(screen, color_cint, cint_draw_pos, cint_draw_radius, thickness)
    dx, dy = cint_draw_pos[0] - cuni_draw_pos[0], cint_draw_pos[1] - cuni_draw_pos[1]
    length = math.hypot(dx, dy)
    if length == 0: return
    ux, uy = dx/length, dy/length
    start = (int(cuni_draw_pos[0] + ux * cuni_draw_radius), int(cuni_draw_pos[1] + uy * cuni_draw_radius))
    end   = (int(cint_draw_pos[0] - ux * cint_draw_radius), int(cint_draw_pos[1] - uy * cint_draw_radius))
    pygame.draw.line(screen, color_arrow, start, end, thickness)
