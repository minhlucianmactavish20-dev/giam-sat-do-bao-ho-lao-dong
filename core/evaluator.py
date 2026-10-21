import cv2
import numpy as np
from config import REQUIRED_PPE_ITEMS


class PPEEvaluator:
    """Đánh giá mức độ tuân thủ Đồ bảo hộ lao động (PPE Compliance)."""

    def __init__(self):
        self.required_items = REQUIRED_PPE_ITEMS

    def evaluate_frame(self, frame, detections):
        """Đánh giá tuân thủ PPE và vẽ khung trực quan lên frame.

        Args:
            frame: BGR frame
            detections: Danh sách dict từ PPEDetector

        Returns:
            (annotated_frame, evaluation_summary)
            evaluation_summary = {
                'is_compliant': bool,
                'compliance_score': float, # 0.0 - 100.0%
                'detected_ppe': list,
                'missing_ppe': list,
                'person_detected': bool
            }
        """
        annotated_frame = frame.copy()
        detected_aliases = set()

        person_boxes = []
        for d in detections:
            c_name = d['class_name']
            if c_name == 'person':
                person_boxes.append(d['box'])
            detected_aliases.add(c_name)

        # Kiểm tra từng item trong REQUIRED_PPE_ITEMS
        detected_ppe = []
        missing_ppe = []

        for ppe_key, ppe_info in self.required_items.items():
            name = ppe_info['name']
            aliases = ppe_info['alias']

            # Kiểm tra xem có alias nào xuất hiện trong detections không
            matched = any(alias in detected_aliases for alias in aliases)
            if matched:
                detected_ppe.append(name)
            else:
                missing_ppe.append(name)

        total_items = len(self.required_items)
        detected_count = len(detected_ppe)
        score = (detected_count / total_items) * 100.0 if total_items > 0 else 100.0

        # Nếu có người nhưng thiếu trang bị -> Vi phạm
        person_detected = len(person_boxes) > 0 or len(detections) > 0
        is_compliant = (len(missing_ppe) == 0) if person_detected else True

        # === VẼ THÔNG TIN TRỰC QUAN LÊN FRAME ===
        # 1. Vẽ bounding boxes của các vật thể
        for d in detections:
            x1, y1, x2, y2 = d['box']
            cls_name = d['class_name']
            conf = d['confidence']

            # Phân loại màu box
            if cls_name == 'person':
                color = (255, 200, 0)  # Cyan/Yellow
            else:
                color = (0, 255, 0) if is_compliant else (0, 165, 255)

            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            label_text = f"{cls_name} ({conf*100:.0f}%)"

            (w, h), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(annotated_frame, (x1, y1 - h - 10), (x1 + w, y1), color, -1)
            cv2.putText(annotated_frame, label_text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        # 2. Vẽ Banner Trạng thái ở trên cùng
        banner_color = (0, 180, 0) if is_compliant else (0, 0, 220)  # Green or Red
        cv2.rectangle(annotated_frame, (0, 0), (annotated_frame.shape[1], 45), banner_color, -1)

        if is_compliant:
            status_text = f"AN TOAN: Tuan thu 100% trang bi ({detected_count}/{total_items})"
        else:
            missing_str = ", ".join(missing_ppe)
            status_text = f"VI PHAM: Thieu {missing_str} ({score:.0f}%)"

        cv2.putText(
            annotated_frame, status_text, (15, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2
        )

        summary = {
            'is_compliant': is_compliant,
            'compliance_score': round(score, 1),
            'detected_ppe': detected_ppe,
            'missing_ppe': missing_ppe,
            'person_detected': person_detected
        }

        return annotated_frame, summary
