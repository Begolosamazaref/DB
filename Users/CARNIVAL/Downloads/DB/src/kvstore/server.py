from __future__ import annotations

import json
import socketserver
from typing import Any, Dict, Optional

from .config import ClusterConfig
from .engine import KVEngine
from .protocol import ProtocolError, decode_message, encode_message
from .replication import LeaderElector, ReplicationEvent, Replicator, ServerState


class KVRequestHandler(socketserver.StreamRequestHandler):
    server: "KVServer"

    def handle(self) -> None:
        raw = self.rfile.readline()
        if not raw:
            return
        try:
            request = decode_message(raw)
        except ProtocolError as exc:
            self.wfile.write(encode_message({"status": "error", "error": str(exc)}))
            return
        response = self.server.handle_request(request)
        self.wfile.write(encode_message(response))


class KVServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

    def __init__(self, config: ClusterConfig) -> None:
        self.config = config
        self.state = ServerState(config.role)
        self.engine = KVEngine(config.data_dir, drop_rate=config.drop_rate)
        self.replicator = Replicator(config)
        self.elector = LeaderElector(config, self.state)
        super().__init__((config.host, config.port), KVRequestHandler)

    def start(self) -> None:
        self.replicator.start()
        self.elector.start()
        self.serve_forever()

    def shutdown(self) -> None:
        self.replicator.stop()
        self.elector.stop()
        super().shutdown()
        self.server_close()

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        op = request.get("op")
        if op == "who_is_primary":
            return {"status": "ok", "role": self.state.get_role()}
        if op == "promote":
            self.state.set_role("primary")
            return {"status": "ok"}
        if op == "replicate":
            event = request.get("event", {})
            self.engine.apply_replication(event.get("op"), event.get("payload", {}))
            return {"status": "ok"}
        if self.config.mode == "leader" and self.state.get_role() != "primary":
            return {"status": "error", "error": "not_primary"}
        try:
            return self._handle_primary(op, request)
        except Exception as exc:  # noqa: BLE001
            return {"status": "error", "error": str(exc)}

    def _handle_primary(self, op: Optional[str], request: Dict[str, Any]) -> Dict[str, Any]:
        if op == "get":
            value = self.engine.get(request["key"])
            return {"status": "ok", "result": value}
        if op == "set":
            self.engine.set(request["key"], request["value"], simulate_drop=bool(request.get("simulate_drop")))
            self.replicator.enqueue(ReplicationEvent(op="set", payload={"key": request["key"], "value": request["value"]}))
            return {"status": "ok"}
        if op == "delete":
            self.engine.delete(request["key"], simulate_drop=bool(request.get("simulate_drop")))
            self.replicator.enqueue(ReplicationEvent(op="delete", payload={"key": request["key"]}))
            return {"status": "ok"}
        if op == "bulk_set":
            items = request.get("items", [])
            self.engine.bulk_set(items, simulate_drop=bool(request.get("simulate_drop")))
            self.replicator.enqueue(ReplicationEvent(op="bulk_set", payload={"items": items}))
            return {"status": "ok"}
        if op == "search_value":
            keys = self.engine.search_by_value(request.get("value"))
            return {"status": "ok", "result": keys}
        if op == "search_text":
            term = request.get("term", "")
            keys = self.engine.search_text(term)
            return {"status": "ok", "result": keys}
        if op == "add_vector":
            self.engine.add_vector(request["key"], request["vector"], simulate_drop=bool(request.get("simulate_drop")))
            self.replicator.enqueue(ReplicationEvent(op="add_vector", payload={"key": request["key"], "vector": request["vector"]}))
            return {"status": "ok"}
        if op == "vector_search":
            vector = request.get("vector", [])
            top_k = int(request.get("top_k", 5))
            results = self.engine.vector_search(vector, top_k=top_k)
            return {"status": "ok", "result": results}
        return {"status": "error", "error": f"unknown op: {op}"}
