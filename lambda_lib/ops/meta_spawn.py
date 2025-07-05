#@module:
#@  version: "0.3"
#@  layer: ops
#@  exposes: [RuleNode, spawn_rules]
#@  doc: Spawn micro-op rules based on correlation heuristics.
#@end
from __future__ import annotations

from typing import List

from ..core.node import LambdaNode
from ..patterns import parse_pattern
from ..patterns.dsl import Pattern


class RuleNode(LambdaNode):
    """Specialised LambdaNode representing a spawned rewrite rule."""

    def __init__(self, name: str, pattern: Pattern):
        super().__init__(f"Rule:{name}", data=pattern, links=[])


_DEFAULT_THRESHOLD = 0.8


#@contract:
#@  post: isinstance(result, list)
#@  assigns: []
#@end
def spawn_rules(node: LambdaNode, threshold: float = _DEFAULT_THRESHOLD) -> List[RuleNode]:
    """Return new :class:`RuleNode` objects if ``node.data`` contains
    correlations above ``threshold``.
    """
    rules: List[RuleNode] = []
    if isinstance(node.data, dict):
        for name, value in node.data.items():
            try:
                corr = float(value)
            except Exception:
                continue
            if corr >= threshold:
                pattern = parse_pattern(f"x -> {name}(x)")
                rules.append(RuleNode(name, pattern))
    return rules
