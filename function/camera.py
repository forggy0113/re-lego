import cv2
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel, QMessageBox
import time
from sql.encrypted import Encrypted
import os

class Camera():
    def __init__(self, db,ui, main_window):
        self.ui = ui
        self.db = db
        self.cap = None  # 初始化攝影機
        self.decoder_text = None
        self.timer = QTimer()
        # self.encrypted = encrypted
        self.main_window = main_window
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)
        self.encrypted = Encrypted(private_key_path= "./sql/private.pem", public_key_path = "./sql/public.pem")
        if not os.path.exists("./sql/private.pem") or not os.path.exists("./sql/public.pem"):
            self.encrypted.generate_keys()

        
    def stu_login_video(self):
        """ 初始化攝影機，並開啟時器讀取一幀 """
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("無法開啟攝影機！")
            return
    
        if not isinstance(self.ui.label, QLabel):
            print("錯誤：self.ui.label 不是 QLabel！")
            return
        
        self.video_label = self.ui.label
        self.detector = cv2.QRCodeDetector() # qrcode解碼器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30) # 每30每30

    def update_frame(self):
        """ 讀取攝影機，並檢測qrcode """
        if not self.cap or not self.cap.isOpened():
            return
        
        ret, frame = self.cap.read()
        if ret:
            self.decoder_text, pts, _ = self.detector.detectAndDecode(frame)
            if self.decoder_text:
                self.draw_qrcode_box(frame, pts)
                self.login_student()
            image_with_crosshair = self.draw_cercent(frame)
            self.display_image(image_with_crosshair) # opencv轉換成Qpixmap
            
    def login_student(self):
        """解密 QR Code 內容，並嘗試登入"""
        try:
            if not self.decoder_text:
                print("解碼後的 QR Code 內容為空")
                
                # 創建 QMessageBox 並自動關閉
                msg_box = QMessageBox(self.main_window)
                msg_box.setWindowTitle("錯誤")
                msg_box.setText("無法讀取 QR Code \n\n  (3 秒後關閉本通知)")
                msg_box.setStandardButtons(QMessageBox.Ok)

                # 設定計時器，3 秒後自動關閉
                QTimer.singleShot(3000, msg_box.accept)
                
                msg_box.exec_()
                return

            print(f"QR Code 原始內容: {self.decoder_text}")  # 確認 QR Code 內容
            
            decrypted_data = self.encrypted.decrypt(self.decoder_text)
            print(f"解密後的內容: {decrypted_data}")  # 確認解密結果
            
            if not decrypted_data:
                print("解密後內容為空，可能是密鑰錯誤")
                
                msg_box = QMessageBox(self.main_window)
                msg_box.setWindowTitle("錯誤")
                msg_box.setText("無法解密 QR Code \n\n  (3 秒後關閉本通知)")
                msg_box.setStandardButtons(QMessageBox.Ok)

                QTimer.singleShot(3000, msg_box.accept)
                
                msg_box.exec_()
                return

            self.db.cursor.execute(
                '''SELECT stu_name, stu_class, stu_seat_num FROM Students WHERE stu_uuid=?''', 
                (decrypted_data,)
            )
            stu_uuid = self.db.cursor.fetchone()

            if stu_uuid is None:
                print(f"資料庫查無此 UUID: {decrypted_data}")

                msg_box = QMessageBox(self.main_window)
                msg_box.setWindowTitle("失敗")
                msg_box.setText(f"查無此學生，UUID={decrypted_data} \n\n  (3 秒後關閉本通知)")
                msg_box.setStandardButtons(QMessageBox.Ok)

                QTimer.singleShot(3000, msg_box.accept)

                msg_box.exec_()
                return

            stu_name, stu_class, stu_seat_num = stu_uuid

            # 成功登入訊息
            msg_box = QMessageBox(self.main_window)
            msg_box.setWindowTitle("成功")
            msg_box.setText(f"{stu_name}_{stu_class}_{stu_seat_num} 學生登入成功 \n\n  (3 秒後啟動遊戲)")
            msg_box.setStandardButtons(QMessageBox.Ok)

            QTimer.singleShot(3000, msg_box.accept)

            msg_box.exec_()

            # 關閉視窗
            self.main_window.close()

        except Exception as e:
            print(f"登入失敗={e}")

            msg_box = QMessageBox(self.main_window)
            msg_box.setWindowTitle("錯誤")
            msg_box.setText(f"學生登入發生錯誤: {e} \n\n  (3 秒後關閉本通知)")
            msg_box.setStandardButtons(QMessageBox.Ok)

            QTimer.singleShot(3000, msg_box.accept)

            msg_box.exec_()
            
    def draw_qrcode_box(self, frame, pts):
        if pts is not None:
            pts = pts[0].astype(int).reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], isClosed=True, color=(0, 0, 255), thickness=2)
            cv2.putText(frame, self.decoder_text, (pts[0][0][0], pts[0][0][1]-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    def draw_cercent(self, image):
        height, width, _ = image.shape
        center_x, center_y = width // 2, height // 2
        cv2.line(image, (0, center_y), (width, center_y), (255, 255, 255), 2)
        cv2.line(image, (center_x, 0), (center_x, height), (255, 255, 255), 2)
        return image

    def display_image(self, image):
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qimg))

    def closeEvent(self):
        self.cap.release()
    # def draw_qrcode_box(self, frame, pts):
    #     """ 在qrcode周圍繪製紅色邊框 """
    #     if pts is not None:
    #         pts = pts[0].astype(int).reshape((-1, 1, 2))
    #         cv2.polylines(frame, [pts], isClosed=True, color=(0, 0, 255), thickness=2)
    #         cv2.putText(frame, self.decoder_text, (pts[0][0][0], pts[0][0][1]-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # def draw_crosshair(self, image):
    #     """在畫面中心繪製十字線"""
    #     height, width, _ = image.shape
    #     center_x, center_y = width // 2, height // 2
    #     cv2.line(image, (0, center_y), (width, center_y), (255, 255, 255), 2)
    #     cv2.line(image, (center_x, 0), (center_x, height), (255, 255, 255), 2)
    #     return image

    # def display_image(self, image):
    #     """將 OpenCV 圖像轉換為 QPixmap 並顯示"""
    #     rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    #     h, w, ch = rgb_image.shape
    #     bytes_per_line = ch * w
    #     qimg = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
    #     self.video_label.setPixmap(QPixmap.fromImage(qimg))

    # def release_camera(self):
    #     """ 釋放攝影機資源 """
    #     if self.cap and self.cap.isOpened():
    #         self.cap.release()
    #         print("攝像機已釋放！")
            
    # """確保攝影機被釋放"""
    # def __del__(self):
    #     self.release_camera()
    
    
    # def login_stu(self):
    #     stu_uuid = self.db.cursor.execute('''SELECT stu_name, stu_class, stu_seat_num FROM Students WHERE stu_uuid=?''', (uuid,))
    #     if stu_uuid:
    #         stu_name, stu_class, stu_seat_num = stu_uuid.fetchone()
    #         QMessageBox.information(self.main_window, "成功",f"{stu_name}_{stu_class}_{stu_seat_num}學生登入成功")
    #         time.sleep(3)
    #         self.main_window.close()
    #     else:
    #         QMessageBox.information(self.main_window, "失敗","學生登入失敗")