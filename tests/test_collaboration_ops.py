import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from lambda_lib.metrics.reward import reward
from lambda_lib.models.classifier import RuleBasedClassifier
from lambda_lib.ops.collaboration import vote, merge_models, convolve


def test_vote_majority():
    assert vote([0, 1, 1]) == 1
    assert vote([0, 0, 1]) == 0


def test_merge_models_averages_threshold():
    a = RuleBasedClassifier(1000)
    b = RuleBasedClassifier(500)
    merged = merge_models([a, b])
    assert isinstance(merged, RuleBasedClassifier)
    assert merged.threshold == 750


def test_convolve_blends_values():
    vals = [0.0, 1.0, 1.0]
    result = convolve(vals, weight=0.5)
    assert result == 0.5 * vals[-1] + 0.5 * sum(vals[:-1]) / (len(vals) - 1)


def test_ensemble_reward_exceeds_individual():
    samples = [
        {"latency_ms": 500, "label": 1},
        {"latency_ms": 900, "label": 1},
        {"latency_ms": 300, "label": 0},
        {"latency_ms": 1100, "label": 1},
    ]
    clf_a = RuleBasedClassifier(800)
    clf_b = RuleBasedClassifier(400)
    rewards_a = []
    rewards_b = []
    rewards_vote = []
    for s in samples:
        f = {"latency_ms": s["latency_ms"]}
        pa = clf_a.predict(f)
        pb = clf_b.predict(f)
        pv = vote([pa, pb])
        label = s["label"]
        rewards_a.append(reward(1.0 if pa == label else -1.0))
        rewards_b.append(reward(1.0 if pb == label else -1.0))
        rewards_vote.append(reward(1.0 if pv == label else -1.0))
    avg_a = sum(rewards_a) / len(rewards_a)
    avg_b = sum(rewards_b) / len(rewards_b)
    avg_vote = sum(rewards_vote) / len(rewards_vote)
    assert avg_vote >= max(avg_a, avg_b)

