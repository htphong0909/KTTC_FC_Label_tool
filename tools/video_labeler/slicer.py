import os
import shutil
import subprocess
from pathlib import Path
from typing import Callable, Dict, List, Optional
import cv2

try:
    import imageio_ffmpeg
    _IMAGEIO_FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    _IMAGEIO_FFMPEG = None

LABEL_TOOL_MAP: Dict[str, str] = {
    "B1": "fast_connector",
    "B2": "kem_cat",
    "B3": "chuoi_oc_fc",
    "B4": "kem_tuot_vo_ftth",
    "B5": "kem_tuot_soi_3lo",
    "B6_clean": "chai_con_giay_lau",
    "B6_cut": "dao_cat_quang",
    "B7": "than_fc",
    "B8": "chuoi_oc_ren",
    "B9": "vo_xanh_fc",
}

# Also support alias names like B6a -> B6_clean, B6b -> B6_cut
LABEL_ALIASES: Dict[str, str] = {
    "B6a": "B6_clean",
    "B6b": "B6_cut",
}


def normalize_label(label: str) -> str:
    return LABEL_ALIASES.get(label, label)


def validate_events(events: List[Dict], duration_sec: float) -> List[str]:
    errors: List[str] = []
    for idx, ev in enumerate(events):
        lbl = ev.get("label", "Unknown")
        s = ev.get("start_sec")
        e = ev.get("end_sec")
        k = ev.get("key_sec")
        
        if s is None or e is None:
            errors.append(f"Sự kiện #{idx+1} ({lbl}): thiếu mốc start_sec hoặc end_sec")
            continue
        if s < 0.0:
            errors.append(f"Sự kiện #{idx+1} ({lbl}): start_sec ({s}) nhỏ hơn 0")
        if e > duration_sec + 0.1:
            errors.append(f"Sự kiện #{idx+1} ({lbl}): end_sec ({e}) vượt quá thời lượng video ({duration_sec})")
        if s >= e:
            errors.append(f"Sự kiện #{idx+1} ({lbl}): start_sec ({s}) >= end_sec ({e})")
        elif lbl != "B0":
            if k is None:
                errors.append(f"Sự kiện #{idx+1} ({lbl}): thiếu mốc then chốt key_sec")
            elif k <= s or k >= e:
                errors.append(f"Sự kiện #{idx+1} ({lbl}): key_sec ({k}) phải nằm trong khoảng ({s}, {e}) (không được trùng start hoặc end)")
    return errors


def _safe_float(val, default: float = 0.0) -> float:
    if val is None or val == "":
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def auto_fill_b0(events: List[Dict], duration_sec: float, min_gap_sec: float = 0.05) -> List[Dict]:
    """Sort active events chronologically and auto-fill B0 into all gaps."""
    # Filter out any existing B0 to recompute cleanly
    active_events = [e for e in events if e.get("label") != "B0"]
    active_events.sort(key=lambda x: _safe_float(x.get("start_sec"), 0.0))

    result: List[Dict] = []
    current_time = 0.0

    for ev in active_events:
        s = round(_safe_float(ev.get("start_sec"), 0.0), 3)
        e = round(_safe_float(ev.get("end_sec"), s), 3)
        k = round(_safe_float(ev.get("key_sec"), s), 3)
        lbl = normalize_label(ev.get("label", ""))

        if s - current_time > min_gap_sec:
            result.append({
                "label": "B0",
                "start_sec": round(current_time, 3),
                "end_sec": round(s, 3),
            })

        event_dict: Dict = {
            "label": lbl,
            "start_sec": s,
            "end_sec": e,
            "key_sec": k,
        }
        if lbl in LABEL_TOOL_MAP:
            event_dict["tool"] = LABEL_TOOL_MAP[lbl]
        result.append(event_dict)
        current_time = max(current_time, e)

    if duration_sec - current_time > min_gap_sec:
        result.append({
            "label": "B0",
            "start_sec": round(current_time, 3),
            "end_sec": round(duration_sec, 3),
        })

    return result


def generate_annotation_json(
    video_name: str,
    fps: float,
    duration_sec: float,
    events: List[Dict]
) -> Dict:
    filled_events = auto_fill_b0(events, duration_sec)
    return {
        "video_name": video_name,
        "fps": round(fps, 3),
        "duration_sec": round(duration_sec, 3),
        "events": filled_events,
    }


def get_ffmpeg_path() -> str:
    if _IMAGEIO_FFMPEG and Path(_IMAGEIO_FFMPEG).exists():
        return _IMAGEIO_FFMPEG
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg
    raise RuntimeError("Không tìm thấy binary ffmpeg trên hệ thống.")


def get_video_info(video_path: str) -> Dict[str, float]:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Không thể mở file video: {video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration_sec = total_frames / fps if fps > 0 else 0.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    cap.release()

    return {
        "fps": round(fps, 3),
        "total_frames": total_frames,
        "duration_sec": round(duration_sec, 3),
        "width": width,
        "height": height,
    }


def slice_video_clip(
    input_path: str,
    output_path: str,
    start_sec: float,
    end_sec: float,
    fast_copy: bool = False
) -> bool:
    ffmpeg_exe = get_ffmpeg_path()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    duration = max(0.01, end_sec - start_sec)
    cmd = [
        ffmpeg_exe,
        "-y",
        "-ss", f"{start_sec:.3f}",
        "-i", str(input_path),
        "-t", f"{duration:.3f}",
    ]

    if fast_copy:
        cmd.extend(["-c", "copy"])
    else:
        cmd.extend([
            "-c:v", "libx264",
            "-crf", "18",
            "-preset", "fast",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "128k",
        ])

    cmd.append(str(output_path))
    
    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    if proc.returncode != 0:
        print(f"Lỗi FFmpeg khi cắt {output_path}: {proc.stderr[:300]}")
        return False
    return True


def batch_slice_video(
    video_path: str,
    events: List[Dict],
    output_root: str,
    slice_b0: bool = False,
    fast_copy: bool = False,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> List[str]:
    video_stem = Path(video_path).stem
    out_files: List[str] = []
    
    target_events = [
        e for e in events 
        if slice_b0 or e.get("label") != "B0"
    ]
    total = len(target_events)

    for idx, ev in enumerate(target_events):
        lbl = ev.get("label", "clip")
        s = float(ev.get("start_sec", 0.0))
        e = float(ev.get("end_sec", 0.0))
        
        # Save to outputs/cut_clips/<label>/<video_stem>_<label>_<index>.mp4
        clip_name = f"{video_stem}_{lbl}_{idx+1:02d}.mp4"
        clip_path = Path(output_root) / lbl / clip_name
        
        if progress_callback:
            progress_callback(idx, total, f"Đang cắt [{lbl}] ({idx+1}/{total})")

        ok = slice_video_clip(video_path, str(clip_path), s, e, fast_copy=fast_copy)
        if ok:
            out_files.append(str(clip_path))

    if progress_callback:
        progress_callback(total, total, "Hoàn tất cắt video!")

    return out_files

