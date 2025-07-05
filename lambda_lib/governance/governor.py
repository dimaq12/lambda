#@module:
#@  version: "0.3"
#@  layer: governance
#@  exposes: [enforce_node_limit]
#@  doc: Simple governor enforcing graph node limits.
#@end

from ..graph import Graph


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
