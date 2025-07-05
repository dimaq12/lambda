#@module:
#@  version: "0.3"
#@  layer: core
#@  exposes: [Rewrite]
#@  doc: Representation of graph rewrite actions.
#@end

from dataclasses import dataclass, field
from typing import List, Tuple

from .node import LambdaNode


@dataclass
class Rewrite:
    """Collects actions that mutate a graph of :class:`LambdaNode`."""

    actions: List[Tuple[str, LambdaNode]] = field(default_factory=list)

    def add(self, node: LambdaNode) -> None:
        """Record an add-node action."""
        self.actions.append(("add", node))

    def remove(self, node: LambdaNode) -> None:
        """Record a remove-node action."""
        self.actions.append(("remove", node))

    #@contract:
    #@  post: len(result) > 0
    #@  assigns: []
    #@end
    def get_actions(self) -> List[Tuple[str, LambdaNode]]:
        """Return the list of rewrite actions."""
        result = list(self.actions)
        assert len(result) > 0
        return result
