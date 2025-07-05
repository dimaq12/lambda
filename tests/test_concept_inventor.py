import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from lambda_lib.core.node import LambdaNode, ConceptNode
from lambda_lib.graph import Graph
from lambda_lib.ops.concept_inventor import _best_corr
from lambda_lib.ops.meta_spawn import RuleNode


def test_concept_spawn_creates_nodes_and_rules():
    _best_corr.clear()
    graph = Graph([])
    metric = LambdaNode("Metric", data={"foo": 0.95})
    graph.add(metric)
    concepts = [n for n in graph.nodes if isinstance(n, ConceptNode)]
    rules = [n for n in graph.nodes if isinstance(n, RuleNode)]
    assert any(c.label == "Concept:foo" for c in concepts)
    assert any(r.label == "Rule:foo" for r in rules)
