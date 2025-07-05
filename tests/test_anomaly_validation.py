import os
import sys
from pathlib import Path
from statistics import mean, pstdev

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from lambda_lib.core.engine import LambdaEngine
from lambda_lib.core.node import LambdaNode
from lambda_lib.core.operation import LambdaOperation
from lambda_lib.graph.graph_utils import load_graph_from_file
from lambda_lib.metrics.reward import reward
from lambda_lib.sensors.anomaly_stream import anomaly_stream
from lambda_lib.ops.spawn_feature import spawn_feature
import time


def run_anomaly_detector(iterations: int = 2000) -> tuple[list[str], dict]:
    """Run anomaly detector training and return feature list and metrics."""
    seed_path = Path("lambda_lib/examples/anomaly_detector/seed.yaml")
    graph = load_graph_from_file(str(seed_path))

    feature_exprs: set[str] = set()

    engine = LambdaEngine()
    step = 0
    current = None
    preds: list[int] = []
    labels: list[int] = []
    values: list[float] = []
    reward_trend: list[float] = [0.0]
    score = 0.0

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
            if current.value > avg + 3 * sigma and "x > mean + 3*sigma" not in feature_exprs:
                feature_exprs.add("x > mean + 3*sigma")
                graph.add(spawn_feature(LambdaNode("FeatureDiscoverer", data={"expr": "x > mean + 3*sigma"})))
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
                if eval(expr, {"__builtins__": None, "abs": abs}, {"x": val, "avg": avg, "mean": avg, "sigma": sigma, "dx": dx}):
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
            r = reward(val)
            score = (score * (len(preds) - 1) + r) / len(preds)
        reward_trend.append(score)
        return LambdaNode("RewardMetric", data={"score": score}, links=node.links)

    engine.register(LambdaOperation("Sensor", sensor))
    engine.register(LambdaOperation("Classifier", classifier))
    engine.register(LambdaOperation("RewardMetric", metric))

    start = time.perf_counter()
    for _ in range(iterations):
        engine.execute(graph)
    duration = time.perf_counter() - start

    true_spikes = sum(labels)
    predicted_spikes = sum(preds)
    true_pos = sum(1 for p, l in zip(preds, labels) if p == 1 and l == 1)
    false_pos = sum(1 for p, l in zip(preds, labels) if p == 1 and l == 0)
    accuracy = sum(1 for p, l in zip(preds, labels) if p == l) / len(labels)
    fpr = false_pos / (len(labels) - true_spikes)

    metrics = {
        "score": score,
        "accuracy": accuracy,
        "fpr": fpr,
        "duration": duration,
        "graph_nodes": [n.label for n in graph.nodes],
        "true_spikes": true_spikes,
        "predicted_spikes": predicted_spikes,
        "true_pos": true_pos,
        "false_pos": false_pos,
        "reward_trend": reward_trend,
    }

    return list(feature_exprs), metrics




def test_anomaly_detector_validation():
    feature_exprs, metrics = run_anomaly_detector()

    assert len(feature_exprs) >= 2
    assert metrics["reward_trend"][-1] - metrics["reward_trend"][0] >= 0.3
    assert metrics["accuracy"] >= 0.75

