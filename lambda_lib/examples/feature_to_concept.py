#@module:
#@  version: "0.3"
#@  layer: examples
#@  exposes: [main]
#@  doc: Demonstrates spawn_feature -> spawn_op -> concept chain.
#@end
from __future__ import annotations

from ..core.node import LambdaNode
from ..graph import Graph
from ..ops.spawn_feature import spawn_feature


def main() -> None:
    graph = Graph([])

    fd = LambdaNode("FeatureDiscoverer", data={"expr": "latency_ms"})
    feature = spawn_feature(fd)
    feature.data = {"latency_ms": 0.95}

    graph.add(feature)

    for node in graph.nodes:
        print(node.label, node.data)


if __name__ == "__main__":  # pragma: no cover - manual run
    main()
