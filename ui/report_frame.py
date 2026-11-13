import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
from datetime import date
from config import REPORTS_DIR, VIOLATIONS_DIR


class ReportFrame(ctk.CTkFrame):

    def __init__(self, parent, ppe_dao):
        super().__init__(parent, fg_color="#0d1117")

        self.ppe_dao = ppe_dao
        self.show_all_mode = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, pady=(15, 10), padx=20, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header_frame,
            text="📊 BÁO CÁO & LỊCH SỬ VI PHẠM AN TOÀN",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#f0f6fc"
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header_frame,
            text="TRUY XUẤT NHẬT KÝ & THỐNG KÊ TỔNG HỢP",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#8b949e",
            fg_color="#161b22",
            corner_radius=6,
            padx=10,
            pady=4
        ).grid(row=0, column=1, sticky="e")

        # === 1. KPI STATS CARDS (4 Cards trực quan) ===
        self.stats_container = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_container.grid(row=1, column=0, padx=20, pady=(0, 12), sticky="ew")
        self.stats_container.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.kpi_labels = {}
        kpi_configs = [
            ("day_count", "🚨 VI PHẠM TRONG NGÀY", "0", "#ef4444", "Ghi nhận theo ngày lọc"),
            ("total_count", "📂 TỔNG VI PHẠM ALL-TIME", "0", "#0ea5e9", "Toàn bộ cơ sở dữ liệu"),
            ("last_time", "⏱️ LẦN VI PHẠM GẦN NHẤT", "--:--", "#f59e0b", "Thời gian ghi nhận"),
            ("system_status", "🛡️ TRẠNG THÁI PIPELINE", "ONLINE", "#10b981", "3 Model Ensemble Active"),
        ]

        for idx, (key, title, default_val, color, subtitle) in enumerate(kpi_configs):
            card = ctk.CTkFrame(
                self.stats_container,
                fg_color="#161b22",
                corner_radius=10,
                border_width=1,
                border_color="#30363d"
            )
            card.grid(row=0, column=idx, padx=(0 if idx == 0 else 6, 0 if idx == 3 else 6), sticky="ew")

            ctk.CTkLabel(
                card,
                text=title,
                font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                text_color="#8b949e"
            ).pack(anchor="w", padx=14, pady=(10, 2))

            val_lbl = ctk.CTkLabel(
                card,
                text=default_val,
                font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
                text_color=color
            )
            val_lbl.pack(anchor="w", padx=14, pady=0)
            self.kpi_labels[key] = val_lbl

            ctk.CTkLabel(
                card,
                text=subtitle,
                font=ctk.CTkFont(family="Segoe UI", size=9),
                text_color="#6e7681"
            ).pack(anchor="w", padx=14, pady=(0, 10))

        # === 2. FILTER TOOLBAR ===
        filter_frame = ctk.CTkFrame(
            self,
            fg_color="#161b22",
            corner_radius=10,
            border_width=1,
            border_color="#30363d",
            height=55
        )
        filter_frame.grid(row=2, column=0, padx=20, pady=(0, 12), sticky="ew")
        filter_frame.grid_columnconfigure(4, weight=1)

        ctk.CTkLabel(
            filter_frame,
            text="Ngày lọc:",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#c9d1d9"
        ).grid(row=0, column=0, padx=(15, 6), pady=10)

        self.date_var = ctk.StringVar(value=date.today().isoformat())
        self.date_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=self.date_var,
            width=130,
            height=36,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color="#0d1117",
            border_color="#30363d",
            corner_radius=6,
            placeholder_text="YYYY-MM-DD"
        )
        self.date_entry.grid(row=0, column=1, padx=4, pady=10)

        self.btn_filter = ctk.CTkButton(
            filter_frame,
            text="🔍 Xem Nhật Ký",
            width=115,
            height=36,
            corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#0ea5e9",
            hover_color="#0284c7",
            command=self.refresh_data
        )
        self.btn_filter.grid(row=0, column=2, padx=4, pady=10)

        self.btn_today = ctk.CTkButton(
            filter_frame,
            text="Hôm nay",
            width=85,
            height=36,
            corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color="#21262d",
            hover_color="#30363d",
            command=self.show_today
        )
        self.btn_today.grid(row=0, column=3, padx=4, pady=10)

        self.btn_all = ctk.CTkButton(
            filter_frame,
            text="Tất cả",
            width=80,
            height=36,
            corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color="#21262d",
            hover_color="#30363d",
            command=self.show_all
        )
        self.btn_all.grid(row=0, column=4, padx=4, pady=10, sticky="w")

        def _open_violations_folder():
            try:
                os.makedirs(VIOLATIONS_DIR, exist_ok=True)
                os.startfile(VIOLATIONS_DIR)
            except Exception as e:
                print(f"Lỗi mở thư mục violations: {e}")

        self.btn_open_folder = ctk.CTkButton(
            filter_frame,
            text="📁 Thư Mục Ảnh",
            width=120,
            height=36,
            corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color="#21262d",
            hover_color="#30363d",
            command=_open_violations_folder
        )
        self.btn_open_folder.grid(row=0, column=5, padx=4, pady=10)

        self.btn_export = ctk.CTkButton(
            filter_frame,
            text="📥 Xuất Báo Cáo Excel",
            width=160,
            height=36,
            corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#10b981",
            hover_color="#059669",
            command=self.export_excel
        )
        self.btn_export.grid(row=0, column=6, padx=(4, 15), pady=10)

        content_frame = ctk.CTkFrame(
            self,
            fg_color="#161b22",
            corner_radius=10,
            border_width=1,
            border_color="#30363d"
        )
        content_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="nswe")
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        table_hdr = ctk.CTkFrame(content_frame, fg_color="#21262d", height=38, corner_radius=6)
        table_hdr.grid(row=0, column=0, padx=12, pady=(12, 6), sticky="ew")
        table_hdr.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(
            table_hdr, text="STT", width=50,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color="#8b949e"
        ).grid(row=0, column=0, padx=8, pady=8)

        ctk.CTkLabel(
            table_hdr, text="THỜI GIAN", width=120,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color="#8b949e", anchor="w"
        ).grid(row=0, column=1, padx=8, pady=8)

        ctk.CTkLabel(
            table_hdr, text="TRANG BỊ VI PHẠM (THIẾU)",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color="#8b949e", anchor="w"
        ).grid(row=0, column=2, padx=8, pady=8, sticky="w")

        ctk.CTkLabel(
            table_hdr, text="ĐIỂM TUÂN THỦ", width=120,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color="#8b949e"
        ).grid(row=0, column=3, padx=8, pady=8)

        ctk.CTkLabel(
            table_hdr, text="TRẠNG THÁI", width=90,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color="#8b949e"
        ).grid(row=0, column=4, padx=8, pady=8)

        ctk.CTkLabel(
            table_hdr, text="BẰNG CHỨNG", width=110,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color="#8b949e"
        ).grid(row=0, column=5, padx=8, pady=8)

        self.table_scroll = ctk.CTkScrollableFrame(
            content_frame,
            fg_color="#0d1117",
            corner_radius=8,
            border_width=1,
            border_color="#30363d"
        )
        self.table_scroll.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nswe")
        self.table_scroll.grid_columnconfigure(2, weight=1)

        self.refresh_data()

    def show_today(self):
        self.show_all_mode = False
        self.date_var.set(date.today().isoformat())
        self.refresh_data()

    def show_all(self):
        self.show_all_mode = True
        self.refresh_data()

    def refresh_data(self):
        target_date = self.date_var.get().strip()
        if not target_date:
            target_date = date.today().isoformat()

        stats = self.ppe_dao.get_statistics(target_date)
        self.kpi_labels["day_count"].configure(text=str(stats['violations_today']))
        self.kpi_labels["total_count"].configure(text=str(stats['total_violations_all_time']))

        if self.show_all_mode:
            records = self.ppe_dao.get_all_violations()
        else:
            records = self.ppe_dao.get_violations_by_date(target_date)

        if records:
            latest = records[0]
            latest_time = latest.get('time', '')
            self.kpi_labels["last_time"].configure(text=latest_time if latest_time else "Hôm nay")
        else:
            self.kpi_labels["last_time"].configure(text="Chưa có")

        for widget in self.table_scroll.winfo_children():
            widget.destroy()

        if records:
            for i, r in enumerate(records, 1):
                bg_col = "#161b22" if i % 2 == 1 else "#1c2129"
                row_frame = ctk.CTkFrame(
                    self.table_scroll,
                    fg_color=bg_col,
                    corner_radius=6,
                    height=36
                )
                row_frame.pack(fill="x", padx=4, pady=2)
                row_frame.grid_columnconfigure(2, weight=1)

                ctk.CTkLabel(
                    row_frame,
                    text=f"#{i}",
                    width=50,
                    font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                    text_color="#8b949e"
                ).grid(row=0, column=0, padx=8, pady=6)

                time_str = f"{r.get('date', '')} {r.get('time', '')}" if self.show_all_mode else r.get('time', '')
                ctk.CTkLabel(
                    row_frame,
                    text=time_str,
                    width=120,
                    font=ctk.CTkFont(family="Segoe UI", size=11),
                    text_color="#c9d1d9",
                    anchor="w"
                ).grid(row=0, column=1, padx=8, pady=6)

                missing_str = r.get('missing_items', '')
                ctk.CTkLabel(
                    row_frame,
                    text=missing_str,
                    font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                    text_color="#f87171",
                    anchor="w"
                ).grid(row=0, column=2, padx=8, pady=6, sticky="w")

                score = r.get('compliance_score', 0)
                ctk.CTkLabel(
                    row_frame,
                    text=f"{score:.0f}%",
                    width=120,
                    font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                    text_color="#f59e0b" if score > 50 else "#ef4444"
                ).grid(row=0, column=3, padx=8, pady=6)

                status_pill = ctk.CTkLabel(
                    row_frame,
                    text="VI PHẠM",
                    width=90,
                    font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                    text_color="#ef4444",
                    fg_color="#2a1719",
                    corner_radius=4,
                    padx=6,
                    pady=2
                )
                status_pill.grid(row=0, column=4, padx=8, pady=6)

                snap_name = r.get('snapshot_path', '')
                snap_full = os.path.join(VIOLATIONS_DIR, snap_name) if snap_name else ''
                if snap_name and os.path.exists(snap_full):
                    def _view_evidence(p=snap_full):
                        try:
                            os.startfile(p)
                        except Exception as ex:
                            print(f"Lỗi mở ảnh {p}: {ex}")

                    btn_snap = ctk.CTkButton(
                        row_frame,
                        text="📷 Xem ảnh",
                        width=95,
                        height=24,
                        corner_radius=4,
                        font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                        fg_color="#1f2937",
                        hover_color="#374151",
                        text_color="#38bdf8",
                        command=_view_evidence
                    )
                    btn_snap.grid(row=0, column=5, padx=8, pady=6)
                else:
                    ctk.CTkLabel(
                        row_frame,
                        text="—",
                        width=95,
                        font=ctk.CTkFont(family="Segoe UI", size=11),
                        text_color="#6e7681"
                    ).grid(row=0, column=5, padx=8, pady=6)
        else:
            msg = "Không có dữ liệu vi phạm nào trong ngày này." if not self.show_all_mode else "Cơ sở dữ liệu chưa có bản ghi vi phạm nào."
            empty_lbl = ctk.CTkLabel(
                self.table_scroll,
                text=f"📋 {msg}\nKhu vực làm việc duy trì an toàn 100%.",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color="#8b949e",
                justify="center"
            )
            empty_lbl.pack(expand=True, pady=40)

    def export_excel(self):
        try:
            import pandas as pd
        except ImportError:
            messagebox.showerror("Lỗi", "Thiếu thư viện pandas/openpyxl!")
            return

        target_date = self.date_var.get().strip()
        if not target_date:
            target_date = date.today().isoformat()

        if self.show_all_mode:
            records = self.ppe_dao.get_all_violations()
            default_name = f"BaoCao_PPE_All_Time_{date.today().strftime('%Y%m%d')}.xlsx"
        else:
            records = self.ppe_dao.get_violations_by_date(target_date)
            default_name = f"BaoCao_PPE_{target_date}.xlsx"

        if not records:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu để xuất file Excel!")
            return

        save_path = filedialog.asksaveasfilename(
            initialdir=REPORTS_DIR,
            initialfile=default_name,
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
        )

        if not save_path:
            return

        try:
            df = pd.DataFrame(records)
            col_map = {
                'id': 'ID',
                'date': 'Ngày',
                'time': 'Thời Gian',
                'missing_items': 'Trang Bị Thiếu (Vi Phạm)',
                'compliance_score': 'Tỷ Lệ Tuân Thủ (%)',
                'snapshot_path': 'Tên Ảnh Bằng Chứng'
            }
            existing_cols = {k: v for k, v in col_map.items() if k in df.columns}
            df = df.rename(columns=existing_cols)

            df.to_excel(save_path, index=False)
            messagebox.showinfo("Thành công", f"Đã xuất file báo cáo thành công:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất file: {e}")
