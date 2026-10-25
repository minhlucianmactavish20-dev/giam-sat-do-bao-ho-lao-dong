import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import cv2
import os
import time
from datetime import datetime
import threading
from config import VIOLATIONS_DIR, REQUIRED_PPE_ITEMS, ENABLE_VIOLATION_SNAPSHOT
from utils.helpers import imwrite_utf8


class MonitorFrame(ctk.CTkFrame):
    """Màn hình giám sát đồ bảo hộ lao động thời gian thực (Modern Industrial AI Dashboard)."""

    def __init__(self, parent, detector, evaluator, alarm_mgr, ppe_dao):
        super().__init__(parent, fg_color="#0d1117")

        self.detector = detector
        self.evaluator = evaluator
        self.alarm_mgr = alarm_mgr
        self.ppe_dao = ppe_dao

        self.camera = None
        self.camera_running = False
        self.photo_image = None
        self.last_snapshot_time = 0
        self.snapshot_cooldown = 4.0  # seconds between snapshot saves

        # Khóa cố định cột bên phải (350px) để không bao giờ bị video đè hoặc co bóp
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0, minsize=350)
        self.grid_rowconfigure(1, weight=1)

        # === HEADER BAR ===
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, pady=(15, 10), padx=20, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        self.header_title = ctk.CTkLabel(
            header_frame,
            text="🎥 GIÁM SÁT AN TOÀN REAL-TIME",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#f0f6fc"
        )
        self.header_title.grid(row=0, column=0, sticky="w")

        self.live_badge = ctk.CTkLabel(
            header_frame,
            text="● HỆ THỐNG SẴN SÀNG",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#8b949e",
            fg_color="#21262d",
            corner_radius=6,
            padx=10,
            pady=4
        )
        self.live_badge.grid(row=0, column=1, sticky="e")

        # === LEFT PANEL: Camera / Video Feed ===
        left_panel = ctk.CTkFrame(
            self,
            fg_color="#161b22",
            corner_radius=12,
            border_width=1,
            border_color="#30363d"
        )
        left_panel.grid(row=1, column=0, padx=(20, 10), pady=(0, 20), sticky="nswe")
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(0, weight=1)

        self.camera_label = ctk.CTkLabel(
            left_panel,
            text="📹 SẴN SÀNG GIÁM SÁT\n\nNhấn 'Mở Webcam' hoặc 'Tải Video / Ảnh' để bắt đầu",
            font=ctk.CTkFont(family="Segoe UI", size=15),
            text_color="#8b949e",
            fg_color="#0d1117",
            corner_radius=10
        )
        self.camera_label.grid(row=0, column=0, padx=15, pady=15, sticky="nswe")

        # Thanh nút điều khiển (Webcam + Tải lên Video)
        btn_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        btn_frame.grid(row=1, column=0, padx=15, pady=(5, 15), sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        self.btn_camera = ctk.CTkButton(
            btn_frame,
            text="📷  Mở Webcam",
            height=44,
            corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color="#10b981",
            hover_color="#059669",
            command=self.start_camera
        )
        self.btn_camera.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        self.btn_upload = ctk.CTkButton(
            btn_frame,
            text="📁  Tải Video / Ảnh Test",
            height=44,
            corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color="#0ea5e9",
            hover_color="#0284c7",
            command=self.select_media
        )
        self.btn_upload.grid(row=0, column=1, padx=(8, 0), sticky="ew")

        # === RIGHT PANEL: Live Status, Meter & Checklist ===
        right_panel = ctk.CTkFrame(
            self,
            fg_color="#161b22",
            corner_radius=12,
            border_width=1,
            border_color="#30363d",
            width=350
        )
        right_panel.grid(row=1, column=1, padx=(10, 20), pady=(0, 20), sticky="nswe")
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_propagate(False)

        # 1. LIVE COMPLIANCE METER CARD (Thanh đồng hồ tuân thủ trực quan)
        self.meter_card = ctk.CTkFrame(
            right_panel,
            fg_color="#21262d",
            corner_radius=10,
            border_width=1,
            border_color="#30363d"
        )
        self.meter_card.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="ew")
        self.meter_card.grid_columnconfigure(0, weight=1)

        top_meter_row = ctk.CTkFrame(self.meter_card, fg_color="transparent")
        top_meter_row.pack(fill="x", padx=12, pady=(10, 0))

        ctk.CTkLabel(
            top_meter_row,
            text="TỶ LỆ TUÂN THỦ (PPE SCORE)",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#8b949e"
        ).pack(side="left")

        self.score_label = ctk.CTkLabel(
            top_meter_row,
            text="100%",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color="#10b981"
        )
        self.score_label.pack(side="right")

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self.meter_card,
            height=10,
            corner_radius=5,
            fg_color="#30363d",
            progress_color="#10b981"
        )
        self.progress_bar.set(1.0)
        self.progress_bar.pack(fill="x", padx=12, pady=(6, 10))

        # Status Badge Pill
        self.status_badge = ctk.CTkLabel(
            self.meter_card,
            text="CHỜ KÍCH HOẠT",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=34,
            fg_color="#30363d",
            corner_radius=6,
            text_color="#ffffff"
        )
        self.status_badge.pack(fill="x", padx=12, pady=(0, 12))

        # 2. CHECKLIST TRANG BỊ BẢO HỘ THEO DÕI
        self.items_frame = ctk.CTkFrame(
            right_panel,
            fg_color="#21262d",
            corner_radius=10,
            border_width=1,
            border_color="#30363d"
        )
        self.items_frame.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="ew")
        self.items_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.items_frame,
            text="TRANG BỊ GIÁM SÁT (AI SPECIALIST)",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#8b949e"
        ).pack(anchor="w", padx=12, pady=(10, 6))

        self.item_status_labels = {}
        self.item_status_pills = {}

        item_icons = {
            'helmet': '🪖',
            'vest': '🦺',
            'mask': '😷'
        }

        for key, info in REQUIRED_PPE_ITEMS.items():
            row = ctk.CTkFrame(self.items_frame, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=3)

            icon = item_icons.get(key, '🛡️')
            name_lbl = ctk.CTkLabel(
                row,
                text=f"{icon} {info['name']}",
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color="#e6edf3"
            )
            name_lbl.pack(side="left")

            pill = ctk.CTkLabel(
                row,
                text="CHƯA XÁC NHẬN",
                font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                text_color="#8b949e",
                fg_color="#161b22",
                corner_radius=5,
                padx=8,
                pady=2
            )
            pill.pack(side="right")

            self.item_status_labels[key] = name_lbl
            self.item_status_pills[key] = pill

        ctk.CTkFrame(self.items_frame, height=8, fg_color="transparent").pack()

        # 3. NHẬT KÝ VI PHẠM DẠNG CARDS (Scrollable)
        log_header_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        log_header_frame.grid(row=2, column=0, padx=15, pady=(5, 4), sticky="ew")

        ctk.CTkLabel(
            log_header_frame,
            text="🚨 NHẬT KÝ VI PHẠM HÔM NAY",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#f87171"
        ).pack(side="left")

        def _open_violations_dir():
            try:
                os.makedirs(VIOLATIONS_DIR, exist_ok=True)
                os.startfile(VIOLATIONS_DIR)
            except Exception as e:
                print(f"Lỗi mở thư mục vi phạm: {e}")

        ctk.CTkButton(
            log_header_frame,
            text="📁 Mở ảnh",
            width=65,
            height=22,
            corner_radius=4,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            fg_color="#21262d",
            hover_color="#30363d",
            command=_open_violations_dir
        ).pack(side="right")

        # Scrollable container for violation cards
        self.log_scroll = ctk.CTkScrollableFrame(
            right_panel,
            fg_color="#0d1117",
            corner_radius=8,
            border_width=1,
            border_color="#30363d"
        )
        self.log_scroll.grid(row=3, column=0, padx=15, pady=(0, 15), sticky="nswe")
        right_panel.grid_rowconfigure(3, weight=1)

        self.refresh_log_box()

    def select_media(self):
        """Mở hộp thoại chọn file video hoặc file ảnh từ máy tính để kiểm thử."""
        file_path = filedialog.askopenfilename(
            title="Chọn file Video hoặc Ảnh để kiểm thử hệ thống PPE",
            filetypes=[
                ("Tất cả tệp Video & Ảnh", "*.mp4 *.avi *.mov *.mkv *.wmv *.webm *.jpg *.jpeg *.png *.webp *.bmp"),
                ("Tệp Video", "*.mp4 *.avi *.mov *.mkv *.wmv *.webm"),
                ("Tệp Hình ảnh", "*.jpg *.jpeg *.png *.webp *.bmp"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.start_source(source_path=file_path)

    def start_camera(self):
        """Bật webcam."""
        self.start_source(source_path=None)

    def start_source(self, source_path=None):
        """Khởi động nguồn phát (Webcam, Video file hoặc File ảnh)."""
        from core.camera import Camera

        self.stop_source()

        self.camera = Camera(source=source_path, loop=True)
        if self.camera.start():
            self.camera_running = True
            self.camera_label.configure(text=" ")

            if source_path:
                filename = os.path.basename(source_path)
                display_name = filename if len(filename) <= 16 else filename[:13] + "..."
                is_img = getattr(self.camera, 'is_image', False)

                self.btn_camera.configure(state="disabled")
                stop_text = "⏹️  Dừng Xem Ảnh" if is_img else "⏹️  Dừng Video"
                badge_title = f"🖼️ ẢNH: {display_name}" if is_img else f"🎬 VIDEO: {display_name}"

                self.btn_upload.configure(
                    text=stop_text,
                    fg_color="#ef4444",
                    hover_color="#dc2626",
                    command=self.stop_source
                )
                self.status_badge.configure(
                    text=badge_title,
                    fg_color="#0284c7",
                    text_color="#ffffff"
                )
                self.live_badge.configure(
                    text=f"● PHÁT FILE: {display_name.upper()}",
                    text_color="#38bdf8",
                    fg_color="#0c2d48"
                )
            else:
                self.btn_upload.configure(state="disabled")
                self.btn_camera.configure(
                    text="⏹️  Dừng Webcam",
                    fg_color="#ef4444",
                    hover_color="#dc2626",
                    command=self.stop_source
                )
                self.status_badge.configure(
                    text="📷 WEBCAM TRỰC TIẾP",
                    fg_color="#059669",
                    text_color="#ffffff"
                )
                self.live_badge.configure(
                    text="● LIVE WEBCAM",
                    text_color="#10b981",
                    fg_color="#13231b"
                )

            self.update_camera()
        else:
            msg = "Không thể mở file này!" if source_path else "Không thể mở webcam!"
            messagebox.showerror("Lỗi", msg)

    def stop_source(self):
        """Dừng nguồn phát (Webcam, Video hoặc Ảnh)."""
        self.camera_running = False
        if self.camera:
            self.camera.stop()
            self.camera = None

        self.btn_camera.configure(
            state="normal",
            text="📷  Mở Webcam",
            fg_color="#10b981",
            hover_color="#059669",
            command=self.start_camera
        )
        self.btn_upload.configure(
            state="normal",
            text="📁  Tải Video / Ảnh Test",
            fg_color="#0ea5e9",
            hover_color="#0284c7",
            command=self.select_media
        )
        self.status_badge.configure(
            text="ĐÃ DỪNG",
            fg_color="#30363d",
            text_color="#8b949e"
        )
        self.live_badge.configure(
            text="● HỆ THỐNG SẴN SÀNG",
            text_color="#8b949e",
            fg_color="#21262d"
        )

        # Làm sạch hoàn toàn khung hình (xóa triệt để ảnh Tkinter đang hiển thị)
        self.photo_image = None
        self.camera_label.configure(
            text="📹 SẴN SÀNG GIÁM SÁT\n\nNhấn 'Mở Webcam' hoặc 'Tải Video / Ảnh' để bắt đầu"
        )
        if hasattr(self.camera_label, '_label'):
            self.camera_label._label.configure(image="")

        # Đưa đồng hồ tuân thủ về trạng thái ban đầu
        self.score_label.configure(text="--%", text_color="#8b949e")
        self.progress_bar.set(0.0)
        self.progress_bar.configure(progress_color="#30363d")

        for key in REQUIRED_PPE_ITEMS.keys():
            if key in self.item_status_pills:
                self.item_status_pills[key].configure(
                    text="CHỜ TÍN HIỆU",
                    text_color="#8b949e",
                    fg_color="#161b22"
                )

    def stop_camera(self):
        """Tương thích với app.py khi chuyển tab hoặc đóng cửa sổ."""
        self.stop_source()

    def update_camera(self):
        if not self.camera_running or self.camera is None:
            return

        ret, frame = self.camera.read_frame()
        if not ret:
            if self.camera_running:
                self.after(30, self.update_camera)
            return

        # 1. Run YOLOv8 Multi-Head detection
        detections = self.detector.detect(frame)

        # 2. Evaluate PPE compliance & overlay
        annotated_frame, summary = self.evaluator.evaluate_frame(frame, detections)

        detected_names = set(summary['detected_ppe'])
        missing_names = set(summary['missing_ppe'])
        person_detected = summary.get('person_detected', False)

        # Cập nhật Checklist Items
        for key, info in REQUIRED_PPE_ITEMS.items():
            name = info['name']
            pill = self.item_status_pills.get(key)
            if pill:
                if not person_detected:
                    pill.configure(text="KHÔNG NGƯỜI", text_color="#8b949e", fg_color="#161b22")
                elif name in detected_names:
                    pill.configure(text="✔ ĐẠT CHUẨN", text_color="#10b981", fg_color="#13231b")
                else:
                    pill.configure(text="✖ THIẾU", text_color="#ef4444", fg_color="#2a1719")

        # Tính toán mức độ tuân thủ
        total_items = len(REQUIRED_PPE_ITEMS)
        missing_count = len(missing_names)
        detected_count = total_items - missing_count
        score = (detected_count / total_items) * 100.0 if total_items > 0 else 100.0
        is_compliant = (missing_count == 0)

        # Cập nhật Compliance Meter & Progress Bar
        self.score_label.configure(text=f"{score:.0f}%")
        self.progress_bar.set(score / 100.0)

        if not person_detected:
            self.score_label.configure(text_color="#8b949e")
            self.progress_bar.configure(progress_color="#8b949e")
            self.status_badge.configure(
                text="ℹ️ KHÔNG CÓ NGƯỜI",
                fg_color="#21262d",
                text_color="#8b949e"
            )
        elif is_compliant:
            self.score_label.configure(text_color="#10b981")
            self.progress_bar.configure(progress_color="#10b981")
            self.status_badge.configure(
                text="✅ TUÂN THỦ AN TOÀN 100%",
                fg_color="#13231b",
                text_color="#10b981"
            )
        else:
            self.score_label.configure(text_color="#ef4444")
            self.progress_bar.configure(progress_color="#ef4444")
            self.status_badge.configure(
                text=f"⚠️ VI PHẠM BẢO HỘ ({score:.0f}%)",
                fg_color="#2a1719",
                text_color="#f87171"
            )

            # Trigger Alarm
            self.alarm_mgr.trigger_alarm()

            # Lưu vi phạm nếu bật tính năng snapshot (lưu bất đồng bộ để tránh giật lag camera)
            if ENABLE_VIOLATION_SNAPSHOT:
                now = time.time()
                if now - self.last_snapshot_time > self.snapshot_cooldown:
                    self.last_snapshot_time = now
                    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
                    snap_filename = f"violation_{timestamp_str}.jpg"
                    snap_path = os.path.join(VIOLATIONS_DIR, snap_filename)

                    frame_copy = annotated_frame.copy()
                    missing_copy = list(missing_names)
                    score_copy = score

                    def _async_save():
                        try:
                            imwrite_utf8(snap_path, frame_copy)
                            self.ppe_dao.log_violation(missing_copy, score_copy, snap_filename)
                            self.after(0, self.refresh_log_box)
                        except Exception as e:
                            print(f"Lỗi lưu ảnh bằng chứng vi phạm: {e}")

                    threading.Thread(target=_async_save, daemon=True).start()

        # 4. Hiển thị khung hình lên giao diện (vừa khít, không bao giờ tràn layout)
        try:
            frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)

            # Tính toán kích thước tối đa dựa trên kích thước cửa sổ MonitorFrame
            frame_w = self.winfo_width()
            frame_h = self.winfo_height()

            # Trừ thanh sidebar bên phải (350px) và khoảng cách padding
            avail_w = frame_w - 350 - 60 if frame_w > 500 else 640
            avail_h = frame_h - 150 if frame_h > 400 else 460

            # Cận giới hạn an toàn để không bao giờ tự động nở rộng làm co cột phải
            max_w = max(460, min(avail_w, 720))
            max_h = max(340, min(avail_h, 480))

            img_w, img_h = img.size
            ratio = min(max_w / img_w, max_h / img_h)
            disp_w = max(1, int(img_w * ratio))
            disp_h = max(1, int(img_h * ratio))

            img_resized = img.resize((disp_w, disp_h), Image.BILINEAR)

            ctk_img = ctk.CTkImage(light_image=img_resized, dark_image=img_resized, size=(disp_w, disp_h))
            self.camera_label.configure(image=ctk_img, text=" ")
            self.photo_image = ctk_img
        except Exception as e:
            print(f"Frame render warning: {e}")

        if self.camera_running:
            self.after(30, self.update_camera)

    def refresh_log_box(self):
        """Cập nhật nhật ký vi phạm hôm nay thành các thẻ vi phạm (Cards) hiện đại."""
        records = self.ppe_dao.get_violations_today()

        # Xóa các card cũ trong scrollable frame
        for widget in self.log_scroll.winfo_children():
            widget.destroy()

        if records:
            for r in records[:15]:
                card = ctk.CTkFrame(
                    self.log_scroll,
                    fg_color="#161b22",
                    corner_radius=8,
                    border_width=1,
                    border_color="#30363d"
                )
                card.pack(fill="x", padx=4, pady=4)

                top_row = ctk.CTkFrame(card, fg_color="transparent")
                top_row.pack(fill="x", padx=8, pady=(6, 2))

                ctk.CTkLabel(
                    top_row,
                    text=f"⏱️ {r['time']}",
                    font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                    text_color="#c9d1d9"
                ).pack(side="left")

                score_val = r.get('compliance_score', 0)
                ctk.CTkLabel(
                    top_row,
                    text=f"{score_val:.0f}%",
                    font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                    text_color="#f87171",
                    fg_color="#2a1719",
                    corner_radius=4,
                    padx=6,
                    pady=1
                ).pack(side="right")

                ctk.CTkLabel(
                    card,
                    text=f"Thiếu: {r['missing_items']}",
                    font=ctk.CTkFont(family="Segoe UI", size=11),
                    text_color="#f87171",
                    wraplength=290,
                    justify="left"
                ).pack(anchor="w", padx=8, pady=(0, 4))

                snap_name = r.get('snapshot_path', '')
                if snap_name:
                    snap_full_path = os.path.join(VIOLATIONS_DIR, snap_name)
                    if os.path.exists(snap_full_path):
                        def _view_snap(p=snap_full_path):
                            try:
                                os.startfile(p)
                            except Exception as ex:
                                print(f"Không thể mở ảnh {p}: {ex}")

                        ctk.CTkButton(
                            card,
                            text="📷 Xem ảnh vi phạm",
                            height=20,
                            font=ctk.CTkFont(family="Segoe UI", size=10),
                            fg_color="#21262d",
                            hover_color="#30363d",
                            text_color="#38bdf8",
                            command=_view_snap
                        ).pack(anchor="e", padx=8, pady=(0, 6))
        else:
            empty_lbl = ctk.CTkLabel(
                self.log_scroll,
                text="Chưa có ghi nhận vi phạm nào hôm nay.\nKhu vực làm việc an toàn.",
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color="#8b949e",
                justify="center"
            )
            empty_lbl.pack(expand=True, pady=30)
