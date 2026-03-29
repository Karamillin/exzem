from __future__ import annotations

import os
import socket
import threading
import time
import webbrowser

from waitress import serve

from app.main import app


def _wait_for_port_and_open(url: str, host: str, port: int) -> None:
    for _ in range(60):
        try:
            with socket.create_connection((host, port), timeout=0.5):
                webbrowser.open(url)
                return
        except OSError:
            time.sleep(0.2)


def main() -> None:
    host = os.getenv("ECZEMA_HOST", "127.0.0.1")
    port = int(os.getenv("ECZEMA_PORT", "8765"))
    url = f"http://{host}:{port}"

    opener = threading.Thread(
        target=_wait_for_port_and_open,
        args=(url, host, port),
        daemon=True,
    )
    opener.start()

    serve(app, host=host, port=port, threads=8)


if __name__ == "__main__":
    main()
