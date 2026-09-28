import os
import socket
import subprocess
import sys
import time
import webbrowser
from threading import Thread

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Check if a local TCP port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def find_pids_on_port(port: int) -> list:
    """Find all process IDs (PIDs) listening on or bound to the specified TCP port."""
    pids = set()
    current_pid = os.getpid()

    if sys.platform == "win32":
        try:
            output = subprocess.check_output(
                ["netstat", "-ano", "-p", "tcp"],
                text=True,
                stderr=subprocess.DEVNULL,
                encoding="utf-8",
                errors="ignore",
            )
            for line in output.splitlines():
                parts = line.strip().split()
                if len(parts) >= 5 and parts[0].upper() == "TCP":
                    local_addr = parts[1]
                    if local_addr.endswith(f":{port}"):
                        try:
                            pid = int(parts[-1])
                            if pid > 0 and pid != current_pid:
                                pids.add(pid)
                        except ValueError:
                            pass
        except Exception:
            pass
    else:
        try:
            output = subprocess.check_output(
                ["lsof", "-t", f"-i:{port}"],
                text=True,
                stderr=subprocess.DEVNULL,
            )
            for pid_str in output.split():
                try:
                    pid = int(pid_str)
                    if pid > 0 and pid != current_pid:
                        pids.add(pid)
                except ValueError:
                    pass
        except Exception:
            pass

    return sorted(list(pids))


def kill_process_on_port(port: int, max_wait: float = 2.0) -> bool:
    """
    Find and forcibly terminate any processes holding or listening on the specified TCP port.
    Waits up to max_wait seconds for the port to become available.
    Returns True if at least one process was terminated, False if port was already free.
    """
    pids = find_pids_on_port(port)
    if not pids:
        return False

    print(f"[*] Phát hiện tiến trình đang chiếm dụng cổng {port}: PID {pids}. Đang tắt...")
    killed_any = False
    for pid in pids:
        try:
            if sys.platform == "win32":
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(pid)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                )
            else:
                import signal
                os.kill(pid, signal.SIGKILL)
            killed_any = True
            print(f"[*] Đã tắt tiến trình PID {pid} giải phóng cổng {port}.")
        except Exception as e:
            print(f"[!] Không thể tắt tiến trình PID {pid}: {e}")

    # Wait for OS to release the socket
    start_time = time.time()
    while time.time() - start_time < max_wait:
        if not is_port_in_use(port):
            break
        time.sleep(0.1)

    return killed_any


def find_free_port(start_port: int = 5055, max_attempts: int = 20, host: str = "127.0.0.1") -> int:
    """Find the first available TCP port starting from start_port."""
    for p in range(start_port, start_port + max_attempts):
        if not is_port_in_use(p, host):
            return p
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, 0))
        return s.getsockname()[1]


