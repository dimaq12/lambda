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
from statistics import mean, pstdev


def test_lambda_autolearns_features_and_classifies():
    engine = LambdaEngine()
    graph = load_graph_from_file("lambda_lib/examples/anomaly_detector/seed.yaml")

    step = 70
    current = None
    preds = []
    labels = []
    values = []
    reward_trend = []
    score = 0.0
    feature_exprs: set[str] = set()

    prev = None

    def sensor(node: LambdaNode) -> LambdaNode:
        nonlocal step, current, prev
        current = anomaly_stream(step)
        step += 1
        values.append(current.value)
        avg = mean(values)
        sigma = pstdev(values) if len(values) > 1 else 0.0
        dx = current.value - prev if prev is not None else 0.0
        if sigma:
            if current.value < avg - 3 * sigma and "x < mean - 3*sigma" not in feature_exprs:
                feature_exprs.add("x < mean - 3*sigma")
                graph.add(spawn_feature(LambdaNode("FeatureDiscoverer", data={"expr": "x < mean - 3*sigma"})))
            if abs(dx) > 3 * sigma and "abs(dx) > 3*sigma" not in feature_exprs:
                feature_exprs.add("abs(dx) > 3*sigma")
                graph.add(spawn_feature(LambdaNode("FeatureDiscoverer", data={"expr": "abs(dx) > 3*sigma"})))
        prev = current.value
        return LambdaNode("Sensor", data=current, links=node.links)

    def classifier(node: LambdaNode) -> LambdaNode:
        val = current.value
        avg = mean(values)
        sigma = pstdev(values) if len(values) > 1 else 0.0
        dx = values[-1] - values[-2] if len(values) > 1 else 0.0
        pred = 0
        for expr in feature_exprs:
            try:
                if eval(expr, {"__builtins__": None, "abs": abs}, {"x": val, "mean": avg, "avg": avg, "sigma": sigma, "dx": dx}):
                    pred = 1
                    break
            except Exception:
                continue
        preds.append(pred)
        labels.append(current.label)
        return LambdaNode("Classifier", data=pred, links=node.links)

    def metric(node: LambdaNode) -> LambdaNode:
        nonlocal score
        if preds:
            val = 1.0 if preds[-1] == labels[-1] else -1.0
            score = (score * (len(preds) - 1) + reward(val)) / len(preds)
        reward_trend.append(score)
        return LambdaNode("RewardMetric", data={"score": score}, links=node.links)

    engine.register(LambdaOperation("Sensor", sensor))
    engine.register(LambdaOperation("Classifier", classifier))
    engine.register(LambdaOperation("RewardMetric", metric))

    for _ in range(2000):
        engine.execute(graph)
    accuracy = sum(1 for p, l in zip(preds, labels) if p == l) / len(labels)

    assert len([n for n in graph.nodes if "Feature" in n.label]) >= 2
    assert reward_trend[-1] - reward_trend[0] >= 0.3
    assert accuracy >= 0.75
