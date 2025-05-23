import time
import pygame
import cv2
import threading
import json

# 假設你已有這些模組
from func.warp_rt import WarpProcessor
from func.yolov7_rt import YoloV7Detector
from func.mediapipe_rt import MediaPipeHandTracker
from func.step_guide_rt import StepGuide
from func.pygame_rt import (
    draw_guidance_np_center,
    play_init_sound, play_step_sound,
    play_end_sound, play_error_sound
)

# 讀取腳本配置（用於音效）
with open(r"func\script.json", "r", encoding="utf-8") as f:
    _cfg = json.load(f)
INIT_AUDIO  = _cfg.get("init",  [{}])[0].get("audio", "")
END_AUDIO   = _cfg.get("end",   [{}])[0].get("audio", "")
ERROR_AUDIO = _cfg.get("error", [{}])[0].get("audio", "")

# ===== 互動圓形按鈕設定 ======================================
BTN_RADIUS    = 40
BTN_CENTERS   = [(140, 40), (1140, 40)]   # 若解析度改變記得調
HOLD_SECONDS  = 1.0                       # 集氣滿格時間
DECAY_SECONDS = 0.5                       # 離開後衰減到 0 的時間
# ============================================================


def run_game(student_data: dict, db) -> float:
    """
    執行 Pygame 組裝遊戲主程式。
    Args:
        student_data (dict): 登入學生資訊（stu_name, stu_class, ...）
    Returns:
        float: 遊玩秒數
    """
    print(f"🎮 開始遊戲，玩家：{student_data}")

    # ---------- 0. 初始化音效與時間計時 ----------
    init_sound_played = False
    end_sound_played = False

    # ---------- 1. 建立 stop_event for Pygame thread ----------
    stop_event = threading.Event()  # 用來通知 show_aruco 執行緒結束

    # ---------- 2. 初始化控制狀態與模組 ----------
    hold_timer = [0.0] * len(BTN_CENTERS)
    ready_flag = [True] * len(BTN_CENTERS)
    progress   = [0.0] * len(BTN_CENTERS)

    warp_proc = WarpProcessor(1280, 720, BTN_CENTERS, BTN_RADIUS)
    yolo = YoloV7Detector(r"func\weight\exp_55best.pt", r"func\all_step_class.txt")
    mp_tracker = MediaPipeHandTracker(
        max_num_hands=2, model_complexity=1,
        detection_confidence=0.6, tracking_confidence=0.6
    )
    step_guide = StepGuide(r"func\script.json")

    # ---------- 3. 文字顯示設定 ----------
    text_settings = {
        "font_path": r"src/ui/font/BpmfGenSenRounded-R.ttf",
        "font_size": 40,
        "color": (255, 255, 255),
        "pos": {
            "play_time": (200, 0),                                 # 左上角：遊玩時間
            "step_id":    (warp_proc.SCREEN_WIDTH // 2, 0),       # 中上：當前步驟 ID
            "stu_name":   (warp_proc.SCREEN_WIDTH - 200, 0)       # 右上：學生名稱
        }
    }

    # ---------- 4. 啟動第二螢幕 Pygame 顯示 ----------
    start_time = time.time()
    pygame_thread = threading.Thread(
        target=warp_proc.show_aruco_on_second_screen,
        args=(
            stop_event,
            student_data.get("stu_name", ""),
            start_time,
            text_settings
        ),
        daemon=True
    )
    pygame_thread.start()

    # ---------- 3. 啟動攝影機 ----------
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ 無法開啟相機")
        return 0.0

    print("▶️ 按 'r' 重新校正，按 'q' 離開")
    last_t = time.perf_counter()

    # ========== 4. 主處理迴圈（校正、引導、互動） ==========
    while True:
        # ---------- 4-1. 讀取與顯示鏡像畫面 ----------
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.flip(frame, -1)
        cv2.imshow("Camera Debug", frame)

        # ---------- 4-2. 校正畫面 ----------
        if not warp_proc.calibrated:
            if warp_proc.calibrate_once(frame):
                print("✅ 校正成功")
            if cv2.waitKey(1) & 0xFF == ord('q'):
                stop_event.set(); break
            continue

        # ---------- 4-3. 透視轉換 + YOLO 偵測 ----------
        warped = warp_proc.warp_frame(frame)
        if warped is None:
            continue
        guide_vis = warped.copy()

        if warp_proc.current_animation_frames:
            ani_h = warp_proc.current_animation_frames[0].get_height()
            ani_w = warp_proc.current_animation_frames[0].get_width()
            x = (warp_proc.SCREEN_WIDTH - ani_w) // 2
            cv2.rectangle(warped, (x, 10), (x+ani_w, 10+ani_h), (0, 0, 0), -1)

        detections = yolo.detect(warped)
        for (xyxy, label) in detections:
            x1, y1, x2, y2 = map(int, xyxy)
            cv2.rectangle(guide_vis, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(guide_vis, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        # ---------- 4-4. 手部追蹤 + 組裝步驟分析 ----------
        guide_vis, hand_lms, handed_list = mp_tracker.process_frame(
            guide_vis, draw_landmarks=True, debug_info=False
        )
        draw_info = step_guide.update_and_get_draw_info(
            detections, hand_lms, handed_list
        )
        # 傳遞當前步驟 ID
        cur = step_guide.get_current_step()
        draw_info["step_id"] = cur.get("id") if cur else None

        # ---------- 4-5. 播放首次 init 音效 ----------
        if (not init_sound_played
            and step_guide.current_index == 0
            and draw_info['cuni_bbox'] is not None
            and draw_info['cint_bbox'] is not None):
            play_init_sound(INIT_AUDIO)
            init_sound_played = True

        # ---------- 4-6. 集氣按鈕邏輯 ----------
        dt = time.perf_counter() - last_t
        last_t = time.perf_counter()
        tips = [(pt[0], pt[1]) for hand in hand_lms for pt in hand] if hand_lms else []

        for i, center in enumerate(BTN_CENTERS):
            inside = any(
                (tx - center[0])**2 + (ty - center[1])**2 <= BTN_RADIUS**2
                for tx, ty in tips
            )
            if inside:
                cv2.circle(guide_vis, center, BTN_RADIUS, (255, 255, 0), 2)
                if ready_flag[i]:
                    hold_timer[i] += dt
                    progress[i] = min(1.0, hold_timer[i] / HOLD_SECONDS)
                    if hold_timer[i] >= HOLD_SECONDS:
                        if step_guide.check_assembly_complete(detections):
                            cur_step = step_guide.get_current_step()
                            if cur_step and cur_step.get("audio"):
                                play_step_sound(cur_step["audio"])
                            step_guide.unlock_for_next_step()
                        else:
                            play_error_sound(ERROR_AUDIO)
                        ready_flag[i] = False
                        hold_timer[i] = progress[i] = 1.0
            else:
                hold_timer[i] = 0.0
                ready_flag[i] = True
                progress[i] = max(0.0, progress[i] - dt / DECAY_SECONDS)

        warp_proc.update_button_progress(progress)

        # ---------- 4-7. 視覺化導引與動畫 ----------
        if draw_info['cuni_draw_pos'] and draw_info['cint_draw_pos']:
            guide_vis = draw_guidance_np_center(
                guide_vis,
                draw_info['cuni_draw_pos'], draw_info['cuni_draw_radius'],
                draw_info['cint_draw_pos'], draw_info['cint_draw_radius']
            )

        cur_step = step_guide.get_current_step()
        if cur_step and cur_step.get("animation"):
            warp_proc.update_animation(cur_step["animation"])

        cv2.imshow("build guide", guide_vis)
        warp_proc.update_proj_draw_info(draw_info)

        # ---------- 4-8. 全部完成 ----------
        if cur_step is None and not end_sound_played:
            play_end_sound(END_AUDIO)
            end_sound_played = True
            time.sleep(3)
            stop_event.set()
            break

        # ---------- 4-9. 手動鍵盤操作 ----------
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            stop_event.set(); break
        elif key == ord('r'):
            print("🔁 重新觸發校正")
            warp_proc.calibrated = False

    # ---------- 5. 收尾處理（釋放資源） ----------
    cap.release()
    cv2.destroyAllWindows()
    pygame_thread.join()

    play_time = time.time() - start_time
    print(f"⏱️ 遊戲完成，遊玩時長：{play_time:.2f} 秒")
    # ---------- 6. 寫入資料庫 Practice ----------
    try:
        stu_uuid     = student_data.get("stu_uuid")
        stu_name     = student_data.get("stu_name")

        # 時間資訊
        start_dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
        end_dt   = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        play_sec = int(play_time)

        db.cursor.execute(
            """
            INSERT INTO Practice (stu_name, stu_uuid, game_time, practice_start_date, practice_end_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            (stu_name, stu_uuid, play_sec, start_dt, end_dt)
        )
        db.conn.commit()
        print("✅ 已寫入 Practice 遊玩紀錄")
    except Exception as e:
        print(f"❌ 寫入 Practice 時出錯: {e}")

    return play_time
