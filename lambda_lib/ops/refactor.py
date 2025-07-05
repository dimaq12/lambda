#@module:
#@  version: "0.3"
#@  layer: ops
#@  exposes: [RefactorOp]
#@  doc: Graph cleanup operation removing duplicates and dead branches.
#@end
from __future__ import annotations

import math
from typing import Dict, Tuple, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from ..graph import Graph

from ..core.node import LambdaNode


class RefactorOp:
    """Deduplicate nodes and prune unused branches based on entropy."""

    def __init__(self, entropy_threshold: float = 1.0) -> None:
        self.entropy_threshold = entropy_threshold

    def _entropy(self, counts: Dict[str, int]) -> float:
        total = sum(counts.values())
        if total == 0:
            return 0.0
        ent = 0.0
        for c in counts.values():
            p = c / total
            if p > 0:
                ent -= p * math.log2(p)
        return ent

    #@contract:
    #@  pre: graph is not None
    #@  post: result is graph
    #@  assigns: [graph.nodes]
    #@end
    def __call__(self, graph: 'Graph') -> 'Graph':
        from ..graph import Graph  # local import to avoid circular dependency

        assert graph is not None
        counts: Dict[str, int] = {}
        for n in graph.nodes:
            counts[n.label] = counts.get(n.label, 0) + 1
        ent = self._entropy(counts)
        if ent <= self.entropy_threshold:
            # deduplicate by label and data
            new_nodes: list[LambdaNode] = []
            seen: Set[Tuple[str, str]] = set()
            for n in graph.nodes:
                key = (n.label, repr(n.data))
                if key in seen:
                    continue
                seen.add(key)
                new_nodes.append(n)

            # compute usage counts
            usage: Dict[LambdaNode, int] = {n: 0 for n in new_nodes}
            for n in new_nodes:
                for link in n.links:
                    if link in usage:
                        usage[link] += 1

            # remove nodes that have no links and are unused
            new_nodes = [n for n in new_nodes if n.links or usage[n] > 0]
            graph.nodes = new_nodes
        return graph
