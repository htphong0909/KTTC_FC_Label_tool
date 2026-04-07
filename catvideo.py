import os
import re
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

import cv2
import imageio_ffmpeg
from PIL import Image, ImageTk


class VideoCutToolStep1:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Cut Tool - Step 2")
        self.root.geometry("1280x980")

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
        self.preview_resize_job = None
        self.step_sections = []
        self.segment_canvas = None
        self.segment_inner_frame = None
        self.segment_window_id = None

        self.segment_count_var = tk.StringVar(value="10")
        self.video_name_var = tk.StringVar(value="Chưa chọn video")
        self.time_var = tk.StringVar(value="00:00.00 / 00:00.00")

        self.build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def build_ui(self):
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill="x")
        top_frame.columnconfigure(1, weight=1)

        ttk.Button(top_frame, text="Chọn video", command=self.select_video).grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(top_frame, textvariable=self.video_name_var, width=60).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(top_frame, text="Số bước cần tạo:").grid(row=0, column=2, padx=(20, 5), pady=5, sticky="e")
        ttk.Entry(top_frame, textvariable=self.segment_count_var, width=10).grid(row=0, column=3, padx=5, pady=5, sticky="w")
        ttk.Button(top_frame, text="Tạo danh sách", command=self.refresh_segment_rows).grid(row=0, column=4, padx=5, pady=5, sticky="w")
        ttk.Button(top_frame, text="Cắt video", command=self.cut_segments).grid(row=0, column=5, padx=5, pady=5, sticky="w")

        self.preview_frame = ttk.Frame(self.root, padding=(10, 0, 10, 8), height=440)
        self.preview_frame.pack(fill="both", expand=True)
        self.preview_frame.pack_propagate(False)
        self.preview_frame.bind("<Configure>", self.on_preview_resize)

        self.video_label = tk.Label(
            self.preview_frame,
            bg=self.root.cget("bg"),
            bd=0,
            highlightthickness=0,
        )
        self.video_label.pack(fill="both", expand=True)

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

        self.build_segment_panel()
        self.refresh_segment_rows()

    def build_segment_panel(self):
        segment_outer = ttk.LabelFrame(self.root, text="Danh sách mốc thời gian", padding=10)
        segment_outer.pack(fill="x", expand=False, padx=10, pady=(0, 10))

        self.segment_canvas = tk.Canvas(segment_outer, height=300, highlightthickness=0)
        scrollbar = ttk.Scrollbar(segment_outer, orient="vertical", command=self.segment_canvas.yview)
        self.segment_inner_frame = ttk.Frame(self.segment_canvas)

        self.segment_inner_frame.bind("<Configure>", self.on_segment_frame_configure)
        self.segment_canvas.bind("<Configure>", self.on_segment_canvas_configure)
        self.segment_canvas.bind("<Enter>", self.bind_segment_mousewheel)
        self.segment_canvas.bind("<Leave>", self.unbind_segment_mousewheel)
        self.segment_inner_frame.bind("<Enter>", self.bind_segment_mousewheel)
        self.segment_inner_frame.bind("<Leave>", self.unbind_segment_mousewheel)

        self.segment_window_id = self.segment_canvas.create_window((0, 0), window=self.segment_inner_frame, anchor="nw")
        self.segment_canvas.configure(yscrollcommand=scrollbar.set)

        self.segment_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def on_preview_resize(self, _event=None):
        if self.preview_resize_job is not None:
            self.root.after_cancel(self.preview_resize_job)

        self.preview_resize_job = self.root.after(80, self.refresh_preview_after_resize)

    def refresh_preview_after_resize(self):
        self.preview_resize_job = None
        if not self.cap or self.is_playing or self.fps <= 0:
            return

        current_time = self.current_frame / self.fps
        self.show_frame_at_time(current_time)

    def refresh_segment_rows(self):
        try:
            count = int(self.segment_count_var.get().strip())
        except ValueError:
            messagebox.showerror("Lỗi", "Số bước cần tạo phải là số nguyên.")
            return

        if count <= 0:
            messagebox.showerror("Lỗi", "Số bước cần tạo phải lớn hơn 0.")
            return

        for widget in self.segment_inner_frame.winfo_children():
            widget.destroy()

        self.segment_inner_frame.columnconfigure(0, weight=1)
        self.step_sections = []

        for step_number in range(1, count + 1):
            self.create_step_section(step_number)

        self.on_segment_frame_configure()

    def create_step_section(self, step_number):
        container = ttk.Frame(self.segment_inner_frame, padding=(0, 0, 0, 8))
        container.grid(row=step_number - 1, column=0, sticky="ew")
        container.columnconfigure(0, weight=1)

        summary_frame = ttk.Frame(container)
        summary_frame.grid(row=0, column=0, sticky="ew")
        summary_frame.columnconfigure(1, weight=1)

        details_frame = ttk.Frame(container, padding=(18, 8, 0, 0))
        details_frame.grid(row=1, column=0, sticky="ew")
        details_frame.grid_remove()

        summary_var = tk.StringVar()
        toggle_var = tk.StringVar(value="Hiện")

        step = {
            "step_number": step_number,
            "container": container,
            "details_frame": details_frame,
            "segments": [],
            "summary_var": summary_var,
            "toggle_var": toggle_var,
            "toggle_button": None,
            "expanded": False,
            "is_adding_segment": False,
        }

        ttk.Label(summary_frame, text=f"B{step_number}", width=8).grid(
            row=0, column=0, padx=(0, 8), pady=4, sticky="w"
        )
        ttk.Label(summary_frame, textvariable=summary_var).grid(
            row=0, column=1, padx=(0, 8), pady=4, sticky="w"
        )
        ttk.Button(summary_frame, text="+", width=3, command=lambda step_ref=step: self.add_segment_row(step_ref)).grid(
            row=0, column=2, padx=(0, 6), pady=4
        )

        toggle_button = ttk.Button(
            summary_frame,
            textvariable=toggle_var,
            width=6,
            command=lambda step_ref=step: self.toggle_step_details(step_ref),
        )
        toggle_button.grid(row=0, column=3, pady=4, sticky="e")
        step["toggle_button"] = toggle_button

        separator = ttk.Separator(container, orient="horizontal")
        separator.grid(row=2, column=0, sticky="ew", pady=(6, 0))

        self.step_sections.append(step)
        self.update_step_summary(step)
        self.set_step_details_visibility(step, False)

    def toggle_step_details(self, step):
        if not step["segments"]:
            return

        self.set_step_details_visibility(step, not step["expanded"])

    def set_step_details_visibility(self, step, expanded):
        has_segments = bool(step["segments"])
        step["expanded"] = expanded and has_segments

        if step["expanded"]:
            step["details_frame"].grid()
        else:
            step["details_frame"].grid_remove()

        if has_segments:
            step["toggle_button"].state(["!disabled"])
        else:
            step["toggle_button"].state(["disabled"])

        step["toggle_var"].set("Ẩn" if step["expanded"] else "Hiện")
        self.on_segment_frame_configure()

    def add_segment_row(self, step, after_index=None):
        if step.get("is_adding_segment"):
            return

        step["is_adding_segment"] = True

        segment = {
            "start_var": tk.StringVar(),
            "end_var": tk.StringVar(),
            "duration_var": tk.StringVar(),
        }

        segment["start_var"].trace_add(
            "write",
            lambda *_args, step_ref=step, segment_ref=segment: self.update_segment_duration(step_ref, segment_ref),
        )
        segment["end_var"].trace_add(
            "write",
            lambda *_args, step_ref=step, segment_ref=segment: self.update_segment_duration(step_ref, segment_ref),
        )

        if after_index is None:
            insert_index = len(step["segments"])
        else:
            insert_index = max(0, min(after_index + 1, len(step["segments"])))

        try:
            step["segments"].insert(insert_index, segment)
            self.render_step_segments(step)
            self.set_step_details_visibility(step, True)
        finally:
            # The first expand can fire the + button twice in the same UI cycle.
            self.root.after_idle(lambda step_ref=step: step_ref.__setitem__("is_adding_segment", False))

    def remove_segment_row(self, step, segment):
        if segment not in step["segments"]:
            return

        step["segments"].remove(segment)
        self.render_step_segments(step)
        self.set_step_details_visibility(step, step["expanded"])

    def render_step_segments(self, step):
        details_frame = step["details_frame"]

        for widget in details_frame.winfo_children():
            widget.destroy()

        if not step["segments"]:
            self.update_step_summary(step)
            self.on_segment_frame_configure()
            return

        headers = [
            ("Đoạn", 10),
            ("Start", 14),
            ("End", 14),
            ("Thời lượng", 14),
            ("Thao tác", 0),
        ]

        for column, (label_text, width) in enumerate(headers):
            label_kwargs = {"text": label_text}
            if width:
                label_kwargs["width"] = width
            ttk.Label(details_frame, **label_kwargs).grid(row=0, column=column, padx=5, pady=4, sticky="w")

        ttk.Label(details_frame, text="", width=6).grid(row=0, column=5, padx=3, pady=4)

        for segment_index, segment in enumerate(step["segments"], start=1):
            row_index = segment_index

            ttk.Label(details_frame, text=f"Đoạn {segment_index}", width=10).grid(
                row=row_index, column=0, padx=5, pady=4, sticky="w"
            )
            ttk.Entry(details_frame, textvariable=segment["start_var"], width=14).grid(
                row=row_index, column=1, padx=5, pady=4, sticky="w"
            )
            ttk.Entry(details_frame, textvariable=segment["end_var"], width=14).grid(
                row=row_index, column=2, padx=5, pady=4, sticky="w"
            )
            ttk.Label(details_frame, textvariable=segment["duration_var"], width=14).grid(
                row=row_index, column=3, padx=5, pady=4, sticky="w"
            )

            action_frame = ttk.Frame(details_frame)
            action_frame.grid(row=row_index, column=4, padx=5, pady=4, sticky="w")

            ttk.Button(
                action_frame,
                text="Lấy start",
                command=lambda segment_ref=segment: self.capture_time(segment_ref, "start"),
            ).pack(side="left", padx=(0, 5))
            ttk.Button(
                action_frame,
                text="Lấy end",
                command=lambda segment_ref=segment: self.capture_time(segment_ref, "end"),
            ).pack(side="left")

            ttk.Button(
                details_frame,
                text="Xóa",
                width=6,
                command=lambda step_ref=step, segment_ref=segment: self.remove_segment_row(step_ref, segment_ref),
            ).grid(row=row_index, column=5, padx=3, pady=4)

        self.update_step_summary(step)
        self.on_segment_frame_configure()

    def capture_time(self, segment, target):
        if not self.cap:
            messagebox.showwarning("Thông báo", "Bạn chưa chọn video.")
            return

        current_time = self.current_frame / self.fps if self.fps > 0 else 0
        value = self.format_time(current_time)

        if target == "start":
            segment["start_var"].set(value)
        else:
            segment["end_var"].set(value)

    def on_segment_frame_configure(self, _event=None):
        if not self.segment_canvas:
            return

        self.segment_canvas.configure(scrollregion=self.segment_canvas.bbox("all") or (0, 0, 0, 0))

    def on_segment_canvas_configure(self, event):
        if self.segment_canvas and self.segment_window_id is not None:
            self.segment_canvas.itemconfigure(self.segment_window_id, width=event.width)

    def bind_segment_mousewheel(self, _event=None):
        if not self.segment_canvas:
            return

        self.segment_canvas.bind_all("<MouseWheel>", self.on_segment_mousewheel)
        self.segment_canvas.bind_all("<Button-4>", self.on_segment_mousewheel)
        self.segment_canvas.bind_all("<Button-5>", self.on_segment_mousewheel)

    def unbind_segment_mousewheel(self, _event=None):
        if not self.segment_canvas:
            return

        self.segment_canvas.unbind_all("<MouseWheel>")
        self.segment_canvas.unbind_all("<Button-4>")
        self.segment_canvas.unbind_all("<Button-5>")

    def on_segment_mousewheel(self, event):
        if not self.segment_canvas:
            return

        if getattr(event, "delta", 0):
            step = -1 if event.delta > 0 else 1
        elif getattr(event, "num", None) == 4:
            step = -1
        elif getattr(event, "num", None) == 5:
            step = 1
        else:
            return

        self.segment_canvas.yview_scroll(step, "units")

    def update_segment_duration(self, step, segment):
        start_text = segment["start_var"].get().strip()
        end_text = segment["end_var"].get().strip()

        if not start_text or not end_text:
            segment["duration_var"].set("")
            self.update_step_summary(step)
            return

        try:
            start_sec = self.parse_time_text(start_text)
            end_sec = self.parse_time_text(end_text)
        except ValueError:
            segment["duration_var"].set("Sai định dạng")
            self.update_step_summary(step)
            return

        if end_sec <= start_sec:
            segment["duration_var"].set("Không hợp lệ")
            self.update_step_summary(step)
            return

        if self.duration > 0 and end_sec > self.duration:
            segment["duration_var"].set("Vượt video")
            self.update_step_summary(step)
            return

        segment["duration_var"].set(self.format_time(end_sec - start_sec))
        self.update_step_summary(step)

    def update_step_summary(self, step):
        segment_count = len(step["segments"])

        if segment_count == 0:
            step["summary_var"].set("Chưa có đoạn nào. Nhấn + để thêm.")
            return

        valid_count = 0
        total_duration = 0

        for segment in step["segments"]:
            time_range = self.try_get_segment_range(segment)
            if not time_range:
                continue

            start_sec, end_sec = time_range
            valid_count += 1
            total_duration += end_sec - start_sec

        if valid_count == segment_count:
            step["summary_var"].set(f"{segment_count} đoạn | Tổng {self.format_time(total_duration)}")
        else:
            step["summary_var"].set(f"{segment_count} đoạn | Đã hoàn chỉnh {valid_count}/{segment_count}")

    def try_get_segment_range(self, segment):
        start_text = segment["start_var"].get().strip()
        end_text = segment["end_var"].get().strip()

        if not start_text or not end_text:
            return None

        try:
            start_sec = self.parse_time_text(start_text)
            end_sec = self.parse_time_text(end_text)
        except ValueError:
            return None

        if start_sec < 0 or end_sec <= start_sec:
            return None

        if self.duration > 0 and end_sec > self.duration:
            return None

        return start_sec, end_sec

    def reset_step_segments(self):
        for step in self.step_sections:
            step["segments"].clear()
            step["is_adding_segment"] = False
            self.render_step_segments(step)
            self.set_step_details_visibility(step, False)

        self.on_segment_frame_configure()

    @staticmethod
    def get_next_clip_number():
        max_clip_number = 199
        pattern = re.compile(r"^clip(\d+)-b[\d.]+(?:-\d+)?\.mp4$", re.IGNORECASE)

        data_dir = "data"
        if not os.path.isdir(data_dir):
            return max_clip_number + 1

        for _root_dir, _, files in os.walk(data_dir):
            for file_name in files:
                match = pattern.match(file_name)
                if not match:
                    continue

                max_clip_number = max(max_clip_number, int(match.group(1)))

        return max_clip_number + 1

    def ensure_ffmpeg(self):
        try:
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception as exc:
            raise RuntimeError(f"Không lấy được ffmpeg từ imageio-ffmpeg: {exc}") from exc

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
        seconds_text = parts[1].strip().replace(",", ".")

        minutes = int(minutes_text)
        seconds = float(seconds_text)

        if minutes < 0 or seconds < 0 or seconds >= 60:
            raise ValueError("Thời gian không hợp lệ.")

        return minutes * 60 + seconds

    def collect_segments_for_cut(self):
        steps_payload = []
        total_segments = 0

        for step in self.step_sections:
            step_number = step["step_number"]
            step_segments = []

            for segment_index, segment in enumerate(step["segments"], start=1):
                start_text = segment["start_var"].get().strip()
                end_text = segment["end_var"].get().strip()

                if not start_text or not end_text:
                    raise ValueError(f"Thiếu thời gian ở B{step_number} - đoạn {segment_index}.")

                try:
                    start_sec = self.parse_time_text(start_text)
                    end_sec = self.parse_time_text(end_text)
                except ValueError as exc:
                    raise ValueError(
                        f"Thời gian ở B{step_number} - đoạn {segment_index} chưa đúng định dạng mm:ss.xx."
                    ) from exc

                if end_sec <= start_sec:
                    raise ValueError(f"End phải lớn hơn Start ở B{step_number} - đoạn {segment_index}.")

                if end_sec > self.duration:
                    raise ValueError(
                        f"End ở B{step_number} - đoạn {segment_index} đang vượt quá thời lượng video."
                    )

                step_segments.append((segment_index, start_sec, end_sec))

            if step_segments:
                steps_payload.append((step_number, step_segments))
                total_segments += len(step_segments)

        if total_segments == 0:
            raise ValueError("Chưa có đoạn nào để cắt.")

        return steps_payload, total_segments

    def prompt_output_base_name(self):
        suggested_name = f"clip{self.get_next_clip_number()}"
        invalid_chars = '<>:"/\\|?*'

        while True:
            base_name = simpledialog.askstring(
                "Đặt tên clip",
                "Nhập tên gốc cho loạt clip đã cắt:",
                initialvalue=suggested_name,
                parent=self.root,
            )

            if base_name is None:
                return None

            base_name = base_name.strip()
            if base_name.lower().endswith(".mp4"):
                base_name = base_name[:-4].strip()

            if not base_name:
                messagebox.showerror("Lỗi", "Tên clip không được để trống.")
                continue

            if any(char in invalid_chars for char in base_name):
                messagebox.showerror("Lỗi", "Tên clip chứa ký tự không hợp lệ cho file trên Windows.")
                continue

            return base_name

    @staticmethod
    def build_output_name(base_name, step_number, sequence_number):
        suffix = "" if sequence_number == 1 else f"-{sequence_number}"
        return f"{base_name}-b{step_number}{suffix}.mp4"

    def collect_output_paths(self, base_name, steps_payload):
        output_paths = []

        for step_number, step_segments in steps_payload:
            output_dir = os.path.join("data", f"B{step_number}")
            for sequence_number, _segment_data in enumerate(step_segments, start=1):
                output_name = self.build_output_name(base_name, step_number, sequence_number)
                output_paths.append(os.path.join(output_dir, output_name))

        return output_paths

    def cut_segments(self):
        if not self.video_path:
            messagebox.showwarning("Thông báo", "Bạn chưa chọn video.")
            return

        if not self.step_sections:
            messagebox.showwarning("Thông báo", "Chưa có danh sách bước.")
            return

        self.pause_video()

        try:
            ffmpeg_path = self.ensure_ffmpeg()
            steps_payload, total_segments = self.collect_segments_for_cut()
            base_name = self.prompt_output_base_name()
            if base_name is None:
                return

            existing_outputs = [
                output_path for output_path in self.collect_output_paths(base_name, steps_payload)
                if os.path.exists(output_path)
            ]
            if existing_outputs:
                should_overwrite = messagebox.askyesno(
                    "Ghi đè file",
                    f"Đã có {len(existing_outputs)} file trùng tên. Bạn có muốn ghi đè không?",
                )
                if not should_overwrite:
                    return

            self.root.config(cursor="watch")
            self.root.update_idletasks()

            for step_number, step_segments in steps_payload:
                output_dir = os.path.join("data", f"B{step_number}")
                os.makedirs(output_dir, exist_ok=True)

                for sequence_number, (_segment_index, start_sec, end_sec) in enumerate(step_segments, start=1):
                    output_name = self.build_output_name(base_name, step_number, sequence_number)
                    output_path = os.path.join(output_dir, output_name)

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
                            f"Bước: B{step_number}",
                            f"Lần cắt: {sequence_number}",
                            f"Return code: {result.returncode}",
                            f"Command: {' '.join(cmd)}",
                            "",
                            "STDOUT:",
                            result.stdout.strip(),
                            "",
                            "STDERR:",
                            result.stderr.strip()
                        ]).strip()

                        output_stem, _ = os.path.splitext(output_name)
                        log_path = os.path.join(output_dir, f"{output_stem}_ffmpeg_error.txt")
                        with open(log_path, "w", encoding="utf-8") as file_obj:
                            file_obj.write(debug_text)

                        stderr_preview = result.stderr.strip()
                        if not stderr_preview:
                            stderr_preview = "FFmpeg không trả stderr. Hãy mở file log để xem command đã chạy."

                        raise RuntimeError(
                            f"B{step_number} lỗi ở clip thứ {sequence_number}.\n"
                            f"Log đã lưu: {log_path}\n\n"
                            f"{stderr_preview[:2000]}"
                        )

            messagebox.showinfo("Hoàn tất", f"Đã cắt xong {total_segments} clip.\nTên gốc: {base_name}")
        except Exception as exc:
            messagebox.showerror("Lỗi", f"Cắt video thất bại: {exc}")
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

        self.reset_step_segments()
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

        box_width = int(self.preview_frame.winfo_width() * 0.96)
        box_height = int(self.preview_frame.winfo_height() * 0.96)

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
        total_centiseconds = max(0, int(round(seconds * 100)))
        minutes = total_centiseconds // 6000
        sec = (total_centiseconds % 6000) // 100
        centiseconds = total_centiseconds % 100
        return f"{minutes:02d}:{sec:02d}.{centiseconds:02d}"

    def release_video(self):
        self.pause_video()
        if self.preview_resize_job is not None:
            self.root.after_cancel(self.preview_resize_job)
            self.preview_resize_job = None

        if self.cap:
            self.cap.release()
            self.cap = None

        self.video_path = ""
        self.fps = 0
        self.frame_count = 0
        self.duration = 0
        self.current_frame = 0
        self.frame_image = None

        if self.video_label:
            self.video_label.config(image="")

        if hasattr(self, "slider"):
            self.slider.configure(to=0.01)
            self.slider.set(0)

        self.video_name_var.set("Chưa chọn video")
        self.time_var.set("00:00.00 / 00:00.00")

    def on_close(self):
        self.release_video()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoCutToolStep1(root)
    root.mainloop()
