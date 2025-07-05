#@module:
#@  version: "0.3"
#@  layer: ops
#@  exposes: [phase_rule]
#@  doc: Pattern rewrite for phase shifting.
#@end

from ..patterns import parse_pattern

#@contract:
#@  post: phase_rule.match is not None
#@  assigns: []
#@end
phase_rule = parse_pattern("x -> phased(x)")
