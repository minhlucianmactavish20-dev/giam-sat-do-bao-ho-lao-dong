import os

# Đường dẫn gốc của project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Đường dẫn thư mục dữ liệu
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
VIOLATIONS_DIR = os.path.join(BASE_DIR, 'violations')
DB_PATH = os.path.join(DATA_DIR, 'ppe_monitoring.db')
YOLO_MODEL_PATH = os.path.join(MODELS_DIR, 'yolov8n.pt')

# Cấu hình camera
CAMERA_INDEX = 0  # Index webcam
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Cấu hình phát hiện & Đánh giá PPE
CONFIDENCE_THRESHOLD = 0.45  # Ngưỡng tin cậy của mô hình YOLOv8

# Danh sách các trang bị bảo hộ cần kiểm tra (PPE Items)
REQUIRED_PPE_ITEMS = {
    'helmet': {'name': 'Mũ bảo hộ', 'alias': ['helmet', 'hat', 'hard-hat', 'cap']},
    'glasses': {'name': 'Kính bảo hộ', 'alias': ['glasses', 'goggles', 'eye-protection', 'sunglasses']},
    'vest': {'name': 'Áo bảo hộ/phản quang', 'alias': ['vest', 'jacket', 'coat', 'safety-vest']},
    'mask': {'name': 'Khẩu trang', 'alias': ['mask', 'face-mask', 'medical-mask']}
}

# Cấu hình Cooldown cảnh báo âm thanh (giây)
ALARM_COOLDOWN = 3.0

# Cấu hình giao diện
APP_TITLE = "Hệ Thống Giám Sát Đồ Bảo Hộ Lao Động — PPE Safety System"
APP_WIDTH = 1240
APP_HEIGHT = 720

# Tạo tự động các thư mục nếu chưa tồn tại
for d in [DATA_DIR, MODELS_DIR, REPORTS_DIR, VIOLATIONS_DIR]:
    os.makedirs(d, exist_ok=True)
