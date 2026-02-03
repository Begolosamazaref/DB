from __future__ import annotations

import socket
from typing import Any, Iterable, List, Tuple

from .protocol import decode_message, encode_message


class KVClient:
    def __init__(self, host: str, port: int, timeout: float = 3.0) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout

    def _request(self, payload: dict) -> dict:
        with socket.create_connection((self.host, self.port), timeout=self.timeout) as sock:
            sock.sendall(encode_message(payload))
            buffer = b""
            while not buffer.endswith(b"\n"):
                chunk = sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk
        return decode_message(buffer)

    def get(self, key: str) -> Any:
        response = self._request({"op": "get", "key": key})
        return response.get("result")

    def set(self, key: str, value: Any) -> None:
        self._request({"op": "set", "key": key, "value": value})

    def delete(self, key: str) -> None:
        self._request({"op": "delete", "key": key})

    def bulk_set(self, items: Iterable[Tuple[str, Any]]) -> None:
        items_list = list(items)
        self._request({"op": "bulk_set", "items": items_list})

    def search_by_value(self, value: Any) -> list[str]:
        response = self._request({"op": "search_value", "value": value})
        return list(response.get("result", []))

    def search_text(self, term: str) -> list[str]:
        response = self._request({"op": "search_text", "term": term})
        return list(response.get("result", []))

    def add_vector(self, key: str, vector: list[float]) -> None:
        self._request({"op": "add_vector", "key": key, "vector": vector})

    def vector_search(self, vector: list[float], top_k: int = 5) -> list[dict]:
        response = self._request({"op": "vector_search", "vector": vector, "top_k": top_k})
        return list(response.get("result", []))
