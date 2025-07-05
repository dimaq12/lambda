#@module:
#@  version: "0.3"
#@  layer: graph
#@  exposes: [load_graph_from_file, save_graph_to_file]
#@  doc: Helpers for loading and saving Graph objects from YAML or JSON files.
#@end
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import Graph
from ..core.node import LambdaNode

try:  # optional dependency
    import yaml  # type: ignore

    def _load(path: str) -> Any:
        return yaml.safe_load(Path(path).read_text())

    def _dump(data: Any, path: str) -> None:
        Path(path).write_text(yaml.safe_dump(data))
except Exception:  # pragma: no cover - fallback when PyYAML not installed
    def _load(path: str) -> Any:
        return json.loads(Path(path).read_text())

    def _dump(data: Any, path: str) -> None:
        Path(path).write_text(json.dumps(data))


def load_graph_from_file(path: str) -> Graph:
    """Return a :class:`Graph` loaded from ``path``."""
    data = _load(path)
    nodes: list[LambdaNode] = []
    for spec in data.get("nodes", []):
        node = LambdaNode(spec.get("label"), spec.get("data"), [], raw=spec.get("raw", False))
        nodes.append(node)
    for node, spec in zip(nodes, data.get("nodes", [])):
        for target in spec.get("links", []):
            node.add_link(nodes[target])
    return Graph(nodes)


def save_graph_to_file(graph: Graph, path: str) -> None:
    """Persist ``graph`` to ``path`` in YAML or JSON format."""
    spec = {"nodes": []}
    for node in graph.nodes:
        links = [graph.nodes.index(l) for l in node.links if l in graph.nodes]
        node_spec = {"label": node.label, "data": node.data, "links": links}
        if node.raw:
            node_spec["raw"] = True
        spec["nodes"].append(node_spec)
    _dump(spec, path)
