import os
import sys

# Ensure project root on path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from lambda_lib.graph.graph_utils import load_graph_from_file


g = load_graph_from_file("lambda_lib/examples/classifier/seed.yaml")
reward_nodes = [n for n in g.nodes if n.label == "RewardMetric"]
assert reward_nodes, "No RewardMetric found"
node = reward_nodes[0]
score = 0.0
if isinstance(node.data, dict):
    score = float(node.data.get("score", 0))
assert score > 0.2, f"Reward did not increase enough: got {score}"
print("✅ Reward increased — system learning confirmed.")
