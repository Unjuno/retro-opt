# Roadmap

`retro-opt` は最終的に **実機データ取得 → 解析 → 最適化 → 実機検証** を縦に通すことを目指すが、当面はハードウェアを必須依存にしない。

現在の優先方針は **Software-first** とする。ROM dumper、FPGA reader、logic analyzer、FC/SFC adapter は将来の実機取得・検証経路として残すが、ROM/実機がなくても進められる設計・solver・実験基盤を先に構築する。

## P0: Repository foundation

- [x] Public repository
- [x] README
- [x] Apache-2.0 license
- [x] ROM / save / trace を除外する `.gitignore`
- [x] 初期 architecture / roadmap
- [x] contribution policy
- [ ] issue / experiment template
- [ ] Python package / test foundation

## P1: Core contracts

ゲーム・エミュレータ・solver を疎結合にするため、以下の抽象契約を先に固定する。

- `State`: solver が扱う構造化状態
- `Observation`: 人間が観測可能な情報
- `Action`: 合法な入力または macro action
- `Transition`: 次状態、時間コスト、確率、付随情報
- `Policy`: observation から action を選ぶ規則
- `GameAdapter`: raw emulator state を game state へ変換する境界
- `Emulator`: reset / step / savestate / RAM access 等の境界

重要: hidden emulator state は解析・検証に利用してよいが、Competition policy は human-observable information のみに依存させる。

## P2: Experiment / result schema

探索結果を後から再現・比較できる形式を作る。

最低限保存するもの:

- experiment id / version
- game / platform / category / ruleset
- software commit
- ROM hash（ROM自体は保存しない）
- initial state / terminal condition
- candidate policy / configuration
- random seed / scenario set
- sample count
- mean / median / variance
- completion probability
- reset cost
- target time を切る確率
- confidence interval
- anomalies / quarantine status

## P3: Solver core on synthetic environments

DQ6やROMに依存せず、人工的な小さい確率環境でsolverの正しさを検証する。

対象:

- deterministic shortest path
- stochastic shortest path
- state-dependent policy
- scenario tree
- dominance pruning
- Pareto frontier
- non-anticipativity / observation-equivalence constraint

小規模環境では brute-force と solver 出力を比較し、最適解一致をテストする。

## P4: Route / battle macro model

フレーム入力と全ゲーム探索を直接つなげず、階層化する。

```text
frame/input
    ↓
turn / encounter
    ↓
segment / dungeon
    ↓
macro event
    ↓
global route
```

下位solverは唯一の局所最短解ではなく、時間・資源・乱数・終了状態についての非支配候補集合を上位へ返す。

## P5: Emulator harness

ROMが用意できた時点で実エミュレータへ接続する。core solver はこの milestone を待たない。

最低要件:

- reset
- deterministic input injection
- frame advance
- savestate load/save
- RAM read
- frame count
- reproducibility check

同一 state + 同一 input から同一結果になることを benchmark 化する。

## P6: DQ6 Game Adapter / knowledge base

ROMなしでも、公開資料・既存チャート・既知仕様から schema と event graph の骨格は作れる。RAM address 等の実測依存部分は後から埋める。

状態候補:

- map / coordinates
- story flags
- party
- HP / MP
- EXP / level
- job / proficiency
- stats
- inventory / equipment
- gold
- encounter / battle state
- observable history
- hidden emulator state（解析・検証用のみ）

行動候補:

- movement / talk / inspect
- item / equipment / buy / sell
- class change
- fight / flee
- battle commands
- recovery
- route branch

## P7: Human baseline / Chart Atlas

既存の人間チャートを「正解」としてhard-codeするのではなく、比較対象として構造化する。

各 route / policy family について可能な範囲で記録する:

- event sequence
- conditional branches
- EXP / proficiency targets
- item / equipment policy
- encounter policy
- boss policy
- observed time / split data
- known rationale / provenance

最終的には平均時間、分散、完走率、reset cost、target突破確率、実行難度等で人間frontierとmachine-generated frontierを比較する。

## P8: DQ6 first optimization benchmark

最初から全編は探索しない。

対象候補:

**夢見の洞窟周辺 → アモール北の洞窟 → ホラービースト周辺**

この区間では、移動・random encounter・Metal Slime・EXP・狩る/逃げる・level threshold・boss battle といった複数イベント間の価値伝播を検証できる。

成功条件:

- 人間の既存 policy を直接 reward / hard-code として与えず、既知の有力な経験値・戦闘政策を再発見できる
- 不一致の場合、model error と genuine route improvement candidate を切り分けられる

## P9: Global optimization

局所solverをmacro transitionとして統合する。

- movement solver
- battle solver
- encounter solver
- scenario tree
- dominance pruning
- Pareto frontier
- global SMDP

最終的には machine policy と human-readable RTA chart の両方を生成する。

---

# Deferred hardware track

以下は重要だが、Software-first phase の blocker にはしない。

## H1: SFC connector acquisition

ジャンクSFCから62-pin cartridge connectorを回収する。

## H2: Protection / interface board

5 V / 3.3 V境界、level translation、buffer、series resistance、電源保護、test pointを備え、高価なFPGA/MCUを外部busから守る。

## H3: MCU SFC ROM reader

ESP32または適切なPIC等でreaderを実装し、同一cartridgeを複数回dumpしてbyte-for-byte / SHA-256一致を検証する。

## H4: FPGA reader core

検証済みadapter/protection layerを流用しFPGAへ移植する。

## H5: FPGA logic analyzer / bus tracer

BRAM capture、trigger、VCD export等を実装する。オシロスコープはsignal integrity、FPGA tracerはdigital behaviorの解析に使う。

## H6: Famicom adapter

SFC側のarchitectureが安定した後、60-pin adapterを追加する。

## 方針

このプロジェクトは趣味研究であり、全milestoneの完遂を前提としない。各層は独立して価値を持ち、ハードウェア取得が止まっていてもsolver・model・experiment designを進められる構造を維持する。
