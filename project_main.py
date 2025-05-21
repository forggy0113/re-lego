# main.py
import json
import time
import threading
import cv2
from func.warp_rt import WarpProcessor
from func.yolov7_rt import YoloV7Detector
from func.mediapipe_rt import MediaPipeHandTracker
from func.step_guide_rt import StepGuide
from func.pygame_rt import (
    draw_guidance_np_center,
    play_init_sound, play_step_sound,
    play_end_sound, play_error_sound
)

# ====== 讀取 script.json 取得音效路徑 =========================
with open("func\script.json", "r", encoding="utf-8") as f:
    _cfg = json.load(f)
INIT_AUDIO  = _cfg.get("init",  [{}])[0].get("audio", "")
END_AUDIO   = _cfg.get("end",   [{}])[0].get("audio", "")
ERROR_AUDIO = _cfg.get("error", [{}])[0].get("audio", "")
# ============================================================

# ===== 互動圓形按鈕設定 ======================================
BTN_RADIUS    = 40
BTN_CENTERS   = [(140, 40), (1140, 40)]   # 若解析度改變記得調
HOLD_SECONDS  = 1.0                       # 集氣滿格時間
DECAY_SECONDS = 0.5                       # 離開後衰減到 0 的時間
# ============================================================

def main():
    # ---------- 0. 音效：開場 / 結束 ------------------------
    init_sound_played = False
    end_sound_played  = False

    # ---------- 1. 初始化模組 --------------------------------
    hold_timer = [0.0] * len(BTN_CENTERS)   # 每顆按鈕累積停留秒數
    ready_flag = [True] * len(BTN_CENTERS)  # True = 尚未觸發，可再次啟動
    progress   = [0.0] * len(BTN_CENTERS)   # 0.0~1.0 充能百分比

    warp_proc = WarpProcessor(1280, 720, BTN_CENTERS, BTN_RADIUS)

    yolo = YoloV7Detector(
        model_path=r"func\weight\exp_55best.pt",
        class_path=r"func\all_step_class.txt"
    )
    mp_tracker = MediaPipeHandTracker(
        max_num_hands=2, model_complexity=1,
        detection_confidence=0.5, tracking_confidence=0.5
    )
    step_guide = StepGuide("func\script.json")

    stop_event = threading.Event()
    pygame_thread = threading.Thread(
        target=warp_proc.show_aruco_on_second_screen,
        args=(stop_event,), daemon=True
    )
    pygame_thread.start()

    # ---------- 2. 開啟相機 ----------------------------------
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ 無法開啟相機")
        return

    print("▶️ 按 'r' 重新校正，按 'q' 離開")
    last_t = time.perf_counter()

    # =========================================================
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.flip(frame, -1)                      # 鏡像
        cv2.imshow("Camera Debug", frame)

        # ---------- 2-1. 校正（只做一次） --------------------
        if not warp_proc.calibrated:
            if warp_proc.calibrate_once(frame):
                print("✅ 校正成功")
            if cv2.waitKey(1) & 0xFF == ord('q'):
                stop_event.set(); break
            continue

        # ---------- 2-2. 透視轉換 ---------------------------
        warped = warp_proc.warp_frame(frame)
        if warped is None:
            continue
        guide_vis = warped.copy()

        # ---------- 2-3. YOLO 偵測 --------------------------
        # 遮蔽動畫區域避免誤偵測
        if warp_proc.current_animation_frames:
            ani_h = warp_proc.current_animation_frames[0].get_height()
            ani_w = warp_proc.current_animation_frames[0].get_width()
            x = (warp_proc.SCREEN_WIDTH - ani_w) // 2
            cv2.rectangle(warped, (x, 10), (x+ani_w, 10+ani_h),
                          (0, 0, 0), thickness=-1)

        detections = yolo.detect(warped)
        for (xyxy, label) in detections:
            x1, y1, x2, y2 = map(int, xyxy)
            cv2.rectangle(guide_vis, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(guide_vis, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        # ---------- 2-4. MediaPipe 手部 ---------------------
        guide_vis, hand_lms, handed_list = mp_tracker.process_frame(
            guide_vis, draw_landmarks=True, debug_info=False
        )

        # ---------- 2-5. StepGuide 更新 --------------------
        draw_info = step_guide.update_and_get_draw_info(
            detections, hand_lms, handed_list
        )

        # 播放 init 音效
        if (not init_sound_played
            and step_guide.current_index == 0
            and draw_info['cuni_bbox'] is not None
            and draw_info['cint_bbox'] is not None):
            play_init_sound(INIT_AUDIO)
            init_sound_played = True

        # ---------- 2-6. 按鈕集氣邏輯 -----------------------
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
                    if hold_timer[i] >= HOLD_SECONDS:   # ---- 觸發驗證 ----
                        if step_guide.check_assembly_complete(detections):
                            cur_step = step_guide.get_current_step()
                            if cur_step and cur_step.get("audio"):
                                play_step_sound(cur_step["audio"])
                            step_guide.unlock_for_next_step()
                        else:
                            play_error_sound(ERROR_AUDIO)

                        ready_flag[i] = False
                        hold_timer[i] = progress[i] = 1.0   # 集氣滿格
            else:
                hold_timer[i] = 0.0
                ready_flag[i] = True
                # 線性衰減
                progress[i] = max(0.0, progress[i] - dt / DECAY_SECONDS)

        # 把進度送到投影執行緒畫面
        warp_proc.update_button_progress(progress)

        # ---------- 2-7. 視覺化導引 & 動畫 -------------------
        if draw_info['cuni_draw_pos'] and draw_info['cint_draw_pos']:
            guide_vis = draw_guidance_np_center(
                guide_vis,
                draw_info['cuni_draw_pos'], draw_info['cuni_draw_radius'],
                draw_info['cint_draw_pos'], draw_info['cint_draw_radius']
            )

        cur_step = step_guide.get_current_step()
        if cur_step and cur_step.get("animation"):
            warp_proc.update_animation(cur_step["animation"])

        cv2.imshow("組裝導引", guide_vis)
        warp_proc.update_proj_draw_info(draw_info)

        # ---------- 2-8. 全部完成？ ------------------------
        if cur_step is None and not end_sound_played:
            play_end_sound(END_AUDIO)
            end_sound_played = True
            time.sleep(3)
            stop_event.set()
            break

        # ---------- 2-9. 鍵盤控制 -------------------------
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            stop_event.set(); break
        elif key == ord('r'):
            print("🔁 重新觸發校正")
            warp_proc.calibrated = False

    # ---------- 3. 收尾 ---------------------------------
    cap.release()
    cv2.destroyAllWindows()
    pygame_thread.join()
    

if __name__ == "__main__":
    main()
