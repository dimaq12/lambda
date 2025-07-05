import os
import sys
import json
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from lambda_lib.core.engine import LambdaEngine
from lambda_lib.core.node import LambdaNode
from lambda_lib.core.operation import LambdaOperation
from lambda_lib.graph.graph_utils import load_graph_from_file
from lambda_lib.metrics.reward import reward
from lambda_lib.sensors.anomaly_stream import anomaly_stream


def test_anomaly_detector_validation():
    seed_path = Path("lambda_lib/examples/anomaly_detector/seed.yaml")
    graph = load_graph_from_file(str(seed_path))

    feature_file = Path("patterns/spawn_feature.yaml")
    feature_exprs = json.loads(feature_file.read_text())

    engine = LambdaEngine()
    step = 0
    current = None
    preds = []
    labels = []
    values = []
    score = 0.0

    def sensor(node: LambdaNode) -> LambdaNode:
        nonlocal step, current
        current = anomaly_stream(step)
        step += 1
        values.append(current.value)
        return LambdaNode("Sensor", data=current, links=node.links)

    def classifier(node: LambdaNode) -> LambdaNode:
        val = current.value
        avg = sum(values) / len(values) if values else val
        pred = 0
        if "x > 140" in feature_exprs and val > 140:
            pred = 1
        if "x / avg > 1.3" in feature_exprs and avg and val / avg > 1.3:
            pred = 1
        preds.append(pred)
        labels.append(current.label)
        return LambdaNode("Classifier", data=pred, links=node.links)

    def metric(node: LambdaNode) -> LambdaNode:
        nonlocal score
        if preds:
            val = 1.0 if preds[-1] == labels[-1] else -1.0
            r = reward(val)
            score = (score * (len(preds) - 1) + r) / len(preds)
        return LambdaNode("RewardMetric", data={"score": score}, links=node.links)

    engine.register(LambdaOperation("Sensor", sensor))
    engine.register(LambdaOperation("Classifier", classifier))
    engine.register(LambdaOperation("RewardMetric", metric))

    for _ in range(2000):
        engine.execute(graph)

    true_spikes = sum(labels)
    predicted_spikes = sum(preds)
    true_pos = sum(1 for p, l in zip(preds, labels) if p == 1 and l == 1)
    false_pos = sum(1 for p, l in zip(preds, labels) if p == 1 and l == 0)
    accuracy = sum(1 for p, l in zip(preds, labels) if p == l) / len(labels)
    fpr = false_pos / (len(labels) - true_spikes)

    assert score > 0.2
    assert len(feature_exprs) >= 2
    assert accuracy >= 0.7
    assert fpr <= 0.2
