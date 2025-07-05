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
from ..ops.model_spawner import ModelNode, spawn_models


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
        # spawn new models from node data
        for node in list(self.graph.nodes):
            for model in spawn_models(node):
                self.graph.add(model)

        # train or execute existing model graphs
        for idx, node in enumerate(self.graph.nodes):
            if isinstance(node, ModelNode) and isinstance(node.data, Graph):
                if node.data.nodes:
                    feat = self.graph.nodes[idx - 1].data if idx > 0 else None
                    node.data.nodes[0].data = feat
                node.engine.execute(node.data)

        self.state = "ready"
        return self.graph


# Backwards compatibility
Executor = Scheduler
