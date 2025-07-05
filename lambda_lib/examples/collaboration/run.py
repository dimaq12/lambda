#@module:
#@  version: "0.3"
#@  layer: examples
#@  exposes: [build_graph]
#@  doc: Build a graph of collaborative classifiers using vote op.
#@end
from __future__ import annotations

from typing import List, Dict, Tuple

from ...core.engine import LambdaEngine
from ...core.node import LambdaNode
from ...core.operation import LambdaOperation
from ...graph import Graph
from ...metrics.reward import reward
from ...models.classifier import RuleBasedClassifier
from ...ops.collaboration import vote


def build_graph(samples: List[Dict], thresholds: List[int]) -> Tuple[LambdaEngine, Graph, Dict[str, List[float]], List[float]]:
    """Return engine, graph and reward histories for individual and ensemble models."""
    idx = 0
    current: Dict | None = None
    features: Dict | None = None
    preds: Dict[str, int] = {}
    rewards: Dict[str, List[float]] = {f"Model#{t}": [] for t in thresholds}
    ensemble_rewards: List[float] = []
    models = {f"Model#{t}": RuleBasedClassifier(t) for t in thresholds}

    def sensor(node: LambdaNode) -> LambdaNode:
        nonlocal idx, current
        current = samples[idx] if idx < len(samples) else None
        idx += 1
        return LambdaNode("Sensor", data=current, links=node.links)

    def feature_maker(node: LambdaNode) -> LambdaNode:
        nonlocal features
        features = None
        if current:
            features = {"latency_ms": current.get("latency_ms", 0), "label": current.get("label", 0)}
        return LambdaNode("FeatureMaker", data=features, links=node.links)

    def make_model(name: str, model: RuleBasedClassifier):
        def model_op(node: LambdaNode) -> LambdaNode:
            pred = None
            if features is not None:
                pred = model.predict(features)
                preds[name] = pred
            return LambdaNode(name, data=pred, links=node.links)
        return model_op

    def vote_node(node: LambdaNode) -> LambdaNode:
        if preds:
            result = vote(list(preds.values()))
        else:
            result = None
        preds["Vote"] = result if result is not None else 0
        return LambdaNode("Vote", data=result, links=node.links)

    def metric(node: LambdaNode) -> LambdaNode:
        if features:
            label = int(features["label"])
            for name in models:
                pred = preds.get(name)
                if pred is not None:
                    val = 1.0 if pred == label else -1.0
                    rewards[name].append(reward(val))
            vote_pred = preds.get("Vote")
            if vote_pred is not None:
                ensemble_rewards.append(reward(1.0 if vote_pred == label else -1.0))
        return LambdaNode("RewardMetric", data=None, links=node.links)

    engine = LambdaEngine()
    engine.register(LambdaOperation("Sensor", sensor))
    engine.register(LambdaOperation("FeatureMaker", feature_maker))
    for name, model in models.items():
        engine.register(LambdaOperation(name, make_model(name, model)))
    engine.register(LambdaOperation("Vote", vote_node))
    engine.register(LambdaOperation("RewardMetric", metric))

    graph = Graph([
        LambdaNode("Sensor"),
        LambdaNode("FeatureMaker"),
        *[LambdaNode(name) for name in models],
        LambdaNode("Vote"),
        LambdaNode("RewardMetric"),
    ])

    return engine, graph, rewards, ensemble_rewards


if __name__ == "__main__":  # pragma: no cover - manual run
    samples = [
        {"latency_ms": 100, "label": 0},
        {"latency_ms": 700, "label": 1},
        {"latency_ms": 400, "label": 0},
        {"latency_ms": 900, "label": 1},
    ]
    engine, graph, rewards, ensemble = build_graph(samples, [800, 500])
    for _ in samples:
        engine.execute(graph)
    print("ensemble rewards", ensemble)

