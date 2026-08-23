from __future__ import annotations


def expected_wall_clock_to_success_seconds(
    *,
    success_probability: float,
    mean_success_duration_seconds: float,
    mean_failure_duration_seconds: float,
) -> float:
    """IID attemptを成功まで繰り返す期待壁時計時間 [s]。

    前提:
    - 各attemptは同一policy・同一分布で独立
    - success_probability = p > 0
    - 成功attemptの平均時間 = Ts
    - 失敗attemptの平均時間 = Tf
    - failure durationには、そのattemptを打ち切るまでに消費する時間を含める

    成功前の失敗回数の期待値は (1-p)/p なので、

        E[T] = Ts + ((1-p)/p) * Tf

    target time突破・完走など、「success」の定義はexperiment側で明示する。
    """

    if not 0.0 < success_probability <= 1.0:
        raise ValueError("success_probability must be in (0, 1]")
    if mean_success_duration_seconds < 0.0:
        raise ValueError("mean_success_duration_seconds must be non-negative")
    if mean_failure_duration_seconds < 0.0:
        raise ValueError("mean_failure_duration_seconds must be non-negative")

    expected_failures = (1.0 - success_probability) / success_probability
    return (
        mean_success_duration_seconds
        + expected_failures * mean_failure_duration_seconds
    )
