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
#@  pre:
#@    - limit >= 0
#@    - max_features is None or max_features >= 0
#@  post: result in ['ok', 'pruned']
#@  assigns: [graph.nodes]
#@end
def enforce_feature_limit(
    graph: Graph, limit: int, max_features: int | None = None
) -> str:
    """Ensure the number of :class:`FeatureNode` objects does not exceed ``limit``.

    If ``max_features`` is provided, it represents a hard cap that ``limit``
    cannot exceed.
    """
    assert limit >= 0
    if max_features is not None:
        assert max_features >= 0
        limit = min(limit, max_features)
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
#@  pre:
#@    - limit >= 0
#@    - max_rules is None or max_rules >= 0
#@  post: result in ['ok', 'pruned']
#@  assigns: [graph.nodes]
#@end
def enforce_rule_limit(
    graph: Graph, limit: int, max_rules: int | None = None
) -> str:
    """Ensure the number of :class:`RuleNode` objects does not exceed ``limit``.

    ``max_rules`` may specify an additional hard cap.
    """
    assert limit >= 0
    if max_rules is not None:
        assert max_rules >= 0
        limit = min(limit, max_rules)
    rules = [n for n in graph.nodes if isinstance(n, RuleNode)]
    if len(rules) > limit:
        excess = rules[limit:]
        graph.nodes = [n for n in graph.nodes if n not in excess]
        result = "pruned"
    else:
        result = "ok"
    assert result in ["ok", "pruned"]
    return result
