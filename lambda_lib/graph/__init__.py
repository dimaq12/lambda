#@module:
#@  version: "0.3"
#@  layer: graph
#@  exposes: [Graph]
#@  doc: Graph utilities for λ structures.
#@end

from dataclasses import dataclass, field
from typing import Iterable, List

from ..core.node import LambdaNode
from ..ops.feature_discoverer import discover_features, discover
from ..ops.spawn_feature import spawn_feature
from ..ops.meta_spawn import spawn_rules
from ..ops.model_spawner import spawn_models
from ..ops.concept_inventor import spawn_concepts


@dataclass
class Graph:
    """Simple collection of :class:`LambdaNode` instances."""

    nodes: List[LambdaNode] = field(default_factory=list)
    state: str = "init"

    def __post_init__(self) -> None:
        self.nodes = list(self.nodes)
        self._check_invariants()

    def _check_invariants(self) -> None:
        assert isinstance(self.nodes, list)
        assert all(isinstance(n, LambdaNode) for n in self.nodes)

    def add(self, node: LambdaNode) -> None:
        self.nodes.append(node)
        if isinstance(node.data, dict) and "label" in node.data:
            for expr in discover([node]):
                self.nodes.append(
                    spawn_feature(LambdaNode("FeatureDiscoverer", data={"expr": expr}))
                )
        for feature in discover_features(node):
            self.nodes.append(feature)
        for rule in spawn_rules(node):
            self.nodes.append(rule)
        for model in spawn_models(node):
            self.nodes.append(model)
        for concept in spawn_concepts(node):
            self.nodes.append(concept)
            for rule in spawn_rules(concept):
                self.nodes.append(rule)
        self._check_invariants()

