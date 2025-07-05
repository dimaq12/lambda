#@module:
#@  version: "0.3"
#@  layer: core
#@  exposes: [Pattern, MatchResult]
#@  doc: Simple pattern matching utilities for LambdaNode graphs.
#@end

from dataclasses import dataclass
from typing import List

from .node import LambdaNode


@dataclass
class MatchResult:
    """Result of applying a :class:`Pattern` to a node."""

    matches: List[LambdaNode]

    def succeeded(self) -> bool:
        """Return True if the pattern matched at least one node."""
        return bool(self.matches)


@dataclass
class Pattern:
    """Pattern that matches :class:`LambdaNode` instances by label."""

    label: str

    #@contract:
    #@  pre: isinstance(node, LambdaNode)
    #@  post:
    #@    - isinstance(result, MatchResult)
    #@    - result.matches is not None
    #@  assigns: []
    #@end
    def match(self, node: LambdaNode) -> MatchResult:
        """Return a MatchResult if this pattern applies to ``node``."""
        assert isinstance(node, LambdaNode)
        if node.label == self.label:
            result = MatchResult([node])
        else:
            result = MatchResult([])
        assert result.matches is not None
        return result
