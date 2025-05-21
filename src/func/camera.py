import cv2
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel, QMessageBox
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sql.encrypted import Encrypted

class Camera():
    def __init__(self, db,ui, main_window):
        """
        初始化攝影機登入控制器。

        Args:
            db (sqlite3.Connection): 資料庫連線物件。
            ui (object): PyQt5 介面物件，需含 QLabel。
            main_window (QMainWindow): PyQt 主視窗實體，用於彈窗與關閉。
        """
        self.ui = ui
        self.db = db
        self.main_window = main_window
        # ----攝影機初始化------
        self.cap = None  # 初始化攝影機
        self.decoder_text = None # 儲存目前偵測到的qrcode解碼後文字 
        self.timer = QTimer() # 計時器
        self.timer.timeout.connect(self.update_frame)
        self.logged_in = False 
        # self.timer.start(30)
        # ----加解密初始化-------
        self.encrypted = Encrypted(private_key_path= "./src/sql/private.pem", public_key_path = "./src/sql/public.pem")
        if not os.path.exists("./src/sql/private.pem") or not os.path.exists("./src/sql/public.pem"):
            self.encrypted.generate_keys()

        
    def stu_login_video(self):
        """ 
        開啟攝影機並啟動畫面更新，30 FPS
        Returns:
          None
        """
        self.logged_in = False
        self.decoder_text = None
        self.student_data = None  # ✅ ← 清除舊登入資料
        if self.cap is not None and self.cap.isOpened():
            return 
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("無法開啟攝影機！")
            return

        
        if not isinstance(self.ui.label, QLabel):
            print("錯誤：self.ui.label 不是 QLabel！")
            return
        
        self.video_label = self.ui.label
        self.detector = cv2.QRCodeDetector() # qrcode解碼器
        # self.timer.timeout.connect(self.update_frame)
        self.timer.start(30) # 每30每30
        print("攝影機已啟動！開始掃描QRcode")

    def update_frame(self):
        """
        每幀更新：讀取攝影機畫面、解析 QRCode、執行登入流程。

        Returns:
            None
        """
        # self.logged_in = False
        if not self.cap or not self.cap.isOpened():
            return
        ret, frame = self.cap.read()

        if not ret:
            return  # 若無法讀取影像，直接返回
        alpha = 1.5
        beta = -10
        frame = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)
        # 解碼 QR Code
        self.decoder_text, pts, _ = self.detector.detectAndDecode(frame)

        # 若尚未登入，且成功解碼 QR Code，就執行登入與畫框
        if not self.logged_in and self.decoder_text:
            self.draw_qrcode_box(frame, pts)
            self.login_student()

        # 在畫面中央繪製十字準心輔助對齊
        # frame_with_cross = self.draw_cercent(frame)

        # 將畫面轉為 QPixmap 並顯示到 PyQt 的 QLabel 中
        # self.display_image(frame_with_cross)
        cv2.imshow("Camera", frame)
        cv2.waitKey(1) # 等待1毫秒，讓畫面更新
            
    def login_student(self):
        """
        嘗試根據解碼後的 QR Code 內容，進行學生登入檢查流程。
        
        流程邏輯：
        1. 檢查 QR Code 解碼結果是否存在。
        2. 使用 Encrypted 類別解密 QR Code 資料。
        3. 用解密後的 UUID 查詢資料庫。
        4. 若查無資料或解密失敗，顯示錯誤訊息。
        5. 若成功登入，顯示成功訊息並可選擇關閉應用程式或切換頁面。

        Returns:
            None
        """
        if self.logged_in:
            return # 已經登入就不再重複登入
            
        countdown_sec = 5  # 顯示訊息的倒數秒數

        try:
            # === 1. 檢查是否成功解碼 QR Code ===
            if not self.decoder_text:
                # print("解碼後的 QR Code 內容為空")
                # self.show_message("錯誤", "無法讀取 QR Code", countdown_sec)
                return None, False

            print(f"QR Code 原始內容: {self.decoder_text}")

            # === 2. 嘗試使用私鑰解密 QR Code 內容 ===
            decrypted_data = self.encrypted.decrypt(self.decoder_text)
            # print(f"解密後的內容: {decrypted_data}")

            if not decrypted_data:
                # 若解密失敗（空字串），可能是密鑰錯誤或 QR Code 被竄改
                self.show_message("錯誤", "無法解密 QR Code", countdown_sec)
                return None, False
            
            # === 3. 查詢資料庫是否存在該 UUID ===
            self.db.cursor.execute(
                '''SELECT stu_name, stu_class, stu_seat_num FROM Students WHERE stu_uuid=?''',
                (decrypted_data,)
            )
            stu_uuid = self.db.cursor.fetchone()

            if stu_uuid is None:
                # 查無此學生
                print(f"資料庫查無此 UUID: {decrypted_data}")
                self.show_message("失敗", f"查無此學生，UUID={decrypted_data}", countdown_sec)
                return None, False

            # === 4. 登入成功，取得學生資訊 ===
            stu_name, stu_class, stu_seat_num = stu_uuid
            student_data = {
                "stu_name": stu_name,
                "stu_class": stu_class,
                "stu_seat_num": stu_seat_num,
                "stu_uuid": decrypted_data
            }
            # 成功後顯示訊息，並執行後續動作（如關閉程式）
            self.logged_in = True # 設定為已登入
            self.student_data = student_data # 儲存學生資料
            print(f"登入成功：{student_data}")
            self.show_message(
                "成功",
                f"{stu_name}_{stu_class}_{stu_seat_num} 登入成功",
                countdown_sec,
                on_finish=self.exit_app 
            )
            return student_data, True

        except Exception as e:
            # 捕捉任何例外錯誤，顯示錯誤訊息
            print(f"登入失敗: {e}")
            self.show_message("錯誤", f"登入失敗：{e}", countdown_sec)
            return None, False

    def draw_qrcode_box(self, frame, pts):
        """
        在 QRCode 周圍畫出紅色邊框。

        Args:
            frame (np.ndarray): 攝影機畫面。
            pts (np.ndarray): QR code 四角點座標。

        Returns:
            None
        """
        if pts is None or len(pts) == 0:
            return

        try:
            pts = pts[0].astype(int).reshape((-1, 1, 2))
            if pts.shape[0] >= 3:  # 至少要 3 點才可構成多邊形
                cv2.polylines(frame, [pts], isClosed=True, color=(0, 0, 255), thickness=2)
                cv2.putText(frame, self.decoder_text, (pts[0][0][0], pts[0][0][1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        except Exception as e:
            print(f"⚠️ 繪製 QRCode 邊框失敗: {e}")
            
    def show_message(self, title, text, countdown_sec=5, on_finish=None):
        """
        顯示倒數提示視窗，可指定倒數後的操作（如關閉程式）。

        Args:
            title (str): QMessageBox 標題
            text (str): 顯示文字
            countdown_sec (int): 倒數秒數
            on_finish (Callable): 倒數後要執行的函式（可為 None）
        """
        msg_box = QMessageBox(self.main_window)
        msg_box.setWindowTitle(title)
        msg_box.setText(f"{text}\n\n({countdown_sec} 秒後自動關閉)")
        msg_box.setStandardButtons(QMessageBox.Ok)

        def close_and_continue():
            msg_box.accept()
            if callable(on_finish):
                on_finish()

        QTimer.singleShot(countdown_sec * 1000, close_and_continue)
        msg_box.exec_()
    
    def release_camera(self):
        """
        釋放攝影機與停止 Timer，以避免資源未釋放或影像畫面殘留。
        """
        if hasattr(self, "timer") and self.timer.isActive():
            self.timer.stop()

        if hasattr(self, "cap") and self.cap is not None:
            if self.cap.isOpened():
                self.cap.release()
            self.cap = None
    
    def exit_app(self):
        """
        隱藏主視窗、關閉攝影機，進入遊戲流程，結束後再顯示主視窗重新登入。
        """
        self.release_camera()
        self.main_window.hide()  # ← 不關掉整個 app，而是隱藏
        
        from main import run_game  # 確保 run_game 接收 student_data 並回傳 play_time
        if hasattr(self, "student_data"):
            play_time = run_game(self.student_data)
            print(f"遊戲完成，遊玩時間：{play_time:.2f} 秒")
        
        # 準備下一位學生登入
        self.logged_in = False
        self.student_data = None
        self.main_window.show()
        self.stu_login_video()  # 再次開啟攝影機


    # def draw_cercent(self, image):
    #     """
    #     繪製白色定位十字線
    #     Return: image 給 update_frame
    #     """
    #     height, width, _ = image.shape
    #     center_x, center_y = width // 2, height // 2
    #     cv2.line(image, (0, center_y), (width, center_y), (255, 255, 255), 2)
    #     cv2.line(image, (center_x, 0), (center_x, height), (255, 255, 255), 2)
    #     return image

    # def display_image(self, image):
    #     """
    #     將 OpenCV 畫面轉為 QPixmap 並顯示於介面。

    #     Args:
    #         image (np.ndarray): BGR 格式的 OpenCV 畫面。

    #     Returns:
    #         None
    #     """
    #     rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    #     h, w, ch = rgb_image.shape
    #     bytes_per_line = ch * w
    #     qimg = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
    #     self.video_label.setPixmap(QPixmap.fromImage(qimg))


