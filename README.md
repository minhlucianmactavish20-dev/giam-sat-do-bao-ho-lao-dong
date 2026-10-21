# Hệ Thống Giám Sát Đồ Bảo Hộ Lao Động (PPE Detection System)

Ứng dụng giám sát việc tuân thủ trang bị bảo hộ lao động (Personal Protective Equipment - PPE) theo thời gian thực qua Camera/Webcam sử dụng **Xử lý ảnh & Thị giác máy tính (Computer Vision)** kết hợp **Mô hình Lai (YOLOv8 + OpenCV Cascades & Feature Analysis)**.

---

## 🌟 Tính Năng Nổi Bật

- **Giám sát thời gian thực (Real-time Video Feed)**: Quét liên tục từ camera/webcam với độ trễ thấp trên CPU.
- **Phát hiện 4 loại trang bị bảo hộ chính**:
  - 🪖 Mũ bảo hộ (Hard hat / Helmet)
  - 🥽 Kính bảo hộ / Mắt kính (Safety Glasses / Eyeglasses)
  - 🦺 Áo bảo hộ / Áo phản quang (Safety Vest / Jacket)
  - 😷 Khẩu trang (Medical Mask / Face Mask)
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
- **Deep Learning**: YOLOv8 Nano (`ultralytics`) cho phát hiện đối tượng người và định vị nhanh cơ thể.
- **Computer Vision**: OpenCV (`cv2`) kết hợp Haar Cascade Classifiers, Canny Edge Detection và Phân đoạn màu sắc HSV (Skin/Color masking) cho các trang bị chi tiết.
- **Cơ sở dữ liệu**: SQLite3
- **Thư viện phụ trợ**: Pillow, Pandas, OpenPyXL

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy

### 1. Yêu cầu môi trường
- Đã cài đặt [Python 3.9+](https://www.python.org/downloads/)

### 2. Clone hoặc tải project
```bash
git clone https://github.com/minhlucianmactavish20-dev/giam-sat-do-bao-ho-lao-dong.git
cd "Giám sát đồ bảo hộ lao động - Xử lý ảnh và thị giác máy tính"
```

### 3. Cài đặt các thư viện cần thiết
```bash
pip install -r requirements.txt
```

> **Lưu ý**: Nếu gặp lỗi với OpenCV, cài đặt bản `opencv-contrib-python`:
```bash
pip install opencv-contrib-python
```

### 4. Chạy ứng dụng
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
│   ├── detector.py       # Bộ nhận diện Hybrid PPEDetector (YOLOv8 + OpenCV)
│   ├── evaluator.py      # Đánh giá tỷ lệ tuân thủ & vẽ khung annotated
│   ├── camera.py         # Quản lý luồng Camera/Webcam
│   └── alarm.py          # Xử lý phát âm thanh cảnh báo
├── database/
│   ├── db_manager.py     # Kết nối và khởi tạo SQLite DB
│   └── ppe_dao.py        # Thao tác thêm/đọc dữ liệu vi phạm
├── ui/
│   ├── app.py            # Cửa sổ chính CustomTkinter
│   ├── monitor_frame.py  # Màn hình Giám sát thời gian thực
│   └── report_frame.py   # Màn hình Lịch sử & Báo cáo
├── utils/
│   └── helpers.py        # Các hàm tiện ích hỗ trợ
├── data/                 # Chứa các file Haar Cascade .xml & DB
└── models/               # Chứa trọng số mô hình YOLO (yolov8n.pt)
```

---

## 🎓 Đề Tài Môn Học
- **Môn**: Xử lý ảnh và thị giác máy tính
- **Đề tài**: Xây dựng chương trình giám sát đồ bảo hộ lao động (PPE Safety System)
