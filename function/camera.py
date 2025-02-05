import cv2
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel, QMessageBox
import time

class Camera():
    def __init__(self, db,ui, encrypted, main_window):
        self.ui = ui
        self.db = db
        self.cap = None  # 初始化攝影機
        self.timer = QTimer()
        self.encrypted = encrypted
        self.main_window = main_window
    def stu_login_video(self):
        """ 初始化攝影機，並開啟時器讀取一幀 """
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("無法開啟攝影機！")
            return
    
        if not isinstance(self.ui.pic, QLabel):
            print("錯誤：self.ui.pic 不是 QLabel！")
            return
        
        self.video_label = self.ui.pic
        self.detector = cv2.QRCodeDetector() # qrcode解碼器
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30) # 每30每30

    def update_frame(self):
        """ 讀取攝影機，並檢測qrcode """
        if not self.cap or not self.cap.isOpened():
            return
        
        ret, frame = self.cap.read()
        if ret:
            decoder_text, pts, _ = self.detector.detectAndDecode(frame)
            if decoder_text:
                self.draw_qrcode_box(frame, pts, decoder_text)
                self.login_student(decoder_text)
            image_with_crosshair = self.draw_crosshair(frame)
            self.display_image(image_with_crosshair) # opencv轉換成Qpixmap

    def login_student(self, decoder_text):
        """解密qrcode內容，並嘗試登入"""
        try:
            decrypted_data = self.encrypted.decrypt(decoder_text)
            if decrypted_data:
                self.login_stu(decrypted_data)
        except Exception as e:
            print(f"登入失敗: {e}")

    def draw_qrcode_box(self, frame, pts, decoder_text):
        """ 在qrcode周圍繪製紅色邊框 """
        if pts is not None:
            pts = pts[0].astype(int).reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], isClosed=True, color=(0, 0, 255), thickness=2)
            cv2.putText(frame, decoder_text, (pts[0][0][0], pts[0][0][1]-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    def draw_crosshair(self, image):
        """在畫面中心繪製十字線"""
        height, width, _ = image.shape
        center_x, center_y = width // 2, height // 2
        cv2.line(image, (0, center_y), (width, center_y), (255, 255, 255), 2)
        cv2.line(image, (center_x, 0), (center_x, height), (255, 255, 255), 2)
        return image

    def display_image(self, image):
        """將 OpenCV 圖像轉換為 QPixmap 並顯示"""
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qimg))

    def release_camera(self):
        """ 釋放攝影機資源 """
        if self.cap and self.cap.isOpened():
            self.cap.release()
            print("攝像機已釋放！")
            
    """確保攝影機被釋放"""
    def __del__(self):
        self.release_camera()
    
    
    def login_stu(self, uuid):
        stu_uuid = self.db.cursor.execute('''SELECT stu_name, stu_class, stu_seat_num FROM Students WHERE stu_uuid=?''', (uuid,))
        if stu_uuid:
            stu_name, stu_class, stu_seat_num = stu_uuid.fetchone()
            QMessageBox.information(self.main_window, "成功",f"{stu_name}_{stu_class}_{stu_seat_num}學生登入成功")
            time.sleep(3)
            self.main_windowclose()
        else:
            QMessageBox.information(self.main_window, "失敗","學生登入失敗")