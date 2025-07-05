import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from lambda_lib.core.node import LambdaNode
from lambda_lib.graph import Graph
from lambda_lib.ops.spawn_feature import spawn_feature
from lambda_lib.ops.feature_discoverer import FeatureNode
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
