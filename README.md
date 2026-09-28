# KTTC_FC Label Tool

Công cụ hỗ trợ duyệt video từng frame chính xác, cắt video và chụp/trích xuất ảnh minh họa 3 mốc chuẩn hóa (**Start - Keyframe - End**) cho bài toán Action Segmentation / Nhận diện thao tác Kỹ thuật Thi công (KTTC) Fast Connector (FC).

---

## 📌 Tính Năng Chính

1. **Công cụ Web Gán Nhãn & Cắt Video (`tools/video_labeler`):**
   - Giao diện web trực quan, timeline đa luồng (multi-track canvas), zoom mượt mà.
   - Hỗ trợ gán 3 điểm: **Start (S)**, **Key_Time (K)**, **End (E)** kèm gợi ý hành vi trực tiếp cho từng bước.
   - Sổ tay quy chuẩn tương tác động: hiển thị ảnh mẫu thực tế, dụng cụ, tiêu chuẩn đạt, lưu ý chống nhầm.
   - Tự động kiểm tra tính hợp lệ của mốc (S < Key < E) và xuất nhãn JSON / cắt video bằng FFmpeg.

2. **Công cụ Chụp & Đánh Dấu Mốc (`capture_tool.py`):**
   - Duyệt video chính xác theo từng frame (Next / Prev / Jump frame).
   - Đánh dấu 3 mốc chuẩn hóa: **S (Start)**, **Key (Keyframe)**, **E (End)** cho từng bước thi công từ **B1 đến B9**.
   - Xem trước thumbnail trực quan các mốc đã chụp.
   - Tự động xuất ảnh chất lượng cao vào thư mục `img/` hoặc `captured_images/`.
   - Xuất file cấu hình mốc `keyframes_metadata.json`.

3. **Công cụ Cắt Video Desktop (`catvideo.py`):**
   - Đánh dấu đoạn video, cắt và gán nhãn từng phân đoạn thao tác bằng giao diện Tkinter.

4. **Tài Liệu Chuẩn Hóa Đi Kèm:**
   - [`QUY_CHUAN_GAN_NHAN_KTTC_FC.html`](QUY_CHUAN_GAN_NHAN_KTTC_FC.html): Sổ tay hướng dẫn gán nhãn nhanh kèm ảnh minh họa trực quan 3 mốc.
   - [`hien_trang_va_dinh_huong_data.html`](hien_trang_va_dinh_huong_data.html): Báo cáo hiện trạng và định hướng chuẩn hóa bộ dữ liệu.
   - [`note_S_M_E.md`](note_S_M_E.md): Ghi chú định nghĩa các mốc bắt đầu, kết thúc và keyframe cho 10 bước thi công.

---

## 🛠️ Cài Đặt

Yêu cầu môi trường Python 3.8+ (khuyên dùng Python 3.10 - 3.12).

1. Cài đặt các thư viện phụ thuộc:
```bash
pip install -r requirements.txt
```

---

## 🚀 Hướng Dẫn Sử Dụng

### 1. Khởi chạy Web Video Labeler (Khuyên dùng)
- Trên Windows: Nhấp đúp vào file [`CHAY_LABELER_DESKTOP.bat`](CHAY_LABELER_DESKTOP.bat)
- Hoặc chạy qua terminal:
```bash
python -m tools.video_labeler.launcher
```

### 2. Khởi chạy công cụ Capture Tool
- Trên Windows: Nhấp đúp vào file [`run_capture_tool.bat`](run_capture_tool.bat)
- Hoặc chạy qua terminal:
```bash
python capture_tool.py
```

### 3. Khởi chạy công cụ Cắt Video (Desktop GUI)
```bash
python catvideo.py
```

---

## 📁 Cấu Trúc Thư Mục

```text
├── tools/video_labeler/            # Web Video Labeler & Slicer hiện đại
├── CHAY_LABELER_DESKTOP.bat        # Script chạy nhanh Web Video Labeler trên Windows
├── capture_tool.py                 # Tool chụp và gán mốc S-Key-E
├── catvideo.py                     # Tool cắt và gán nhãn video
├── run_capture_tool.bat            # Script chạy nhanh Capture Tool trên Windows
├── requirements.txt                # Thư viện phụ thuộc (Flask, OpenCV, Pillow, FFmpeg)
├── QUY_CHUAN_GAN_NHAN_KTTC_FC.html # Sổ tay quy chuẩn gán nhãn HTML
├── hien_trang_va_dinh_huong_data.html # Báo cáo hiện trạng dữ liệu
├── note_S_M_E.md                   # Ghi chú định nghĩa các mốc
├── img/                            # Ảnh minh họa mẫu các bước B1 - B9
├── captured_images/                # Thư mục lưu trữ ảnh chụp trích xuất
├── LICENSE                         # Giấy phép Apache 2.0
└── .gitignore                      # Cấu hình bỏ qua môi trường ảo và cache
```

---

## 📄 License
Dự án được phát hành theo giấy phép [Apache License 2.0](LICENSE).
