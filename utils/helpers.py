import cv2
import numpy as np
import os
import winsound


def imread_utf8(path, flags=cv2.IMREAD_COLOR):
    """Đọc ảnh hỗ trợ đường dẫn tiếng Việt (Unicode)."""
    try:
        data = np.fromfile(path, dtype=np.uint8)
        if len(data) == 0:
            return None
        return cv2.imdecode(data, flags)
    except Exception as e:
        print(f"Lỗi đọc ảnh {path}: {e}")
        return None


def imwrite_utf8(path, img, ext='.jpg'):
    """Ghi ảnh hỗ trợ đường dẫn tiếng Việt (Unicode)."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        ret, buf = cv2.imencode(ext, img)
        if ret:
            buf.tofile(path)
            return True
        return False
    except Exception as e:
        print(f"Lỗi ghi ảnh {path}: {e}")
        return False


def play_alarm_sound(freq=1000, duration=300):
    """Phát âm thanh cảnh báo bíp bíp trên Windows."""
    try:
        winsound.Beep(freq, duration)
    except Exception as e:
        print(f"Lỗi phát âm thanh: {e}")
