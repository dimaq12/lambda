#!/usr/bin/env python3
"""Run anomaly validation in worker processes and print metrics."""

import os
import sys
from multiprocessing import Process, Manager

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from tests.test_anomaly_validation import run_anomaly_detector


def _worker(idx: int, results):
    feature_exprs, metrics = run_anomaly_detector()
    results[idx] = (feature_exprs, metrics)


def main() -> None:
    runs = 3
    manager = Manager()
    results = manager.dict()
    processes = []
    for i in range(runs):
        p = Process(target=_worker, args=(i, results))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()

    for i in range(runs):
        feature_exprs, m = results[i]
        print(f"Run {i} features: {feature_exprs}")
        print(
            f"Run {i} duration: {m['duration']:.3f}s, accuracy: {m['accuracy']:.3f}, "
            f"fpr: {m['fpr']:.3f}, score: {m['score']:.3f}"
        )
        print(f"Graph nodes: {m['graph_nodes']}")
        print()


if __name__ == "__main__":
    main()

