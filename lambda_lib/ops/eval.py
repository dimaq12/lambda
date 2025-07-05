#@module:
#@  version: "0.3"
#@  layer: ops
#@  exposes: [eval_rule]
#@  doc: Pattern rewrite for evaluation.
#@end

from ..patterns import parse_pattern

#@contract:
#@  post: eval_rule.match is not None
#@  assigns: []
#@end
eval_rule = parse_pattern("x -> eval(x)")
