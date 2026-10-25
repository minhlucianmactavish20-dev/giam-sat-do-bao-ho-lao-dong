import os

# Đường dẫn gốc của project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Đường dẫn thư mục dữ liệu
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
VIOLATIONS_DIR = os.path.join(BASE_DIR, 'violations')
DB_PATH = os.path.join(DATA_DIR, 'ppe_monitoring.db')
# Đường dẫn các mô hình Specialist (Multi-head Ensemble)
CUSTOM_MODEL_PATH = os.path.join(MODELS_DIR, 'best.pt')
DEFAULT_MODEL_PATH = os.path.join(MODELS_DIR, 'yolov8n.pt')
MODEL_HAT_PATH = os.path.join(MODELS_DIR, 'hardhat_keremberke.pt')
MODEL_MASK_PATH = os.path.join(MODELS_DIR, 'mask_nma.pt')
YOLO_MODEL_PATH = CUSTOM_MODEL_PATH if os.path.exists(CUSTOM_MODEL_PATH) else DEFAULT_MODEL_PATH

# Cấu hình camera
CAMERA_INDEX = 0  # Index webcam
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Cấu hình phát hiện & Đánh giá PPE
CONFIDENCE_THRESHOLD = 0.25  # Ngưỡng tin cậy tối ưu cho mô hình PPE

# Danh sách các trang bị bảo hộ cần kiểm tra (Bỏ kính bảo hộ theo yêu cầu)
REQUIRED_PPE_ITEMS = {
    'helmet': {
        'name': 'Mũ bảo hộ',
        'alias': ['helmet', 'hardhat', 'hat', 'hard-hat', 'cap'],
        'negative_alias': ['no-hardhat', 'no_hardhat', 'no-helmet']
    },
    'vest': {
        'name': 'Áo bảo hộ/phản quang',
        'alias': ['vest', 'safety vest', 'safety-vest', 'jacket', 'coat'],
        'negative_alias': ['no-safety vest', 'no-safety-vest', 'no_safety_vest', 'no-vest']
    },
    'mask': {
        'name': 'Khẩu trang',
        'alias': ['mask', 'face_masked', 'face-mask', 'medical-mask'],
        'negative_alias': ['no-mask', 'no_mask']
    }
}

# Cấu hình Cooldown cảnh báo âm thanh (giây)
ALARM_COOLDOWN = 3.0

# Tùy chọn chụp ảnh bằng chứng vi phạm (Tự động chụp và lưu ảnh vào thư mục violations)
ENABLE_VIOLATION_SNAPSHOT = True

# Cấu hình giao diện
APP_TITLE = "Hệ Thống Giám Sát Đồ Bảo Hộ Lao Động — PPE Safety System"
APP_WIDTH = 1240
APP_HEIGHT = 720

# Tạo tự động các thư mục nếu chưa tồn tại
for d in [DATA_DIR, MODELS_DIR, REPORTS_DIR, VIOLATIONS_DIR]:
    os.makedirs(d, exist_ok=True)
