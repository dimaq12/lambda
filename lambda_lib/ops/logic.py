#@module:
#@  version: "0.3"
#@  layer: ops
#@  exposes: [logical_and]
#@  doc: Logical λ operations.
#@end
#@contract:
#@  pre: isinstance(p, bool) and isinstance(q, bool)
#@  post: result == (p and q)
#@  assigns: []
#@end
def logical_and(p, q):
    pass
