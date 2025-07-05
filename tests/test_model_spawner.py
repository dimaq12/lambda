import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from lambda_lib.core.engine import LambdaEngine
from lambda_lib.core.node import LambdaNode
from lambda_lib.core.operation import LambdaOperation
from lambda_lib.graph import Graph
from lambda_lib.metrics.reward import reward
from lambda_lib.ops.model_spawner import ModelNode, _best_reward


def test_spawn_model_nodes_added():
    _best_reward.clear()
    graph = Graph([])
    metric = LambdaNode("Metric", data={"400": 0.9})
    graph.add(metric)
    assert any(isinstance(n, ModelNode) for n in graph.nodes)


def test_spawned_model_runs_and_replaces():
    _best_reward.clear()
    samples = [
        {"latency_ms": 500, "label": 1},
        {"latency_ms": 700, "label": 1},
    ]
    thresholds = {"Model#0": 800, "Model#1": 400}
    idx = 0
    current = None
    features = None
    preds: dict[str, int] = {}
    rewards: dict[str, float] = {}
    models = {"Model#0"}

    def sensor(n: LambdaNode) -> LambdaNode:
        nonlocal idx, current
        current = samples[idx] if idx < len(samples) else None
        idx += 1
        return LambdaNode("Sensor", data=current, links=n.links)

    def feature_maker(n: LambdaNode) -> LambdaNode:
        nonlocal features
        features = None
        if current:
            features = {"latency_ms": current["latency_ms"]}
        return LambdaNode("FeatureMaker", data=features, links=n.links)

    def make_model(name: str, thr: int):
        def model(n: LambdaNode) -> LambdaNode:
            pred = None
            if features is not None:
                pred = int(features["latency_ms"] >= thr)
                preds[name] = pred
            return LambdaNode(name, data=pred, links=n.links)
        return model

    def metric(n: LambdaNode) -> LambdaNode:
        if current:
            label = current["label"]
            for name, thr in thresholds.items():
                val = int(current["latency_ms"] >= thr)
                rew = reward(1.0 if val == label else -1.0)
                rewards[str(thr)] = rew
        return LambdaNode("RewardMetric", data=rewards.copy(), links=n.links)

    engine = LambdaEngine()
    engine.register(LambdaOperation("Sensor", sensor))
    engine.register(LambdaOperation("FeatureMaker", feature_maker))
    engine.register(LambdaOperation("Model#0", make_model("Model#0", thresholds["Model#0"])))
    engine.register(LambdaOperation("RewardMetric", metric))

    graph = Graph([
        LambdaNode("Sensor"),
        LambdaNode("FeatureMaker"),
        LambdaNode("Model#0"),
        LambdaNode("RewardMetric"),
    ])

    for _ in samples:
        scheduler = engine.execute(graph)
        scheduler.execute()
        if "Model#1" not in models and rewards.get("400", 0) > rewards.get("800", 0):
            models.add("Model#1")
            engine.register(LambdaOperation("Model#1", make_model("Model#1", thresholds["Model#1"])))
            graph.add(LambdaNode("Model#1"))
        if "Model#1" in models and "Model#0" in models:
            if rewards.get("400", -1) > rewards.get("800", -1):
                graph.nodes = [n for n in graph.nodes if n.label != "Model#0"]
                engine.registry.pop("Model#0", None)
                models.remove("Model#0")

    labels = [n.label for n in graph.nodes if n.label.startswith("Model#")]
    assert "Model#1" in labels
    assert "Model#0" not in labels
