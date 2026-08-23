# Methodology

## 1. 目的

`retro-opt` は、特定の既存チャートを正解として模倣するのではなく、ゲームの状態遷移・所要時間・確率分布から route / policy を評価する。

最終的な成果物は単一の最速入力列ではなく、少なくとも以下を区別する。

- machine-internal optimum
- human-observable policy
- human-executable RTA chart
- quarantineされた異常・glitch候補

## 2. State と Observation を分離する

完全なエミュレータ状態を `State`、走者が実際に利用可能な情報を `Observation` とする。

```text
full emulator state x_t
        ↓ observation model
human-observable state o_t
        ↓ policy
      action a_t
```

解析・遷移モデルの検証では RNG state、内部counter等の hidden state を利用してよい。

ただし通常RTA向け Competition policy は原則として

```text
a_t = policy(o_t)
```

でなければならず、走者が知り得ない hidden state を action selection に利用してはならない。

人間から区別不能な複数scenarioで同じactionを要求する制約を、non-anticipativity / observation-equivalence constraint として扱う。

## 3. Reward shaping を主目的にしない

探索器へ「メタルは価値が高い」「この装備を取るべき」といった人間由来の報酬を可能な限り与えない。

基本目的は時間コストと状態遷移で定義し、既存知識は以下の用途に限定する。

- legality / ruleset
- game mechanics
- state decoding
- benchmark / validation
- search spaceを安全に表現するためのaction定義

既存RTA chartは答えではなく human baseline として扱う。

## 4. 局所最適と全体最適を分離する

下位solverは「その区間だけで最速の1経路」を返さず、上位で最適になり得る非支配候補を保持する。

例:

```text
route A: 速い / EXP少 / RNG多
route B: 少し遅い / EXP多 / RNG少
route C: 遅い / resource温存
```

局所的に遅い寄り道が数イベント後の戦闘・回復・稼ぎを削除して全体では高速になる可能性を許す。

## 5. Dominance pruning

同じ将来条件へ接続できる2状態について、一方が時間・HP/MP・EXP・所持資源等の関連軸で完全に劣る場合、劣る状態を探索から除外できる。

ただし「将来価値に影響しない」と証明・検証できていない変数を無視して支配判定してはならない。

## 6. 三つのlane

### Competition

対象categoryのrulesetに適合し、人間観測可能かつ最終的に人間実行可能な候補。

### Quarantine

以下を含む候補を隔離する。

- glitch / bugの疑い
- ruleset上の扱いが不明
- emulator依存の可能性
- hidden RNG state依存
- replay不安定
- 通常速度・通常入力で再現できない

### Unrestricted

TAS、glitch、RNG固定等を許容する別研究lane。Competitionの統計へ混入させない。

## 7. 異常候補のpromotion gate

極端に速い候補は少なくとも以下を確認してからCompetitionへ昇格する。

1. ruleset legality
2. human observability
3. normal-speed replay
4. emulator core差の確認
5. 必要なら実機再現
6. 小さなinput timing perturbationへのrobustness
7. 統計的再検証

## 8. Benchmark-first

未知戦略を信用する前に、solverが既知の強い人間戦略を再発見できるかを見る。

DQ6初期benchmark候補:

- 夢見の洞窟周辺のMetal Slimeを含む経験値政策
- アモール北の洞窟からホラービーストまでの狩る/逃げる政策
- 将来的には旧メタルキング安定routeと低stat Mortamor policyの比較

既知policyと一致しない場合は、直ちに新発見と断定せず、model error / missing state / measurement error と genuine improvement candidate を切り分ける。

## 9. 評価指標

単一の平均タイムだけで評価しない。

候補ごとに可能な限り以下を保存する。

- mean completion time
- median completion time
- variance / standard deviation
- completion probability
- mean reset time
- target timeを切る確率
- sample count
- confidence interval
- human execution difficulty（定義後）

これらからPareto frontierを構成し、human baselineとmachine candidateを同じ空間上で比較する。
