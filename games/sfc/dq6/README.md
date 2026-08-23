# SFC Dragon Quest VI

`games/sfc/dq6/` は、`retro-opt` の最初の Game Adapter / optimization benchmark である。

対象は日本版スーパーファミコン『ドラゴンクエストVI 幻の大地』の Normal Ending RTA を基本とする。

## 目的

既存 RTA チャートを固定解として実装するのではなく、ゲーム状態・合法行動・状態遷移を記述し、機械探索から既知の有力 policy を再発見できることを最初の validation とする。

その後、人間がまだ明示的に利用していない非支配 policy や長距離依存の改善候補を探索する。

## 状態モデル候補

- location / map / coordinates
- story flags
- party composition
- HP / MP
- EXP / level
- job / proficiency
- stats
- equipment
- inventory / bag
- gold
- encounter state
- enemy / boss state
- observed battle history
- human-observable state
- hidden emulator state（model validation 用。competition policy の入力にはしない）

## 行動候補

- movement
- talk / inspect
- menu operation
- item / equipment
- buy / sell
- class change
- fight / escape
- battle command
- recovery
- route choice

## Competition policy

competition 用 policy は、人間が観測できない RNG state や hidden RAM value に依存してはならない。

内部評価では完全 emulator state を使ってよいが、最終的な action selection は human-observable state から決定可能であることを条件とする。

## 最初の benchmark

最初の本格的な探索区間は、夢見の洞窟周辺からアモール北の洞窟・ホラービースト周辺を候補とする。

ここでは次の非局所効果を扱える。

- Metal Slime encounter
- 通常 encounter の狩る / 逃げる
- EXP の前倒し
- level threshold
- 後続 battle performance
- 移動時間と encounter exposure の trade-off
- 現在 EXP に応じた conditional policy

「メタルは価値がある」「ホラービースト前にこのレベルへ上げる」といった既存知識を reward として与えるのではなく、所要時間と状態遷移から再発見できるかを検証する。

## ルール・異常挙動

探索結果は以下へ分離する。

- Competition
- Quarantine
- Unrestricted

未知 glitch、emulator-specific behavior、hidden-state dependent action 等は自動的に Competition へ採用しない。

## 今後のファイル候補

```text
memory/
  ram-map.yaml
  flags.yaml
mechanics/
maps/
battle/
rulesets/
  normal-ending.yaml
experiments/
```
