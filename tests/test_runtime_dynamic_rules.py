import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from lambda_lib.core.engine import LambdaEngine
from lambda_lib.core.node import LambdaNode
from lambda_lib.core.operation import LambdaOperation
from lambda_lib.graph import Graph
from lambda_lib.ops.meta_spawn import RuleNode
from lambda_lib.patterns import parse_pattern


def test_dynamic_rule_activation():
    engine = LambdaEngine()

    def base(node: LambdaNode) -> LambdaNode:
        return LambdaNode("A", data=0, links=node.links)

    engine.register(LambdaOperation("A", base))

    graph = Graph([LambdaNode("A")])

    engine.execute(graph)
    before = int(graph.nodes[0].data)

    rule = RuleNode("B", parse_pattern("A -> 1"))
    graph.add(rule)

    engine.execute(graph)
    after = int(graph.nodes[0].data)

    assert any(evt[0] == "rule_spawned" for evt in engine.events)
    assert after > before

