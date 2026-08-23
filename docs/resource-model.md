# Resource-aware route model

## 1. 目的

DQ6 の route optimization では、EXP だけを将来価値として扱うと不十分である。

同じ進行地点でも、以下が異なれば後続の合法 action、所要時間、勝率、金策、menu 操作量が変わり得る。

- HP / MP / alive / status
- EXP / level / stats
- vocation / proficiency
- bag contents
- 各キャラの personal items とその順序
- equipment
- gold
- 未回収 item / 回収済み item
- 売却済み / 消費済み resource
- story flags
- reachable shop / future purchase requirements
- observable random outcomes

したがって macro state は「現在位置 + 資源ベクトル」として扱う。

## 2. Action feasibility と value を分離する

「この item がないと勝てない」「所持金が足りないので買えない」といった条件を、恣意的な penalty として reward に埋め込まない。

例:

```text
buy(iron_shield)
  legal iff gold >= 720

boss_policy_X
  legal iff required items / party members / flags are available
```

物理的には実行可能だが弱い戦術は legal action として残し、その差を transition の time / clear probability / resource consumption で表現する。

物理的・ruleset 的に不可能な action のみ action set から除外する。

## 3. Resource action

route graph では以下を同列の action として扱う。

- pickup / skip pickup
- use / hold
- transfer
- equip / unequip
- sell / keep
- buy / skip purchase
- rest / revive
- fight / flee / farm / leave farming area
- route branch

1つの pickup は複数の役割を持ち得る。

例:

```text
iron_claw
  ├─ weaponとして使う
  ├─ 後で売る
  ├─ gold不足を解消する
  └─ 別の装備を売らずに済ませる
```

したがって「現在の戦闘で使わない」ことは、その item が不要であることを意味しない。

## 4. Complementarity

資源は独立に評価できない場合がある。

```text
item A 単体: pickup timeの方が大きく不採用
item B 単体: pickup timeの方が大きく不採用
A + B: shop / boss policyが新たに成立して全体では採用
```

`experiments/resource_dependency_toy/` はこの補完関係を synthetic environment で regression test する。

## 5. Dominance pruning の注意

単純な

```text
faster + more EXP + more gold + more items
```

を常に優越とはみなさない。

### 比較的 monotone と扱いやすい候補

- 同一の他状態を保ったままの extra gold
- 同一位置・同一配置・同一操作列で得た純粋な stat increase

ただし将来価値へ影響しないことを別途確認する。

### 原則として単純比較しない候補

- personal item の配置
- inventory order
- equipment
- consumable の有無
- small medal の枚数
- sellable asset
- story / resource flags

item が1個多いことで menu cursor distance が増える場合すらあるため、`item count >=` だけを理由に state を支配判定してはならない。

安全な pruning は、将来の action set と transition value に影響する状態次元が同値、または一方向に単調であることを確認してから行う。

## 6. Long-horizon value

pickup の価値は最初に使われる地点までではなく、価値が消滅する地点まで伝播させる。

例:

- small medal: medal exchange の選択肢へ影響するまで
- sellable equipment: 売却または不要化するまで
- seed: 永続 stat change なのでその stat が意味を持つ将来戦闘まで
- gold: future mandatory/candidate purchase が終了するまで
- MP item: 使用・売却・run終了まで

このため「序盤だけを独立に最適化する」場合でも、区間終端には downstream value function が必要になる。

## 7. 現在の実装

- `src/retro_opt/games/dq6/state.py`
  - party / stats / personal items / equipment / bag / gold / resource flags
- `src/retro_opt/games/dq6/feasibility.py`
  - action requirements
  - resource effects
- `games/sfc/dq6/model/state_dimensions.json`
  - state から落としてはいけない候補次元
- `games/sfc/dq6/model/early_resource_candidates.json`
  - 公開チャートから抽出した序盤の資源判断候補
- `games/sfc/dq6/model/early_resource_event_graph.json`
  - アモール北〜ホラービースト後買物の資源付き macro graph

## 8. 未測定値

現段階では以下を推測値で固定しない。

- chest / item detour time
- menu 操作時間
- inventory order による cursor cost
- formation別 battle/flee distribution
- seed roll distribution
- boss clear probability / time by resource state
- asset-specific sell action time
- downstream value of medals / gold / equipment

これらは公開資料で確定できる mechanics と emulator 実測値へ順次置換する。
