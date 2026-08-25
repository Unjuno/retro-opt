# DQ6 mechanics-derived search space

## 1. 目的

SFC版DQ6のRTA探索空間を、人間が思いついた少数の変数から設計しない。
攻略サイト・解析資料・既存RTAチャートに既知のゲーム機構を列挙し、

```text
static game data
    ↓
state variables / latent variables
    ↓
legal actions
    ↓
transition probabilities
    ↓
local solvers
    ↓
global resource-aware policy
```

の順で探索モデルを構築する。

原則として、攻略・解析データから厳密に決まるものは emulator sampling で推定しない。
emulator実測は frame cost、menu cost、未解明仕様の検証、公開情報とのcross-checkに使う。

## 2. Mechanics inventory

### 2.1 Movement / encounter process

SFC版DQ6の通常遭遇は単純な「1歩ごとの一定確率」ではなく、戦闘発生counterを歩行で減少させる形式として解析されている。
地形・地域・floorごとに減少係数が異なり、floor移動、戦闘、ルーラ/キメラ/リレミト等でcounterがresetされる。
忍び足はcounter消費量を変化させ、聖水/トヘロスにはarea levelとの関係がある。

したがってroute edgeは距離だけではなく、少なくとも以下を持つ。

- tile sequence / terrain class
- encounter-table id
- encounter-counter distribution or belief
- floor-transition/reset points
- repel / stealth state and remaining duration
- protagonist level versus area level
- preemptive / enemy-preemptive setting

このため「最短歩数」と「期待最短時間」は一致しない。1歩の差が次のencounterを跨ぐかどうか、floor transitionでcounterを捨てるかどうかまで価値を持つ。

### 2.2 Encounter formation

敵編成は地域ごとの単純なmonster listではない。解析資料では、通常戦闘用のformation tableが

- single group / multiple groups / fixed group
- frequency weights
- monster id
- member-count rule
- additional-group count

を持ち、乱数から編成を生成することが示されている。

したがって「メタル出現率」を直接1個の定数にするより、formation generatorから厳密に導出する方がよい。

探索時には

```text
route position
  -> encounter table
  -> formation distribution
  -> battle policy / flee policy
  -> time, EXP, gold, HP/MP, drops distribution
```

と接続する。

### 2.3 Escape / preemptive / action order

既知の仕様として、通常逃走は試行回数で成功率が変わる。
また主人公levelとarea levelの関係、先制状態、敵全員行動不能等で確定逃走になる場合がある。
レンジャーは通常判定失敗後に熟練度依存の追加逃走判定を持つ。

行動順も固定ではなく、通常行動では概ね `(agility + 20) × random(0.5..1)` によりturnごとに変動する。
疾風突き等には別priorityがある。

従ってbattle stateには最低でも

- escape attempt count
- preemptive state
- area level
- protagonist level
- current vocation and proficiency
- effective agility
- priority-action class

が必要になる。

### 2.4 Monster AI

monster dataにはHP/MP/attack/defense/agilityだけでなく、

- action slot probabilities
- rotation state
- phase transition
- 1–2 actions / 2 actions
- target-selection intelligence
- low-HP focus / fixed focus / rear focus
- automatic HP recovery
- initial status
- resistances

が存在する。

したがってboss battleを単純な「平均DPS対HP」として扱ってはいけない。
rotation indexやphaseは将来行動分布を変えるのでbattle stateである。

### 2.5 Damage / resistance / equipment

敵には複数種類の属性・状態異常耐性があり、武器/特技にはdragon/zombie/flying/metal等の系統補正もある。
防具はdefenseだけでなく、炎・吹雪・呪文の固定軽減、回避、反射、戦闘中使用効果等を持つ。

従ってequipment comparisonは `defense` 一軸ではなく、

```text
attack contribution
physical defense
fixed elemental reduction
status interaction
in-battle use effect
action-order effect
menu/equip cost
resale value
```

のvectorとして扱う。

### 2.6 EXP / level / innate growth

character levelは単なるHP増加ではない。

- next EXP threshold
- HP/MP/stat increase
- innate spell/skill unlock
- area-levelとの比較によるescape/repel条件
- agility変化によるaction order

へ波及する。

したがってEXP valueはboss直前だけでなく、以後の全encounter/flee/battle costへ伝播する。

### 2.7 Vocation / proficiency

職業は重要な離散stateである。

- current vocation
- rank
- wins toward next rank
- previously mastered vocations
- unlocked advanced vocations
- learned commands
- vocation stat multipliers
- vocation special ability
- master bonus
- special vocation item availability

が将来action setとtransitionを変える。

さらにareaごとに熟練度獲得のlevel limitがあるため、同じ1戦でも「EXPは得るが熟練度は得ない」場合がある。
よってbattle rewardを単純な `(exp, proficiency=1)` にしてはいけない。

### 2.8 Gold economy

Goldは

- enemy gold reward
- chest / fixed pickup
- sale
- merchant vocation bonus等
- recovery / revive cost
- shop purchase
- future optional chest requirement

へ接続する。

itemは売価だけに圧縮せず、combat valueを保持したままsell actionを生成する。

### 2.9 Drops / steal / conditional routing

monster drop ratesには既知の段階（1/8, 1/16, ..., 1/4096等）が存在する。
盗賊の盗みは別判定で、熟練度・人数・死亡状態等が関係し、盗みに成功した場合は通常dropと排他的になる仕様が公開されている。

従ってbattle terminal transitionは

```text
clear
 + exp
 + gold
 + hp/mp/status
 + drop/steal outcome
```

をjoint distributionとして返す。

