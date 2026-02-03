from __future__ import annotations

import json
import os
import random
import threading
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List


@dataclass
class WALEntry:
    op: str
    data: Dict[str, Any]


class StorageEngine:
    def __init__(self, data_dir: str, drop_rate: float = 0.0) -> None:
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self._data_file = os.path.join(self.data_dir, "data.json")
        self._wal_file = os.path.join(self.data_dir, "wal.log")
        self._lock = threading.Lock()
        self.drop_rate = drop_rate

    def load(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        if os.path.exists(self._data_file):
            with open(self._data_file, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        if os.path.exists(self._wal_file):
            with open(self._wal_file, "r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    entry = json.loads(line)
                    self._apply_entry(data, entry)
        return data

    def append_wal(self, entry: WALEntry) -> None:
        encoded = json.dumps({"op": entry.op, "data": entry.data}, separators=(",", ":"))
        with self._lock:
            with open(self._wal_file, "a", encoding="utf-8") as handle:
                handle.write(encoded + "\n")
                handle.flush()
                os.fsync(handle.fileno())

    def save_snapshot(self, data: Dict[str, Any], simulate_drop: bool = False) -> None:
        if simulate_drop and self.drop_rate > 0.0:
            if random.random() < self.drop_rate:
                return
        temp_file = self._data_file + ".tmp"
        with self._lock:
            with open(temp_file, "w", encoding="utf-8") as handle:
                json.dump(data, handle)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_file, self._data_file)
            self._rotate_wal()

    def _rotate_wal(self) -> None:
        if os.path.exists(self._wal_file):
            os.remove(self._wal_file)

    @staticmethod
    def _apply_entry(data: Dict[str, Any], entry: Dict[str, Any]) -> None:
        op = entry.get("op")
        payload = entry.get("data", {})
        if op == "set":
            data[payload["key"]] = payload["value"]
        elif op == "delete":
            data.pop(payload["key"], None)
        elif op == "bulk_set":
            for key, value in payload["items"]:
                data[key] = value

    def replay_entries(self, entries: Iterable[WALEntry]) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        for entry in entries:
            self._apply_entry(data, {"op": entry.op, "data": entry.data})
        return data
