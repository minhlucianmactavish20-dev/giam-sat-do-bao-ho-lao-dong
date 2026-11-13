import customtkinter as ctk
from ui.monitor_frame import MonitorFrame
from ui.report_frame import ReportFrame
from config import APP_TITLE, APP_WIDTH, APP_HEIGHT


class App(ctk.CTk):

    def __init__(self, db_manager, detector, evaluator, alarm_mgr, ppe_dao):
        super().__init__()

        self.db_manager = db_manager
        self.detector = detector
        self.evaluator = evaluator
        self.alarm_mgr = alarm_mgr
        self.ppe_dao = ppe_dao

        self.title(APP_TITLE)
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.minsize(1100, 680)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color="#0d1117")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="#161b22")
        self.sidebar.grid(row=0, column=0, sticky="nswe")
        self.sidebar.grid_rowconfigure(6, weight=1)

        self.brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.brand_frame.grid(row=0, column=0, padx=20, pady=(25, 15), sticky="w")

        self.logo_label = ctk.CTkLabel(
            self.brand_frame,
            text="🛡️ PPE SAFETY AI",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#0ea5e9"
        )
        self.logo_label.pack(anchor="w")

        self.sub_label = ctk.CTkLabel(
            self.brand_frame,
            text="HỆ THỐNG GIÁM SÁT AN TOÀN",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#8b949e"
        )
        self.sub_label.pack(anchor="w", pady=(2, 0))

        # Separator line
        self.separator = ctk.CTkFrame(self.sidebar, height=1, fg_color="#30363d")
        self.separator.grid(row=1, column=0, sticky="ew", padx=16, pady=5)

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
                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                height=44,
                corner_radius=8,
                fg_color="transparent",
                text_color="#c9d1d9",
                hover_color="#21262d",
                anchor="w",
                command=lambda n=name: self.show_frame(n)
            )
            btn.grid(row=i + 2, column=0, padx=16, pady=5, sticky="ew")
            self.nav_buttons.append((name, btn))

        self.models_card = ctk.CTkFrame(self.sidebar, fg_color="#21262d", corner_radius=10, border_width=1, border_color="#30363d")
        self.models_card.grid(row=4, column=0, padx=16, pady=(25, 10), sticky="ew")

        ctk.CTkLabel(
            self.models_card,
            text="🤖 AI ENSEMBLE PIPELINE",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#00adb5"
        ).pack(anchor="w", padx=12, pady=(10, 6))

        specialists = [
            ("🦺 Áo & Người", "best.pt"),
            ("🪖 Mũ bảo hộ", "hardhat_keremberke"),
            ("😷 Khẩu trang", "mask_nma"),
        ]
        for name, file_tag in specialists:
            row = ctk.CTkFrame(self.models_card, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=3)
            ctk.CTkLabel(
                row,
                text=f"🟢 {name}",
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color="#e6edf3"
            ).pack(side="left")
            ctk.CTkLabel(
                row,
                text="ACTIVE",
                font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
                text_color="#10b981",
                fg_color="#13231b",
                corner_radius=4,
                padx=6,
                pady=1
            ).pack(side="right")

        self.bottom_card = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.bottom_card.grid(row=7, column=0, padx=20, pady=(10, 20), sticky="s")

        self.version_label = ctk.CTkLabel(
            self.bottom_card,
            text="v2.0 • Ultra-Precision Pipeline\nTrạng thái: 🟢 Trực tuyến",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#8b949e",
            justify="center"
        )
        self.version_label.pack()

        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="#0d1117")
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
        if self.current_frame == "monitor" and name != "monitor":
            self.frames["monitor"].stop_camera()

        for btn_name, btn in self.nav_buttons:
            if btn_name == name:
                btn.configure(
                    fg_color="#0ea5e9",
                    text_color="#ffffff",
                    hover_color="#0284c7"
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color="#c9d1d9",
                    hover_color="#21262d"
                )

        self.frames[name].tkraise()
        self.current_frame = name

        if name == "report":
            self.frames["report"].refresh_data()

    def on_closing(self):
        for frame in self.frames.values():
            if hasattr(frame, 'stop_camera'):
                frame.stop_camera()
        self.destroy()

