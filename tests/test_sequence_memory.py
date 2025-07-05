import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from lambda_lib.memory.sequence import SequenceMemory, convolve_context


def test_sequence_memory_push_and_limit():
    mem = SequenceMemory(capacity=3)
    for i in range(5):
        mem.push(i)
    assert len(mem) == 3
    assert mem.as_list() == [2, 3, 4]


def test_n_step_reward_influences_learning():
    labels = [1, 0, 1, 1]
    memory = SequenceMemory(capacity=2)
    weight_nomem = 0.0
    weight_mem = 0.0
    preds_nomem = []
    preds_mem = []

    for t, label in enumerate(labels):
        p_nomem = int(weight_nomem > 0.5)
        preds_nomem.append(p_nomem)
        p_mem = int(weight_mem > 0.5)
        preds_mem.append(p_mem)
        if t >= memory.capacity:
            r = 1.0 if preds_mem[t - memory.capacity] == labels[t - memory.capacity] else -1.0
            memory.push_reward(r)
            weight_mem = convolve_context(weight_mem, memory, weight=0.5)

    for t in range(len(labels) - memory.capacity, len(labels)):
        r = 1.0 if preds_mem[t] == labels[t] else -1.0
        memory.push_reward(r)
        weight_mem = convolve_context(weight_mem, memory, weight=0.5)

    assert weight_nomem == 0.0
    assert weight_mem != weight_nomem
    assert len(memory.reward_history()) <= memory.capacity

