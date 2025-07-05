import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from lambda_lib.core.node import LambdaNode
from lambda_lib.graph import Graph
from lambda_lib.ops.feature_discoverer import FeatureNode, _best_accuracy, _event_memory
from lambda_lib.governance.governor import enforce_feature_limit


def test_feature_discovery_inserts_nodes():
    _best_accuracy.clear()
    graph = Graph([])
    metric = LambdaNode("Metric", data={"clf": 0.6})
    graph.add(metric)
    assert any(isinstance(n, FeatureNode) for n in graph.nodes)

    metric2 = LambdaNode("Metric", data={"clf": 0.5})
    graph.add(metric2)
    assert len([n for n in graph.nodes if isinstance(n, FeatureNode)]) == 1

    metric3 = LambdaNode("Metric", data={"clf": 0.7})
    graph.add(metric3)
    assert len([n for n in graph.nodes if isinstance(n, FeatureNode)]) == 2


def test_feature_limit_governor():
    graph = Graph([LambdaNode("Base")])
    for i in range(5):
        graph.add(FeatureNode(f"f{i}", i))

    result = enforce_feature_limit(graph, limit=3)
    assert result == "pruned"
    assert len([n for n in graph.nodes if isinstance(n, FeatureNode)]) == 3


def test_batch_discover_inserts_feature_nodes():
    _event_memory.events.clear()
    graph = Graph([])
    graph.add(LambdaNode("Event", data={"x": 1, "label": 0}))
    graph.add(LambdaNode("Event", data={"x": 2, "label": 1}))
    features = [
        n
        for n in graph.nodes
        if isinstance(n, FeatureNode)
        and isinstance(n.data, dict)
        and str(n.data.get("expr", "")).startswith("x")
    ]
    assert len(features) >= 1
