import os
from ultralytics import YOLO
from config import (
    YOLO_MODEL_PATH,
    CUSTOM_MODEL_PATH,
    MODEL_MASK_PATH,
    CONFIDENCE_THRESHOLD,
    MAIN_MODEL_CLASSES,
    ENABLE_PERSON_DETECTION,
    PERSON_MODEL_PATH,
    PERSON_CONFIDENCE
)


class PPEDetector:

    def __init__(self, model_path=None):
        self.model_path = model_path or YOLO_MODEL_PATH
        self.model_ppe = None
        self.model_mask = None
        self.model_person = None
        self._load_models()

    def _load_models(self):
        target_path = self.model_path
        if os.path.exists(CUSTOM_MODEL_PATH):
            target_path = CUSTOM_MODEL_PATH

        try:
            if os.path.exists(target_path):
                self.model_ppe = YOLO(target_path)
                self.model_path = target_path
                print(f"Đã nạp Main PPE Model: {self.model_path}")
                print(f"  Các lớp của model: {list(self.model_ppe.names.values())}")
                print(f"  Các lớp được dùng: {list(MAIN_MODEL_CLASSES.keys())}")
            else:
                self.model_ppe = YOLO('yolov8n.pt')
                self.model_path = 'yolov8n.pt'
        except Exception as e:
            print(f"Lỗi load Main PPE model: {e}")

        if os.path.exists(MODEL_MASK_PATH):
            try:
                self.model_mask = YOLO(MODEL_MASK_PATH)
                print(f"Đã nạp Mask Model: {MODEL_MASK_PATH}")
            except Exception as e:
                print(f"Lỗi nạp Mask model: {e}")

        if ENABLE_PERSON_DETECTION:
            try:
                person_path = PERSON_MODEL_PATH if os.path.exists(PERSON_MODEL_PATH) else 'yolov8n.pt'
                self.model_person = YOLO(person_path)
                print(f"Đã nạp Person Model: {person_path}")
            except Exception as e:
                print(f"Lỗi nạp Person model: {e}")

        print("Pipeline 3 model sẵn sàng hoạt động!")

    def detect(self, frame, conf_threshold=CONFIDENCE_THRESHOLD):
        if frame is None:
            return []

        detections = []

        if self.model_ppe is not None:
            try:
                results_ppe = self.model_ppe.predict(frame, conf=conf_threshold, verbose=False)
                if results_ppe:
                    for box in results_ppe[0].boxes:
                        cls_id = int(box.cls[0])
                        cls_name = self.model_ppe.names[cls_id].lower()
                        if cls_name not in MAIN_MODEL_CLASSES:
                            continue
                        conf = float(box.conf[0])
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        detections.append({
                            'class_id': cls_id,
                            'class_name': MAIN_MODEL_CLASSES[cls_name],
                            'confidence': conf,
                            'box': (x1, y1, x2, y2)
                        })
            except Exception as e:
                print(f"PPE model error: {e}")

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
                print(f"Mask model error: {e}")

        if self.model_person is not None:
            try:
                results_person = self.model_person.predict(
                    frame, conf=PERSON_CONFIDENCE, classes=[0], verbose=False
                )
                if results_person:
                    for box in results_person[0].boxes:
                        conf = float(box.conf[0])
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        detections.append({
                            'class_id': 0,
                            'class_name': 'person',
                            'confidence': conf,
                            'box': (x1, y1, x2, y2)
                        })
            except Exception as e:
                print(f"Person model error: {e}")

        return detections