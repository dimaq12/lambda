#@module:
#@  version: "0.3"
#@  layer: ops
#@  exposes: [mirror_rule]
#@  doc: Pattern rewrite for mirroring nodes.
#@end

from ..patterns import parse_pattern

#@contract:
#@  post: mirror_rule.match is not None
#@  assigns: []
#@end
mirror_rule = parse_pattern("x -> x")
