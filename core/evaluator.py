import cv2
import numpy as np
from config import REQUIRED_PPE_ITEMS, ENABLE_PERSON_DETECTION

CLASS_LABELS = {
    'hardhat': ('Mu bao ho', (0, 200, 0)),
    'helmet': ('Mu bao ho', (0, 200, 0)),
    'safety vest': ('Ao phan quang', (0, 200, 0)),
    'vest': ('Ao phan quang', (0, 200, 0)),
    'mask': ('Khau trang', (0, 200, 0)),
    'person': ('Nguoi', (255, 200, 0)),

    'no-hardhat': ('[!] KHONG MU', (0, 0, 230)),
    'no-mask': ('[!] KHONG KHAU TRANG', (0, 0, 230)),
    'no-safety vest': ('[!] KHONG AO VEST', (0, 0, 230)),

    'safety cone': ('Chop non', (150, 150, 150)),
    'machinery': ('May moc', (150, 150, 150)),
    'vehicle': ('Phuong tien', (150, 150, 150)),

    'goggles': ('Kinh bao ho', (0, 200, 0)),
    'no-goggles': ('[!] KHONG KINH', (0, 0, 230)),
}


class PPEEvaluator:

    def __init__(self):
        self.required_items = REQUIRED_PPE_ITEMS

    def evaluate_frame(self, frame, detections):

        annotated_frame = frame.copy()
        detected_aliases = set()

        person_boxes = []
        explicit_violations = set()

        for d in detections:
            c_name = d['class_name'].strip().lower()
            detected_aliases.add(c_name)

            if c_name == 'person':
                person_boxes.append(d['box'])

            if 'no-hardhat' in c_name:
                explicit_violations.add('Mũ bảo hộ')
            elif 'no-mask' in c_name:
                explicit_violations.add('Khẩu trang')
            elif 'no-safety vest' in c_name or 'no-vest' in c_name:
                explicit_violations.add('Áo bảo hộ/phản quang')

        detected_ppe = []
        missing_ppe = []

        if ENABLE_PERSON_DETECTION:
            person_detected = len(person_boxes) > 0
        else:
            person_detected = len(person_boxes) > 0 or len(detections) > 0

        for ppe_key, ppe_info in self.required_items.items():
            name = ppe_info['name']
            aliases = [a.lower() for a in ppe_info['alias']]
            neg_aliases = [na.lower() for na in ppe_info.get('negative_alias', [])]

            has_negative = any(na in detected_aliases for na in neg_aliases) or (name in explicit_violations)

            has_positive = any(a in detected_aliases for a in aliases)

            if has_positive and not has_negative:
                detected_ppe.append(name)
            elif has_negative:
                missing_ppe.append(name)
            elif person_detected:
                missing_ppe.append(name)

        total_items = len(self.required_items)
        detected_count = len(detected_ppe)
        score = (detected_count / total_items) * 100.0 if total_items > 0 else 100.0

        is_compliant = (len(missing_ppe) == 0) if person_detected else True


        for d in detections:
            x1, y1, x2, y2 = d['box']
            cls_name = d['class_name'].strip().lower()
            conf = d['confidence']

            if cls_name in CLASS_LABELS:
                label_prefix, color = CLASS_LABELS[cls_name]
            elif cls_name.startswith('no-'):
                label_prefix, color = f"❌ {cls_name}", (0, 0, 230)
            else:
                label_prefix, color = cls_name, (0, 200, 0)

            if cls_name in ['machinery', 'vehicle', 'safety cone']:
                continue

            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            label_text = f"{label_prefix} ({conf*100:.0f}%)"

            (w, h), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
            bg_y1 = max(0, y1 - h - 8)
            cv2.rectangle(annotated_frame, (x1, bg_y1), (x1 + w + 6, y1), color, -1)
            cv2.putText(
                annotated_frame, label_text, (x1 + 3, y1 - 4),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2
            )

        banner_color = (0, 180, 0) if is_compliant else (0, 0, 220)  # Xanh nếu An toàn, Đỏ nếu Vi phạm
        cv2.rectangle(annotated_frame, (0, 0), (annotated_frame.shape[1], 45), banner_color, -1)

        if not person_detected:
            status_text = "DANG CHO: Khong phat hien nguoi trong khung hinh"
            banner_color = (80, 80, 80)
            cv2.rectangle(annotated_frame, (0, 0), (annotated_frame.shape[1], 45), banner_color, -1)
        elif is_compliant:
            status_text = f"AN TOAN: Tuan thu 100% trang bi ({detected_count}/{total_items})"
        else:
            missing_map = {
                'Mũ bảo hộ': 'Mu',
                'Áo bảo hộ/phản quang': 'Ao vest',
                'Khẩu trang': 'Khau trang',
                'Kính bảo hộ': 'Kinh'
            }
            missing_clean = [missing_map.get(m, m) for m in missing_ppe]
            missing_str = ", ".join(missing_clean)
            status_text = f"VI PHAM: Thieu {missing_str} ({score:.0f}%)"

        cv2.putText(
            annotated_frame, status_text, (15, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.70, (255, 255, 255), 2
        )

        summary = {
            'is_compliant': is_compliant,
            'compliance_score': round(score, 1),
            'detected_ppe': detected_ppe,
            'missing_ppe': missing_ppe,
            'person_detected': person_detected
        }

        return annotated_frame, summary
