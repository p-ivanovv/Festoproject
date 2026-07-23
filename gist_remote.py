import json
import threading
import time

import requests
from PyQt5.QtCore import QObject, pyqtSignal


COMMAND_FILENAME = "command.json"
STATUS_FILENAME = "status.json"
POLL_INTERVAL = 2  # seconds


def _headers(github_token: str) -> dict:
    return {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
    }


def _gist_url(gist_id: str) -> str:
    return f"https://api.github.com/gists/{gist_id}"


class GistRemoteListener(QObject):
    """Polls a GitHub Gist and emits newly received remote commands."""

    command_received = pyqtSignal(str, object)

    def __init__(self, gist_id: str, github_token: str):
        super().__init__()
        self._headers = _headers(github_token.strip())
        self._gist_url = _gist_url(gist_id.strip())
        self._last_command_id = None
        self._running = False
        self._thread = None
        self.last_processed_command_id = None

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
            except Exception as error:
                print(f"[GistRemote] Error polling gist: {error}")

            time.sleep(POLL_INTERVAL)

    def _check_once(self):
        response = requests.get(
            self._gist_url,
            headers=self._headers,
            timeout=10,
        )
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

        if (
            self._running
            and command_id is not None
            and command_id != self._last_command_id
        ):
            self._last_command_id = command_id
            self.last_processed_command_id = command_id
            self.command_received.emit(
                payload.get("cmd", ""),
                payload.get("value"),
            )


def push_status(status: dict, gist_id: str, github_token: str,
                last_command_id: str = None):
    """Writes the current desktop state into status.json asynchronously."""

    gist_id = gist_id.strip()
    github_token = github_token.strip()

    if not gist_id or not github_token:
        return

    if last_command_id is not None:
        status["ack_command_id"] = last_command_id

    gist_url = _gist_url(gist_id)
    headers = _headers(github_token)

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
                gist_url,
                headers=headers,
                json=body,
                timeout=10,
            )
            response.raise_for_status()

        except Exception as error:
            print(f"[GistRemote] Error pushing status: {error}")

    threading.Thread(target=_do_push, daemon=True).start()
