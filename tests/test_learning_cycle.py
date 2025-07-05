import os
import sys

# Ensure project root on path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from lambda_lib.core.engine import LambdaEngine
from lambda_lib.core.node import LambdaNode
from lambda_lib.core.operation import LambdaOperation
from lambda_lib.graph import Graph
from lambda_lib.metrics.accuracy import accuracy


def test_learning_cycle_self_modifies():
    samples = [
        {"latency_ms": 100, "status": 200, "label": 0},
        {"latency_ms": 900, "status": 403, "label": 1},
        {"latency_ms": 300, "status": 200, "label": 0},
        {"latency_ms": 700, "status": 200, "label": 1},
        {"latency_ms": 1500, "status": 200, "label": 1},
        {"latency_ms": 400, "status": 403, "label": 0},
        {"latency_ms": 800, "status": 200, "label": 1},
        {"latency_ms": 200, "status": 200, "label": 0},
        {"latency_ms": 600, "status": 200, "label": 1},
        {"latency_ms": 1100, "status": 403, "label": 1},
    ]

    thresholds = {"Classifier#0": 1000, "Classifier#1": 600}
    idx = 0
    current_event = None
    features = None
    labels: list[int] = []
    pred_history: dict[str, list[int]] = {name: [] for name in thresholds}
    accuracy_values: dict[str, float] = {}
    predictions: dict[str, int] = {}
    classifiers = {"Classifier#0": 1000}

    def sensor(node: LambdaNode) -> LambdaNode:
        nonlocal idx, current_event
        if idx < len(samples):
            current_event = samples[idx]
            idx += 1
        else:
            current_event = None
        return LambdaNode("Sensor", data=current_event, links=node.links)

    def feature_maker(node: LambdaNode) -> LambdaNode:
        nonlocal features
        features = None
        if current_event:
            features = {
                "latency_ms": current_event["latency_ms"],
                "status": current_event["status"],
                "label": current_event["label"],
            }
        return LambdaNode("FeatureMaker", data=features, links=node.links)

    def make_classifier(name: str, threshold: int):
        def classifier(node: LambdaNode) -> LambdaNode:
            pred = predictions.get(name)
            return LambdaNode(name, data=pred, links=node.links)
        return classifier

    def metric(node: LambdaNode) -> LambdaNode:
        if features:
            labels.append(int(features["label"]))
            for cname, thr in thresholds.items():
                pred = int(features["latency_ms"] >= thr)
                predictions[cname] = pred
                pred_history[cname].append(pred)
                accuracy_values[cname] = accuracy(pred_history[cname], labels)
        return LambdaNode("Metric", data=accuracy_values.copy(), links=node.links)

    engine = LambdaEngine()
    engine.register(LambdaOperation("Sensor", sensor))
    engine.register(LambdaOperation("FeatureMaker", feature_maker))
    engine.register(LambdaOperation("Classifier#0", make_classifier("Classifier#0", thresholds["Classifier#0"])))
    engine.register(LambdaOperation("Metric", metric))

    graph = Graph([
        LambdaNode("Sensor"),
        LambdaNode("FeatureMaker"),
        LambdaNode("Classifier#0"),
        LambdaNode("Metric"),
    ])

    initial_len = len(graph.nodes)

    for _ in range(len(samples)):
        engine.execute(graph)

        if "Classifier#1" not in classifiers and accuracy_values.get("Classifier#0", 1.0) < 0.7:
            classifiers["Classifier#1"] = thresholds["Classifier#1"]
            engine.register(LambdaOperation("Classifier#1", make_classifier("Classifier#1", thresholds["Classifier#1"])))
            graph.add(LambdaNode("Classifier#1"))

        if "Classifier#1" in classifiers and "Classifier#0" in classifiers:
            if accuracy_values.get("Classifier#0", 1.0) < accuracy_values.get("Classifier#1", 0.0):
                graph.nodes = [n for n in graph.nodes if n.label != "Classifier#0"]
                engine.registry.pop("Classifier#0", None)
                classifiers.pop("Classifier#0", None)

    classifier_labels = [n.label for n in graph.nodes if n.label.startswith("Classifier")]
    assert len(classifier_labels) >= 1
    assert "Classifier#0" not in classifier_labels
    assert "Classifier#1" in classifier_labels
    assert any(v >= 0.7 for v in accuracy_values.values())
    assert any(n.label == "Metric" for n in graph.nodes)
