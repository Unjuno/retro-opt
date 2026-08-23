# Retry / cyclic SSP cross-check v0

## 目的

RTAでは失敗後に同じ判断点へ戻る再戦・retryがあるため、acyclic graphだけでなくself-loopを含むstochastic shortest pathでも`solve_ssp`を検証する。

## 環境

state `start` で2 actionを持つ。

- `safe`: `safe_cost_seconds`を払い確実にgoal
- `retry`: 1回あたり`attempt_cost_seconds`を払い、確率`p`でgoal、失敗時は`start`へ戻る

`retry`をstationary policyとして繰り返した期待時間は解析的に `attempt_cost_seconds / p`。

したがって最適値は

```text
min(safe_cost_seconds, attempt_cost_seconds / p)
```

で求められる。

## 方法

- random seed: `20260824`
- 200 cases
- `p`: 0.01〜0.99
- retry cost: 0.1〜20秒
- safe cost: 1〜100秒
- value iterationと解析解を比較

## 結果

- mismatches: 0 / 200
- max absolute error: `9.542588941258145e-12` s
- PASS

これは単純な1-state self-loopについてのvalidationであり、一般のmulti-state cyclic SSP全体の証明ではない。
