# step_guide_rt.py
import json, numpy as np
from typing import List, Optional, Tuple


class StepGuide:
    """紅圈 cuni / 綠圈 cint 的追蹤與放手邏輯"""

    SPREAD_RATIO_THRESH = 0.7   # 收攏門檻
    RADIUS_MULT = 1.5           # 食指尖進圈倍率
    RELEASE_FRAMES = 15          # 張開幀數判定放手

    # ------------------------------------------------------------
    def __init__(self, json_path: str):
        self.steps = self._load_steps(json_path)
        self.current_index = 0

        self.locked_cuni_bbox = self.locked_cint_bbox = None
        self.locked_cuni_center = self.locked_cint_center = None
        self.locked_cuni_radius = self.locked_cint_radius = 30

        self.is_grabbed = False
        self.grabbed_tip = None
        self.grabbed_hand_idx: Optional[int] = None
        self.grabbed_hand_label: Optional[str] = None
        self._release_counter = 0
        
        self._cuni_lost_counter = 0      # 失效累計幀
        self.LOST_THRESHOLD = 60          # ★ 連續幾幀才換鎖
        
        # 放手後延遲重新鎖定用
        self._post_release_frames = 0   # 放手後經過幾幀
        self.WAIT_AFTER_RELEASE = 30     # ★ N 幀才跳下一個 cuni


    # ------------------------------------------------------------
    def _load_steps(self, path: str) -> List[dict]:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("steps", [])

    def get_current_step(self) -> Optional[dict]:
        return self.steps[self.current_index] if self.current_index < len(self.steps) else None

    # ------------------------------------------------------------
    def update_and_get_draw_info(
        self,
        detections,
        hand_landmarks,
        handedness_list,
        mp_tracker=None,
    ) -> dict:

        if hand_landmarks and False:
            for idx, hand in enumerate(hand_landmarks):
                ratio = self._spread_ratio(hand)
                label = handedness_list[idx] if idx < len(handedness_list) else "N/A"
                print(f"[Spread] frame hand{idx}-{label}: {ratio:.2f}")
        
        step = self.get_current_step()
        if not step:
            return self._blank_info()

        cuni_label, cint_label = step["cuni"], step["cint"]

        # 初次鎖定最近 cuni / cint
        if self.locked_cuni_bbox is None or self.locked_cint_bbox is None:
            self._lock_nearest_pair(detections, cuni_label, cint_label)

        # 嘗試抓取
        if hand_landmarks and self.locked_cuni_center and not self.is_grabbed:
            self._try_grab(hand_landmarks, handedness_list)

        # 追蹤 / 放手
        if self.is_grabbed and self.grabbed_tip is not None:
            self._drag_or_release(
                hand_landmarks, handedness_list,
                detections, cuni_label, cint_label
            )

        # 非抓取：更新綠圈到最近 cint
        if not self.is_grabbed:
            self._update_cint_nearest(detections, cint_label)

        self._ensure_cuni_valid(
        detections, cuni_label, cint_label,
        hand_landmarks                 # ← 傳入手座標
        )


        return dict(
            cuni_draw_pos=self.locked_cuni_center,
            cuni_draw_radius=self.locked_cuni_radius,
            cint_draw_pos=self.locked_cint_center,
            cint_draw_radius=self.locked_cint_radius,
            is_grabbed=self.is_grabbed,
            grabbed_hand=self.grabbed_hand_label,
            hand_pos=self.grabbed_tip,
            cuni_bbox=self.locked_cuni_bbox,
            cint_bbox=self.locked_cint_bbox,
        )

    # ============================================================
    # 抓 / 放 實作
    # ------------------------------------------------------------
    def _spread_ratio(self, hand):
        palm = np.hypot(hand[5][0]-hand[0][0], hand[5][1]-hand[0][1]) + 1e-6
        spread = max(
            np.hypot(hand[4][0]-hand[8][0], hand[4][1]-hand[8][1]),
            np.hypot(hand[4][0]-hand[12][0], hand[4][1]-hand[12][1]),
            np.hypot(hand[8][0]-hand[12][0], hand[8][1]-hand[12][1]),
        )
        return spread / palm

    def _try_grab(self, hands, handed):
        for idx, hand in enumerate(hands):
            if self._spread_ratio(hand) >= self.SPREAD_RATIO_THRESH:
                continue
            dist = np.hypot(
                hand[8][0]-self.locked_cuni_center[0],
                hand[8][1]-self.locked_cuni_center[1]
            )
            if dist < self.locked_cuni_radius * self.RADIUS_MULT:
                self.is_grabbed = True
                self.grabbed_hand_idx = idx
                self.grabbed_hand_label = handed[idx] if idx < len(handed) else "Unknown"
                self.grabbed_tip = (int(hand[8][0]), int(hand[8][1]))
                # ★ 同步紅圈中心
                self.locked_cuni_center = self.grabbed_tip
                self._release_counter = 0
                break

    def _drag_or_release(
        self, hands, handed,
        detections, cuni_label, cint_label
    ):
        idx = next((i for i, lab in enumerate(handed) if lab == self.grabbed_hand_label), None)

        if idx is None:
            self._release_counter += 1
        else:
            if self._spread_ratio(hands[idx]) < self.SPREAD_RATIO_THRESH:
                # 更新指尖 & 紅圈中心
                self.grabbed_tip = (int(hands[idx][8][0]), int(hands[idx][8][1]))
                self.locked_cuni_center = self.grabbed_tip
                self._release_counter = 0
            else:
                self._release_counter += 1

        if self._release_counter >= self.RELEASE_FRAMES:
            self._reset_grab_state()
            self._jump_cuni_near_cint(detections, cuni_label, cint_label)

    def _reset_grab_state(self):
        self.is_grabbed = False
        self.grabbed_tip = None
        self.grabbed_hand_idx = None
        self.grabbed_hand_label = None
        self._release_counter = 0

    # ------------------------------------------------------------
    # 放手後：紅圈跳到離綠圈最近的紅圈
    def _jump_cuni_near_cint(self, detections, cuni_label, cint_label):
        if self.locked_cint_center is None:
            return
        cx, cy = self.locked_cint_center
        best, best_center, d2_min = None, None, float("inf")
        for bbox, lab in detections:
            if lab.split()[0] != cuni_label:
                continue
            ccx, ccy = (bbox[0]+bbox[2])//2, (bbox[1]+bbox[3])//2
            d2 = (ccx-cx)**2 + (ccy-cy)**2
            if d2 < d2_min:
                best, best_center, d2_min = bbox, (ccx, ccy), d2
        if best:
            self.locked_cuni_bbox = best
            self.locked_cuni_center = best_center
            self.locked_cuni_radius = int(
                np.hypot(best[2]-best[0], best[3]-best[1]) / 2
            )

    # ------------------------------------------------------------
    def _update_cint_nearest(self, detections, cint_label):
        if self.locked_cuni_center is None:
            return
        cx, cy = self.locked_cuni_center
        best, bc, d2_min = None, None, float("inf")
        for bbox, lab in detections:
            if lab.split()[0] != cint_label:
                continue
            ccx, ccy = (bbox[0]+bbox[2])//2, (bbox[1]+bbox[3])//2
            d2 = (ccx-cx)**2 + (ccy-cy)**2
            if d2 < d2_min:
                best, bc, d2_min = bbox, (ccx, ccy), d2
        if best:
            self.locked_cint_bbox = best
            self.locked_cint_center = bc
            self.locked_cint_radius = int(
                np.hypot(best[2]-best[0], best[3]-best[1]) / 2
            )

    # ------------------------------------------------------------
    # 初次鎖定最近 cuni / cint
    def _lock_nearest_pair(self, detections, cuni_label, cint_label):
        best_cuni = best_cint = None
        best_cuni_center = best_cint_center = None
        d2_min = float("inf")
        for b1, l1 in detections:
            if l1.split()[0] != cuni_label:
                continue
            c1 = ((b1[0]+b1[2])//2, (b1[1]+b1[3])//2)
            for b2, l2 in detections:
                if l2.split()[0] != cint_label:
                    continue
                c2 = ((b2[0]+b2[2])//2, (b2[1]+b2[3])//2)
                d2 = (c1[0]-c2[0])**2 + (c1[1]-c2[1])**2
                if d2 < d2_min:
                    best_cuni, best_cint = b1, b2
                    best_cuni_center, best_cint_center = c1, c2
                    d2_min = d2
        if best_cuni and best_cint:
            self.locked_cuni_bbox, self.locked_cint_bbox = best_cuni, best_cint
            self.locked_cuni_center, self.locked_cint_center = best_cuni_center, best_cint_center
            self.locked_cuni_radius = int(np.hypot(best_cuni[2]-best_cuni[0], best_cuni[3]-best_cuni[1])/2)
            self.locked_cint_radius = int(np.hypot(best_cint[2]-best_cint[0], best_cint[3]-best_cint[1])/2)

    # ------------------------------------------------------------
    def _blank_info(self):
        return dict(
            cuni_draw_pos=None, cuni_draw_radius=30,
            cint_draw_pos=None, cint_draw_radius=30,
            is_grabbed=False, grabbed_hand=None, hand_pos=None,
            cuni_bbox=None, cint_bbox=None
        )

    
    def check_assembly_complete(self, detections):
        """YOLO 偵測到當前 step 的 id 就算完成"""
        step = self.get_current_step()
        if not step:
            return False
        sid = str(step["id"])
        for _, lab in detections:
            if lab.split()[0] == sid:
                print(f"[StepGuide] 🎯 組裝完成 id={sid}")
                return True
        return False

    def unlock_for_next_step(self):
        """完成後呼叫：重置並進入下一步"""
        print(f"[StepGuide] unlock {self.current_index} → {self.current_index + 1}")
        self.locked_cuni_bbox = self.locked_cint_bbox = None
        self.locked_cuni_center = self.locked_cint_center = None
        self.locked_cuni_radius = self.locked_cint_radius = 30
        self._reset_grab_state()
        self.current_index += 1

    # ------------------------------------------------------------
    def _blank_info(self):
        """當步驟皆完成時回傳空畫面配置"""
        return dict(
            cuni_draw_pos=None, cuni_draw_radius=30,
            cint_draw_pos=None, cint_draw_radius=30,
            is_grabbed=False, grabbed_hand=None, hand_pos=None,
            cuni_bbox=None, cint_bbox=None
        )
        
        # ------------------------------------------------------------
    def _ensure_cuni_valid(
        self,
        detections,
        cuni_label,
        cint_label,
        hand_landmarks,
    ):
        if self.locked_cuni_center is None:
            return

        cx, cy = self.locked_cuni_center

        # ---- 1. 紅圈仍在同類 bbox？----
        for bbox, lab in detections:
            if lab.split()[0] == cuni_label and \
               bbox[0] <= cx <= bbox[2] and bbox[1] <= cy <= bbox[3]:
                self._cuni_lost_counter = 0          # ★ 恢復計數器
                return

        # ---- 2. 手是否遮住？ ----
        hand_near = False
        if hand_landmarks:
            min_dist = min(
                np.hypot(hand[8][0]-cx, hand[8][1]-cy) for hand in hand_landmarks
            )
            if min_dist < self.locked_cuni_radius * self.RADIUS_MULT:
                hand_near = True

        if hand_near:
            self._cuni_lost_counter = 0              # ★ 視作暫時遮擋
            return

        # ---- 3. 累積失效幀 ----
        self._cuni_lost_counter += 1                 # ★ +1
        if self._cuni_lost_counter < self.LOST_THRESHOLD:
            return                                   # ★ 未達門檻先不換鎖

        # ---- 4. 真的失效 → 跳下一個 ----
        self._cuni_lost_counter = 0                  # ★ 重置
        self._jump_cuni_near_cint(detections, cuni_label, cint_label)


