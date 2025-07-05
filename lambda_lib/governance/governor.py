#@module:
#@  version: "0.3"
#@  layer: governance
#@  exposes: [enforce_node_limit, enforce_feature_limit, enforce_rule_limit]
#@  doc: Simple governor enforcing graph node limits.
#@end

from ..graph import Graph
from ..ops.feature_discoverer import FeatureNode
from ..ops.meta_spawn import RuleNode


#@contract:
#@  pre: limit >= 0
#@  post: result in ['ok', 'pruned']
#@  assigns: [graph.nodes]
#@end
def enforce_node_limit(graph: Graph, limit: int) -> str:
    """Ensure ``graph`` does not exceed ``limit`` nodes."""
    assert limit >= 0
    if len(graph.nodes) > limit:
        graph.nodes = graph.nodes[:limit]
        result = "pruned"
    else:
        result = "ok"
    assert result in ["ok", "pruned"]
    return result


#@contract:
#@  pre: limit >= 0
#@  post: result in ['ok', 'pruned']
#@  assigns: [graph.nodes]
#@end
def enforce_feature_limit(graph: Graph, limit: int) -> str:
    """Ensure no more than ``limit`` :class:`FeatureNode` exist in ``graph``."""
    assert limit >= 0
    features = [n for n in graph.nodes if isinstance(n, FeatureNode)]
    if len(features) > limit:
        excess = features[limit:]
        graph.nodes = [n for n in graph.nodes if n not in excess]
        result = "pruned"
    else:
        result = "ok"
    assert result in ["ok", "pruned"]
    return result


#@contract:
#@  pre: limit >= 0
#@  post: result in ['ok', 'pruned']
#@  assigns: [graph.nodes]
#@end
def enforce_rule_limit(graph: Graph, limit: int) -> str:
    """Ensure no more than ``limit`` :class:`RuleNode` exist in ``graph``."""
    assert limit >= 0
    rules = [n for n in graph.nodes if isinstance(n, RuleNode)]
    if len(rules) > limit:
        excess = rules[limit:]
        graph.nodes = [n for n in graph.nodes if n not in excess]
        result = "pruned"
    else:
        result = "ok"
    assert result in ["ok", "pruned"]
    return result
