#@module:
#@  version: "0.3"
#@  layer: graph
#@  exposes: [transform]
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
