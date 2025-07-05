import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from lambda_lib.core.node import LambdaNode
from lambda_lib.graph import Graph
from lambda_lib.governance.governor import enforce_node_limit


def test_enforce_node_limit_prunes():
    nodes = [LambdaNode(str(i)) for i in range(5)]
    graph = Graph(nodes)
    result = enforce_node_limit(graph, limit=3)
    assert result == "pruned"
    assert len(graph.nodes) == 3


def test_enforce_node_limit_ok():
    nodes = [LambdaNode(str(i)) for i in range(2)]
    graph = Graph(nodes)
    result = enforce_node_limit(graph, limit=5)
    assert result == "ok"
    assert len(graph.nodes) == 2
