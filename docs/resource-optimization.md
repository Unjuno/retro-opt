# Resource-aware route optimization

## 1. 目的

DQ6 RTAのroute optimizationを、EXPや移動距離だけの問題として扱わない。

ある行動の価値は数イベント先まで伝播する。

- 宝箱を取る / 取らない
- アイテムを保持する / 使用する / 売る
- 装備する / 外す / 別キャラへ渡す
- 金策する / しない
- 店で買う / 買わない
- 種・木の実を誰に使うか
- 通常敵を狩る / 逃げる
- 宿・回復・蘇生を使う
- メダル等の累積資源を回収する

局所的には遅い行動でも、後続の買物・戦闘・回復・稼ぎ・menu操作を削除できれば全体では速くなり得る。

## 2. Stateに保持すべき資源

最低限、以下を将来価値を持つstateとして扱う。

### Party / combat

- HP / MP / alive / status
- EXP / level
- stats
- vocation / proficiency
- equipment

### Item

- 袋の所持品
- 各キャラの手持ち
- 装備中アイテム
- 消費済み / 売却済み / 未回収
- 必要ならitem slot / order（menu timeへ影響するため）

### Economy

- gold
- 売却可能資産
- shop availability
- purchase price / sale price
- 将来必要な最低gold

「売却可能資産」はgoldと同一視しない。売却するには店へ行く必要があり、売却時間がかかり、装備・戦闘資源を失う場合がある。

### Progress / route

- story flags
- key item / route unlock
- location
- 回収済みchest / event
- medal等の累積unlock資源
- remaining route / available future events

### Information / execution

- human-observable history
- item位置やmenu順序など、人間のcommand timeへ影響する情報

## 3. Action

macro actionは少なくとも以下を許す。

- move / route branch
- pickup / skip pickup
- use / transfer / equip / unequip
- buy / sell
- fight / flee / farm
- rest / heal / revive
- class change
- talk / inspect / event progress

各actionは以下を持つ。

- precondition
- duration distribution
- transition distribution
- deterministic resource effects
- stochastic effects
- legality / observability / executability metadata

## 4. 必須条件をrewardで表現しない

「このitemがないと先へ進めない」「gold不足で買えない」「死者がいるとeventを進められない」等は、恣意的な大きな罰点を与えない。

原則としてaction feasibilityで表現する。

例:

```text
buy(item)
  requires: gold >= price(item)

open_gate
  requires: owns(required_key)

boss_clear_policy_X
  requires: policy Xの実行に必要なitem/resourceを保持
```

物理的には挑戦できるが勝率が非常に低い場合は、actionを禁止せずtransition probabilityとして表現する。

## 5. Goldとitemの相互変換

itemは複数の価値を持つ。

```text
item
├─ combat value
├─ healing / consumable value
├─ route unlock value
├─ resale value
└─ menu / inventory placement cost
```

従って、単純な`item -> gold換算値`へ早期に圧縮してはいけない。

例として、ある盾は

- 装備してboss突破率を上げる
- 売って別装備の購入資金にする
- 持っていることで別の売却候補を温存する

という複数の未来を持つ。

## 6. Dominance pruning上の注意

同じlocationでも、所持資源が違えば将来価値が異なる。

`time`だけで枝刈りしてはいけない。

例えばAがBより10秒遅くても、Aだけが

- 50G多い
- 回復itemを保持
- boss向け装備を保持
- level thresholdに近い

なら支配関係は未確定である。

安全なdominance判定に使うstate projectionは、将来価値へ影響しないことを確認した変数だけを落とす。

## 7. 現在のsynthetic benchmark

`experiments/resource_dependency_toy/` では、optional shield pickup、gold pickup、sell/buy、boss retry riskを同一state spaceへ入れている。

局所的にはpickupをskipする方が速いが、資源の補完関係により複数の寄り道を取るpolicyが全体最適になるケースをregression testとして固定する。

この数値はDQ6実測値ではない。実ゲームで必要な状態次元とsolver挙動を先に検証するためのfixtureである。
