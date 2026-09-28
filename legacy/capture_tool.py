"""
KTTC_FC - Công Cụ Chọn & Trích Xuất Ảnh Minh Họa 3 Mốc (S - Keyframe - E)
Tác vụ: Dò video chính xác từng frame, hỗ trợ chụp và xuất bộ ảnh ví dụ minh họa
chuẩn hóa cho tài liệu và bộ dữ liệu Action Segmentation KTTC_FC.
"""

import json
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import cv2
from PIL import Image, ImageTk

# ==============================================================================
# BẢNG ĐỊNH NGHĨA CHUẨN 3 MỐC CHO 10 BƯỚC THI CÔNG FAST CONNECTOR
# ==============================================================================
STEP_DEFINITIONS = {
    "B1": {
        "name": "B1: Tháo FC",
        "full_name": "Bước 1: Tháo Đầu Fast Connector",
        "S": "khoảnh khắc KTV cầm FC chuẩn bị vặn",
        "Key": "khoảnh khắc KTV đang vặn FC",
        "E": "khoảnh khắc 2 phần của FC tách rời nhau ra",
        "files": {"S": "B1_1.jpg", "Key": "B1_2.jpg", "E": "B1_3.jpg"},
        "files_alt": {"S": "B1_S.jpg", "Key": "B1_Key.jpg", "E": "B1_E.jpg"},
    },
    "B2": {
        "name": "B2: Cắt dây treo",
        "full_name": "Bước 2: Tách & Cắt Dây Treo Kim Loại",
        "S": "khoảnh khắc KTV dùng kiềm cắt cắt tách đôi đầu lõi và treo",
        "Key": "khoảnh khắc KTV đang kéo tách đôi lõi và dây treo",
        "E": "KTV bấm cắt dây treo",
        "files": {"S": "B2_1.jpg", "Key": "B2_2.jpg", "E": "B2_3.jpg"},
        "files_alt": {"S": "B2_S.jpg", "Key": "B2_Key.jpg", "E": "B2_E.jpg"},
    },
    "B3": {
        "name": "B3: Luồn ốc",
        "full_name": "Bước 3: Luồn Cáp Vào Chuôi Ốc Chốt",
        "S": "khoảnh khắc đuôi FC sắp chạm vào dây",
        "Key": "khoảnh khắc đuôi FC được luồng hoàn toàn vào dây",
        "E": "khoảnh khắc đuôi FC được luồng xuống sâu, cách đầu dây khoảng dài",
        "files": {"S": "B3_1.jpg", "Key": "B3_2.jpg", "E": "B3_3.jpg"},
        "files_alt": {"S": "B3_S.jpg", "Key": "B3_Key.jpg", "E": "B3_E.jpg"},
    },
    "B4": {
        "name": "B4: Tuốt vỏ ngoài",
        "full_name": "Bước 4: Tuốt Vỏ Ngoài Cáp Phẳng FTTH",
        "S": "khoảnh khắc dây treo chạm kiềm tách",
        "Key": "khoảnh khắc KTV dùng sức bấm kiềm tách",
        "E": "khoảnh khắc lộ ra lõi dây quang",
        "files": {"S": "B4_1.jpg", "Key": "B4_2.jpg", "E": "B4_3.jpg"},
        "files_alt": {"S": "B4_S.jpg", "Key": "B4_Key.jpg", "E": "B4_E.jpg"},
    },
    "B5": {
        "name": "B5: Tuốt vỏ màu",
        "full_name": "Bước 5: Tuốt Lớp Vỏ Màu Sợi Quang",
        "S": "khoảnh khắc dây quang được đặt hoàn toàn vào thước đo",
        "Key": "khoảnh khắc KTV đang dùng lực bấm kiềm tuốt tuốt lõi quang",
        "E": "khoảnh khắc kiềm tuốt rời khỏi dây quang",
        "files": {"S": "B5_1.jpg", "Key": "B5_2.jpg", "E": "B5_3.jpg"},
        "files_alt": {"S": "B5_S.jpg", "Key": "B5_Key.jpg", "E": "B5_E.jpg"},
    },
    "B6a": {
        "name": "B6a: Lau cồn",
        "full_name": "Bước 6a: Vệ Sinh Sợi Quang Bằng Cồn",
        "S": "khoảnh khắc KTV cho cồn vào khăn giấy",
        "Key": "khoảnh khắc khăn giấy chạm vào sợi quang",
        "E": "khoảnh khắc khăn giấy được KTV để ra chỗ khác",
        "files": {"S": "B6a_1.jpg", "Key": "B6a_2.jpg", "E": "B6a_3.jpg"},
        "files_alt": {"S": "B6a_S.jpg", "Key": "B6a_Key.jpg", "E": "B6a_E.jpg"},
    },
    "B6b": {
        "name": "B6b: Cắt dao",
        "full_name": "Bước 6b: Cắt Sợi Bằng Dao Cắt Chính Xác",
        "S": "khoảnh khắc KTV đặt FC + thước đo vào kéo cắt",
        "Key": "khoảnh khắc đóng nắp kéo cắt, cắt lõi quang",
        "E": "khoảnh khắc FC + thước đo tách rời khỏi kéo cắt",
        "files": {"S": "B6b_1.jpg", "Key": "B6b_2.jpg", "E": "B6b_3.jpg"},
        "files_alt": {"S": "B6b_S.jpg", "Key": "B6b_Key.jpg", "E": "B6b_E.jpg"},
    },
    "B7": {
        "name": "B7: Luồn sợi FC",
        "full_name": "Bước 7: Luồn Sợi Vào Thân Fast Connector",
        "S": "khoảnh khắc KTV cầm cả đầu FC và dây quang",
        "Key": "khoảnh khắc dây quang chạm vào đầu FC",
        "E": "khoảnh khắc dây quang nằm hẳn trong đầu FC",
        "files": {"S": "B7_1.jpg", "Key": "B7_2.jpg", "E": "B7_3.jpg"},
        "files_alt": {"S": "B7_S.jpg", "Key": "B7_Key.jpg", "E": "B7_E.jpg"},
    },
    "B8": {
        "name": "B8: Vặn siết ốc",
        "full_name": "Bước 8: Vặn Siết Chuôi Ốc Chốt Cáp",
        "S": "khoảnh khắc KTV kéo đuôi FC lên sát đầu FC chuẩn bị vặn",
        "Key": "khoảnh khắc KTV vặn FC",
        "E": "khoảnh khắc KTV dừng vặn FC",
        "files": {"S": "B8_1.jpg", "Key": "B8_2.jpg", "E": "B8_3.jpg"},
        "files_alt": {"S": "B8_S.jpg", "Key": "B8_Key.jpg", "E": "B8_E.jpg"},
    },
    "B9": {
        "name": "B9: Khóa nắp vỏ",
        "full_name": "Bước 9: Khóa Chốt & Đóng Nắp Vỏ Hoàn Thiện",
        "S": "khoảnh khắc tay KTV chạm nắp FC",
        "Key": "khoảnh khắc KTV dùng lực gỡ nắp FC",
        "E": "khoảnh khắc nắp FC rời hẳn ra khỏi FC",
        "files": {"S": "B9_1.jpg", "Key": "B9_2.jpg", "E": "B9_3.jpg"},
        "files_alt": {"S": "B9_S.jpg", "Key": "B9_Key.jpg", "E": "B9_E.jpg"},
    },
}

