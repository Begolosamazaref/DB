from __future__ import annotations

import socket
import threading
from pathlib import Path

import pytest

from kvstore.client import KVClient
from kvstore.config import ClusterConfig
from kvstore.server import KVServer


@pytest.fixture()
def server(tmp_path: Path):
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    host, port = sock.getsockname()
    sock.close()

    config = ClusterConfig(node_id=1, host=host, port=port, data_dir=str(tmp_path))
    server = KVServer(config)

    thread = threading.Thread(target=server.start, daemon=True)
    thread.start()
    yield server
    server.shutdown()


def test_set_get(server: KVServer):
    client = KVClient(server.config.host, server.config.port)
    client.set("alpha", {"value": 1})
    assert client.get("alpha") == {"value": 1}


def test_set_delete_get(server: KVServer):
    client = KVClient(server.config.host, server.config.port)
    client.set("beta", 2)
    client.delete("beta")
    assert client.get("beta") is None


def test_get_missing(server: KVServer):
    client = KVClient(server.config.host, server.config.port)
    assert client.get("missing") is None


def test_overwrite(server: KVServer):
    client = KVClient(server.config.host, server.config.port)
    client.set("gamma", 1)
    client.set("gamma", 2)
    assert client.get("gamma") == 2
