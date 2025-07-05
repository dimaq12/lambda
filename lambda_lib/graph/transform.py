#@module:
#@  version: "0.3"
#@  layer: graph
#@  exposes: [transform, compose_patterns, apply_rules]
#@  doc: Graph transformation utilities.
#@end
#@contract:
#@  pre: callable(rule)
#@  post: result is not None
#@  assigns: []
#@end
from . import Graph


def transform(graph: Graph, rule):
    assert callable(rule)
    new_nodes = [rule(n) for n in graph.nodes]
    return Graph(new_nodes)


#@contract:
#@  pre: len(rules) > 0
#@  post: callable(result)
#@  assigns: []
#@end
def compose_patterns(*rules):
    """Return a rule applying all ``rules`` sequentially to a node."""
    assert len(rules) > 0
    for r in rules:
        assert callable(r)

    def composed(node):
        for r in rules:
            node = r(node)
        return node

    return composed


#@contract:
#@  pre:
#@    - graph is not None
#@    - len(rules) > 0
#@  post: result is not None
#@  assigns: []
#@end
def apply_rules(graph: Graph, *rules) -> Graph:
    """Apply ``rules`` sequentially to all nodes in ``graph``."""
    assert graph is not None
    composed = compose_patterns(*rules)
    return transform(graph, composed)
