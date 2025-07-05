#@module:
#@  version: "0.3"
#@  layer: runtime
#@  exposes: [Executor]
#@  doc: Runtime executor for λ graphs.
#@end
#@contract:
#@  pre: self.graph is not None
#@  post: result == self.graph
#@  assigns: [self.state]
#@end
class Executor:
    pass
