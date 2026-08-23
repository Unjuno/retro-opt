# Random DAG solver cross-check v0

## 目的

`retro-opt` の本solverをDQ6へ投入する前に、小さい確率環境では**全policy総当たり**と一致することを確認する。

## 方法

- 6 stateのacyclic stochastic graphを200個生成
- terminal以外の各stateに2 action
- actionごとに後方stateへ1〜2本の確率遷移
- durationは0.1〜20秒の乱数
- random seed: `20260824`
- 各環境でdeterministic stationary policyを全列挙
- `solve_bruteforce_acyclic` の最小期待時間と `solve_ssp` のvalue iteration結果を比較

6 state中5 decision stateなので、各caseで最大 `2^5 = 32` policyを総当たりする。

## 結果

- case count: 200
- mismatch: 0
- max absolute error: 0.0 s
- PASS

この結果はacyclicかつ小規模な問題に限ったvalidationであり、cycleを含む一般SSPの完全な正しさを証明するものではない。

## 次のvalidation

- self-loop / retryを含むproper SSP
- reset actionを含むrenewal型問題
- observation-equivalence制約付きpolicy
- Pareto frontierのbrute-force照合
