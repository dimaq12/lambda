#@module:
#@  version: "0.3"
#@  layer: runtime
#@  exposes: [Scheduler, Executor]
#@  doc: Scheduling utilities supporting rule selection strategies.
#@end
from __future__ import annotations

import random
from typing import Iterable, Sequence

from ..graph import Graph


class Scheduler:
    """Simple scheduler that selects rules according to a strategy."""

    def __init__(self, graph: Graph, strategy: str = "fifo") -> None:
        self.graph = graph
        self.state = "init"
        self.strategy = strategy

    def select_rule(self, rules: Sequence[str]) -> str:
        """Return the next rule name according to the configured strategy."""
        assert len(rules) > 0
        rules = list(rules)
        if self.strategy == "random":
            return random.choice(rules)
        return rules[0]

    #@contract:
    #@  pre: self.graph is not None
    #@  post: result == self.graph
    #@  assigns: [self.state]
    #@end
    def execute(self) -> Graph:
        assert self.graph is not None
        self.state = "ready"
        return self.graph


# Backwards compatibility
Executor = Scheduler
