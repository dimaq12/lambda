#@module:
#@  version: "0.3"
#@  layer: ops
#@  exposes: [spawn_rule]
#@  doc: Pattern rewrite for spawning new nodes.
#@end

from ..patterns import parse_pattern

#@contract:
#@  post: spawn_rule.match is not None
#@  assigns: []
#@end
spawn_rule = parse_pattern("x -> spawned(x)")
