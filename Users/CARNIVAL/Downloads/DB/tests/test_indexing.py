from __future__ import annotations

import socket
import threading
from pathlib import Path

from kvstore.client import KVClient
from kvstore.config import ClusterConfig
from kvstore.server import KVServer


def _start_server(tmp_path: Path):
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    host, port = sock.getsockname()
    sock.close()

    config = ClusterConfig(node_id=1, host=host, port=port, data_dir=str(tmp_path))
    server = KVServer(config)
    thread = threading.Thread(target=server.start, daemon=True)
    thread.start()
    return server


def test_secondary_index(tmp_path: Path):
    server = _start_server(tmp_path)
    client = KVClient(server.config.host, server.config.port)

    client.set("k1", "blue")
    client.set("k2", "blue")
    client.set("k3", "red")

    keys = set(client.search_by_value("blue"))
    assert keys == {"k1", "k2"}

    server.shutdown()


def test_inverted_index(tmp_path: Path):
    server = _start_server(tmp_path)
    client = KVClient(server.config.host, server.config.port)

    client.set("doc1", "hello world")
    client.set("doc2", {"text": "hello kv store"})

    keys = set(client.search_text("hello"))
    assert keys == {"doc1", "doc2"}

    server.shutdown()


def test_vector_index(tmp_path: Path):
    server = _start_server(tmp_path)
    client = KVClient(server.config.host, server.config.port)

    client.add_vector("v1", [1.0, 0.0])
    client.add_vector("v2", [0.0, 1.0])

    results = client.vector_search([1.0, 0.0], top_k=1)
    assert results[0]["key"] == "v1"

    server.shutdown()
