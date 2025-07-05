#@module:
#@  version: "0.3"
#@  layer: examples
#@  exposes: [main]
#@  doc: Launch the classifier seed graph via the scheduler.
#@end
from __future__ import annotations

import json
from pathlib import Path

from ...core.engine import LambdaEngine
from ...core.node import LambdaNode
from ...core.operation import LambdaOperation
from ...graph import Graph

try:  # optional dependency
    import yaml  # type: ignore
    def _load(path: str):
        return yaml.safe_load(Path(path).read_text())
except Exception:  # pragma: no cover - fallback when PyYAML not installed
    def _load(path: str):
        return json.loads(Path(path).read_text())


def load_graph(path: str) -> Graph:
    """Load nodes from ``path`` and return a Graph."""
    data = _load(path)
    nodes: list[LambdaNode] = []
    for spec in data.get("nodes", []):
        node = LambdaNode(spec["label"], spec.get("data"), [])
        nodes.append(node)
    # resolve links by index
    for node, spec in zip(nodes, data.get("nodes", [])):
        for target in spec.get("links", []):
            node.add_link(nodes[target])
    return Graph(nodes)


def main() -> None:
    seed_file = Path(__file__).with_name("seed.yaml")
    graph = load_graph(str(seed_file))

    engine = LambdaEngine()

    def data_stream(node: LambdaNode) -> LambdaNode:
        value = (node.data or 0) + 1
        return LambdaNode("DataStream", data=value, links=node.links)

    def feature_maker(node: LambdaNode) -> LambdaNode:
        return LambdaNode("FeatureMaker", data=node.data, links=node.links)

    def classifier(node: LambdaNode) -> LambdaNode:
        return LambdaNode("Classifier", data="NORMAL", links=node.links)

    def statistics(node: LambdaNode) -> LambdaNode:
        return LambdaNode("Statistics", data=node.data, links=node.links)

    engine.register(LambdaOperation("DataStream", data_stream))
    engine.register(LambdaOperation("FeatureMaker", feature_maker))
    engine.register(LambdaOperation("Classifier", classifier))
    engine.register(LambdaOperation("Statistics", statistics))

    scheduler = engine.execute(graph)
    print(f"done: {scheduler.state}")


if __name__ == "__main__":  # pragma: no cover - manual invocation
    main()
