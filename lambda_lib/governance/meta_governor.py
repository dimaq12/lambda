#@module:
#@  version: "0.3"
#@  layer: governance
#@  exposes: [MetaGovernor]
#@  doc: Adaptive governor adjusting limits based on reward and resource cost.
#@end
from __future__ import annotations

from dataclasses import dataclass

from ..graph import Graph
from .governor import (
    enforce_node_limit,
    enforce_rule_limit,
    enforce_feature_limit,
)


@dataclass
class MetaGovernor:
    """Adaptive governor that tunes node and rule limits."""

    node_limit: int = 10
    rule_limit: int = 5
    max_features: int = 5
    max_rules: int = 5
    cpu_limit: float = 1.0
    ram_limit: float = 1.0
    graph_limit: int = 100

    def _cost(self, cpu: float, ram: float, graph_size: int) -> float:
        cost = 0.0
        if self.cpu_limit:
            cost += cpu / self.cpu_limit
        if self.ram_limit:
            cost += ram / self.ram_limit
        if self.graph_limit:
            cost += graph_size / self.graph_limit
        return cost

    def evaluate(self, reward: float, cpu: float, ram: float, graph: Graph) -> None:
        """Update limits based on reward to cost ratio."""
        cost = self._cost(cpu, ram, len(graph.nodes))
        if cost <= 0:
            ratio = reward
        else:
            ratio = reward / cost
        if ratio < 1.0:
            self.node_limit = max(1, self.node_limit - 1)
            self.rule_limit = max(1, self.rule_limit - 1)
        else:
            self.node_limit += 1
            self.rule_limit += 1

        if ratio > 1.2:
            self.max_features += 1
            self.max_rules += 1
        elif ratio < 1.2:
            self.max_features = max(1, self.max_features - 1)
            self.max_rules = max(1, self.max_rules - 1)

    def govern(self, graph: Graph) -> None:
        """Apply current limits to ``graph``."""
        enforce_node_limit(graph, self.node_limit)
        enforce_rule_limit(graph, self.rule_limit, self.max_rules)
        enforce_feature_limit(graph, self.max_features)
