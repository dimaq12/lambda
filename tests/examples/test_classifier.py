import os
import sys
from pathlib import Path

# Ensure project root on path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from lambda_lib.examples.classifier import run
from lambda_lib.core.engine import LambdaEngine
from lambda_lib.core.node import LambdaNode
from lambda_lib.core.operation import LambdaOperation
from lambda_lib.metrics.reward import reward


def test_classifier_example_runs():
    seed_file = Path(run.__file__).with_name("seed.yaml")
    graph = run.load_graph(str(seed_file))

    engine = LambdaEngine()

    event = {"latency_ms": 700, "label": 1}
    pred = None

    def sensor(node: LambdaNode) -> LambdaNode:
        return LambdaNode("Sensor", data=event, links=node.links)

    def classifier(node: LambdaNode) -> LambdaNode:
        nonlocal pred
        pred = int(event["latency_ms"] >= 600)
        return LambdaNode("Classifier", data=pred, links=node.links)

    def metric(node: LambdaNode) -> LambdaNode:
        score = reward(1.0 if pred == event["label"] else -1.0)
        return LambdaNode("RewardMetric", data={"score": score}, links=node.links)

    engine.register(LambdaOperation("Sensor", sensor))
    engine.register(LambdaOperation("Classifier", classifier))
    engine.register(LambdaOperation("RewardMetric", metric))

    scheduler = engine.execute(graph)
    assert scheduler.state == "ready"
    assert any(n.label == "RewardMetric" for n in graph.nodes)
    assert isinstance(graph.nodes[2].data, dict)
