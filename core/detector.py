import cv2
import numpy as np
import os
from ultralytics import YOLO
from config import (
    YOLO_MODEL_PATH,
    CUSTOM_MODEL_PATH,
    MODEL_HAT_PATH,
    MODEL_MASK_PATH,
    CONFIDENCE_THRESHOLD
)


class PPEDetector:
    """Mô hình phát hiện Đồ bảo hộ lao động (Multi-Head Specialist Ensemble Pipeline).

    Kết hợp 3 mô hình chuyên sâu:
    - Main PPE Model: Phát hiện Áo phản quang (Vest) & Người (Person)
    - Hardhat Specialist: Phát hiện Mũ bảo hộ (Hardhat / Helmet)
    - Mask Specialist: Phát hiện Khẩu trang y tế & N95 (Face Mask)
    """

    def __init__(self, model_path=None):
        self.model_path = model_path or YOLO_MODEL_PATH
        self.model_ppe = None
        self.model_hat = None
        self.model_mask = None
        self.is_custom_model = True
        self._load_models()

    def _load_models(self):
        """Khởi tạo các mô hình nhận diện chuyên sâu."""
        # 1. Mô hình chính (Áo phản quang / PPE Body)
        target_path = self.model_path
        if os.path.exists(CUSTOM_MODEL_PATH):
            target_path = CUSTOM_MODEL_PATH

        try:
            if os.path.exists(target_path):
                self.model_ppe = YOLO(target_path)
                self.model_path = target_path
                print(f"🦺 Đã nạp Main PPE Model: {self.model_path}")
            else:
                self.model_ppe = YOLO('yolov8n.pt')
                self.model_path = 'yolov8n.pt'
        except Exception as e:
            print(f"Lỗi load Main PPE model: {e}")

        # 2. Mô hình chuyên sâu Mũ bảo hộ (Hardhat Specialist)
        if os.path.exists(MODEL_HAT_PATH):
            try:
                self.model_hat = YOLO(MODEL_HAT_PATH)
                print(f"🪖 Đã nạp Hardhat Specialist Model: {MODEL_HAT_PATH}")
            except Exception as e:
                print(f"Lỗi nạp Hardhat model: {e}")

        # 3. Mô hình chuyên sâu Khẩu trang (Mask Specialist)
        if os.path.exists(MODEL_MASK_PATH):
            try:
                self.model_mask = YOLO(MODEL_MASK_PATH)
                print(f"😷 Đã nạp Mask Specialist Model: {MODEL_MASK_PATH}")
            except Exception as e:
                print(f"Lỗi nạp Mask model: {e}")

        print("🎯 Multi-Head Specialist Pipeline sẵn sàng hoạt động!")

    def detect(self, frame, conf_threshold=CONFIDENCE_THRESHOLD):
        """Phát hiện đồng thời Mũ, Áo và Khẩu trang với độ chính xác cao nhất.

        Returns:
            list các dict: [{'class_id', 'class_name', 'confidence', 'box': (x1, y1, x2, y2)}]
        """
        if frame is None:
            return []

        detections = []

        # 1. Chạy Main PPE Model (Nhận diện Áo bảo hộ / Vest & Người)
        if self.model_ppe is not None:
            try:
                results_ppe = self.model_ppe.predict(frame, conf=conf_threshold, verbose=False)
                if results_ppe:
                    for box in results_ppe[0].boxes:
                        cls_id = int(box.cls[0])
                        cls_name = self.model_ppe.names[cls_id].lower()
                        conf = float(box.conf[0])
                        x1, y1, x2, y2 = map(int, box.xyxy[0])

                        # Chỉ lấy các nhãn có ích, bỏ qua xe cộ hoặc nhãn rác
                        if any(k in cls_name for k in ['vest', 'jacket', 'person', 'helmet', 'hardhat']):
                            # Chuẩn hóa tên class
                            clean_name = 'vest' if 'vest' in cls_name else cls_name
                            detections.append({
                                'class_id': cls_id,
                                'class_name': clean_name,
                                'confidence': conf,
                                'box': (x1, y1, x2, y2)
                            })
            except Exception as e:
                print(f"PPE model error: {e}")

        # 2. Chạy Hardhat Specialist (Chuyên nhận diện Mũ bảo hộ)
        if self.model_hat is not None:
            try:
                results_hat = self.model_hat.predict(frame, conf=conf_threshold, verbose=False)
                if results_hat:
                    for box in results_hat[0].boxes:
                        cls_id = int(box.cls[0])
                        cls_name = self.model_hat.names[cls_id].lower()
                        conf = float(box.conf[0])
                        x1, y1, x2, y2 = map(int, box.xyxy[0])

                        if cls_name == 'hardhat':
                            detections.append({
                                'class_id': 101,
                                'class_name': 'hardhat',
                                'confidence': conf,
                                'box': (x1, y1, x2, y2)
                            })
            except Exception as e:
                print(f"Hardhat specialist error: {e}")

        # 3. Chạy Mask Specialist (Chuyên nhận diện Khẩu trang)
        if self.model_mask is not None:
            try:
                results_mask = self.model_mask.predict(frame, conf=conf_threshold, verbose=False)
                if results_mask:
                    for box in results_mask[0].boxes:
                        cls_id = int(box.cls[0])
                        cls_name = self.model_mask.names[cls_id].lower()
                        conf = float(box.conf[0])
                        x1, y1, x2, y2 = map(int, box.xyxy[0])

                        if 'masked' in cls_name:
                            detections.append({
                                'class_id': 102,
                                'class_name': 'mask',
                                'confidence': conf,
                                'box': (x1, y1, x2, y2)
                            })
            except Exception as e:
                print(f"Mask specialist error: {e}")

        return detections
