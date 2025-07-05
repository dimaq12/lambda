import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from lambda_lib.core.node import LambdaNode
from lambda_lib.graph import Graph
from lambda_lib.ops.meta_spawn import RuleNode
from lambda_lib.patterns import parse_pattern
from lambda_lib.governance.meta_governor import MetaGovernor


def test_meta_governor_tightens_on_high_cost():
    graph = Graph([LambdaNode(str(i)) for i in range(5)])
    pat = parse_pattern("x -> y")
    for i in range(3):
        graph.add(RuleNode(f"r{i}", pat))

    mg = MetaGovernor(node_limit=5, rule_limit=3, cpu_limit=1.0, ram_limit=1.0, graph_limit=10)
    mg.evaluate(reward=0.2, cpu=2.0, ram=2.0, graph=graph)
    mg.govern(graph)

    assert mg.node_limit == 4
    assert mg.rule_limit == 2
    assert len(graph.nodes) <= mg.node_limit
    assert len([n for n in graph.nodes if isinstance(n, RuleNode)]) <= mg.rule_limit


def test_meta_governor_relaxes_on_low_cost():
    graph = Graph([LambdaNode("base")])
    mg = MetaGovernor(node_limit=1, rule_limit=1, cpu_limit=1.0, ram_limit=1.0, graph_limit=10)
    mg.evaluate(reward=2.0, cpu=0.1, ram=0.1, graph=graph)

    assert mg.node_limit == 2
    assert mg.rule_limit == 2


def test_meta_governor_adjusts_feature_rule_limits():
    graph = Graph([LambdaNode("base")])
    mg = MetaGovernor(
        node_limit=1,
        rule_limit=1,
        max_features=3,
        max_rules=3,
        cpu_limit=1.0,
        ram_limit=1.0,
        graph_limit=10,
    )

    mg.evaluate(reward=0.5, cpu=2.0, ram=2.0, graph=graph)
    assert mg.max_features == 2
    assert mg.max_rules == 2

    mg.evaluate(reward=10.0, cpu=0.1, ram=0.1, graph=graph)
    assert mg.max_features == 3
    assert mg.max_rules == 3