dropが後続pickupやshopをcutする場合、route policyは観測後にbranchできる。

### 2.10 Seeds / nuts / permanent resources

種・木の実はpickup時間だけでなく永久stat stateを変更する。
さらに使用者、使用時期、random gainがある場合にはそれもdecision/stochastic transitionになる。

最適化対象は `take/skip` だけでなく、

- take now / take later
- use now / hold
- recipient
- use timing relative to vocation/stat calculation

を含む。

### 2.11 Small medals and cumulative unlocks

小さなメダルはinventory itemというより累積counterである。
景品thresholdが複数存在するため、序盤の1枚の価値は「その場の価値」ではなく、将来必要な別pickupを1枚減らせるoption valueとして表現する。

### 2.12 Inventory layout / human execution

既存RTA chartには、誰に何を持たせるか、袋へ移すタイミング、装備変更を戦闘前に行うか戦闘中に行うかが明示されている。
これは単なる整理ではなくcommand timeとexecution complexityへ影響する。

Competition modelでは

- party order
- personal inventory order
- bag location
- equipped slot
- current tactics
- cursor/menu state if materially relevant
- number/complexity of conditional branches

も必要に応じてstateへ残す。

## 3. Parameter classes

各parameterを以下の4種に分類する。

### A. Static exact data

攻略/解析資料またはROM tableから固定値として取得可能。

例:
- monster stats
- action slots / rotations
- resistances
- drop rates
- equipment effects
- item prices/sale values
- EXP thresholds
- vocation requirements and stat multipliers
- medal thresholds
- encounter-table definitions

→ samplingせずDB化する。

### B. Derived exact distribution

static table + known algorithmから確率分布を計算できる。

例:
- encounter formation distribution
- flee probability by attempt count
- action-order probability for fixed agility values
- drop probability
- proficiency eligibility

→ exact enumeration / symbolic or discrete calculationを優先する。

### C. Emulator-measured timing

ゲームルールは分かるがRTA時間として資料にない。

例:
- chest detour frames
- menu command frames
- battle animation/message frames
- flee failure/success frame cost
- equipment transfer/equip cost
- map transition/dialogue time

→ deterministic replayまたは大量samplingで測定する。

### D. Human execution model

ゲーム内部だけでは決まらない。

例:
- reaction delay
- menu execution variance
- branch recognition error
- difficult timing success rate
- policy complexity cost

→ runner trial / configurable human modelとして別レイヤに置く。

## 4. Solver mapping

| Subproblem | Primary method |
| --- | --- |
| deterministic movement + event ordering | shortest path / DP / A* |
| encounter process along a path | exact counter-state DP / belief-state DP |
| encounter formation | exact discrete enumeration |
| small boss battle | exact MDP / policy enumeration |
| large boss battle | state aggregation + DP / Monte Carlo cross-check |
| item pickup / shop / sale / equipment | resource-constrained shortest path / SSP |
| vocation schedule | DP over proficiency counters and unlock graph |
| cumulative medals | threshold DP / resource state |
| drops and observed outcomes | scenario tree with non-anticipativity |
| whole route | hierarchical SMDP / stochastic shortest path |
| repeated WR attempts | renewal / repeated-attempt objective |
| human chart compilation | observation-constrained policy compression |

## 5. Important modeling consequences

### Encounter counter should be a latent state

runnerが内部counterを直接知らないならCompetition policyはその値で分岐できない。
しかしpath choiceによってcounter distributionが変わるため、optimizerはbelief/distributionとして保持する必要がある。

### Battle outcome and route resources are coupled

敵編成によってEXP、gold、drop、damage、MP consumption、戦闘時間が同時に変わる。
これらを独立期待値に分解しすぎると相関を失う。
可能な範囲でjoint terminal-state distributionを返す。

### Skills have negative option value as well

新しい特技はaction setを増やすだけとは限らない。AIが特定技を選ぶことでA連打戦闘が遅くなる等、既存RTA chartで実際に考慮されている。
従って「learned skill set」も必要ならstateであり、習得は常に単調改善ではない。

### More resources do not always dominate

item数、skill数、装備変更候補数が増えるとmenu timeやAI選択が悪化する場合がある。
resource dominanceはゲーム機構上単調性が証明/確認できる次元だけに適用する。

## 6. Data ingestion priority

1. encounter tables + encounter counter algorithm
2. monster database + formation generator
3. battle formulas + resistances + action patterns
4. level/EXP/growth tables
5. vocation/proficiency/stat multipliers/skills
6. item/equipment/shop/drop database
7. fixed pickups + route/event graph
8. RTA chart-specific inventory placement / human branch policy
9. emulator timing measurements
10. human execution measurements

この順に進めると、emulatorが無くても確率モデルの大部分を先に構築できる。

## 7. Sources used for this design pass

- https://gcgx.games/dq6/analyze.html
- https://gcgx.games/dq6/encounter.html
- https://showa-yojyo.github.io/dqbook/dq6_encounter.html
- http://hotarubita.blog.fc2.com/blog-entry-16.html
- https://dqwiz.net/dq6/monster.html
- https://dqwiz.net/dq6/job.html
- https://dq6.pidlio.com/dq6sfc/drop.html
- https://dq6.pidlio.com/dq6sfc/medal.html
- https://mamemommm.com/dq6_chart_mmm
- https://github.com/Maru0137/DQRTA-chart/blob/master/SFCDQ6RTA_stone_cut_chart.txt

公開攻略情報には誤記・版違いがあり得るため、SFC版であることを確認し、重要値は複数sourceまたはROM/emulatorでcross-checkする。