def is_server_ready(url: str, timeout: float = 0.5) -> bool:
    try:
        import urllib.request
        req = urllib.request.Request(f"{url}/", headers={"User-Agent": "KTTC_FC_Launcher"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status in (200, 302, 304, 404)
    except Exception:
        return False


def get_default_browser_type() -> str:
    """Detect default browser type from Windows registry (ProgId)."""
    if sys.platform != "win32":
        return "default"
    try:
        import winreg
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice",
        ) as key:
            prog_id, _ = winreg.QueryValueEx(key, "ProgId")
            prog_id = prog_id.lower()
            if "chrome" in prog_id:
                return "chrome"
            if "edge" in prog_id:
                return "edge"
            if "firefox" in prog_id:
                return "firefox"
            if "brave" in prog_id:
                return "brave"
    except Exception:
        pass
    return "default"


def find_browser_app_cmd(url: str):
    """
    Look for Chrome or Edge executable and return command to run in App mode:
    --app=url --window-size=1600,950
    Crucially includes --no-proxy-server to prevent Windows/Edge loopback proxy refusal.
    """
    profile_dir = os.path.join(os.path.expanduser("~"), ".kttc_fc", "browser_profile")
    try:
        os.makedirs(profile_dir, exist_ok=True)
    except Exception:
        profile_dir = None

    app_flags = [
        f"--app={url}",
        "--window-size=1600,950",
        "--no-proxy-server",
        "--proxy-bypass-list=<-loopback>",
        "--allow-insecure-localhost",
        "--disable-features=IsolateOrigins,site-per-process",
    ]
    if profile_dir:
        app_flags.append(f"--user-data-dir={profile_dir}")

    chrome_paths = [
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
    ]
    edge_paths = [
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\Application\msedge.exe"),
    ]

    default_browser = get_default_browser_type()
    # Prioritize Chrome over Edge because Edge has strict AppContainer loopback isolation on Windows
    if default_browser == "edge":
        candidates = [edge_paths, chrome_paths]
    else:
        candidates = [chrome_paths, edge_paths]

    for path_group in candidates:
        for p in path_group:
            if os.path.exists(p):
                return [p] + app_flags

    return None


def launch_desktop_window(url: str):
    """
    Launch the app UI window using:
    1. pywebview if available
    2. Chrome / Edge in app window mode (--app=...)
    3. Default system browser as fallback
    """
    # 1. Try pywebview if installed
    try:
        import webview
        webview.create_window("KTTC_FC - Gán Nhãn & Cắt Video", url, width=1600, height=950)
        webview.start()
        return
    except (ImportError, Exception):
        pass

    # 2. Try Chrome / Edge in App Mode
    cmd = find_browser_app_cmd(url)
    if cmd:
        try:
            t0 = time.time()
            proc = subprocess.Popen(cmd)
            time.sleep(0.8)
            # If proc exited immediately with error, fallback to default browser
            if proc.poll() is not None and proc.poll() != 0:
                print("[!] Không thể mở ở chế độ App Mode, chuyển sang mở trình duyệt mặc định...")
                webbrowser.open(url)
                return

            if proc.poll() is None:
                try:
                    proc.wait()
                except KeyboardInterrupt:
                    try:
                        proc.terminate()
                    except Exception:
                        pass
                    return

            elapsed = time.time() - t0
            # If exited quickly (< 2.0s), it handed off to an existing instance
            if elapsed < 2.0:
                print("[*] Trình duyệt đã mở trong tiến trình nền. Máy chủ tiếp tục hoạt động...")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    pass
            return
        except Exception as e:
            print(f"[!] Lỗi khi mở cửa sổ App Mode: {e}")

    # 3. Fallback to default browser
    print("[*] Đang mở ứng dụng trên trình duyệt mặc định của bạn...")
    webbrowser.open(url)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass


def ensure_dependencies():
    """Ensure required dependencies (Flask, cv2, Pillow, etc.) are installed."""
    missing = []
    try:
        import flask
    except ImportError:
        missing.append("flask>=2.2.0")
    try:
        import cv2
    except ImportError:
        missing.append("opencv-python")
    try:
        from PIL import Image
    except ImportError:
        missing.append("Pillow")

    if missing:
        print(f"[*] Phat hien thieu thu vien: {', '.join(missing)}. Dang tu dong cai dat...")
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        req_file = os.path.join(root_dir, "requirements.txt")
        if os.path.exists(req_file):
            cmd = [sys.executable, "-m", "pip", "install", "-r", req_file]
        else:
            cmd = [sys.executable, "-m", "pip", "install"] + missing
        try:
            subprocess.check_call(cmd)
            print("[*] Cai dat thu vien thanh cong!")
        except Exception as e:
            print(f"[!] Khong the tu dong cai dat thu vien: {e}")
            print(f"[!] Vui long chay: {sys.executable} -m pip install -r requirements.txt")
            sys.exit(1)


def main():
    ensure_dependencies()

    default_port = 5055

    # Luôn kiểm tra và tắt mọi tác vụ tại port đó trước khi khởi động
    print(f"[*] Luôn giải phóng cổng {default_port} trước khi khởi động...")
    kill_process_on_port(default_port)

    # Đảm bảo có cổng khả dụng để chạy máy chủ
    if is_port_in_use(default_port):
        port = find_free_port(start_port=5056)
        print(f"[!] Cổng {default_port} vẫn bận sau khi giải phóng. Chuyển sang cổng dự phòng: {port}")
    else:
        port = default_port

    url = f"http://127.0.0.1:{port}"

    from tools.video_labeler.app import create_app
    app = create_app()

    # Bind host 0.0.0.0 so both 127.0.0.1 and localhost connect seamlessly
    server_thread = Thread(
        target=lambda: app.run(host="0.0.0.0", port=port, threaded=True),
        daemon=True,
    )
    server_thread.start()

    # Wait for server to start and become responsive to HTTP requests
    for _ in range(50):
        if is_server_ready(url, timeout=0.2):
            break
        time.sleep(0.1)

    print("\n=======================================================")
    print(f"  KTTC_FC VIDEO LABELER & SLICER ĐANG CHẠY TẠI:")
    print(f"  --> {url}  (hoặc http://localhost:{port})")
    print("  Nhấn Ctrl + C hoặc đóng cửa sổ ứng dụng để thoát.")
    print("=======================================================\n")

    launch_desktop_window(url)
    print("[*] Đã đóng cửa sổ ứng dụng. Kết thúc.")


if __name__ == "__main__":
    main()
