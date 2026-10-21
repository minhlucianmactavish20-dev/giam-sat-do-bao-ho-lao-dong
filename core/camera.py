import cv2
import os
from config import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT


class Camera:
    """Quản lý luồng webcam sử dụng OpenCV VideoCapture."""

    def __init__(self, camera_index=None):
        self.camera_index = camera_index if camera_index is not None else CAMERA_INDEX
        self.cap = None
        self.is_running = False

    def start(self):
        """Mở camera."""
        if self.is_running:
            return True

        if os.name == 'nt':
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                self.cap = cv2.VideoCapture(self.camera_index)
        else:
            self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            print(f"Không thể mở camera (index={self.camera_index})!")
            return False

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        self.is_running = True
        return True

    def read_frame(self):
        """Đọc một frame từ camera.

        Returns:
            (success, frame) - success là bool, frame là ảnh BGR
        """
        if not self.is_running or self.cap is None:
            return False, None

        ret, frame = self.cap.read()
        if not ret:
            return False, None

        # Flip ngang (hội họa mirror)
        frame = cv2.flip(frame, 1)
        return True, frame

    def stop(self):
        """Đóng camera."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.is_running = False

    def __del__(self):
        self.stop()
