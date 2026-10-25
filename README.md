# Hệ Thống Giám Sát Đồ Bảo Hộ Lao Động (PPE Detection System)

Ứng dụng giám sát việc tuân thủ trang bị bảo hộ lao động (Personal Protective Equipment - PPE) theo thời gian thực qua Camera/Webcam sử dụng **Xử lý ảnh & Thị giác máy tính (Computer Vision)** kết hợp **Mô hình Lai (YOLOv8 + OpenCV Cascades & Feature Analysis)**.

---

## 🌟 Tính Năng Nổi Bật

- **Giám sát thời gian thực (Real-time Video Feed)**: Quét liên tục từ camera/webcam với độ trễ thấp trên CPU.
- **Phát hiện 3 loại trang bị bảo hộ cốt lõi (Construction Safety)**:
  - 🪖 Mũ bảo hộ (Hard hat / Helmet / `Hardhat` vs `NO-Hardhat`)
  - 🦺 Áo bảo hộ / Áo phản quang (Safety Vest / Hi-Vis Jacket / `Safety Vest` vs `NO-Safety Vest`)
  - 😷 Khẩu trang (Mask / Face Mask / `Mask` vs `NO-Mask`)
- **Đánh giá mức độ tuân thủ (Compliance Evaluation)**:
  - Hiển thị trực quan khung viền (Bounding Box) phân biệt an toàn (Xanh) và vi phạm (Đỏ/Cam).
  - Banner hiển thị tỷ lệ tuân thủ (%) và danh sách trang bị bị thiếu.
- **Cảnh báo vi phạm (Alarm & Evidence)**:
  - Phát âm thanh cảnh báo (Beep) theo chu kỳ khi phát hiện vi phạm.
  - Tự động chụp lại khung hình vi phạm làm bằng chứng và lưu trữ có hệ thống.
- **Quản lý dữ liệu & Báo cáo (SQLite & Excel Export)**:
  - Ghi nhận lịch sử vi phạm vào SQLite database.
  - Giao diện tra cứu nhật ký và chức năng xuất báo cáo ra file Excel (.xlsx).

---

## 🛠️ Công Nghệ & Mô Hình Ứng Dụng

- **Ngôn ngữ**: Python 3.x
- **Giao diện người dùng**: CustomTkinter (Dark Theme hiện đại)
- **Deep Learning**: YOLOv8 Nano (`ultralytics`) với kiến trúc Multi-Head Specialist Pipeline:
  - `best.pt`: Mô hình nhận diện Áo bảo hộ/phản quang và cơ thể người.
  - `hardhat_keremberke.pt`: Mô hình chuyên sâu Mũ bảo hộ.
  - `mask_nma.pt`: Mô hình chuyên sâu Khẩu trang y tế & N95.
- **Computer Vision**: OpenCV (`cv2`) xử lý luồng video, định vị bounding box và phân tích vi phạm.
- **Cơ sở dữ liệu**: SQLite3 lưu vết nhật ký vi phạm.
- **Thư viện phụ trợ**: Pillow, Pandas, OpenPyXL.

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy

### 1. Yêu cầu môi trường
- Đã cài đặt [Python 3.9+](https://www.python.org/downloads/)

### 2. Cài đặt các thư viện cần thiết
```bash
pip install -r requirements.txt
```

### 3. Chạy ứng dụng
```bash
python main.py
```

---

## 📂 Cấu Trúc Thư Mục

```text
├── config.py             # File cấu hình chung của hệ thống (ngưỡng conf, camera, trang bị)
├── main.py               # Điểm khởi chạy chương trình (Entry point)
├── requirements.txt      # Danh sách thư viện phụ thuộc
├── core/
│   ├── detector.py       # Bộ nhận diện Multi-Head PPEDetector (YOLOv8 Specialist Ensemble)
│   ├── evaluator.py      # Đánh giá tỷ lệ tuân thủ & vẽ khung annotated
│   ├── camera.py         # Quản lý luồng Camera/Webcam/Video/Image
│   └── alarm.py          # Xử lý phát âm thanh cảnh báo vi phạm
├── database/
│   ├── db_manager.py     # Kết nối và khởi tạo SQLite DB
│   └── ppe_dao.py        # Thao tác thêm/đọc dữ liệu vi phạm
├── ui/
│   ├── app.py            # Cửa sổ chính CustomTkinter
│   ├── monitor_frame.py  # Màn hình Giám sát thời gian thực & Upload test media
│   └── report_frame.py   # Màn hình Lịch sử & Xuất báo cáo Excel
├── utils/
│   └── helpers.py        # Các hàm tiện ích hỗ trợ định dạng & xử lý ảnh
├── data/
│   └── ppe_monitoring.db # Cơ sở dữ liệu SQLite lưu vết vi phạm
├── models/               # Bộ trọng số mô hình YOLOv8 Multi-Head Specialist
│   ├── best.pt           # Model Áo phản quang & Người
│   ├── hardhat_keremberke.pt # Model Chuyên sâu Mũ bảo hộ
│   ├── mask_nma.pt       # Model Chuyên sâu Khẩu trang
│   └── yolov8n.pt        # Model YOLOv8 gốc (Fallback)
└── test/                 # Thư mục chứa hình ảnh & video mẫu phục vụ kiểm thử
```

---

## 🎓 Đề Tài Môn Học
- **Môn**: Xử lý ảnh và thị giác máy tính
- **Đề tài**: Xây dựng chương trình giám sát đồ bảo hộ lao động (PPE Safety System)
