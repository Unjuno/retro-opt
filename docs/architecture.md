# Architecture

## 1. 設計目標

`retro-opt` は、特定ゲームや特定エミュレータに依存しない層と、機種・ゲーム固有層を分離する。

主な設計原則は次の通り。

1. **実機取得と最適化を疎結合にする**  
   optimizer は実機 reader がなくても、ローカルに用意された ROM と emulator adapter があれば動作できること。
2. **ゲーム固有知識を Game Adapter に閉じ込める**  
   DQ6 固有の RAM address、イベントフラグ、戦闘仕様等を core に流入させないこと。
3. **観測可能状態と内部状態を分離する**  
   hidden RNG / RAM state は解析・検証に利用できるが、人間向け competition policy は人間が観測可能な情報のみで決定できること。
4. **局所最適を固定しない**  
   移動・戦闘・経験値計画等の下位 solver は単一解ではなく、必要に応じて非支配候補集合を上位 solver に返すこと。
5. **測定可能性と再現性を優先する**  
   実験条件、ROM hash、emulator core、設定、入力系列、seed / state、結果を追跡可能にすること。
6. **高価な機器を外部バスから保護する**  
   FPGA 等へ実機 5 V bus を直接接続せず、保護・レベル変換層を必ず介すこと。

## 2. レイヤ構成

```text
[Physical cartridge / console]
          ↓
[Console adapter]
          ↓
[Protection / level translation]
          ↓
[Reader / FPGA / MCU]
          ↓
[Host acquisition tools]
          ↓
[ROM / SRAM / trace artifacts]
          ↓
[Emulator abstraction]
          ↓
[Raw emulator state]
          ↓
[Game adapter]
          ↓
[Structured state / legal actions]
          ↓
[Local solvers]
          ↓
[Macro transition models]
          ↓
[Global optimizer]
          ↓
[Human policy compiler]
```

## 3. Hardware acquisition

### Universal reader

reader 本体は可能な限り機種非依存とし、console adapter を交換して FC / SFC 等へ対応する。

想定モジュール:

- FPGA / MCU interface
- power control
- protection / level translation
- address / data bus abstraction
- capture buffer
- USB / serial / network transport

### Console adapter

機種ごとの物理コネクタ、pinout、電源条件、bus mapping を担当する。

最初の対象:

- Super Famicom 62-pin cartridge adapter
- Famicom 60-pin cartridge adapter

ジャンク本体から回収した cartridge connector の再利用手順も documentation として管理する。

## 4. Emulator abstraction

emulator ごとの差を隠蔽し、上位層に最低限以下を提供する。

```text
reset()
load_state()
save_state()
step_frame(input)
read_memory(region, address, length)
write_memory(...)
get_frame_count()
get_determinism_metadata()
```

候補として BizHawk、Snes9x 系、headless core 等を adapter として追加する。

## 5. Game Adapter

Game Adapter は raw memory / emulator event をゲーム意味論へ変換する。

例: SFC DQ6

```text
raw RAM
  ↓
party HP / MP
EXP / level
job / proficiency
inventory / equipment
gold
map / coordinates
story flags
enemy state
observable history
```

また、その状態で許される action と、competition policy が参照可能な observable state を定義する。

## 6. Optimization

### Local solver

- movement
- battle
- encounter
- shop / inventory
- resource acquisition

下位 solver は必要に応じて以下を返す。

- duration distribution
- resulting-state distribution
- resource deltas
- clear / failure probability
- non-dominated alternatives

### Global solver

全体は Stochastic Shortest Path / SMDP として扱うことを基本とする。

候補手法:

- dynamic programming
- branch-and-bound
- dominance pruning
- scenario tree
- Monte Carlo evaluation
- sequential sampling
- MCTS / approximate search（厳密探索が破綻する区間のみ）

RL は第一選択ではなく、状態・遷移を直接利用した探索で扱えない部分の補助とする。

## 7. Competition / Quarantine / Unrestricted

探索結果は最低でも次の3レーンに分離する。

- **Competition**: 現行ルールに適合し、人間が観測・実行可能
- **Quarantine**: glitch、rule ambiguity、emulator-specific behavior、未検証異常
- **Unrestricted**: TAS / glitch / hidden-state dependent 等を許す研究

高速な未知挙動を自動的に Competition へ昇格させない。

## 8. 実験の再現性

各 experiment は最低限以下を記録する。

```yaml
experiment_id: example
platform: sfc
game: dq6-jp
rom_sha256: "..."
emulator: "..."
emulator_version: "..."
config: "..."
input_source: "..."
state_source: "..."
solver_revision: "..."
```

ROM 本体、BIOS、配布権限のないデータは repository に含めない。
