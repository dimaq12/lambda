#@module:
#@  version: "0.3"
#@  layer: examples
#@  exposes: [build_graph]
#@  doc: Example graph with fixed features and accuracy metric.
#@end
from __future__ import annotations

from typing import List, Dict, Tuple

from ...core.engine import LambdaEngine
from ...core.node import LambdaNode
from ...core.operation import LambdaOperation
from ...graph import Graph
from ...metrics.accuracy import accuracy
from ...models.classifier import RuleBasedClassifier


def build_graph(samples: List[Dict], threshold: int = 1000) -> Tuple[LambdaEngine, Graph, List[int], List[int]]:
    """Return engine, graph and histories for predictions and labels."""
    idx = 0
    current_event: Dict | None = None
    features: Dict | None = None
    preds: List[int] = []
    labels: List[int] = []
    model = RuleBasedClassifier(threshold)

    def sensor(node: LambdaNode) -> LambdaNode:
        nonlocal idx, current_event
        current_event = samples[idx] if idx < len(samples) else None
        idx += 1
        return LambdaNode("Sensor", data=current_event, links=node.links)

    def feature_maker(node: LambdaNode) -> LambdaNode:
        nonlocal features
        if current_event is None:
            features = None
        else:
            features = {
                "latency_ms": current_event.get("latency_ms", 0),
                "label": current_event.get("label", 0),
            }
        return LambdaNode("FeatureMaker", data=features, links=node.links)

    def model_op(node: LambdaNode) -> LambdaNode:
        pred = None
        if features is not None:
            pred = model.predict(features)
            preds.append(pred)
            labels.append(int(features.get("label", 0)))
        return LambdaNode("Model", data=pred, links=node.links)

    def metric(node: LambdaNode) -> LambdaNode:
        acc = accuracy(preds, labels)
        return LambdaNode("AccuracyMetric", data=acc, links=node.links)

    engine = LambdaEngine()
    engine.register(LambdaOperation("Sensor", sensor))
    engine.register(LambdaOperation("FeatureMaker", feature_maker))
    engine.register(LambdaOperation("Model", model_op))
    engine.register(LambdaOperation("AccuracyMetric", metric))

    graph = Graph([
        LambdaNode("Sensor"),
        LambdaNode("FeatureMaker"),
        LambdaNode("Model"),
        LambdaNode("AccuracyMetric"),
    ])

    return engine, graph, preds, labels
