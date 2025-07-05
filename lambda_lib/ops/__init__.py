#@module:
#@  version: "0.3"
#@  layer: ops
#@  exposes: [eval_rule, mirror_rule, phase_rule, convolve_rule, spawn_rule]
#@  doc: Package for built‑in λ operations.
#@end

from .eval import eval_rule
from .mirror import mirror_rule
from .phase import phase_rule
from .convolve import convolve_rule
from .spawn import spawn_rule
