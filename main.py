"""
Hệ Thống Giám Sát Đồ Bảo Hộ Lao Động (PPE Detection System)
============================================================
Sử dụng YOLOv8 + OpenCV + CustomTkinter + SQLite

Cách chạy:
    python main.py
"""

import sys
import os

# Tắt warning log không cần thiết của OpenCV trên Windows
os.environ["OPENCV_LOG_LEVEL"] = "OFF"

# Thêm thư mục gốc vào Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from database.ppe_dao import PPEDAO
from core.detector import PPEDetector
from core.evaluator import PPEEvaluator
from core.alarm import AlarmManager
from ui.app import App


def main():
    """Hàm chính — Khởi chạy ứng dụng."""

    print("=" * 55)
    print("  HỆ THỐNG GIÁM SÁT ĐỒ BẢO HỘ LAO ĐỘNG (PPE SYSTEM)")
    print("  Xử lý ảnh & Thị giác máy tính - YOLOv8 + OpenCV")
    print("=" * 55)

    # 1. Khởi tạo Database
    print("\n[1/4] Khởi tạo Database SQLite...")
    db_manager = DatabaseManager()
    ppe_dao = PPEDAO(db_manager)
    print("  ✓ Database sẵn sàng")

    # 2. Khởi tạo YOLOv8 Detector
    print("[2/4] Khởi tạo mô hình YOLOv8 Detector...")
    detector = PPEDetector()

    # 3. Khởi tạo Evaluator & Alarm Manager
    print("[3/4] Khởi tạo Bộ đánh giá tuân thủ & Quản lý cảnh báo...")
    evaluator = PPEEvaluator()
    alarm_mgr = AlarmManager()
    print("  ✓ Core Processing Engine sẵn sàng")

    # 4. Khởi chạy Giao diện UI
    print("[4/4] Khởi chạy giao diện CustomTkinter...\n")
    app = App(db_manager, detector, evaluator, alarm_mgr, ppe_dao)
    app.mainloop()

    print("\nĐã đóng ứng dụng Giám sát Bảo hộ Lao động. Tạm biệt!")


if __name__ == "__main__":
    main()
