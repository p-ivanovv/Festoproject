import json
import threading
import time

import requests
from PyQt5.QtCore import QObject, pyqtSignal

# ── ПОПЪЛНИ ТУК ─────────────────────────────────────
GITHUB_TOKEN = "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"
GIST_ID = "f7892579389e55fdedac6544fccf2751"
# ─────────────────────────────────────────────────────

COMMAND_FILENAME = "command.json"
STATUS_FILENAME = "status.json"
POLL_INTERVAL = 2  # seconds

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}
GIST_URL = f"https://api.github.com/gists/{GIST_ID}"


class GistRemoteListener(QObject):
    """Polls a GitHub Gist and emits newly received remote commands."""

    command_received = pyqtSignal(str, object)

    def __init__(self):
        super().__init__()
        self._last_command_id = None
        self._running = False
        self._thread = None

    def start(self):
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _poll_loop(self):
        while self._running:
            try:
                self._check_once()
            except Exception as e:
                print(f"[GistRemote] Error polling gist: {e}")

            time.sleep(POLL_INTERVAL)

    def _check_once(self):
        response = requests.get(GIST_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()

        data = response.json()
        command_file = data.get("files", {}).get(COMMAND_FILENAME)

        if not command_file:
            return

        content = command_file.get("content", "")
        if not content:
            return

        payload = json.loads(content)
        command_id = payload.get("command_id")

        if command_id is not None and command_id != self._last_command_id:
            self._last_command_id = command_id
            self.command_received.emit(
                payload.get("cmd", ""),
                payload.get("value"),
            )


def push_status(status: dict):
    """Writes the current desktop state into status.json asynchronously."""

    def _do_push():
        try:
            body = {
                "files": {
                    STATUS_FILENAME: {
                        "content": json.dumps(status, ensure_ascii=False),
                    }
                }
            }

            response = requests.patch(
                GIST_URL,
                headers=HEADERS,
                json=body,
                timeout=10,
            )
            response.raise_for_status()

        except Exception as e:
            print(f"[GistRemote] Error pushing status: {e}")

    threading.Thread(target=_do_push, daemon=True).start()