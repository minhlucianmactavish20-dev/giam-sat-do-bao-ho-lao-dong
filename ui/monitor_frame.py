import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import os
import time
from datetime import datetime
from config import VIOLATIONS_DIR, REQUIRED_PPE_ITEMS
from utils.helpers import imwrite_utf8


class MonitorFrame(ctk.CTkFrame):
    """Màn hình giám sát đồ bảo hộ lao động thời gian thực (Real-time PPE Monitoring)."""

    def __init__(self, parent, detector, evaluator, alarm_mgr, ppe_dao):
        super().__init__(parent, fg_color="#0f3460")

        self.detector = detector
        self.evaluator = evaluator
        self.alarm_mgr = alarm_mgr
        self.ppe_dao = ppe_dao

        self.camera = None
        self.camera_running = False
        self.photo_image = None
        self.last_snapshot_time = 0
        self.snapshot_cooldown = 4.0  # seconds between snapshot saves

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # === HEADER ===
        header = ctk.CTkLabel(
            self, text="🎥 Giám Sát Real-Time Đồ Bảo Hộ Lao Động",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#e94560"
        )
        header.grid(row=0, column=0, columnspan=2, pady=(15, 10), padx=20, sticky="w")

        # === LEFT PANEL: Camera Feed ===
        left_panel = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=12)
        left_panel.grid(row=1, column=0, padx=(20, 10), pady=(0, 20), sticky="nswe")
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(0, weight=1)

        self.camera_label = ctk.CTkLabel(
            left_panel,
            text="📷 Nhấn 'Bắt Đầu Giám Sát' để mở camera",
            font=ctk.CTkFont(size=16),
            fg_color="#1a1a2e", corner_radius=8
        )
        self.camera_label.grid(row=0, column=0, padx=15, pady=15, sticky="nswe")

        # Control button
        self.btn_start = ctk.CTkButton(
            left_panel, text="▶️  Bắt Đầu Giám Sát", height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#2ecc71", hover_color="#27ae60",
            command=self.toggle_camera
        )
        self.btn_start.grid(row=1, column=0, padx=15, pady=(5, 15), sticky="ew")

        # === RIGHT PANEL: Live Status & Demo Checklist ===
        right_panel = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=12)
        right_panel.grid(row=1, column=1, padx=(10, 20), pady=(0, 20), sticky="nswe")
        right_panel.grid_columnconfigure(0, weight=1)

        # Badge Trạng thái
        self.status_badge = ctk.CTkLabel(
            right_panel,
            text="CHỜ KÍCH HOẠT",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40, fg_color="#333333", corner_radius=8, text_color="#ffffff"
        )
        self.status_badge.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="ew")

        # Checklist & Interactive Demo Controls
        self.items_frame = ctk.CTkFrame(right_panel, fg_color="#1a1a2e", corner_radius=8)
        self.items_frame.grid(row=1, column=0, padx=15, pady=5, sticky="ew")
        self.items_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.items_frame, text="Trang bị bảo hộ (AI Auto + Demo):",
            font=ctk.CTkFont(size=13, weight="bold"), text_color="#aaa"
        ).grid(row=0, column=0, padx=10, pady=(8, 4), sticky="w")

        self.item_checkboxes = {}
        self.item_vars = {}

        for idx, (key, info) in enumerate(REQUIRED_PPE_ITEMS.items(), 1):
            var = ctk.BooleanVar(value=True)  # Mặc định checked cho demo mượt
            cb = ctk.CTkCheckBox(
                self.items_frame,
                text=f"{info['name']}",
                variable=var,
                font=ctk.CTkFont(size=13),
                text_color="#2ecc71",
                fg_color="#2ecc71",
                hover_color="#27ae60"
            )
            cb.grid(row=idx, column=0, padx=15, pady=3, sticky="w")
            self.item_checkboxes[key] = cb
            self.item_vars[key] = var

        # Title danh sách vi phạm hôm nay
        self.log_title = ctk.CTkLabel(
            right_panel,
            text="🚨 Nhật ký vi phạm mới nhất:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#e94560"
        )
        self.log_title.grid(row=2, column=0, padx=15, pady=(15, 5), sticky="w")

        self.log_box = ctk.CTkTextbox(
            right_panel, fg_color="#1a1a2e",
            font=ctk.CTkFont(size=12), state="disabled"
        )
        self.log_box.grid(row=3, column=0, padx=15, pady=(0, 15), sticky="nswe")
        right_panel.grid_rowconfigure(3, weight=1)

        self.refresh_log_box()

    def toggle_camera(self):
        if self.camera_running:
            self.stop_camera()
        else:
            self.start_camera()

    def start_camera(self):
        from core.camera import Camera

        if self.camera:
            self.camera.stop()
            self.camera = None

        self.camera = Camera()
        if self.camera.start():
            self.camera_running = True
            self.btn_start.configure(
                text="⏹️  Dừng Giám Sát",
                fg_color="#e94560", hover_color="#c81e45"
            )
            self.update_camera()
        else:
            messagebox.showerror("Lỗi", "Không thể mở camera!")

    def stop_camera(self):
        self.camera_running = False
        if self.camera:
            self.camera.stop()
            self.camera = None
        self.btn_start.configure(
            text="▶️  Bắt Đầu Giám Sát",
            fg_color="#2ecc71", hover_color="#27ae60"
        )
        self.status_badge.configure(
            text="ĐÃ DỪNG", fg_color="#333333", text_color="#ffffff"
        )
        self.camera_label.configure(
            image=None,
            text="📷 Nhấn 'Bắt Đầu Giám Sát' để mở camera"
        )

    def update_camera(self):
        if not self.camera_running or self.camera is None:
            return

        ret, frame = self.camera.read_frame()
        if not ret:
            self.after(30, self.update_camera)
            return

        # 1. Run YOLOv8 detection
        detections = self.detector.detect(frame)

        # 2. Evaluate PPE compliance & overlay
        annotated_frame, summary = self.evaluator.evaluate_frame(frame, detections)

        detected_names = set(summary['detected_ppe'])
        missing_names = set(summary['missing_ppe'])

        # Cập nhật Checkbox theo Auto AI
        for key, info in REQUIRED_PPE_ITEMS.items():
            name = info['name']
            var = self.item_vars[key]
            cb = self.item_checkboxes[key]

            # Gán chính xác theo kết quả nhận diện AI (True nếu có, False nếu không có)
            is_present = (name in detected_names)
            var.set(is_present)

            # Cập nhật màu Checkbox UI
            if is_present:
                cb.configure(text_color="#2ecc71", fg_color="#2ecc71")
            else:
                cb.configure(text_color="#e94560", fg_color="#e94560")

        # Kiểm tra tổng thể các checkbox
        active_missing = [info['name'] for key, info in REQUIRED_PPE_ITEMS.items() if not self.item_vars[key].get()]
        total_items = len(REQUIRED_PPE_ITEMS)
        active_detected = total_items - len(active_missing)
        score = (active_detected / total_items) * 100.0

        is_compliant = (len(active_missing) == 0)

        # Render status badge
        if is_compliant:
            self.status_badge.configure(text=f"✅ AN TOÀN ({score:.0f}%)", fg_color="#2ecc71", text_color="#ffffff")
        else:
            self.status_badge.configure(text=f"⚠️ VI PHẠM BẢO HỘ ({score:.0f}%)", fg_color="#e94560", text_color="#ffffff")

            # Trigger Alarm
            self.alarm_mgr.trigger_alarm()

            # Snapshot log
            now = time.time()
            if now - self.last_snapshot_time > self.snapshot_cooldown:
                self.last_snapshot_time = now
                timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
                snap_filename = f"violation_{timestamp_str}.jpg"
                snap_path = os.path.join(VIOLATIONS_DIR, snap_filename)

                imwrite_utf8(snap_path, annotated_frame)
                self.ppe_dao.log_violation(active_missing, score, snap_filename)
                self.refresh_log_box()

        # 4. Render to CTkLabel safely
        try:
            frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)

            label_w = self.camera_label.winfo_width()
            label_h = self.camera_label.winfo_height()
            if label_w > 10 and label_h > 10:
                img_w, img_h = img.size
                ratio = min(label_w / img_w, label_h / img_h)
                new_size = (int(img_w * ratio), int(img_h * ratio))
                img = img.resize(new_size, Image.NEAREST)
            else:
                img = img.resize((640, 480), Image.NEAREST)

            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            self.camera_label.configure(image=ctk_img, text="")
            self.photo_image = ctk_img
        except Exception as e:
            print(f"Frame render warning: {e}")

        if self.camera_running:
            self.after(30, self.update_camera)

    def refresh_log_box(self):
        """Cập nhật nhật ký vi phạm hôm nay."""
        records = self.ppe_dao.get_violations_today()
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")

        if records:
            for r in records[:15]:  # Top 15 mới nhất
                self.log_box.insert(
                    "end",
                    f"⚠️ [{r['time']}] Thiếu: {r['missing_items']} ({r['compliance_score']}%)\n"
                )
        else:
            self.log_box.insert("end", "Chưa có vi phạm nào hôm nay.")

        self.log_box.configure(state="disabled")
