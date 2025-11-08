import json
import threading
from pathlib import Path

class SettingsStore:
    def __init__(self, path: str, defaults: dict):
        self.path = Path(path)
        self.defaults = defaults
        self._lock = threading.Lock()
        if not self.path.exists():
            self._write({})

    def _read(self):
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text("utf-8"))
        except Exception:
            return {}

    def _write(self, data: dict):
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), "utf-8")
        tmp.replace(self.path)

    def get(self, user_id: int) -> dict:
        with self._lock:
            data = self._read()
            s = data.get(str(user_id), {}).copy()
            out = self.defaults.copy()
            out.update(s)
            return out

    def set(self, user_id: int, settings: dict):
        with self._lock:
            data = self._read()
            data[str(user_id)] = settings
            self._write(data)

