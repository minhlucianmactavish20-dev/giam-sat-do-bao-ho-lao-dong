import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
from datetime import date
from config import REPORTS_DIR


class ReportFrame(ctk.CTkFrame):
    """Màn hình lịch sử vi phạm, thống kê & xuất báo cáo Excel."""

    def __init__(self, parent, ppe_dao):
        super().__init__(parent, fg_color="#0f3460")

        self.ppe_dao = ppe_dao

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # === HEADER ===
        header = ctk.CTkLabel(
            self, text="📊 Báo Cáo Nhật Ký Vi Phạm An Toàn Lao Động",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#e94560"
        )
        header.grid(row=0, column=0, pady=(15, 10), padx=20, sticky="w")

        # === FILTER BAR ===
        filter_frame = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=12, height=60)
        filter_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        filter_frame.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(
            filter_frame, text="Ngày:",
            font=ctk.CTkFont(size=14)
        ).grid(row=0, column=0, padx=(15, 5), pady=12)

        self.date_var = ctk.StringVar(value=date.today().isoformat())
        self.date_entry = ctk.CTkEntry(
            filter_frame, textvariable=self.date_var,
            width=140, height=35, font=ctk.CTkFont(size=14),
            placeholder_text="YYYY-MM-DD"
        )
        self.date_entry.grid(row=0, column=1, padx=5, pady=12)

        self.btn_filter = ctk.CTkButton(
            filter_frame, text="🔍 Xem Nhật Ký", width=110, height=35,
            fg_color="#e94560", hover_color="#c81e45",
            command=self.refresh_data
        )
        self.btn_filter.grid(row=0, column=2, padx=5, pady=12)

        self.btn_today = ctk.CTkButton(
            filter_frame, text="Hôm nay", width=90, height=35,
            fg_color="#533483", hover_color="#3d2668",
            command=self.show_today
        )
        self.btn_today.grid(row=0, column=3, padx=5, pady=12, sticky="w")

        self.btn_export = ctk.CTkButton(
            filter_frame, text="📥 Xuất File Excel", width=140, height=35,
            fg_color="#2ecc71", hover_color="#27ae60",
            command=self.export_excel
        )
        self.btn_export.grid(row=0, column=4, padx=(5, 15), pady=12)

        # === CONTENT AREA ===
        content_frame = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=12)
        content_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nswe")
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        # Statistics Summary Bar
        self.stats_frame = ctk.CTkFrame(content_frame, fg_color="#1a1a2e", corner_radius=8)
        self.stats_frame.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="ew")
        self.stats_frame.grid_columnconfigure((0, 1), weight=1)

        self.stat_labels = {}
        stat_items = [
            ("today", "🚨 Số vi phạm ngày xem", "0"),
            ("total", "📂 Tổng vi phạm toàn thời gian", "0"),
        ]
        for i, (key, title, default_val) in enumerate(stat_items):
            frame = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
            frame.grid(row=0, column=i, padx=10, pady=10)
            ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=12), text_color="#aaa").pack()
            lbl = ctk.CTkLabel(frame, text=default_val, font=ctk.CTkFont(size=22, weight="bold"), text_color="#e94560")
            lbl.pack()
            self.stat_labels[key] = lbl

        # Table View
        self.table = ctk.CTkTextbox(
            content_frame, fg_color="#1a1a2e",
            font=ctk.CTkFont(family="Consolas", size=13),
            state="disabled"
        )
        self.table.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nswe")

        self.refresh_data()

    def show_today(self):
        self.date_var.set(date.today().isoformat())
        self.refresh_data()

    def refresh_data(self):
        """Tải dữ liệu thống kê & danh sách vi phạm."""
        target_date = self.date_var.get().strip()
        if not target_date:
            target_date = date.today().isoformat()

        stats = self.ppe_dao.get_statistics(target_date)
        self.stat_labels["today"].configure(text=str(stats['violations_today']))
        self.stat_labels["total"].configure(text=str(stats['total_violations_all_time']))

        records = self.ppe_dao.get_violations_by_date(target_date)

        self.table.configure(state="normal")
        self.table.delete("1.0", "end")

        header = f"{'STT':<6}{'Thời gian':<12}{'Trang bị thiếu (Vi phạm)':<45}{'Điểm tuân thủ':<15}\n"
        separator = "─" * 78 + "\n"
        self.table.insert("end", header)
        self.table.insert("end", separator)

        if records:
            for i, r in enumerate(records, 1):
                time_str = r.get('time', '')
                missing = r.get('missing_items', '')
                score = f"{r.get('compliance_score', 0):.0f}%"
                row = f"{i:<6}{time_str:<12}{missing:<45}{score:<15}\n"
                self.table.insert("end", row)
        else:
            self.table.insert("end", "\n    Không có dữ liệu vi phạm nào trong ngày này.\n")

        self.table.configure(state="disabled")

    def export_excel(self):
        """Xuất danh sách vi phạm ra file Excel."""
        try:
            import pandas as pd
        except ImportError:
            messagebox.showerror("Lỗi", "Thiếu thư viện pandas/openpyxl!")
            return

        target_date = self.date_var.get().strip()
        if not target_date:
            target_date = date.today().isoformat()

        records = self.ppe_dao.get_violations_by_date(target_date)

        if not records:
            messagebox.showwarning("Thông báo", f"Không có dữ liệu vi phạm ngày {target_date} để xuất Excel!")
            return

        rows = []
        for i, r in enumerate(records, 1):
            rows.append({
                'STT': i,
                'Ngày': r.get('date', ''),
                'Giờ vi phạm': r.get('time', ''),
                'Trang bị bảo hộ thiếu': r.get('missing_items', ''),
                'Mức độ tuân thủ (%)': f"{r.get('compliance_score', 0):.0f}%",
                'File ảnh vi phạm': r.get('snapshot_path', '')
            })

        df = pd.DataFrame(rows)

        filename = f"baocao_viphambaoho_{target_date}.xlsx"
        filepath = filedialog.asksaveasfilename(
            initialdir=REPORTS_DIR,
            initialfile=filename,
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )

        if filepath:
            df.to_excel(filepath, index=False, engine='openpyxl')
            messagebox.showinfo("Thành công", f"Đã xuất báo cáo Excel thành công:\n{filepath}")
