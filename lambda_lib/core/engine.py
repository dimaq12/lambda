#@module:
#@  version: "0.3"
#@  layer: core
#@  exposes: [LambdaEngine]
#@  doc: Executes λ graphs defined by nodes & operations.
#@end
from typing import Dict, Set

from ..patterns import parse_pattern
from ..patterns.dsl import Pattern

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
        self._seen_rules: Set[LambdaNode] = set()
        self.events: list[tuple[str, str]] = []

    def _register_rule_ops(self, graph: Graph) -> None:
        for node in graph.nodes:
            if node in self._seen_rules:
                continue
            is_pattern = False
            if isinstance(node.data, dict) and node.data.get("type") == "pattern":
                is_pattern = True
            if node.label.startswith("Rule:"):
                is_pattern = True
            if not is_pattern:
                continue

            pattern: Pattern | None = None
            if isinstance(node.data, Pattern):
                pattern = node.data
            elif isinstance(node.data, str):
                pattern = parse_pattern(node.data)
            elif isinstance(node.data, dict):
                spec = (
                    node.data.get("expr")
                    or node.data.get("pattern")
                    or node.data.get("rule")
                )
                if isinstance(spec, str):
                    pattern = parse_pattern(spec)
            if pattern is None:
                continue

            def rule_op(n: LambdaNode, _pat: Pattern = pattern) -> LambdaNode:
                return LambdaNode(n.label, data=_pat.rewrite, links=n.links)

            self.register(LambdaOperation(pattern.match, rule_op))
            self.events.append(("rule_spawned", f"{pattern.match}->{pattern.rewrite}"))
            self._seen_rules.add(node)

    def register(self, operation: LambdaOperation) -> None:
        self.registry[operation.name] = operation

    def execute(self, graph: Graph) -> Scheduler:
        assert len(graph.nodes) > 0

        # register rule operations present in graph
        self._register_rule_ops(graph)

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
        self._register_rule_ops(graph)
        assert scheduler.state == "ready"
        return scheduler