STEP_KEYS = list(STEP_DEFINITIONS.keys())


class CaptureKeyframeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KTTC_FC • Công Cụ Chọn & Trích Xuất Ảnh Minh Họa 3 Mốc (S - Keyframe - E)")
        self.root.geometry("1400x920")
        self.root.minsize(1100, 750)

        # Video State
        self.video_path = ""
        self.cap = None
        self.fps = 25.0
        self.total_frames = 0
        self.duration_sec = 0.0
        self.current_frame_idx = 0
        self.is_playing = False
        self.is_updating_slider = False
        self.play_job = None
        self.current_cv2_frame = None

        # Data Store: {step_key: {'S': {'frame': idx, 'time': sec, 'image': cv2_img}, ...}}
        self.captured_data = {step: {} for step in STEP_KEYS}
        self.current_step_key = "B1"

        # Default save path: Prioritize Desktop/KTTC_FC/KTTC_FC/img if exists
        default_dir = r"C:\Users\htpho\Desktop\KTTC_FC\KTTC_FC\img"
        if not os.path.exists(default_dir):
            default_dir = os.path.join(os.path.dirname(__file__), "captured_images")
        self.output_dir_var = tk.StringVar(value=default_dir)
        self.naming_mode_var = tk.StringVar(value="standard")  # 'standard': B1_1.jpg | 'named': B1_S.jpg

        # UI State Vars
        self.time_label_var = tk.StringVar(value="00:00.00 / 00:00.00")
        self.frame_label_var = tk.StringVar(value="Frame: 0 / 0")
        self.video_info_var = tk.StringVar(value="Chưa mở video. Vui lòng bấm 'Chọn Video' để bắt đầu.")

        # Build UI
        self.setup_styles()
        self.build_ui()
        self.bind_keyboard_shortcuts()
        self.load_existing_images_if_any()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Configure custom button looks
        style.configure("Accent.TButton", font=("Segoe UI", 9, "bold"), foreground="white", background="#0284c7")
        style.map("Accent.TButton", background=[("active", "#0369a1")])

        style.configure("Success.TButton", font=("Segoe UI", 9, "bold"), foreground="white", background="#059669")
        style.map("Success.TButton", background=[("active", "#047857")])

        style.configure("Warning.TButton", font=("Segoe UI", 9, "bold"), foreground="#78350f", background="#fde047")
        style.map("Warning.TButton", background=[("active", "#facc15")])

        style.configure("Danger.TButton", font=("Segoe UI", 9, "bold"), foreground="white", background="#dc2626")
        style.map("Danger.TButton", background=[("active", "#b91c1c")])

        style.configure("StepActive.TButton", font=("Segoe UI", 9, "bold"), background="#1e293b", foreground="white")

    def build_ui(self):
        # 1. TOP HEADER / TOOLBAR
        top_bar = tk.Frame(self.root, bg="#0f172a", padx=12, pady=10)
        top_bar.pack(fill="x", side="top")

        # Top row: Video Select + Save Dir + Export Buttons
        btn_open = tk.Button(
            top_bar,
            text="📂 Chọn Video Thi Công",
            bg="#2563eb",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2",
            command=self.select_video,
        )
        btn_open.pack(side="left", padx=(0, 10))

        lbl_video = tk.Label(
            top_bar,
            textvariable=self.video_info_var,
            bg="#1e293b",
            fg="#94a3b8",
            font=("Segoe UI", 9),
            anchor="w",
            padx=10,
            pady=4,
        )
        lbl_video.pack(side="left", fill="x", expand=True, padx=(0, 10))

        btn_dir = tk.Button(
            top_bar,
            text="📁 Thư mục lưu",
            bg="#334155",
            fg="#e2e8f0",
            font=("Segoe UI", 9),
            relief="flat",
            padx=8,
            pady=4,
            cursor="hand2",
            command=self.select_output_dir,
        )
        btn_dir.pack(side="left", padx=(0, 6))

        btn_open_folder = tk.Button(
            top_bar,
            text="↗️ Mở Thư Mục",
            bg="#334155",
            fg="#e2e8f0",
            font=("Segoe UI", 9),
            relief="flat",
            padx=8,
            pady=4,
            cursor="hand2",
            command=self.open_output_folder,
        )
        btn_open_folder.pack(side="left", padx=(0, 10))

        btn_save_all = tk.Button(
            top_bar,
            text="💾 XUẤT TẤT CẢ ẢNH & JSON",
            bg="#059669",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2",
            command=self.save_all_captured,
        )
        btn_save_all.pack(side="right")

        # 2. MAIN SPLIT BODY
        main_paned = tk.PanedWindow(self.root, orient="horizontal", bg="#1e293b", sashwidth=4)
        main_paned.pack(fill="both", expand=True)

        # ----------------- LEFT PANEL: VIDEO PLAYER -----------------
        left_frame = tk.Frame(main_paned, bg="#020617")
        main_paned.add(left_frame, minsize=650)

        # Video Canvas / Screen
        self.video_canvas = tk.Canvas(left_frame, bg="#000000", highlightthickness=0)
        self.video_canvas.pack(fill="both", expand=True, padx=8, pady=(8, 4))
        self.video_canvas.bind("<Configure>", self.on_canvas_resize)

        # Scrubbing Slider
        slider_frame = tk.Frame(left_frame, bg="#020617", padx=8)
        slider_frame.pack(fill="x", pady=2)

        self.time_slider = ttk.Scale(slider_frame, from_=0, to=100, orient="horizontal", command=self.on_slider_change)
        self.time_slider.pack(fill="x", side="top", pady=(0, 4))

        # Time & Frame Display
        info_row = tk.Frame(slider_frame, bg="#020617")
        info_row.pack(fill="x")

        tk.Label(
            info_row,
            textvariable=self.time_label_var,
            bg="#020617",
            fg="#38bdf8",
            font=("Consolas", 11, "bold"),
        ).pack(side="left")

        tk.Label(
            info_row,
            textvariable=self.frame_label_var,
            bg="#020617",
            fg="#94a3b8",
            font=("Consolas", 10),
        ).pack(side="right")

        # Player Navigation Controls Strip
        ctrl_frame = tk.Frame(left_frame, bg="#0f172a", pady=6, padx=8)
        ctrl_frame.pack(fill="x", pady=(4, 6))

        # Jump buttons
        tk.Button(ctrl_frame, text="<< -5s", bg="#1e293b", fg="#cbd5e1", relief="flat", padx=6, command=lambda: self.seek_relative(-5.0)).pack(side="left", padx=2)
        tk.Button(ctrl_frame, text="< -1s", bg="#1e293b", fg="#cbd5e1", relief="flat", padx=6, command=lambda: self.seek_relative(-1.0)).pack(side="left", padx=2)
        tk.Button(ctrl_frame, text="◀ -1 Frame", bg="#334155", fg="#f8fafc", relief="flat", padx=6, font=("Segoe UI", 9, "bold"), command=lambda: self.step_frame(-1)).pack(side="left", padx=3)

        self.btn_play = tk.Button(
            ctrl_frame,
            text="▶ PLAY",
            bg="#2563eb",
            fg="white",
            relief="flat",
            padx=16,
            pady=2,
            font=("Segoe UI", 10, "bold"),
            command=self.toggle_play,
        )
        self.btn_play.pack(side="left", padx=6)

        tk.Button(ctrl_frame, text="+1 Frame ▶", bg="#334155", fg="#f8fafc", relief="flat", padx=6, font=("Segoe UI", 9, "bold"), command=lambda: self.step_frame(1)).pack(side="left", padx=3)
        tk.Button(ctrl_frame, text="+1s >", bg="#1e293b", fg="#cbd5e1", relief="flat", padx=6, command=lambda: self.seek_relative(1.0)).pack(side="left", padx=2)
        tk.Button(ctrl_frame, text="+5s >>", bg="#1e293b", fg="#cbd5e1", relief="flat", padx=6, command=lambda: self.seek_relative(5.0)).pack(side="left", padx=2)

        # 3 PROMINENT CAPTURE BUTTONS (BOTTOM OF LEFT PANEL)
        capture_bar = tk.Frame(left_frame, bg="#0b1329", pady=8, padx=8)
        capture_bar.pack(fill="x")

        btn_cap_s = tk.Button(
            capture_bar,
            text="🟢 CHỤP MỐC START (S)\n[Phím 1]",
            bg="#065f46",
            fg="#a7f3d0",
            activebackground="#047857",
            activeforeground="white",
            font=("Segoe UI", 9, "bold"),
            relief="groove",
            bd=2,
            pady=6,
            cursor="hand2",
            command=lambda: self.capture_point("S"),
        )
        btn_cap_s.pack(side="left", fill="x", expand=True, padx=3)

        btn_cap_key = tk.Button(
            capture_bar,
            text="⭐ CHỤP KEYFRAME (KEY)\n[Phím 2]",
            bg="#854d0e",
            fg="#fef08a",
            activebackground="#b45309",
            activeforeground="white",
            font=("Segoe UI", 9, "bold"),
            relief="groove",
            bd=2,
            pady=6,
            cursor="hand2",
            command=lambda: self.capture_point("Key"),
        )
        btn_cap_key.pack(side="left", fill="x", expand=True, padx=3)

        btn_cap_e = tk.Button(
            capture_bar,
            text="🔴 CHỤP MỐC END (E)\n[Phím 3]",
            bg="#881337",
            fg="#fecdd3",
            activebackground="#be123c",
            activeforeground="white",
            font=("Segoe UI", 9, "bold"),
            relief="groove",
            bd=2,
            pady=6,
            cursor="hand2",
            command=lambda: self.capture_point("E"),
        )
        btn_cap_e.pack(side="left", fill="x", expand=True, padx=3)

        # ----------------- RIGHT PANEL: STEP SELECTION & THUMBNAILS -----------------
        right_frame = tk.Frame(main_paned, bg="#0f172a", padx=10, pady=8)
        main_paned.add(right_frame, minsize=420)

        # Step Selection Header
        tk.Label(
            right_frame,
            text="CHỌN BƯỚC ĐANG CẦN CHỤP ẢNH MINH HỌA:",
            bg="#0f172a",
            fg="#94a3b8",
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", pady=(0, 6))

        # 10 Step Buttons (Grid of 5x2)
        step_grid = tk.Frame(right_frame, bg="#0f172a")
        step_grid.pack(fill="x", pady=(0, 8))

        self.step_buttons = {}
        for idx, key in enumerate(STEP_KEYS):
            row = idx // 5
            col = idx % 5
            btn = tk.Button(
                step_grid,
                text=key,
                bg="#1e293b",
                fg="#f1f5f9",
                font=("Segoe UI", 9, "bold"),
                relief="flat",
                pady=4,
                cursor="hand2",
                command=lambda k=key: self.select_step(k),
            )
            btn.grid(row=row, column=col, sticky="ew", padx=2, pady=2)
            step_grid.columnconfigure(col, weight=1)
            self.step_buttons[key] = btn

        # Selected Step Definition Card (Crucial for labeler reference!)
        self.def_card = tk.LabelFrame(
            right_frame,
            text="Định nghĩa chuẩn của bước được chọn",
            bg="#1e293b",
            fg="#38bdf8",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=8,
        )
        self.def_card.pack(fill="x", pady=(0, 10))

        self.lbl_def_step_title = tk.Label(
            self.def_card, text="", bg="#1e293b", fg="#ffffff", font=("Segoe UI", 10, "bold"), anchor="w"
        )
        self.lbl_def_step_title.pack(fill="x", pady=(0, 4))

        self.lbl_def_s = tk.Label(self.def_card, text="", bg="#1e293b", fg="#a7f3d0", font=("Segoe UI", 9), anchor="w", wraplength=400, justify="left")
        self.lbl_def_s.pack(fill="x", pady=1)

        self.lbl_def_key = tk.Label(self.def_card, text="", bg="#1e293b", fg="#fef08a", font=("Segoe UI", 9, "bold"), anchor="w", wraplength=400, justify="left")
        self.lbl_def_key.pack(fill="x", pady=1)

        self.lbl_def_e = tk.Label(self.def_card, text="", bg="#1e293b", fg="#fecdd3", font=("Segoe UI", 9), anchor="w", wraplength=400, justify="left")
        self.lbl_def_e.pack(fill="x", pady=1)

        # 3 Thumbnail Cards (S, Key, E)
        thumb_container = tk.Frame(right_frame, bg="#0f172a")
        thumb_container.pack(fill="both", expand=True)

        self.thumb_cards = {}
        for point, label_text, color in [
            ("S", "🟢 Mốc START (S)", "#10b981"),
            ("Key", "⭐ KEYFRAME (Then chốt)", "#eab308"),
            ("E", "🔴 Mốc END (Kết thúc)", "#ef4444"),
        ]:
            card = tk.LabelFrame(
                thumb_container,
                text=label_text,
                bg="#1e293b",
                fg=color,
                font=("Segoe UI", 9, "bold"),
                padx=8,
                pady=4,
            )
            card.pack(fill="both", expand=True, pady=3)

            # Left thumbnail img
            canvas = tk.Canvas(card, width=170, height=95, bg="#090d16", highlightthickness=1, highlightbackground="#334155")
            canvas.pack(side="left", padx=(0, 10))

            # Right actions / info
            right_meta = tk.Frame(card, bg="#1e293b")
            right_meta.pack(side="left", fill="both", expand=True)

            lbl_time = tk.Label(right_meta, text="Chưa chụp", bg="#1e293b", fg="#94a3b8", font=("Consolas", 10, "bold"), anchor="w")
            lbl_time.pack(anchor="w", pady=(2, 4))

            btn_box = tk.Frame(right_meta, bg="#1e293b")
            btn_box.pack(anchor="w")

            btn_jump = tk.Button(
                btn_box,
                text="Tua tới đây",
                bg="#334155",
                fg="#f1f5f9",
                font=("Segoe UI", 8),
                relief="flat",
                command=lambda pt=point: self.jump_to_captured(pt),
            )
            btn_jump.pack(side="left", padx=(0, 4))

            btn_del = tk.Button(
                btn_box,
                text="Xóa",
                bg="#451a03",
                fg="#fed7aa",
                font=("Segoe UI", 8),
                relief="flat",
                command=lambda pt=point: self.delete_captured(pt),
            )
            btn_del.pack(side="left")

            self.thumb_cards[point] = {
                "canvas": canvas,
                "lbl_time": lbl_time,
                "photo": None,
            }

        # Bottom Bar of Right Panel: Save current step
        bottom_right = tk.Frame(right_frame, bg="#0f172a", pady=6)
        bottom_right.pack(fill="x", side="bottom")

        tk.Button(
            bottom_right,
            text="💾 Lưu 3 ảnh của bước này",
            bg="#1d4ed8",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            pady=4,
            command=self.save_current_step,
        ).pack(fill="x")

        # Initial view
        self.select_step("B1")

    def bind_keyboard_shortcuts(self):
        self.root.bind("<space>", lambda e: self.toggle_play())
        self.root.bind("<Left>", lambda e: self.step_frame(-1))
        self.root.bind("<Right>", lambda e: self.step_frame(1))
        self.root.bind("<Shift-Left>", lambda e: self.seek_relative(-1.0))
        self.root.bind("<Shift-Right>", lambda e: self.seek_relative(1.0))
        self.root.bind("<Control-Left>", lambda e: self.seek_relative(-5.0))
        self.root.bind("<Control-Right>", lambda e: self.seek_relative(5.0))

        # Hotkeys for capturing
        self.root.bind("1", lambda e: self.capture_point("S"))
        self.root.bind("2", lambda e: self.capture_point("Key"))
        self.root.bind("3", lambda e: self.capture_point("E"))

    # ==========================================================================
    # VIDEO LOADING & PLAYBACK ENGINE
    # ==========================================================================
    def select_video(self):
        file_types = [("Video Files", "*.mp4 *.mov *.avi *.mkv *.MOV *.MP4"), ("All Files", "*.*")]
        path = filedialog.askopenfilename(title="Chọn video thi công", filetypes=file_types)
        if not path:
            return

        self.pause()
        if self.cap:
            self.cap.release()

        self.video_path = path
        self.cap = cv2.VideoCapture(self.video_path)

        if not self.cap.isOpened():
            messagebox.showerror("Lỗi", f"Không thể mở video:\n{path}")
            self.video_path = ""
            return

        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 25.0
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration_sec = self.total_frames / self.fps if self.fps > 0 else 0.0

        filename = os.path.basename(path)
        self.video_info_var.set(f"Video: {filename} | {self.fps:.2f} FPS | {self.format_time(self.duration_sec)} ({self.total_frames} frames)")
        self.time_slider.configure(to=max(1, self.total_frames - 1))

        self.seek_frame(0)

    def select_output_dir(self):
        directory = filedialog.askdirectory(
            title="Chọn thư mục lưu bộ ảnh minh họa",
            initialdir=self.output_dir_var.get()
        )
        if directory:
            self.output_dir_var.set(directory)
            self.load_existing_images_if_any()

    def open_output_folder(self):
        folder = self.output_dir_var.get()
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        os.startfile(folder)

    def seek_frame(self, frame_idx, update_slider=True):
        if not self.cap:
            return

        frame_idx = max(0, min(frame_idx, self.total_frames - 1))
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = self.cap.read()
        if ret:
            self.current_frame_idx = frame_idx
            self.current_cv2_frame = frame
            self.render_frame_to_canvas(frame)
            self.update_player_labels()
            if update_slider and not self.is_updating_slider:
                self.is_updating_slider = True
                self.time_slider.set(frame_idx)
                self.is_updating_slider = False

    def seek_relative(self, delta_sec):
        if not self.cap:
            return
        delta_frames = int(round(delta_sec * self.fps))
        self.seek_frame(self.current_frame_idx + delta_frames)

    def step_frame(self, step_delta):
        if not self.cap:
            return
        self.pause()
        self.seek_frame(self.current_frame_idx + step_delta)

    def on_slider_change(self, val):
        if self.is_updating_slider or not self.cap or self.is_playing:
            return
        try:
            frame_idx = int(float(val))
        except (ValueError, TypeError):
            return

        if frame_idx == self.current_frame_idx:
            return

        self.seek_frame(frame_idx, update_slider=False)

    def toggle_play(self):
        if not self.cap:
            return
        if self.is_playing:
            self.pause()
        else:
            self.play()

    def play(self):
        if not self.cap:
            return
        self.is_playing = True
        self.btn_play.configure(text="⏸ PAUSE", bg="#dc2626")
        self.play_loop()

    def pause(self):
        self.is_playing = False
        if self.play_job:
            self.root.after_cancel(self.play_job)
            self.play_job = None
        self.btn_play.configure(text="▶ PLAY", bg="#2563eb")

    def play_loop(self):
        if not self.is_playing or not self.cap:
            return

        ret, frame = self.cap.read()
        if ret:
            self.current_frame_idx = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1
            self.current_cv2_frame = frame
            self.render_frame_to_canvas(frame)
            self.update_player_labels()
            self.is_updating_slider = True
            self.time_slider.set(self.current_frame_idx)
            self.is_updating_slider = False

            delay_ms = max(1, int(1000.0 / self.fps))
            self.play_job = self.root.after(delay_ms, self.play_loop)
        else:
            self.pause()

    def render_frame_to_canvas(self, frame_bgr):
        if frame_bgr is None:
            return
        canvas_w = self.video_canvas.winfo_width()
        canvas_h = self.video_canvas.winfo_height()
        if canvas_w < 10 or canvas_h < 10:
            return

        # Resize preserving aspect ratio
        fh, fw = frame_bgr.shape[:2]
        if fh <= 0 or fw <= 0:
            return

        scale = min(canvas_w / fw, canvas_h / fh)
        nw, nh = int(fw * scale), int(fh * scale)
        if nw < 1 or nh < 1:
            return

        resized = cv2.resize(frame_bgr, (nw, nh), interpolation=cv2.INTER_AREA)
        rgb_frame = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb_frame)
        self.video_photo = ImageTk.PhotoImage(image=img)

        # Center on canvas
        self.video_canvas.delete("all")
        x_center = canvas_w // 2
        y_center = canvas_h // 2
        self.video_canvas.create_image(x_center, y_center, anchor="center", image=self.video_photo)

    def on_canvas_resize(self, _event):
        if self.current_cv2_frame is not None and not self.is_playing:
            self.render_frame_to_canvas(self.current_cv2_frame)

    def update_player_labels(self):
        curr_sec = self.current_frame_idx / self.fps if self.fps > 0 else 0.0
        self.time_label_var.set(f"{self.format_time(curr_sec)} / {self.format_time(self.duration_sec)}")
        self.frame_label_var.set(f"Frame: {self.current_frame_idx} / {self.total_frames}")

    @staticmethod
    def format_time(seconds):
        total_cs = max(0, int(round(seconds * 100)))
        minutes = total_cs // 6000
        sec = (total_cs % 6000) // 100
        cs = total_cs % 100
        return f"{minutes:02d}:{sec:02d}.{cs:02d}"

    # ==========================================================================
    # STEP & CAPTURE LOGIC
    # ==========================================================================
    def select_step(self, step_key):
        self.current_step_key = step_key

        # Highlight active button
        for k, btn in self.step_buttons.items():
            is_active = (k == step_key)
            has_data = len(self.captured_data[k])
            status_text = f" ({has_data}/3)" if has_data > 0 else ""
            if has_data == 3:
                status_text = " ✓"

            if is_active:
                btn.configure(bg="#3b82f6", fg="white", text=f"▶ {k}{status_text}")
            else:
                btn.configure(bg="#10b981" if has_data == 3 else "#1e293b", fg="white" if has_data == 3 else "#cbd5e1", text=f"{k}{status_text}")

        # Update definition card
        info = STEP_DEFINITIONS[step_key]
        self.lbl_def_step_title.configure(text=f"📋 {info['full_name']}")
        self.lbl_def_s.configure(text=f"🟢 Mốc S: {info['S']}")
        self.lbl_def_key.configure(text=f"⭐ Keyframe: {info['Key']}")
        self.lbl_def_e.configure(text=f"🔴 Mốc E: {info['E']}")

        # Refresh Thumbnails
        self.refresh_thumbnails()

    def capture_point(self, point_type):
        """point_type is 'S', 'Key', or 'E'"""
        if not self.cap or self.current_cv2_frame is None:
            messagebox.showwarning("Chưa có video", "Vui lòng chọn video trước khi chụp mốc.")
            return

        curr_sec = round(self.current_frame_idx / self.fps, 3)
        curr_frame = self.current_frame_idx

        # Clone current frame
        frame_copy = self.current_cv2_frame.copy()

        self.captured_data[self.current_step_key][point_type] = {
            "frame": curr_frame,
            "time_sec": curr_sec,
            "image": frame_copy,
            "video_path": self.video_path,
        }

        # Refresh current step buttons & UI
        self.select_step(self.current_step_key)

    def jump_to_captured(self, point_type):
        data = self.captured_data[self.current_step_key].get(point_type)
        if data and "frame" in data:
            self.pause()
            self.seek_frame(data["frame"])

    def delete_captured(self, point_type):
        if point_type in self.captured_data[self.current_step_key]:
            del self.captured_data[self.current_step_key][point_type]
            self.select_step(self.current_step_key)

    def refresh_thumbnails(self):
        step_data = self.captured_data[self.current_step_key]
        for point in ["S", "Key", "E"]:
            card_ui = self.thumb_cards[point]
            canvas = card_ui["canvas"]
            lbl_time = card_ui["lbl_time"]

            canvas.delete("all")
            if point in step_data:
                item = step_data[point]
                cv_img = item["image"]
                t_sec = item["time_sec"]
                f_idx = item["frame"]

                # Resize to thumbnail (170x95)
                th_h, th_w = cv_img.shape[:2]
                scale = min(170 / th_w, 95 / th_h)
                nw, nh = int(th_w * scale), int(th_h * scale)
                thumb_resized = cv2.resize(cv_img, (nw, nh), interpolation=cv2.INTER_AREA)
                rgb = cv2.cvtColor(thumb_resized, cv2.COLOR_BGR2RGB)
                photo = ImageTk.PhotoImage(image=Image.fromarray(rgb))

                card_ui["photo"] = photo  # keep reference
                canvas.create_image(85, 47, anchor="center", image=photo)
                lbl_time.configure(text=f"⏱ {self.format_time(t_sec)} (F: {f_idx})", fg="#38bdf8")
            else:
                card_ui["photo"] = None
                lbl_time.configure(text="Chưa chụp", fg="#64748b")
                canvas.create_text(85, 47, text="Trống", fill="#475569", font=("Segoe UI", 10))

    # ==========================================================================
    # SAVE & EXPORT (FILES & METADATA JSON)
    # ==========================================================================
    def save_current_step(self):
        step_data = self.captured_data[self.current_step_key]
        if not step_data:
            messagebox.showinfo("Chưa có ảnh", f"Bước {self.current_step_key} chưa có ảnh nào được chụp.")
            return

        out_dir = self.output_dir_var.get()
        os.makedirs(out_dir, exist_ok=True)

        info = STEP_DEFINITIONS[self.current_step_key]
        saved_files = []

        for point, data in step_data.items():
            filename = info["files"][point]
            filepath = os.path.join(out_dir, filename)
            self.safe_save_image(filepath, data["image"])
            saved_files.append(filename)

        messagebox.showinfo("Thành công", f"Đã lưu các ảnh của {self.current_step_key} vào:\n{out_dir}\n\nFiles: {', '.join(saved_files)}")

    def save_all_captured(self):
        total_captured = sum(len(d) for d in self.captured_data.values())
        if total_captured == 0:
            messagebox.showwarning("Trống", "Bạn chưa chụp ảnh mốc nào cả.")
            return

        out_dir = self.output_dir_var.get()
        os.makedirs(out_dir, exist_ok=True)

        metadata = {
            "source_video": self.video_path,
            "fps": self.fps,
            "total_frames": self.total_frames,
            "duration_sec": self.duration_sec,
            "steps": {},
        }

        saved_count = 0
        for step_key, step_data in self.captured_data.items():
            if not step_data:
                continue

            info = STEP_DEFINITIONS[step_key]
            metadata["steps"][step_key] = {"title": info["full_name"], "points": {}}

            for point, data in step_data.items():
                filename = info["files"][point]
                filepath = os.path.join(out_dir, filename)
                self.safe_save_image(filepath, data["image"])
                saved_count += 1

                metadata["steps"][step_key]["points"][point] = {
                    "filename": filename,
                    "frame": data["frame"],
                    "time_sec": data["time_sec"],
                    "description": info[point],
                }

        # Save metadata.json
        meta_path = os.path.join(out_dir, "keyframes_metadata.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        messagebox.showinfo(
            "Xuất Thành Công",
            f"Đã lưu thành công {saved_count} ảnh mốc và file metadata JSON!\n\nThư mục:\n{out_dir}\nFile JSON: keyframes_metadata.json"
        )

    def load_existing_images_if_any(self):
        """If directory has existing B1_1.jpg etc, preview them!"""
        out_dir = self.output_dir_var.get()
        if not os.path.exists(out_dir):
            return

        found_any = False
        for step_key, info in STEP_DEFINITIONS.items():
            for point, fname in info["files"].items():
                fpath = os.path.join(out_dir, fname)
                if os.path.exists(fpath) and point not in self.captured_data[step_key]:
                    img = self.safe_load_image(fpath)
                    if img is not None:
                        self.captured_data[step_key][point] = {
                            "frame": 0,
                            "time_sec": 0.0,
                            "image": img,
                            "video_path": "loaded_from_disk",
                        }
                        found_any = True

        if found_any:
            self.select_step(self.current_step_key)

    @staticmethod
    def safe_save_image(filepath, bgr_img):
        try:
            rgb_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_img)
            pil_img.save(filepath, format="JPEG", quality=95)
            return True
        except Exception:
            try:
                success, enc = cv2.imencode(".jpg", bgr_img, [cv2.IMWRITE_JPEG_QUALITY, 95])
                if success:
                    with open(filepath, "wb") as f:
                        f.write(enc)
                    return True
            except Exception:
                pass
        return False

    @staticmethod
    def safe_load_image(filepath):
        try:
            with Image.open(filepath) as pil_img:
                rgb_arr = pil_img.convert("RGB")
                import numpy as np
                return cv2.cvtColor(np.array(rgb_arr), cv2.COLOR_RGB2BGR)
        except Exception:
            try:
                return cv2.imread(filepath)
            except Exception:
                return None

    def on_close(self):
        self.pause()
        if self.cap:
            self.cap.release()
            self.cap = None
        self.root.destroy()


def main():
    root = tk.Tk()
    app = CaptureKeyframeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
