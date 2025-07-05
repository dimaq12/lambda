import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from lambda_lib.core.node import LambdaNode
from lambda_lib.graph import Graph
from lambda_lib.ops.meta_spawn import RuleNode
from lambda_lib.patterns import parse_pattern
from lambda_lib.governance.governor import enforce_rule_limit


def test_spawn_rules_inserts_nodes():
    graph = Graph([])
    metric = LambdaNode("Metric", data={"foo": 0.9, "bar": 0.3})
    graph.add(metric)
    rules = [n for n in graph.nodes if isinstance(n, RuleNode)]
    assert len(rules) == 1
    assert rules[0].label == "Rule:foo"


def test_rule_limit_governor():
    graph = Graph([LambdaNode("Base")])
    pat = parse_pattern("x -> y")
    for i in range(5):
        graph.add(RuleNode(f"r{i}", pat))
    result = enforce_rule_limit(graph, limit=2)
    assert result == "pruned"
    assert len([n for n in graph.nodes if isinstance(n, RuleNode)]) == 2
