import cv2
import os
from config import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT


class Camera:
    """Quản lý luồng webcam, video file hoặc ảnh tĩnh sử dụng OpenCV."""

    def __init__(self, source=None, loop=True):
        self.source = CAMERA_INDEX if source is None else source
        self.is_file = isinstance(self.source, str)
        self.is_image = False
        self.static_frame = None

        if self.is_file:
            ext = os.path.splitext(self.source)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.webp', '.bmp']:
                self.is_image = True

        self.loop = loop
        self.cap = None
        self.is_running = False

    def start(self):
        """Mở camera, file video hoặc file ảnh."""
        if self.is_running:
            return True

        if self.is_image:
            # Đọc ảnh tĩnh (hỗ trợ đường dẫn có khoảng trắng/ký tự đặc biệt)
            self.static_frame = cv2.imread(self.source)
            if self.static_frame is None:
                print(f"Không thể đọc file ảnh: {self.source}")
                return False
            self.is_running = True
            return True

        if self.is_file:
            self.cap = cv2.VideoCapture(self.source)
        else:
            if os.name == 'nt':
                self.cap = cv2.VideoCapture(self.source, cv2.CAP_DSHOW)
                if not self.cap.isOpened():
                    self.cap = cv2.VideoCapture(self.source)
            else:
                self.cap = cv2.VideoCapture(self.source)

        if not self.cap or not self.cap.isOpened():
            print(f"Không thể mở nguồn phát (source={self.source})!")
            return False

        if not self.is_file:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

        self.is_running = True
        return True

    def read_frame(self):
        """Đọc một frame từ nguồn phát.

        Returns:
            (success, frame) - success là bool, frame là ảnh BGR
        """
        if not self.is_running:
            return False, None

        if self.is_image:
            if self.static_frame is not None:
                return True, self.static_frame.copy()
            return False, None

        if self.cap is None:
            return False, None

        ret, frame = self.cap.read()
        if not ret:
            if self.is_file and self.loop:
                # Tua lại đầu video
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                if not ret:
                    return False, None
            else:
                return False, None

        # Chỉ lật gương đối với webcam
        if not self.is_file:
            frame = cv2.flip(frame, 1)

        return True, frame

    def stop(self):
        """Đóng nguồn phát."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.static_frame = None
        self.is_running = False

    def __del__(self):
        self.stop()
