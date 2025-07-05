#@module:
#@  version: "0.3"
#@  layer: core
#@  exposes: [LambdaEngine]
#@  doc: Executes λ graphs defined by nodes & operations.
#@end
from typing import Dict

from ..graph import Graph
from ..runtime.executor import Executor
from .operation import LambdaOperation
#@contract:
#@  pre: len(graph.nodes) > 0
#@  post:
#@    - result is not None
#@    - result.state == "ready"
#@  assigns: [self.registry]
#@end
class LambdaEngine:
    """Executes graphs of :class:`LambdaNode` operations."""

    def __init__(self) -> None:
        self.registry: Dict[str, LambdaOperation] = {}

    def register(self, operation: LambdaOperation) -> None:
        self.registry[operation.name] = operation

    def execute(self, graph: Graph) -> Executor:
        assert len(graph.nodes) > 0
        executor = Executor(graph)
        executor.execute()
        assert executor.state == "ready"
        return executor
