from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class NodeConfig:
    node_id: int
    host: str
    port: int


@dataclass
class ClusterConfig:
    node_id: int
    host: str
    port: int
    data_dir: str
    role: str = "primary"
    mode: str = "leader"
    peers: Optional[List[NodeConfig]] = None
    replication_timeout: float = 2.0
    election_interval: float = 0.5
    heartbeat_interval: float = 1.0
    drop_rate: float = 0.0

    def all_nodes(self) -> List[NodeConfig]:
        nodes = [NodeConfig(self.node_id, self.host, self.port)]
        if self.peers:
            nodes.extend(self.peers)
        return nodes
