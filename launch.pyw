"""Start Job Search Ledger and open it in its own window (pywebview) or the default browser.

Double-click on Windows (runs with pythonw, no console). Works on macOS and Linux too.
"""
import os
import socket
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOG = HERE / "data" / "launcher.log"


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def wait_ready(url, timeout=60):
    end = time.time() + timeout
    while time.time() < end:
        try:
            with urllib.request.urlopen(url + "/_stcore/health", timeout=2) as r:
                if r.status == 200:
                    return True
        except OSError:
            time.sleep(0.4)
    return False


def main():
    LOG.parent.mkdir(exist_ok=True)
    port = free_port()
    url = f"http://127.0.0.1:{port}"
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    python = Path(sys.executable)
    if python.name.lower() == "pythonw.exe":  # streamlit needs the console interpreter, hidden via CREATE_NO_WINDOW
        python = python.with_name("python.exe")
    with open(LOG, "w", encoding="utf-8") as log:
        server = subprocess.Popen(
            [str(python), "-m", "streamlit", "run", str(HERE / "app.py"), "--server.port", str(port),
             "--server.address", "127.0.0.1", "--server.headless", "true"],
            cwd=HERE, stdout=log, stderr=subprocess.STDOUT, creationflags=flags)
        try:
            if not wait_ready(url):
                raise SystemExit(f"Server did not start, see {LOG}")
            try:
                import webview  # pywebview
                webview.create_window("Job Search Ledger", url, width=1400, height=900, min_size=(1000, 700))
                webview.start()
            except ImportError:
                webbrowser.open(url)
                server.wait()
        finally:
            server.terminate()


if __name__ == "__main__":
    main()
