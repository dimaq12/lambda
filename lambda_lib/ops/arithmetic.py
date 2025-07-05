#@module:
#@  version: "0.3"
#@  layer: ops
#@  exposes: [add, sub]
#@  doc: Arithmetic λ operations.
#@end
#@contract:
#@  pre: isinstance(a, (int, float)) and isinstance(b, (int, float))
#@  post: result == a + b
#@  assigns: []
#@end
def add(a, b):
    pass

def sub(a, b):
    pass
