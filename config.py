import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, 'data')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
VIOLATIONS_DIR = os.path.join(BASE_DIR, 'violations')
DB_PATH = os.path.join(DATA_DIR, 'ppe_monitoring.db')

PPE10_MODEL_PATH = os.path.join(MODELS_DIR, 'best_ppe10.pt')
OLD_MODEL_PATH = os.path.join(MODELS_DIR, 'best.pt')
CUSTOM_MODEL_PATH = PPE10_MODEL_PATH if os.path.exists(PPE10_MODEL_PATH) else OLD_MODEL_PATH
DEFAULT_MODEL_PATH = os.path.join(MODELS_DIR, 'yolov8n.pt')
MODEL_MASK_PATH = os.path.join(MODELS_DIR, 'mask_nma.pt')
YOLO_MODEL_PATH = CUSTOM_MODEL_PATH if os.path.exists(CUSTOM_MODEL_PATH) else DEFAULT_MODEL_PATH

ENABLE_PERSON_DETECTION = True
PERSON_MODEL_PATH = DEFAULT_MODEL_PATH
PERSON_CONFIDENCE = 0.4

MAIN_MODEL_CLASSES = {
    'helmet': 'helmet',
    'vest': 'vest',
    'goggles': 'goggles',
}

CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

CONFIDENCE_THRESHOLD = 0.25

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
    'goggles': {
        'name': 'Kính bảo hộ',
        'alias': ['goggles', 'glasses', 'safety glasses'],
        'negative_alias': ['no-goggles']
    },
    'mask': {
        'name': 'Khẩu trang',
        'alias': ['mask', 'face_masked', 'face-mask', 'medical-mask'],
        'negative_alias': ['no-mask', 'no_mask']
    }
}

ALARM_COOLDOWN = 3.0

ENABLE_VIOLATION_SNAPSHOT = True

APP_TITLE = "Hệ Thống Giám Sát Đồ Bảo Hộ Lao Động — PPE Safety System"
APP_WIDTH = 1240
APP_HEIGHT = 720

for d in [DATA_DIR, MODELS_DIR, REPORTS_DIR, VIOLATIONS_DIR]:
    os.makedirs(d, exist_ok=True)