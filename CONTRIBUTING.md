# Contributing

`retro-opt` への Issue、調査結果、回路、コード、実験結果の共有を歓迎します。

## 言語

- README、docs、Issue、実験記録は原則として日本語
- code identifier、API、protocol name は原則として英語
- 英語による Issue / PR も拒否しない

## 著作物・ROM

以下を commit / upload しないでください。

- ゲーム ROM
- BIOS
- 配布権限のない game asset
- ROM 由来の大量 binary dump
- 個人が適法性を確認できない取得物

再現性が必要な場合は、file size、revision、SHA-256 等の識別情報を記録してください。

## 実験結果

可能な限り以下を添えてください。

- hypothesis /目的
- hardware / emulator / software version
- ROM hash
- config
- input / initial state
- measurement method
- raw result の保存場所または生成方法
- PASS / FAIL / UNCERTAIN の判定基準
- known uncertainty

## Hardware

回路変更を共有する場合、可能な範囲で次を記録してください。

- voltage domain
- pinout
- current limit / power condition
- protection / level translation
- schematic / BOM
- measurement result
- 接続対象を破損する可能性がある既知の注意点

高価な FPGA、PC、console 等へ未検証の外部 bus を直接接続する設計は避けてください。

## Optimization

既知の RTA policy を benchmark として利用することと、それを solver の reward / hard-coded answer として与えることは区別します。

新規 policy を Competition 候補とする場合は、少なくとも legality、human observability、replay reproducibility を確認してください。未知 glitch や emulator-specific behavior は Quarantine として扱います。
