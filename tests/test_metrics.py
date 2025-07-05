import pytest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from lambda_lib.metrics.accuracy import accuracy
from lambda_lib.metrics.gradient import gradient_norm
from lambda_lib.metrics.reward import reward


def test_accuracy_basic():
    preds = [1, 0, 1]
    labels = [1, 1, 1]
    assert accuracy(preds, labels) == pytest.approx(2/3)


def test_gradient_norm_clamped():
    assert gradient_norm([0.5, -0.6]) == 1.0
    assert gradient_norm([2.0]) == 1.0


def test_reward_scaling():
    assert reward(0.5, scale=1.0) == 0.5
    assert reward(2.0, scale=1.0) == 1.0
    assert reward(-3.0, scale=1.0) == -1.0
