#@module:
#@  version: "0.3"
#@  layer: ops
#@  exposes: [spawn_concepts]
#@  doc: Spawn ConceptNode objects when correlations exceed a threshold.
#@end
from __future__ import annotations

from typing import Dict, List

from ..core.node import LambdaNode, ConceptNode

_DEFAULT_CONCEPT_THRESHOLD = 0.9

_best_corr: Dict[str, float] = {}


def spawn_concepts(node: LambdaNode, threshold: float = _DEFAULT_CONCEPT_THRESHOLD) -> List[ConceptNode]:
    """Return new ConceptNode objects if ``node.data`` contains
    correlation values above ``threshold``.
    """
    concepts: List[ConceptNode] = []
    if isinstance(node.data, dict):
        for name, value in node.data.items():
            try:
                corr = float(value)
            except Exception:
                continue
            prev = _best_corr.get(name, float("-inf"))
            if corr >= threshold and corr > prev:
                _best_corr[name] = corr
                concepts.append(ConceptNode(name, corr))
    return concepts
