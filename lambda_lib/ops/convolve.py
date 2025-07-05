#@module:
#@  version: "0.3"
#@  layer: ops
#@  exposes: [convolve_rule]
#@  doc: Pattern rewrite for convolving variants.
#@end

from ..patterns import parse_pattern

#@contract:
#@  post: convolve_rule.match is not None
#@  assigns: []
#@end
convolve_rule = parse_pattern("x -> convolved(x)")
