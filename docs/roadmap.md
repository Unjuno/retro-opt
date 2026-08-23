# Roadmap

このロードマップは、`retro-opt` を **実機データ取得 → 解析 → 最適化 → 実機検証** まで縦に通すための初期計画である。

## M0: Repository foundation

- [x] Public repository
- [x] README
- [x] Apache-2.0 license
- [x] ROM / save / trace を除外する `.gitignore`
- [x] 初期 architecture / roadmap
- [ ] contribution policy
- [ ] issue / experiment template

## M1: SFC connector acquisition

目的: ジャンク SFC から cartridge connector を安全に回収し、adapter の物理入口を作る。

完了条件:

- connector の取り外し工程を写真・文章で記録
- pin 1 / orientation を特定
- GND / VCC を確認
- 全 pin の導通確認
- connector revision / donor board 情報を記録

## M2: Protection / interface board v0

目的: 高価な FPGA / MCU を cartridge bus から保護する中間層を作る。

最低要件:

- 5 V / 3.3 V 境界の明示
- level translation / buffer
- series resistance
- current limiting を考慮した電源構成
- test point
- FPGA へ生の 5 V signal を入力しない

最初は bench power supply、multimeter、oscilloscope を基準器として用いる。

## M3: MCU SFC ROM reader

目的: FPGA を実カートリッジへ投入する前に、安価な MCU で電気系・mapping を検証する。

候補:

- ESP32
- 5 V 対応 PIC

完了条件:

1. 同じ SFC cartridge を独立に3回 dump
2. 3 dump が byte-for-byte 一致
3. SHA-256 が一致
4. emulator で正常起動
5. dump 手順と測定条件を記録

速度は M3 の評価対象としない。

## M4: FPGA reader core

M3 で検証済みの adapter / protection board を流用し、FPGA へ移植する。

実装候補:

- address generator
- data sampler
- read/write controller
- BRAM capture buffer
- trigger
- host transport

完了条件: MCU dump と FPGA dump が完全一致すること。

## M5: FPGA logic analyzer / bus tracer

自作 logic analyzer を FPGA 上に実装する。

初期目標:

- 32ch 程度
- 50–100 MS/s を目安（実 FPGA 仕様に合わせて決定）
- pre-trigger / post-trigger
- edge / pattern trigger
- VCD export

オシロスコープは signal integrity / voltage / timing、FPGA tracer は digital behavior の解析に使い分ける。

## M6: Famicom adapter

SFC で reader architecture が安定した後、ジャンク FC から 60-pin connector を回収して adapter を追加する。

目標: reader core を変更せず console adapter と protocol layer の差し替えで対応する。

## M7: Host ROM tools

CLI の初期案:

```text
retro-opt rom dump --platform sfc
retro-opt rom inspect <file>
retro-opt rom hash <file>
retro-opt rom compare <a> <b>
retro-opt trace capture
retro-opt trace decode
retro-opt trace export-vcd
```

ROM 自体は repository に置かない。

## M8: Emulator harness

最低要件:

- deterministic input injection
- frame advance
- savestate load/save
- RAM read
- frame count
- reproducibility check

同一 state + 同一 input から同一結果になることを benchmark 化する。

## M9: DQ6 Game Adapter

最初の実証対象として SFC DQ6 を構造化する。

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

## M10: DQ6 first optimization benchmark

最初から全編は探索しない。

対象候補:

**夢見の洞窟周辺 → アモール北の洞窟 → ホラービースト周辺**

この区間では、移動・random encounter・Metal Slime・EXP・狩る/逃げる・level threshold・boss battle といった複数イベント間の価値伝播を検証できる。

成功条件:

- 人間の既存 policy を直接 hard-code せず、既知の有力な経験値・戦闘政策を再発見できる
- 不一致の場合、model error と genuine route improvement candidate を切り分けられる

## M11: Global optimization

局所 solver を macro transition として統合する。

- movement solver
- battle solver
- encounter solver
- scenario tree
- dominance pruning
- Pareto frontier
- global SMDP

最終的には machine policy と human-readable RTA chart の両方を生成する。

## 方針

このプロジェクトは趣味研究であり、全 milestone の完遂を前提としない。各 milestone 単体でも、回路・RTL・測定結果・失敗記録・再現手順が独立した成果になるように設計する。
