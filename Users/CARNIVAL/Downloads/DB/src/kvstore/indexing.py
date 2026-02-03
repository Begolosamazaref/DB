from __future__ import annotations

from typing import Any, Dict, List


class SecondaryIndex:
    """Placeholder for value-based secondary indexes."""

    def __init__(self) -> None:
        self._index: Dict[Any, List[str]] = {}

    def add(self, key: str, value: Any) -> None:
        self._index.setdefault(value, []).append(key)

    def remove(self, key: str, value: Any) -> None:
        keys = self._index.get(value, [])
        if key in keys:
            keys.remove(key)
        if not keys and value in self._index:
            self._index.pop(value, None)

    def search(self, value: Any) -> List[str]:
        return list(self._index.get(value, []))


class InvertedIndex:
    """Placeholder for full-text inverted index support."""

    def __init__(self) -> None:
        self._index: Dict[str, List[str]] = {}

    def add_document(self, key: str, text: str) -> None:
        for token in text.split():
            self._index.setdefault(token.lower(), []).append(key)

    def remove_document(self, key: str, text: str) -> None:
        for token in text.split():
            token = token.lower()
            keys = self._index.get(token, [])
            while key in keys:
                keys.remove(key)
            if not keys and token in self._index:
                self._index.pop(token, None)

    def search(self, term: str) -> List[str]:
        return list(self._index.get(term.lower(), []))


class VectorIndex:
    """Placeholder for vector-based embedding search."""

    def __init__(self) -> None:
        self._vectors: Dict[str, List[float]] = {}

    def add_vector(self, key: str, vector: List[float]) -> None:
        self._vectors[key] = vector

    def remove_vector(self, key: str) -> None:
        self._vectors.pop(key, None)

    def items(self):
        return self._vectors.items()
