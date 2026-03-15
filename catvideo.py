import os
import subprocess
import imageio_ffmpeg
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import cv2
from PIL import Image, ImageTk


class VideoCutToolStep1:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Cut Tool - Step 2")
        self.root.geometry("1100x950")

        self.video_path = ""
        self.cap = None
        self.fps = 0
        self.frame_count = 0
        self.duration = 0
        self.current_frame = 0

        self.is_playing = False
        self.is_updating_slider = False

        self.preview_frame = None
        self.video_label = None
        self.frame_image = None
        self.segment_rows = []
        self.segment_canvas = None
        self.segment_inner_frame = None

        self.segment_count_var = tk.StringVar(value="10")
        self.video_name_var = tk.StringVar(value="Chưa chọn video")
        self.time_var = tk.StringVar(value="00:00.00 / 00:00.00")

        self.build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def build_ui(self):
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill="x")

        ttk.Button(top_frame, text="Chọn video", command=self.select_video).grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(top_frame, textvariable=self.video_name_var, width=70).grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(top_frame, text="Số đoạn cần cắt:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(top_frame, textvariable=self.segment_count_var, width=10).grid(row=1, column=1, padx=5, pady=5, sticky="w")
        ttk.Button(top_frame, text="Tạo danh sách", command=self.refresh_segment_rows).grid(row=1, column=2, padx=5, pady=5, sticky="w")
        ttk.Button(top_frame, text="Cắt video", command=self.cut_segments).grid(row=1, column=3, padx=5, pady=5, sticky="w")

        self.preview_frame = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        self.preview_frame.pack(fill="both", expand=True)
        self.preview_frame.pack_propagate(False)

        self.video_label = tk.Label(self.preview_frame, bg="black")
        self.video_label.pack(expand=True)

        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill="x")

        ttk.Button(control_frame, text="<< -1s", command=lambda: self.seek_relative(-1)).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Play", command=self.play_video).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Pause", command=self.pause_video).pack(side="left", padx=5)
        ttk.Button(control_frame, text="+1s >>", command=lambda: self.seek_relative(1)).pack(side="left", padx=5)

        self.slider = ttk.Scale(
            control_frame,
            from_=0,
            to=100,
            orient="horizontal",
            command=self.on_slider_move
        )
        self.slider.pack(side="left", fill="x", expand=True, padx=10)

        ttk.Label(control_frame, textvariable=self.time_var, width=20).pack(side="right", padx=5)

        bottom_frame = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        bottom_frame.pack(fill="x")

        self.info_label = ttk.Label(
            bottom_frame,
            text="Bước 3: đã có nút cắt video và lưu file vào data/B1...Bn.",
            foreground="blue"
        )
        self.info_label.pack(anchor="w")

        self.build_segment_panel()
        self.refresh_segment_rows()
    def build_segment_panel(self):
        segment_outer = ttk.LabelFrame(self.root, text="Danh sách mốc thời gian", padding=10)
        segment_outer.pack(fill="both", expand=False, padx=10, pady=(0, 10))

        self.segment_canvas = tk.Canvas(segment_outer, height=240)
        scrollbar = ttk.Scrollbar(segment_outer, orient="vertical", command=self.segment_canvas.yview)
        self.segment_inner_frame = ttk.Frame(self.segment_canvas)

        self.segment_inner_frame.bind(
            "<Configure>",
            lambda e: self.segment_canvas.configure(scrollregion=self.segment_canvas.bbox("all"))
        )

        self.segment_canvas.create_window((0, 0), window=self.segment_inner_frame, anchor="nw")
        self.segment_canvas.configure(yscrollcommand=scrollbar.set)

        self.segment_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def refresh_segment_rows(self):
        try:
            count = int(self.segment_count_var.get().strip())
        except ValueError:
            messagebox.showerror("Lỗi", "Số đoạn cần cắt phải là số nguyên.")
            return

        if count <= 0:
            messagebox.showerror("Lỗi", "Số đoạn cần cắt phải lớn hơn 0.")
            return

        for widget in self.segment_inner_frame.winfo_children():
            widget.destroy()

        self.segment_rows = []

        ttk.Label(self.segment_inner_frame, text="Bước", width=8).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(self.segment_inner_frame, text="Start", width=14).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(self.segment_inner_frame, text="End", width=14).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ttk.Label(self.segment_inner_frame, text="Thao tác").grid(row=0, column=3, columnspan=2, padx=5, pady=5, sticky="w")

        for i in range(1, count + 1):
            start_var = tk.StringVar()
            end_var = tk.StringVar()

            ttk.Label(self.segment_inner_frame, text=f"B{i}", width=8).grid(row=i, column=0, padx=5, pady=4, sticky="w")
            ttk.Entry(self.segment_inner_frame, textvariable=start_var, width=14).grid(row=i, column=1, padx=5, pady=4, sticky="w")
            ttk.Entry(self.segment_inner_frame, textvariable=end_var, width=14).grid(row=i, column=2, padx=5, pady=4, sticky="w")
            ttk.Button(
                self.segment_inner_frame,
                text="Lấy start",
                command=lambda idx=i - 1: self.capture_time(idx, "start")
            ).grid(row=i, column=3, padx=5, pady=4, sticky="w")
            ttk.Button(
                self.segment_inner_frame,
                text="Lấy end",
                command=lambda idx=i - 1: self.capture_time(idx, "end")
            ).grid(row=i, column=4, padx=5, pady=4, sticky="w")

            self.segment_rows.append({
                "start_var": start_var,
                "end_var": end_var
            })

    def capture_time(self, index, target):
        if not self.cap:
            messagebox.showwarning("Thông báo", "Bạn chưa chọn video.")
            return

        current_time = self.current_frame / self.fps if self.fps > 0 else 0
        value = self.format_time(current_time)

        if target == "start":
            self.segment_rows[index]["start_var"].set(value)
        else:
            self.segment_rows[index]["end_var"].set(value)


    def ensure_ffmpeg(self):
        try:
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception as e:
            raise RuntimeError(f"Không lấy được ffmpeg từ imageio-ffmpeg: {e}")

        if not ffmpeg_path or not os.path.exists(ffmpeg_path):
            raise RuntimeError("Không tìm thấy ffmpeg khả dụng từ imageio-ffmpeg.")

        return ffmpeg_path

    def format_seconds_for_ffmpeg(self, seconds):
        total_ms = int(round(seconds * 1000))
        hours = total_ms // 3600000
        minutes = (total_ms % 3600000) // 60000
        secs = (total_ms % 60000) // 1000
        ms = total_ms % 1000
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{ms:03d}"

    def parse_time_text(self, text):
        text = text.strip()
        if not text:
            raise ValueError("Thời gian không được để trống.")

        parts = text.split(":")
        if len(parts) != 2:
            raise ValueError("Định dạng thời gian phải là mm:ss.xx")

        minutes_text = parts[0].strip()
        seconds_text = parts[1].strip()

        minutes = int(minutes_text)
        seconds = float(seconds_text)

        total_seconds = minutes * 60 + seconds
        return total_seconds

    def cut_segments(self):
        if not self.video_path:
            messagebox.showwarning("Thông báo", "Bạn chưa chọn video.")
            return

        if not self.segment_rows:
            messagebox.showwarning("Thông báo", "Chưa có danh sách đoạn cắt.")
            return

        self.pause_video()

        try:
            ffmpeg_path = self.ensure_ffmpeg()

            segments = []
            for index, row in enumerate(self.segment_rows, start=1):
                start_text = row["start_var"].get().strip()
                end_text = row["end_var"].get().strip()

                if not start_text or not end_text:
                    messagebox.showerror("Lỗi", f"Thiếu thời gian ở B{index}.")
                    return

                start_sec = self.parse_time_text(start_text)
                end_sec = self.parse_time_text(end_text)

                if start_sec < 0 or end_sec < 0:
                    messagebox.showerror("Lỗi", f"Thời gian ở B{index} không hợp lệ.")
                    return

                if end_sec <= start_sec:
                    messagebox.showerror("Lỗi", f"End phải lớn hơn Start ở B{index}.")
                    return

                if end_sec > self.duration:
                    messagebox.showerror("Lỗi", f"End ở B{index} đang vượt quá thời lượng video.")
                    return

                segments.append((index, start_sec, end_sec))

            base_name = os.path.splitext(os.path.basename(self.video_path))[0]

            self.root.config(cursor="watch")
            self.root.update_idletasks()

            for index, start_sec, end_sec in segments:
                output_dir = os.path.join("data", f"B{index}")
                os.makedirs(output_dir, exist_ok=True)

                output_path = os.path.join(output_dir, f"b{index}_{base_name}.mp4")

                start_text = self.format_seconds_for_ffmpeg(start_sec)
                duration_text = self.format_seconds_for_ffmpeg(end_sec - start_sec)

                cmd = [
                    ffmpeg_path,
                    "-y",
                    "-i",
                    self.video_path,
                    "-ss",
                    start_text,
                    "-t",
                    duration_text,
                    "-avoid_negative_ts",
                    "make_zero",
                    "-c:v",
                    "mpeg4",
                    "-q:v",
                    "3",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "128k",
                    "-movflags",
                    "+faststart",
                    output_path
                ]

                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    errors="replace"
                )

                if result.returncode != 0:
                    debug_text = "\n".join([
                        f"Segment: B{index}",
                        f"Return code: {result.returncode}",
                        f"Command: {' '.join(cmd)}",
                        "",
                        "STDOUT:",
                        result.stdout.strip(),
                        "",
                        "STDERR:",
                        result.stderr.strip()
                    ]).strip()

                    log_path = os.path.join(output_dir, f"b{index}_ffmpeg_error.txt")
                    with open(log_path, "w", encoding="utf-8") as f:
                        f.write(debug_text)

                    stderr_preview = result.stderr.strip()
                    if not stderr_preview:
                        stderr_preview = "FFmpeg không trả stderr. Hãy mở file log để xem command đã chạy."

                    raise RuntimeError(
                        f"B{index} lỗi.\n"
                        f"Log đã lưu: {log_path}\n\n"
                        f"{stderr_preview[:2000]}"
                    )

            messagebox.showinfo("Hoàn tất", "Đã cắt xong toàn bộ video.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Cắt video thất bại: {e}")
        finally:
            self.root.config(cursor="")

    def select_video(self):
        path = filedialog.askopenfilename(
            title="Chọn video",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv"),
                ("All files", "*.*")
            ]
        )
        if not path:
            return

        self.load_video(path)

    def load_video(self, path):
        self.release_video()

        self.cap = cv2.VideoCapture(path)
        if not self.cap.isOpened():
            messagebox.showerror("Lỗi", "Không mở được video.")
            self.cap = None
            return

        self.video_path = path
        self.video_name_var.set(os.path.basename(path))

        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        if not self.fps or self.fps <= 0:
            self.fps = 25

        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if self.frame_count <= 0:
            self.frame_count = 1

        self.duration = self.frame_count / self.fps
        self.current_frame = 0

        self.slider.configure(to=max(self.duration, 0.01))
        self.slider.set(0)

        self.show_frame_at_time(0)

    def show_frame_at_time(self, time_sec):
        if not self.cap:
            return

        time_sec = max(0, min(time_sec, self.duration))
        frame_index = int(time_sec * self.fps)
        frame_index = max(0, min(frame_index, self.frame_count - 1))

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        success, frame = self.cap.read()
        if not success:
            return

        self.current_frame = frame_index
        self.display_frame(frame)

        current_time = self.current_frame / self.fps
        self.update_time_label(current_time)

        self.is_updating_slider = True
        self.slider.set(current_time)
        self.is_updating_slider = False

    def display_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        box_width = self.preview_frame.winfo_width()
        box_height = self.preview_frame.winfo_height()

        if box_width < 10 or box_height < 10:
            box_width = 960
            box_height = 540

        h, w = frame.shape[:2]
        scale = min(box_width / w, box_height / h)
        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))

        frame = cv2.resize(frame, (new_w, new_h))
        image = Image.fromarray(frame)
        self.frame_image = ImageTk.PhotoImage(image=image)
        self.video_label.config(image=self.frame_image)

    def play_video(self):
        if not self.cap:
            messagebox.showwarning("Thông báo", "Bạn chưa chọn video.")
            return

        if not self.is_playing:
            self.is_playing = True
            self.play_loop()

    def pause_video(self):
        self.is_playing = False

    def play_loop(self):
        if not self.is_playing or not self.cap:
            return

        success, frame = self.cap.read()
        if not success:
            self.is_playing = False
            return

        self.current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1
        self.display_frame(frame)

        current_time = self.current_frame / self.fps
        self.update_time_label(current_time)

        self.is_updating_slider = True
        self.slider.set(current_time)
        self.is_updating_slider = False

        delay = max(1, int(1000 / self.fps))
        self.root.after(delay, self.play_loop)

    def on_slider_move(self, value):
        if self.is_updating_slider or not self.cap:
            return

        self.pause_video()
        try:
            time_sec = float(value)
        except ValueError:
            return

        self.show_frame_at_time(time_sec)

    def seek_relative(self, seconds):
        if not self.cap:
            return

        self.pause_video()
        current_time = self.current_frame / self.fps
        new_time = current_time + seconds
        self.show_frame_at_time(new_time)

    def update_time_label(self, current_time):
        self.time_var.set(f"{self.format_time(current_time)} / {self.format_time(self.duration)}")

    @staticmethod
    def format_time(seconds):
        minutes = int(seconds // 60)
        sec = int(seconds % 60)
        centiseconds = int((seconds - int(seconds)) * 100)
        return f"{minutes:02d}:{sec:02d}.{centiseconds:02d}"

    def release_video(self):
        self.pause_video()
        if self.cap:
            self.cap.release()
            self.cap = None

    def on_close(self):
        self.release_video()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoCutToolStep1(root)
    root.mainloop()