#@module:
#@  version: "0.3"
#@  layer: core
#@  exposes: [LambdaEngine]
#@  doc: Executes λ graphs defined by nodes & operations.
#@end
from typing import Dict

from ..graph import Graph
from ..runtime.scheduler import Scheduler
from .operation import LambdaOperation
from .node import LambdaNode
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

    def execute(self, graph: Graph) -> Scheduler:
        assert len(graph.nodes) > 0

        # simple evaluation loop applying registered operations by name
        graph.state = "running"
        new_nodes = []
        for idx, node in enumerate(graph.nodes):
            operation = self.registry.get(node.label)
            if node.raw and node.label == "FeatureMaker":
                prev_data = new_nodes[idx - 1].data if idx > 0 else None
                node = LambdaNode(node.label, data=prev_data, links=node.links, raw=node.raw)
            elif operation is not None:
                node = operation(node)
            new_nodes.append(node)
        graph.nodes = new_nodes

        scheduler = Scheduler(graph)
        scheduler.execute()
        assert scheduler.state == "ready"
        return scheduler
