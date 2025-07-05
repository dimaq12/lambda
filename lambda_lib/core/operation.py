#@module:
#@  version: "0.3"
#@  layer: core
#@  exposes: [LambdaOperation]
#@  doc: Describes a transformation that can be applied to LambdaNode.
#@end
#@contract:
#@  post: result.name == self.name
#@  assigns: []
#@end
class LambdaOperation:
    """Skeleton operation descriptor."""
    pass
