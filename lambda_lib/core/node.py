#@module:
#@  version: "0.3"
#@  layer: core
#@  exposes: [LambdaNode]
#@  doc: Fundamental λ entity representing a unit of meaning.
#@end
#@contract:
#@  inv:
#@    - self.label is not None
#@    - isinstance(self.links, list)
#@    - forall n in self.links: isinstance(n, LambdaNode)
#@  assigns: [self.data, self.links]
#@end
class LambdaNode:
    """Skeleton entity."""
    pass
