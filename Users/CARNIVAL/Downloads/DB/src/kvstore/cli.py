from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import ClusterConfig, NodeConfig
from .server import KVServer


def _load_peers(peers_json: str | None) -> list[NodeConfig] | None:
    if not peers_json:
        return None
    peers_data = json.loads(peers_json)
    return [NodeConfig(node_id=item["node_id"], host=item["host"], port=item["port"]) for item in peers_data]


def main() -> None:
    parser = argparse.ArgumentParser(description="KV Store Server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9000)
    parser.add_argument("--node-id", type=int, default=1)
    parser.add_argument("--data-dir", default="./data")
    parser.add_argument("--role", choices=["primary", "secondary"], default="primary")
    parser.add_argument("--mode", choices=["leader", "dynamo"], default="leader")
    parser.add_argument("--peers", help="JSON list of peers with node_id/host/port")
    parser.add_argument("--drop-rate", type=float, default=0.0)
    args = parser.parse_args()

    data_dir = Path(args.data_dir).resolve()
    config = ClusterConfig(
        node_id=args.node_id,
        host=args.host,
        port=args.port,
        data_dir=str(data_dir),
        role=args.role,
        mode=args.mode,
        peers=_load_peers(args.peers),
        drop_rate=args.drop_rate,
    )
    server = KVServer(config)
    try:
        server.start()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
