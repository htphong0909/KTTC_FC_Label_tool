# KTTC_FC Label Tool

Công cụ hỗ trợ duyệt video từng frame chính xác, cắt video và chụp/trích xuất ảnh minh họa 3 mốc chuẩn hóa (**Start - Keyframe - End**) cho bài toán Action Segmentation / Nhận diện thao tác Kỹ thuật Thi công (KTTC) Fast Connector (FC).

---

## 📌 Tính Năng Chính

1. **Công cụ Web Gán Nhãn & Cắt Video (`tools/video_labeler`):**
   - Giao diện web trực quan, timeline đa luồng (multi-track canvas), zoom mượt mà.
   - Hỗ trợ gán 3 điểm: **Start (S)**, **Key_Time (K)**, **End (E)** kèm gợi ý hành vi trực tiếp cho từng bước.
   - Sổ tay quy chuẩn tương tác động: hiển thị ảnh mẫu thực tế, dụng cụ, tiêu chuẩn đạt, lưu ý chống nhầm.
   - Tự động kiểm tra tính hợp lệ của mốc (S < Key < E) và xuất nhãn JSON / cắt video bằng FFmpeg.

2. **Công cụ Cũ / Bổ Trợ trong thư mục `legacy/`:**
   - **Chụp & Đánh Dấu Mốc (`legacy/capture_tool.py`)**: Duyệt video từng frame, trích xuất bộ 3 ảnh minh họa S-Key-E.
   - **Cắt Video Desktop (`legacy/catvideo.py`)**: Cắt phân đoạn video bằng giao diện Tkinter.

3. **Tài Liệu Quy Chuẩn trong thư mục `docs/`:**
   - [`docs/QUY_CHUAN_GAN_NHAN_KTTC_FC.html`](docs/QUY_CHUAN_GAN_NHAN_KTTC_FC.html): Sổ tay hướng dẫn gán nhãn nhanh kèm ảnh minh họa trực quan 3 mốc.
   - [`docs/QUY_CHUAN_GAN_NHAN_KTTC_FC.pdf`](docs/QUY_CHUAN_GAN_NHAN_KTTC_FC.pdf): Tài liệu xuất bản PDF hoàn chỉnh.
   - [`docs/QUY_CHUAN_GAN_NHAN_KTTC_FC_STANDALONE.html`](docs/QUY_CHUAN_GAN_NHAN_KTTC_FC_STANDALONE.html): File HTML độc lập nhúng ảnh Base64 offline.
   - [`docs/hien_trang_va_dinh_huong_data.html`](docs/hien_trang_va_dinh_huong_data.html): Báo cáo hiện trạng và định hướng chuẩn hóa bộ dữ liệu.
   - [`docs/note_S_M_E.md`](docs/note_S_M_E.md): Ghi chú định nghĩa các mốc bắt đầu, kết thúc và keyframe cho 10 bước thi công.

---

## 🛠️ Cài Đặt

Yêu cầu môi trường Python 3.8+ (khuyên dùng Python 3.10 - 3.12).

1. Cài đặt các thư viện phụ thuộc:
```bash
pip install -r requirements.txt
```

---

## 🚀 Hướng Dẫn Sử Dụng

Thư mục chính được tinh gọn tối đa, chỉ chứa các file thực thi `.bat` để nhấp đúp chạy ngay:

### 1. Khởi chạy Web Video Labeler (Khuyên dùng)
- **Trên Windows**: Nhấp đúp vào file [`CHAY_LABELER_DESKTOP.bat`](CHAY_LABELER_DESKTOP.bat)
- Hoặc chạy qua terminal:
```bash
python -m tools.video_labeler.launcher
```

### 2. Khởi chạy Tool Chụp Ảnh Mốc (Legacy)
- **Trên Windows**: Nhấp đúp vào file [`CHAY_TOOL_CHUP_ANH_CU.bat`](CHAY_TOOL_CHUP_ANH_CU.bat)
- Hoặc chạy qua terminal:
```bash
python legacy/capture_tool.py
```

### 3. Khởi chạy Tool Cắt Video Desktop Tkinter (Legacy)
- **Trên Windows**: Nhấp đúp vào file [`CHAY_TOOL_CAT_VIDEO_CU.bat`](CHAY_TOOL_CAT_VIDEO_CU.bat)
- Hoặc chạy qua terminal:
```bash
python legacy/catvideo.py
```

---

## 📁 Cấu Trúc Thư Mục Tinh Gọn

```text
├── CHAY_LABELER_DESKTOP.bat        # [Chính] Chạy Web Video Labeler trên cổng 5055
├── CHAY_TOOL_CHUP_ANH_CU.bat       # [Phụ] Chạy tool chụp ảnh 3 mốc S-Key-E cũ
├── CHAY_TOOL_CAT_VIDEO_CU.bat      # [Phụ] Chạy tool cắt video Tkinter cũ
├── requirements.txt                # Thư viện phụ thuộc (Flask, OpenCV, Pillow, FFmpeg)
├── README.md                       # Tài liệu hướng dẫn dự án
├── LICENSE                         # Giấy phép Apache 2.0
├── .gitignore                      # Cấu hình loại trừ cache & môi trường ảo
│
├── tools/                          # Bộ công cụ Web Video Labeler & Slicer hiện đại
│   └── video_labeler/              # App Flask, timeline canvas, launcher, guide data
│
├── docs/                           # Thư mục toàn bộ tài liệu & quy chuẩn
│   ├── QUY_CHUAN_GAN_NHAN_KTTC_FC.html
│   ├── QUY_CHUAN_GAN_NHAN_KTTC_FC.pdf
│   ├── QUY_CHUAN_GAN_NHAN_KTTC_FC_STANDALONE.html
│   ├── QUY_CHUAN_GAN_NHAN_KTTC_FC_PACKAGE.zip
│   ├── hien_trang_va_dinh_huong_data.html
│   └── note_S_M_E.md
│
├── legacy/                         # Thư mục lưu trữ công cụ cũ
│   ├── capture_tool.py
│   ├── catvideo.py
│   ├── run_capture_tool.bat
│   ├── run_catvideo.bat
│   └── captured_images/            # Ảnh đã trích xuất từ tool cũ
│
├── img/                            # Ảnh mẫu chuẩn hóa các bước B1 - B9
├── VIDEO_TRAIN/                    # Thư mục chứa video đầu vào để gán nhãn
└── outputs/                        # Kết quả xuất ra (annotations & cut clips)
```

---

## 📄 License
Dự án được phát hành theo giấy phép [Apache License 2.0](LICENSE).
