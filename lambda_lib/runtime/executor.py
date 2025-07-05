#@module:
#@  version: "0.3"
#@  layer: runtime
#@  exposes: [Executor]
#@  doc: Runtime executor for λ graphs.
#@end
from ..graph import Graph
#@contract:
#@  pre: self.graph is not None
#@  post: result == self.graph
#@  assigns: [self.state]
#@end
class Executor:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.state = "init"

    def execute(self) -> Graph:
        assert self.graph is not None
        self.state = "ready"
        return self.graph
