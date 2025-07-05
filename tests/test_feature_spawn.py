import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from lambda_lib.core.node import LambdaNode
from lambda_lib.graph import Graph
from lambda_lib.ops.spawn_feature import spawn_feature
from lambda_lib.ops.feature_discoverer import FeatureNode, _event_memory
from lambda_lib.governance.governor import enforce_feature_limit


def test_feature_spawn_and_governor_pruning():
    graph = Graph([])
    fd = LambdaNode("FeatureDiscoverer", data={"expr": "f0"})
    graph.add(spawn_feature(fd))
    assert any(isinstance(n, FeatureNode) for n in graph.nodes)

    # spawn extra features
    for i in range(4):
        graph.add(spawn_feature(LambdaNode("FeatureDiscoverer", data={"expr": f"f{i+1}"})))

    assert len([n for n in graph.nodes if isinstance(n, FeatureNode)]) == 5
    enforce_feature_limit(graph, limit=3)
    assert len([n for n in graph.nodes if isinstance(n, FeatureNode)]) == 3


def test_feature_growth_with_changing_correlation():
    _event_memory.events.clear()
    graph = Graph([])

    correlated = [
        {"x": 0, "label": 0},
        {"x": 1, "label": 1},
        {"x": 0, "label": 0},
    ]
    for event in correlated:
        graph.add(LambdaNode("Event", data=event))

    initial = len([n for n in graph.nodes if isinstance(n, FeatureNode)])
    assert initial > 0

    uncorrelated = [
        {"x": 1, "label": 0},
        {"x": 0, "label": 1},
        {"x": 1, "label": 0},
    ]
    for event in uncorrelated:
        graph.add(LambdaNode("Event", data=event))

    grown = len([n for n in graph.nodes if isinstance(n, FeatureNode)])
    assert grown > initial

    enforce_feature_limit(graph, limit=1)
    final = len([n for n in graph.nodes if isinstance(n, FeatureNode)])
    assert final == 1

