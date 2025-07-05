#@module:
#@  version: "0.3"
#@  layer: app
#@  exposes: [main]
#@  doc: Command line interface to run seed λ graphs.
#@end
from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence

from .core.engine import LambdaEngine
from .core.node import LambdaNode
from .core.operation import LambdaOperation
from .graph import Graph
from .graph.graph_utils import load_graph_from_file, save_graph_to_file
from .sensors.latency_stream import latency_stream
from .metrics.reward import reward


#@contract:
#@  pre: len(argv) >= 2
#@  post: result in [0, 1]
#@end
def main(argv: Sequence[str]) -> int:
    """Run the seed graph specified in ``argv``."""
    if len(argv) < 2:
        return 1

    command = argv[1]

    if command == "noop":
        node = LambdaNode("noop")
        graph = Graph([node])

        def noop_op(n: LambdaNode) -> LambdaNode:
            return LambdaNode("noop", data=n.data, links=n.links)

        op = LambdaOperation("noop", noop_op)

        engine = LambdaEngine()
        engine.register(op)

        executor = engine.execute(graph)
        return 0 if executor.state == "ready" else 1

    if command == "run" and len(argv) >= 3:
        seed_file = argv[2]
        path = Path(seed_file)
        if not path.exists():
            alt = Path(__file__).resolve().parent / seed_file
            if alt.exists():
                seed_file = str(alt)
        steps = 1
        if "--steps" in argv:
            idx = argv.index("--steps")
            if idx + 1 < len(argv):
                try:
                    steps = int(argv[idx + 1])
                except ValueError:
                    pass

        graph = load_graph_from_file(seed_file)

        engine = LambdaEngine()

        threshold = 600
        current_event = None
        prediction = None
        score = 0.0

        def sensor(node: LambdaNode) -> LambdaNode:
            nonlocal current_event
            event = latency_stream()
            current_event = {"latency_ms": event.latency_ms, "label": int(event.latency_ms >= threshold)}
            return LambdaNode("Sensor", data=current_event, links=node.links)

        def classifier(node: LambdaNode) -> LambdaNode:
            nonlocal prediction
            if current_event:
                prediction = int(current_event["latency_ms"] >= threshold)
            else:
                prediction = None
            return LambdaNode("Classifier", data=prediction, links=node.links)

        def metric(node: LambdaNode) -> LambdaNode:
            nonlocal score
            if current_event and prediction is not None:
                val = 1.0 if prediction == current_event["label"] else -1.0
                score = (score + reward(val)) / 2.0
            return LambdaNode("RewardMetric", data={"score": score}, links=node.links)

        engine.register(LambdaOperation("Sensor", sensor))
        engine.register(LambdaOperation("Classifier", classifier))
        engine.register(LambdaOperation("RewardMetric", metric))

        for _ in range(steps):
            engine.execute(graph)

        save_graph_to_file(graph, seed_file)
        return 0

    return 1


if __name__ == "__main__":  # pragma: no cover - manual invocation
    sys.exit(main(sys.argv))
