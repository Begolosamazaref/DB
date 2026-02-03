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


def test_bulk_set_atomic(tmp_path: Path):
    server = _start_server(tmp_path)
    client = KVClient(server.config.host, server.config.port)

    items_a = [("k1", "A1"), ("k2", "A2"), ("k3", "A3")]
    items_b = [("k1", "B1"), ("k2", "B2"), ("k3", "B3")]

    start = threading.Event()

    def worker(items):
        start.wait()
        client.bulk_set(items)

    t1 = threading.Thread(target=worker, args=(items_a,))
    t2 = threading.Thread(target=worker, args=(items_b,))
    t1.start()
    t2.start()
    start.set()
    t1.join()
    t2.join()

    values = {"k1": client.get("k1"), "k2": client.get("k2"), "k3": client.get("k3")}
    assert values in ({"k1": "A1", "k2": "A2", "k3": "A3"}, {"k1": "B1", "k2": "B2", "k3": "B3"})

    server.shutdown()
