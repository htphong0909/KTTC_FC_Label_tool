import json
import mimetypes
import os
import re
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict
from flask import Flask, Response, jsonify, render_template, request, send_file

from tools.video_labeler import config
from tools.video_labeler.slicer import (
    auto_fill_b0,
    batch_slice_video,
    generate_annotation_json,
    get_video_info,
    validate_events,
)

slicing_jobs: Dict[str, Dict] = {}
executor = ThreadPoolExecutor(max_workers=2)


def create_app(test_config=None) -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    if test_config:
        app.config.update(test_config)

    ann_dir = Path(app.config.get("ANNOTATION_DIR", config.ANNOTATION_DIR) if test_config else config.ANNOTATION_DIR)
    cuts_dir = Path(app.config.get("CUT_CLIPS_DIR", config.CUT_CLIPS_DIR) if test_config else config.CUT_CLIPS_DIR)
    ann_dir.mkdir(parents=True, exist_ok=True)
    cuts_dir.mkdir(parents=True, exist_ok=True)

    @app.route("/")
    def index():
        try:
            return render_template("index.html")
        except Exception:
            return "Video Labeler API Ready", 200

    @app.route("/api/videos")
    def list_videos():
        folder_str = request.args.get("folder", str(config.DEFAULT_VIDEO_DIR))
        folder_path = Path(folder_str)
        if not folder_path.is_absolute():
            folder_path = (config.BASE_DIR / folder_path).resolve()

        if not folder_path.exists():
            return jsonify({"error": f"Thư mục không tồn tại: {folder_str}", "videos": []}), 404

        video_files = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                ext = Path(file).suffix.lower()
                if ext in config.ALLOWED_VIDEO_EXTS:
                    full_p = Path(root) / file
                    try:
                        rel_p = str(full_p.relative_to(config.BASE_DIR)).replace("\\", "/")
                    except ValueError:
                        rel_p = str(full_p).replace("\\", "/")
                    stem = full_p.stem
                    
                    ann_file = ann_dir / f"{stem}.json"
                    has_ann = ann_file.exists()
                    
                    status = "not_annotated"
                    if has_ann:
                        try:
                            with open(ann_file, "r", encoding="utf-8") as f:
                                d = json.load(f)
                                active = [e for e in d.get("events", []) if e.get("label") != "B0"]
                                status = "annotated" if len(active) >= 8 else "in_progress"
                        except Exception:
                            status = "annotated"

                    video_files.append({
                        "name": file,
                        "rel_path": rel_p,
                        "abs_path": str(full_p).replace("\\", "/"),
                        "size_bytes": full_p.stat().st_size,
                        "status": status,
                    })

        video_files.sort(key=lambda x: x["name"])
        return jsonify({"folder": str(folder_path), "videos": video_files, "total": len(video_files)})

    @app.route("/api/video_info")
    def video_info():
        p = request.args.get("path")
        if not p:
            return jsonify({"error": "Thiếu tham số path"}), 400
        full_p = (config.BASE_DIR / p).resolve() if not Path(p).is_absolute() else Path(p)
        if not full_p.exists():
            return jsonify({"error": "File không tồn tại"}), 404
        try:
            info = get_video_info(str(full_p))
            return jsonify(info)
        except Exception as e:
            return jsonify({"error": f"Lỗi đọc video: {str(e)}"}), 500

    @app.route("/api/stream_video")
    def stream_video():
        p = request.args.get("path")
        if not p:
            return "Thiếu path", 400
        full_p = (config.BASE_DIR / p).resolve() if not Path(p).is_absolute() else Path(p)
        if not full_p.exists():
            return "File không tồn tại", 404

        file_size = full_p.stat().st_size
        range_header = request.headers.get("Range", None)
        mime_type, _ = mimetypes.guess_type(str(full_p))
        mime_type = mime_type or "video/mp4"

        if not range_header or file_size == 0:
            resp = send_file(full_p, mimetype=mime_type)
            resp.headers["Accept-Ranges"] = "bytes"
            resp.headers["Cache-Control"] = "public, max-age=86400"
            return resp

        byte1, byte2 = 0, None
        match = re.search(r"bytes=(\d+)-(\d*)", range_header)
        if match:
            g = match.groups()
            byte1 = int(g[0])
            if g[1]:
                byte2 = int(g[1])

        if byte2 is not None and byte1 > byte2:
            return Response(status=416)

        if byte1 >= file_size:
            rv = Response(status=416)
            rv.headers.add("Content-Range", f"bytes */{file_size}")
            return rv

        if byte2 is None:
            byte2 = min(byte1 + 2 * 1024 * 1024 - 1, file_size - 1)  # 2MB chunks for smooth scrub
        else:
            byte2 = min(byte2, file_size - 1)

        length = byte2 - byte1 + 1

        with open(full_p, "rb") as f:
            f.seek(byte1)
            data = f.read(length)

        rv = Response(data, 206, mimetype=mime_type, direct_passthrough=True)
        rv.headers.add("Content-Range", f"bytes {byte1}-{byte2}/{file_size}")
        rv.headers.add("Accept-Ranges", "bytes")
        rv.headers.add("Content-Length", str(length))
        rv.headers.add("Cache-Control", "public, max-age=86400")
        return rv

    @app.route("/api/annotation", methods=["GET", "POST"])
    def handle_annotation():
        if request.method == "GET":
            p = request.args.get("path")
            if not p:
                return jsonify({"error": "Thiếu path"}), 400
            stem = Path(p).stem
            ann_file = ann_dir / f"{stem}.json"
            if not ann_file.exists():
                return jsonify({"status": "not_found", "annotation": None})
            with open(ann_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return jsonify({"status": "ok", "annotation": data})

        # POST: save
        payload = request.get_json() or {}
        video_path = payload.get("video_path")
        if not video_path:
            return jsonify({"error": "Thiếu video_path"}), 400
        
        video_stem = Path(video_path).stem
        video_name = Path(video_path).name
        try:
            fps = float(payload.get("fps", 30.0))
            duration_sec = float(payload.get("duration_sec", 0.0))
        except (ValueError, TypeError):
            return jsonify({"status": "error", "errors": ["fps hoặc duration_sec không hợp lệ (phải là số)"]}), 400
        events = payload.get("events", [])

        # Validate
        errors = validate_events(events, duration_sec)
        if errors:
            return jsonify({"status": "error", "errors": errors}), 400

        data = generate_annotation_json(video_name, fps, duration_sec, events)
        
        # Atomic save
        ann_file = ann_dir / f"{video_stem}.json"
        tmp_file = ann_dir / f"{video_stem}.json.tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        tmp_file.replace(ann_file)

        return jsonify({"status": "ok", "saved_path": str(ann_file)})

    @app.route("/api/slice", methods=["POST"])
    def trigger_slice():
        payload = request.get_json() or {}
        video_path = payload.get("video_path")
        if not video_path:
            return jsonify({"error": "Thiếu video_path"}), 400

        events = payload.get("events", [])
        slice_b0 = bool(payload.get("slice_b0", False))
        fast_copy = bool(payload.get("fast_copy", False))

        full_p = (config.BASE_DIR / video_path).resolve() if not Path(video_path).is_absolute() else Path(video_path)
        if not full_p.exists():
            return jsonify({"error": "File video không tồn tại"}), 404

        job_id = str(uuid.uuid4())
        slicing_jobs[job_id] = {
            "status": "running",
            "progress": 0,
            "total": len(events),
            "message": "Đang khởi tạo...",
            "clips": [],
        }

        def run_slice():
            def cb(curr, total, msg):
                slicing_jobs[job_id]["progress"] = int((curr / max(1, total)) * 100)
                slicing_jobs[job_id]["message"] = msg

            try:
                clips = batch_slice_video(
                    str(full_p),
                    events,
                    str(cuts_dir),
                    slice_b0=slice_b0,
                    fast_copy=fast_copy,
                    progress_callback=cb,
                )
                slicing_jobs[job_id]["status"] = "finished"
                slicing_jobs[job_id]["progress"] = 100
                slicing_jobs[job_id]["clips"] = clips
                slicing_jobs[job_id]["message"] = f"Đã cắt thành công {len(clips)} clips!"
            except Exception as ex:
                slicing_jobs[job_id]["status"] = "failed"
                slicing_jobs[job_id]["message"] = f"Lỗi: {str(ex)}"

        executor.submit(run_slice)
        return jsonify({"status": "started", "job_id": job_id})

    @app.route("/api/slice_progress")
    def slice_progress():
        job_id = request.args.get("job_id")
        if not job_id or job_id not in slicing_jobs:
            return jsonify({"status": "not_found"}), 404
        return jsonify(slicing_jobs[job_id])

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=config.DEFAULT_PORT, debug=True)
