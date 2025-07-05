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
from lambda_lib.ops.spawn_feature import spawn_feature


def test_lambda_autolearns_features_and_classifies():
    engine = LambdaEngine()
    graph = load_graph_from_file("lambda_lib/examples/anomaly_detector/seed.yaml")

    feature_file = Path("patterns/spawn_feature.yaml")
    feature_exprs = json.loads(feature_file.read_text())
    spawned = False

    step = 70
    current = None
    preds = []
    labels = []
    values = []
    reward_trend = []
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
        features = {n.label.split("Feature:", 1)[1] for n in graph.nodes if n.label.startswith("Feature:")}
        if "x > 140" in features and val > 140:
            pred = 1
        if "x / avg > 1.3" in features and avg and val / avg > 1.3:
            pred = 1
        preds.append(pred)
        labels.append(current.label)
        return LambdaNode("Classifier", data=pred, links=node.links)

    def metric(node: LambdaNode) -> LambdaNode:
        nonlocal score, spawned
        if preds:
            val = 1.0 if preds[-1] == labels[-1] else -1.0
            score = (score * (len(preds) - 1) + reward(val)) / len(preds)
        if not spawned and len(values) >= 120:
            for expr in feature_exprs:
                graph.add(spawn_feature(LambdaNode("FeatureDiscoverer", data={"expr": expr})))
            spawned = True
        reward_trend.append(score)
        return LambdaNode("RewardMetric", data={"score": score}, links=node.links)

    engine.register(LambdaOperation("Sensor", sensor))
    engine.register(LambdaOperation("Classifier", classifier))
    engine.register(LambdaOperation("RewardMetric", metric))

    for _ in range(2000):
        engine.execute(graph)

    assert len([n for n in graph.nodes if "Feature" in n.label]) >= 2
    assert reward_trend[-1] - reward_trend[0] > 0.2
