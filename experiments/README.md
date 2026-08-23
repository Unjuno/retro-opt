# Experiments

このディレクトリには再現可能な実験を置く。結果の種類を必ず区別し、仮説モデルの数値を実ゲームの測定値として扱わない。

## Status

| Experiment | Type | Status | 主な目的 |
| --- | --- | --- | --- |
| `solver_random_dag_crosscheck/` | solver validation | PASS | value iterationを小規模全policy総当たりと照合 |
| `solver_retry_crosscheck/` | solver validation | PASS | self-loopを含むretry SSPを解析解と照合 |
| `dq6_early_break_even/` | sensitivity analysis | provisional | 追加1戦のEXP閾値価値の損益分岐を計算 |
| `dq6_early_policy/` | sensitivity analysis | provisional | 現在EXPに応じたfight/skip境界を確認 |
| `dq6_early_horizon/` | sensitivity analysis | provisional | 残りencounter機会を含む有限horizon policyを確認 |
| `dq6_metal_kill_sensitivity/` | sensitivity analysis | provisional | Metal出現率と撃破成功率を分離して評価 |

## 用語

- **solver validation**: synthetic environmentでsolver自体の数理的整合性を確認する。DQ6の実測値を主張しない。
- **sensitivity analysis**: 公開値の一部と明示した仮定を使い、未知パラメータに対してdecision boundaryがどう変わるかを見る。
- **empirical experiment**: emulator / 実機等から取得した測定データを用いる。ROM取得後に追加する。

## 現時点の重要な結論

1. 小規模acyclic stochastic problemでは、`solve_ssp` と全policy総当たりreferenceが200/200ケースで一致した。
2. 単純なself-loop retry問題では、`solve_ssp` と解析解が200/200ケースで一致した。
3. DQ6序盤の仮説モデルでは、fight/skipは固定ruleではなく現在EXPで切り替わる。
4. 同じEXPでも、ボスまでに残る戦闘機会の数によってactionが変わり得る。
5. Metal Slimeはappearance rateとEXP reward probabilityを分離しなければならない。公開資料のB2約20%はappearanceの参考値であり、撃破率を別途測る必要がある。

## 次にempirical化する順序

1. encounter formation / appearance probability
2. flee / fight所要時間分布
3. Metal出現時の撃破成功率・所要時間分布
4. EXP状態別のHorror Beast戦時間・突破率
5. 847 / 930等のEXP状態がさらに後続へ与えるvalue

この順で仮定を実測値へ置換する。
