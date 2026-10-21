import customtkinter as ctk
from ui.monitor_frame import MonitorFrame
from ui.report_frame import ReportFrame
from config import APP_TITLE, APP_WIDTH, APP_HEIGHT


class App(ctk.CTk):
    """Cửa sổ chính của ứng dụng Giám sát đồ bảo hộ lao động."""

    def __init__(self, db_manager, detector, evaluator, alarm_mgr, ppe_dao):
        super().__init__()

        self.db_manager = db_manager
        self.detector = detector
        self.evaluator = evaluator
        self.alarm_mgr = alarm_mgr
        self.ppe_dao = ppe_dao

        # Cấu hình Window
        self.title(APP_TITLE)
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.minsize(1050, 650)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # === SIDEBAR ===
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#1a1a2e")
        self.sidebar.grid(row=0, column=0, sticky="nswe")
        self.sidebar.grid_rowconfigure(5, weight=1)

        # Logo / Title
        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="🦺 GIÁM SÁT\nBẢO HỘ LAO ĐỘNG",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#e94560"
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 25))

        # Separator
        self.separator = ctk.CTkFrame(self.sidebar, height=2, fg_color="#333333")
        self.separator.grid(row=1, column=0, sticky="ew", padx=15, pady=5)

        # Nav Buttons
        self.nav_buttons = []
        nav_items = [
            ("🎥  Giám Sát Real-Time", "monitor"),
            ("📊  Nhật Ký & Báo Cáo", "report"),
        ]

        for i, (text, name) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                font=ctk.CTkFont(size=15),
                height=45,
                corner_radius=8,
                fg_color="transparent",
                hover_color="#16213e",
                anchor="w",
                command=lambda n=name: self.show_frame(n)
            )
            btn.grid(row=i + 2, column=0, padx=15, pady=6, sticky="ew")
            self.nav_buttons.append((name, btn))

        # Bottom info
        self.version_label = ctk.CTkLabel(
            self.sidebar,
            text="v1.0 — YOLOv8 + OpenCV",
            font=ctk.CTkFont(size=11),
            text_color="#666666"
        )
        self.version_label.grid(row=6, column=0, padx=20, pady=(10, 20))

        # === MAIN CONTAINER ===
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="#0f3460")
        self.main_container.grid(row=0, column=1, sticky="nswe")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        self.frames = {}
        self.frames["monitor"] = MonitorFrame(
            self.main_container, detector, evaluator, alarm_mgr, ppe_dao
        )
        self.frames["report"] = ReportFrame(
            self.main_container, ppe_dao
        )

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nswe")

        self.current_frame = None
        self.show_frame("monitor")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def show_frame(self, name):
        """Chuyển đổi giữa các màn hình."""
        # Stop camera khi rời khỏi tab monitor
        if self.current_frame == "monitor" and name != "monitor":
            self.frames["monitor"].stop_camera()

        for btn_name, btn in self.nav_buttons:
            if btn_name == name:
                btn.configure(fg_color="#e94560", hover_color="#c81e45")
            else:
                btn.configure(fg_color="transparent", hover_color="#16213e")

        self.frames[name].tkraise()
        self.current_frame = name

        if name == "report":
            self.frames["report"].refresh_data()

    def on_closing(self):
        """Đóng ứng dụng an toàn."""
        for frame in self.frames.values():
            if hasattr(frame, 'stop_camera'):
                frame.stop_camera()
        self.destroy()
