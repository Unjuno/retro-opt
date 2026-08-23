# Hardware

`hardware/` では、実カートリッジ・実機から再現可能にデータを取得するための回路、adapter、計測手順を管理する。

## 設計原則

1. **高価な FPGA / PC / measurement equipment を生の cartridge bus に直結しない。**
2. **5 V / 3.3 V 等の電圧ドメインを回路図上で明示する。**
3. **電源投入前に GND / VCC / orientation / continuity を確認する。**
4. **初回通電は bench power supply の current limit を用いる。**
5. **未知回路は multimeter / oscilloscope で確認してから FPGA へ接続する。**
6. **壊れても交換しやすい protection / buffer layer を FPGA の前段に置く。**
7. **adapter と reader core を分離する。**

## 想定構成

```text
Cartridge
   ↓
Console Adapter
   ↓
Protection / Level Translation
   ↓
Universal Reader Interface
   ↓
MCU / FPGA
   ↓
Host PC
```

## 初期サブプロジェクト

```text
hardware/
├── cartridge-reader/        汎用 reader architecture
├── protection/              保護・level conversion
├── adapters/
│   ├── super-famicom/       SFC 62-pin adapter
│   └── famicom/             FC 60-pin adapter
└── logic-analyzer/          FPGA logic analyzer frontend 等
```

各 directory は実装開始時に以下を揃える。

- README
- schematic
- pinout
- BOM
- assembly / salvage procedure
- validation procedure
- measured results
- known failures / caveats

## 基準器と自作対象

原則として次の切り分けを採用する。

**既製品を基準器として使う:**

- oscilloscope
- multimeter
- bench power supply
- FPGA development board

**自作する:**

- cartridge adapter
- ROM / SRAM reader
- protection / level translation board
- FPGA bus tracer / logic analyzer
- host acquisition software

測定器そのものを無制限に自作するのではなく、自作回路を検証できる独立した基準器を残す。

## ROM dump validation

最初の reader validation では、同じ cartridge から少なくとも3回独立に dump し、byte-for-byte 比較と SHA-256 を用いて一致を確認する。

一致しない場合は ROM を解析へ使用せず、接触、電源、timing、mapping、level translation、reader firmware の問題を先に切り分ける。
