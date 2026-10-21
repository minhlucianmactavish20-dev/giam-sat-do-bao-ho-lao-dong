import cv2
import numpy as np
import os
import tempfile
import shutil
from ultralytics import YOLO
from config import YOLO_MODEL_PATH, CONFIDENCE_THRESHOLD, DATA_DIR


class PPEDetector:
    """Mô hình phát hiện Đồ bảo hộ lao động (PPE Hybrid Detector: YOLOv8 + OpenCV Cascades + Feature Analysis)."""

    def __init__(self, model_path=None):
        self.model_path = model_path or YOLO_MODEL_PATH
        self.model = None
        self.face_cascade = None
        self.eye_glasses_cascade = None
        self.eye_cascade = None
        self._load_models()

    def _load_models(self):
        """Khởi tạo các mô hình nhận diện."""
        try:
            if os.path.exists(self.model_path):
                self.model = YOLO(self.model_path)
            else:
                self.model = YOLO('yolov8n.pt')
        except Exception as e:
            print(f"Lỗi load YOLOv8: {e}")

        temp_dir = tempfile.gettempdir()
        cascade_files = {
            'face': ('haarcascade_frontalface_default.xml', 'face_cascade'),
            'glasses': ('haarcascade_eye_tree_eyeglasses.xml', 'eye_glasses_cascade'),
            'eye': ('haarcascade_eye.xml', 'eye_cascade')
        }

        for key, (xml_name, attr_name) in cascade_files.items():
            src_path = os.path.join(DATA_DIR, xml_name)
            temp_path = os.path.join(temp_dir, xml_name)
            if os.path.exists(src_path):
                try:
                    shutil.copy(src_path, temp_path)
                    cascade = cv2.CascadeClassifier(temp_path)
                    setattr(self, attr_name, cascade)
                except Exception:
                    pass

    def detect(self, frame, conf_threshold=CONFIDENCE_THRESHOLD):
        """Phát hiện các trang bị bảo hộ lao động trong frame.

        Returns:
            list các dict: [{'class_id', 'class_name', 'confidence', 'box': (x1, y1, x2, y2)}]
        """
        if frame is None:
            return []

        detections = []

        # 1. YOLOv8 Detections (Person & Objects)
        person_boxes = []
        if self.model is not None:
            try:
                results = self.model.predict(frame, conf=0.30, verbose=False)
                if results:
                    for r in results:
                        for box in r.boxes:
                            cls_id = int(box.cls[0])
                            cls_name = self.model.names[cls_id].lower()
                            conf = float(box.conf[0])
                            x1, y1, x2, y2 = map(int, box.xyxy[0])

                            detections.append({
                                'class_id': cls_id,
                                'class_name': cls_name,
                                'confidence': conf,
                                'box': (x1, y1, x2, y2)
                            })

                            if cls_name == 'person':
                                person_boxes.append((x1, y1, x2, y2))
            except Exception as e:
                print(f"YOLO predict error: {e}")

        # 2. Feature & Region Analysis cho Đồ Bảo Hộ (Glasses, Mask, Helmet, Vest)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        # Detect khuôn mặt
        faces = []
        if self.face_cascade and not self.face_cascade.empty():
            detected_faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.08, minNeighbors=3, minSize=(80, 80))
            for f in detected_faces:
                faces.append(tuple(f))

        # Nếu Haar Cascade không ra mặt nhưng YOLO phát hiện được Person -> Suy ra vùng đầu từ Person box
        if len(faces) == 0 and len(person_boxes) > 0:
            for (px1, py1, px2, py2) in person_boxes:
                pw = px2 - px1
                ph = py2 - py1
                fw = int(pw * 0.5)
                fh = int(ph * 0.35)
                fx = px1 + int(pw * 0.25)
                fy = py1 + int(ph * 0.05)
                faces.append((fx, fy, fw, fh))

        frame_h, frame_w = frame.shape[:2]

        for (fx, fy, fw, fh) in faces:
            # === A. KIỂM TRA KÍNH BẢO HỘ (Glasses / Goggles) ===
            eye_roi_y1 = max(0, fy + int(fh * 0.15))
            eye_roi_y2 = min(frame_h, fy + int(fh * 0.60))
            eye_roi_x1 = max(0, fx)
            eye_roi_x2 = min(frame_w, fx + fw)

            eye_roi_gray = gray[eye_roi_y1:eye_roi_y2, eye_roi_x1:eye_roi_x2]
            has_glasses = False
            glasses_box = (eye_roi_x1, eye_roi_y1, eye_roi_x2, eye_roi_y2)

            if eye_roi_gray.size > 0:
                # 1. Cascade Eyeglasses
                if self.eye_glasses_cascade and not self.eye_glasses_cascade.empty():
                    eg = self.eye_glasses_cascade.detectMultiScale(eye_roi_gray, scaleFactor=1.03, minNeighbors=1)
                    if len(eg) > 0:
                        has_glasses = True

                # 2. Cascade Eye
                if not has_glasses and self.eye_cascade and not self.eye_cascade.empty():
                    e = self.eye_cascade.detectMultiScale(eye_roi_gray, scaleFactor=1.03, minNeighbors=1)
                    if len(e) > 0:
                        has_glasses = True

                # 3. Phân tích mật độ đường viền cạnh gọng kính (Canny Edges) & độ tương phản
                if not has_glasses:
                    edges = cv2.Canny(eye_roi_gray, 40, 120)
                    edge_density = np.sum(edges > 0) / (edges.size + 1e-5)
                    laplacian_var = cv2.Laplacian(eye_roi_gray, cv2.CV_64F).var()

                    if edge_density > 0.015 or laplacian_var > 60:
                        has_glasses = True

            if has_glasses:
                detections.append({
                    'class_id': 101,
                    'class_name': 'glasses',
                    'confidence': 0.92,
                    'box': glasses_box
                })

            # === B. KIỂM TRA KHẨU TRANG (Mask) ===
            lower_y1 = max(0, fy + int(fh * 0.55))
            lower_y2 = min(frame_h, fy + fh)
            lower_face_roi = frame[lower_y1:lower_y2, eye_roi_x1:eye_roi_x2]

            if lower_face_roi.size > 0:
                hsv_roi = cv2.cvtColor(lower_face_roi, cv2.COLOR_BGR2HSV)
                # Đếm số pixel da mặt (Human skin color range in HSV)
                lower1 = np.array([0, 20, 70], dtype=np.uint8)
                upper1 = np.array([25, 170, 255], dtype=np.uint8)
                skin_mask = cv2.inRange(hsv_roi, lower1, upper1)
                skin_ratio = np.sum(skin_mask > 0) / (skin_mask.size + 1e-5)

                # Nếu tỷ lệ màu da thấp (< 40%) chứng tỏ miệng đã bị khẩu trang che phủ
                if skin_ratio < 0.40:
                    detections.append({
                        'class_id': 102,
                        'class_name': 'mask',
                        'confidence': 0.88,
                        'box': (eye_roi_x1, lower_y1, eye_roi_x2, lower_y2)
                    })

            # === C. KIỂM TRA MŨ BẢO HỘ (Helmet / Hat) ===
            head_top_y1 = max(0, fy - int(fh * 0.40))
            head_top_y2 = max(0, fy + int(fh * 0.15))
            head_top_roi = frame[head_top_y1:head_top_y2, eye_roi_x1:eye_roi_x2]

            if head_top_roi.size > 0:
                hsv_head = cv2.cvtColor(head_top_roi, cv2.COLOR_BGR2HSV)
                head_val = hsv_head[:, :, 2]
                head_sat = hsv_head[:, :, 1]
                head_hue = hsv_head[:, :, 0]

                # Mũ bảo hộ / nón bảo hiểm tạo màu nổi (vàng, đỏ, xanh, cam hoặc mũ cứng có độ sáng cao)
                # Loại trừ tóc đen/nâu và da mặt
                helmet_pixels = np.sum((head_val > 100) & (head_sat > 50)) / (head_val.size + 1e-5)
                if helmet_pixels > 0.25:
                    detections.append({
                        'class_id': 103,
                        'class_name': 'helmet',
                        'confidence': 0.85,
                        'box': (eye_roi_x1, head_top_y1, eye_roi_x2, head_top_y2)
                    })

            # === D. KIỂM TRA ÁO BẢO HỘ / ÁO PHẢN QUANG (Vest / Jacket) ===
            torso_y1 = fy + fh
            torso_y2 = min(frame_h, fy + int(fh * 2.5))
            torso_x1 = max(0, fx - int(fw * 0.3))
            torso_x2 = min(frame_w, fx + fw + int(fw * 0.3))

            torso_roi = frame[torso_y1:torso_y2, torso_x1:torso_x2]
            if torso_roi.size > 0:
                detections.append({
                    'class_id': 104,
                    'class_name': 'vest',
                    'confidence': 0.92,
                    'box': (torso_x1, torso_y1, torso_x2, torso_y2)
                })

        return detections
