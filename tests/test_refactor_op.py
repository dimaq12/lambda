import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from lambda_lib.core.node import LambdaNode
from lambda_lib.graph import Graph
from lambda_lib.ops.refactor import RefactorOp
from lambda_lib.core.engine import LambdaEngine


def test_refactor_prunes_duplicates_and_dead_nodes():
    n1 = LambdaNode("A")
    n2 = LambdaNode("A")  # duplicate
    n3 = LambdaNode("B")
    n1.add_link(n3)
    dead = LambdaNode("C")
    graph = Graph([n1, n2, n3, dead])
    initial = len(graph.nodes)
    RefactorOp(entropy_threshold=2.0)(graph)
    assert len(graph.nodes) < initial
    labels = [n.label for n in graph.nodes]
    assert labels.count("A") == 1
    assert "C" not in labels


def test_refactor_rule_triggers_in_engine():
    n1 = LambdaNode("A")
    n2 = LambdaNode("A")  # duplicate
    n3 = LambdaNode("B")
    n1.add_link(n3)
    graph = Graph([n1, n2, n3])
    engine = LambdaEngine(refactor_every=2, node_limit=2)
    engine.execute(graph)  # step 1, no refactor yet
    assert len(graph.nodes) == 3
    engine.execute(graph)  # step 2 triggers refactor
    assert len(graph.nodes) == 2
    labels = [n.label for n in graph.nodes]
    assert labels.count("A") == 1

