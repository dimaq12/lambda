#@module:
#@  version: "0.3"
#@  layer: examples
#@  exposes: []
#@  doc: Example demonstrating simple eval flow.
#@end
from __future__ import annotations

from ..core.engine import LambdaEngine
from ..core.node import LambdaNode
from ..core.operation import LambdaOperation
from ..graph import Graph


def build_graph(samples: list[dict]) -> tuple[LambdaEngine, Graph]:
    """Return engine and graph for a simple evaluation loop."""
    idx = 0
    current = None

    def sensor(node: LambdaNode) -> LambdaNode:
        nonlocal idx, current
        current = samples[idx] if idx < len(samples) else None
        idx += 1
        return LambdaNode("Sensor", data=current, links=node.links)

    def feature_maker(node: LambdaNode) -> LambdaNode:
        return LambdaNode("FeatureMaker", data=current, links=node.links)

    def model(node: LambdaNode) -> LambdaNode:
        pred = None
        if current:
            pred = int(current.get("latency_ms", 0) >= 500)
        return LambdaNode("Model", data=pred, links=node.links)

    engine = LambdaEngine()
    engine.register(LambdaOperation("Sensor", sensor))
    engine.register(LambdaOperation("FeatureMaker", feature_maker))
    engine.register(LambdaOperation("Model", model))

    graph = Graph([
        LambdaNode("Sensor"),
        LambdaNode("FeatureMaker", raw=True),
        LambdaNode("Model"),
    ])

    return engine, graph


def main() -> None:
    samples = [
        {"latency_ms": 100, "label": 0},
        {"latency_ms": 700, "label": 1},
    ]
    engine, graph = build_graph(samples)
    for _ in samples:
        engine.execute(graph)
        print([f"{n.label}:{n.data}" for n in graph.nodes])


if __name__ == "__main__":  # pragma: no cover - manual run
    main()
