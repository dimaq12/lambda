import os
import sys
import pytest

# Ensure the project root is on sys.path so lambda_lib can be imported when
# running tests directly.
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from lambda_lib.core.engine import LambdaEngine
from lambda_lib.core.node import LambdaNode
from lambda_lib.core.operation import LambdaOperation
from lambda_lib.graph import Graph


def test_engine_execute_returns_ready_executor():
    node = LambdaNode("noop")
    graph = Graph([node])

    def noop_op(n: LambdaNode) -> LambdaNode:
        return LambdaNode("noop", data=n.data, links=n.links)

    op = LambdaOperation("noop", noop_op)

    engine = LambdaEngine()
    engine.register(op)

    executor = engine.execute(graph)
    assert executor.state == "ready"
