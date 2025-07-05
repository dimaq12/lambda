#@module:
#@  version: "0.3"
#@  layer: ops
#@  exposes: [eval_rule, mirror_rule, phase_rule, convolve_rule, spawn_rule,
#@            FeatureNode, discover_features, spawn_feature,
#@            RuleNode, spawn_rules, RefactorOp, vote, merge_models, convolve]
#@  doc: Package for built‑in λ operations.
#@end

from .eval import eval_rule
from .mirror import mirror_rule
from .phase import phase_rule
from .convolve import convolve_rule
from .spawn import spawn_rule
from .feature_discoverer import FeatureNode, discover_features
from .spawn_feature import spawn_feature
from .meta_spawn import RuleNode, spawn_rules
from .refactor import RefactorOp
from .collaboration import vote, merge_models, convolve
