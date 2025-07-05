import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from lambda_lib.core.engine import LambdaEngine
from lambda_lib.core.node import LambdaNode
from lambda_lib.core.operation import LambdaOperation
from lambda_lib.graph import Graph
from lambda_lib.metrics.reward import reward


def test_reward_guides_model_updates():
    samples = [
        {"latency_ms": 500, "label": 1},
        {"latency_ms": 700, "label": 1},
    ]

    thresholds = {"Classifier#0": 800, "Classifier#1": 400}
    idx = 0
    current_event = None
    features = None
    predictions: dict[str, int] = {}
    reward_values: dict[str, float] = {}
    classifiers = {"Classifier#0": thresholds["Classifier#0"]}

    def sensor(node: LambdaNode) -> LambdaNode:
        nonlocal idx, current_event
        current_event = samples[idx] if idx < len(samples) else None
        idx += 1
        return LambdaNode("Sensor", data=current_event, links=node.links)

    def feature_maker(node: LambdaNode) -> LambdaNode:
        nonlocal features
        features = None
        if current_event:
            features = {"latency_ms": current_event["latency_ms"]}
        return LambdaNode("FeatureMaker", data=features, links=node.links)

    def make_classifier(name: str, thr: int):
        def classifier(node: LambdaNode) -> LambdaNode:
            pred = None
            if features is not None:
                pred = int(features["latency_ms"] >= thr)
                predictions[name] = pred
            return LambdaNode(name, data=pred, links=node.links)
        return classifier

    def metric(node: LambdaNode) -> LambdaNode:
        if current_event:
            true_label = current_event["label"]
            for cname in list(classifiers.keys()):
                pred = predictions.get(cname)
                if pred is not None:
                    val = 1.0 if pred == true_label else -1.0
                    reward_values[cname] = reward(val)
        return LambdaNode("RewardMetric", data=reward_values.copy(), links=node.links)

    engine = LambdaEngine()
    engine.register(LambdaOperation("Sensor", sensor))
    engine.register(LambdaOperation("FeatureMaker", feature_maker))
    engine.register(LambdaOperation("Classifier#0", make_classifier("Classifier#0", thresholds["Classifier#0"])))
    engine.register(LambdaOperation("RewardMetric", metric))

    graph = Graph([
        LambdaNode("Sensor"),
        LambdaNode("FeatureMaker"),
        LambdaNode("Classifier#0"),
        LambdaNode("RewardMetric"),
    ])

    for _ in samples:
        engine.execute(graph)

        if "Classifier#1" not in classifiers and reward_values.get("Classifier#0", 0) < 0:
            classifiers["Classifier#1"] = thresholds["Classifier#1"]
            engine.register(LambdaOperation("Classifier#1", make_classifier("Classifier#1", thresholds["Classifier#1"])))
            new_node = LambdaNode("Classifier#1")
            graph.nodes.insert(len(graph.nodes) - 1, new_node)

        if "Classifier#1" in classifiers and "Classifier#0" in classifiers:
            if reward_values.get("Classifier#1", -1) > reward_values.get("Classifier#0", -1):
                graph.nodes = [n for n in graph.nodes if n.label != "Classifier#0"]
                engine.registry.pop("Classifier#0", None)
                classifiers.pop("Classifier#0", None)

    classifier_labels = [n.label for n in graph.nodes if n.label.startswith("Classifier")]
    assert "Classifier#1" in classifier_labels
    assert "Classifier#0" not in classifier_labels
    assert any(n.label == "RewardMetric" for n in graph.nodes)
