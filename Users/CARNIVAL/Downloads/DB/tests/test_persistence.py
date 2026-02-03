from __future__ import annotations

import socket
import threading
from pathlib import Path

from kvstore.client import KVClient
from kvstore.config import ClusterConfig
from kvstore.server import KVServer


def _start_server(data_dir: Path):
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    host, port = sock.getsockname()
    sock.close()

    config = ClusterConfig(node_id=1, host=host, port=port, data_dir=str(data_dir))
    server = KVServer(config)
    thread = threading.Thread(target=server.start, daemon=True)
    thread.start()
    return server


def test_persistence(tmp_path: Path):
    server = _start_server(tmp_path)
    client = KVClient(server.config.host, server.config.port)
    client.set("persist", "yes")
    server.shutdown()

    server = _start_server(tmp_path)
    client = KVClient(server.config.host, server.config.port)
    assert client.get("persist") == "yes"
    server.shutdown()
