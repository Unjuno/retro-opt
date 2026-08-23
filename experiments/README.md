# Experiments

このディレクトリには再現可能な実験を置く。結果の種類を必ず区別し、仮説モデルの数値を実ゲームの測定値として扱わない。

## Status

| Experiment | Type | Status | 主な目的 |
| --- | --- | --- | --- |
| `solver_random_dag_crosscheck/` | solver validation | PASS | value iterationを小規模全policy総当たりと照合 |
| `solver_retry_crosscheck/` | solver validation | PASS | self-loopを含むretry SSPを解析解と照合 |
| `resource_dependency_toy/` | solver validation | PASS | item / gold / sell / buy / boss riskの相互依存を同一探索で扱えるか確認 |
| `repeated_attempt_objective/` | synthetic objective demo | PASS | 目標successまでの期待壁時計時間を比較 |
| `dq6_early_graph_sanity/` | structural validation | PASS | 夢見〜ホラービーストmacro graphの構造検証 |
| `dq6_early_resource_graph_sanity/` | structural validation | PASS | pickup / shopを含むresource graphの構造検証 |
| `dq6_early_resource_parameter_audit/` | parameter audit | PASS | resource graph内の未測定値を機械的に列挙 |
| `dq6_410g_shop_feasibility/` | structural sensitivity | provisional | 410G回収が鉄の盾購入可否を変える所持金帯を算出 |
| `dq6_early_break_even/` | sensitivity analysis | provisional | 追加1戦のEXP閾値価値の損益分岐を計算 |
| `dq6_early_policy/` | sensitivity analysis | provisional | 現在EXPに応じたfight/skip境界を確認 |
| `dq6_early_horizon/` | sensitivity analysis | provisional | 残りencounter機会を含む有限horizon policyを確認 |
| `dq6_metal_kill_sensitivity/` | sensitivity analysis | provisional | Metal出現率と撃破成功率を分離して評価 |

## 用語

- **solver validation**: synthetic environmentでsolver自体の数理的整合性を確認する。DQ6の実測値を主張しない。
- **structural validation**: graph / schema / state表現の構造上の矛盾を確認する。時間や勝率の正しさは主張しない。
- **parameter audit**: `unknown:*` のような未測定値を列挙し、推測で埋めずに測定対象を明示する。
- **synthetic objective demo**: route比較の目的関数が意図通り振る舞うか人工例で確認する。
- **structural sensitivity**: mechanics上確定している離散条件だけで、意思決定に影響し得る境界を調べる。時間最適性は主張しない。
- **sensitivity analysis**: 公開値の一部と明示した仮定を使い、未知パラメータに対してdecision boundaryがどう変わるかを見る。
- **empirical experiment**: emulator / 実機等から取得した測定データを用いる。ROM取得後に追加する。

## 現時点の重要な結論

1. 小規模acyclic stochastic problemでは、`solve_ssp` と全policy総当たりreferenceが200/200ケースで一致した。
2. 単純なself-loop retry問題では、`solve_ssp` と解析解が200/200ケースで一致した。
3. itemは単なる所持/非所持ではなく、combat value・売却価値・購入資金との補完関係を持つため、goldへ早期圧縮してはいけない。
4. `resource_dependency_toy` では、局所的には遅い複数pickupを組み合わせて保持・購入するpolicyが全体最適になった。resource interactionを探索しなければこの解は得られない。
5. DQ6序盤resource graphは12 nodes / 1 terminal / 0 structural errorsでPASSした。
6. 同graphには現時点で24箇所、18種類の `unknown:*` 参照があり、これらを実測・公開mechanicsで順次置換する必要がある。
7. 410G回収は、売却を無視した購入可否だけなら、開始所持金310–719Gで鉄の盾1枚、1030–1439Gで2枚の可否を変える。
8. DQ6序盤の仮説モデルでは、fight/skipは固定ruleではなく現在EXPで切り替わる。
9. 同じEXPでも、ボスまでに残る戦闘機会の数によってactionが変わり得る。
10. Metal Slimeはappearance rateとEXP reward probabilityを分離しなければならない。公開資料のB2約20%はappearanceの参考値であり、撃破率を別途測る必要がある。
11. 最速成功runと、目標successまでの期待壁時計時間が最小のrouteは一致しない場合がある。

## 次にempirical化する順序

1. event / chest / shopの所要時間
2. item pickup・売却・購入・装備変更・道具移動のcommand time
3. shop価格・売価・gold flowと、route上で利用可能なshop位置
4. encounter formation / appearance probability
5. flee / fight所要時間分布
6. Metal出現時の撃破成功率・所要時間分布
7. boss entry resource state別の戦闘時間・突破率
8. EXP / item / equipment / gold状態がさらに後続へ与えるvalue
9. small medal等の累積資源が交換地点まで持つlong-horizon value

この順で仮定を実測値へ置換する。
