import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from lambda_lib.core.engine import LambdaEngine
from lambda_lib.core.node import LambdaNode
from lambda_lib.core.operation import LambdaOperation
from lambda_lib.graph.graph_utils import load_graph_from_file
from lambda_lib.metrics.reward import reward
from lambda_lib.sensors.anomaly_stream import anomaly_stream
from lambda_lib.ops.spawn_feature import spawn_feature
from lambda_lib.ops.feature_discoverer import _event_memory


def test_lambda_autolearns_features_and_classifies():
    engine = LambdaEngine()
    graph = load_graph_from_file("lambda_lib/examples/anomaly_detector/seed.yaml")

    _event_memory.events.clear()

    step = 70
    current = None
    preds: list[int] = []
    labels: list[int] = []
    values: list[float] = []
    reward_trend: list[float] = []
    score = 0.0
    accuracy = 0.0

    def sensor(node: LambdaNode) -> LambdaNode:
        nonlocal step, current
        current = anomaly_stream(step)
        step += 1
        values.append(current.value)
        _event_memory.push({"x": current.value, "label": current.label})
        return LambdaNode("Sensor", data=current, links=node.links)

    def classifier(node: LambdaNode) -> LambdaNode:
        val = current.value
        avg = sum(values) / len(values) if values else val
        prev = values[-2] if len(values) >= 2 else val
        dx = val - prev
        pred = 0
        for feature in [n for n in graph.nodes if n.label.startswith("Feature:")]:
            expr = feature.data.get("expr") if isinstance(feature.data, dict) else None
            if not expr:
                continue
            try:
                if eval(expr, {}, {"x": val, "avg": avg, "dx": dx}):
                    pred = 1
                    break
            except Exception:
                continue
        preds.append(pred)
        labels.append(current.label)
        return LambdaNode("Classifier", data=pred, links=node.links)

    def metric(node: LambdaNode) -> LambdaNode:
        nonlocal score, accuracy
        if preds:
            val = 1.0 if preds[-1] == labels[-1] else -1.0
            score = (score * (len(preds) - 1) + reward(val)) / len(preds)
            accuracy = sum(1 for p, l in zip(preds, labels) if p == l) / len(labels)
        reward_trend.append(score)
        return LambdaNode("RewardMetric", data={"score": score}, links=node.links)

    engine.register(LambdaOperation("Sensor", sensor))
    engine.register(LambdaOperation("Classifier", classifier))
    engine.register(LambdaOperation("RewardMetric", metric))

    for _ in range(2000):
        engine.execute(graph)
        if len([n for n in graph.nodes if n.label.startswith("Feature:")]) < 2 and len(values) >= 120:
            graph.add(spawn_feature(LambdaNode("FeatureDiscoverer", data={})))

    assert len([n for n in graph.nodes if n.label.startswith("Feature:")]) >= 2
    assert reward_trend[-1] - reward_trend[0] >= 0.5
    assert accuracy >= 0.75
