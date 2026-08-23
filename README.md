# retro-opt

レトロゲームを対象に、**実機データ取得からエミュレーション、状態解析、探索・最適化、実機検証まで**を再現可能にするためのオープンな研究基盤です。

最初の実証対象として、スーパーファミコン版『ドラゴンクエストVI 幻の大地』の Normal Ending RTA を扱います。

## 現在の開発方針: Software-first

ハードウェア取得系は重要な構成要素ですが、現在は blocker にしません。ROM dumper、FPGA reader、logic analyzer、FC/SFC cartridge adapter は将来の実機取得・検証経路として設計を残しつつ、当面は ROM がなくても進められる以下を優先します。

- ゲーム非依存の State / Observation / Action / Transition interface
- human-observable policy の制約
- stochastic shortest path / Pareto / dominance pruning 等の solver core
- 再現可能な experiment / result schema
- 既存 DQ6 RTA chart の human baseline / Chart Atlas 化
- emulator harness の抽象 interface
- DQ6 Game Adapter の schema / event graph

詳細は [`docs/roadmap.md`](docs/roadmap.md) と [`docs/methodology.md`](docs/methodology.md) を参照してください。

## 目的

`retro-opt` は、既存チャートを少し改善するためだけの専用ツールではありません。実カートリッジからの ROM / SRAM 取得、バス解析、エミュレータ状態の観測、RNG を含む状態遷移の計測、入力系列・戦闘方策・イベント間経路の探索を、一つの再現可能な実験系として接続することを目的とします。

特に次を目標とします。

- 実カートリッジから ROM / SRAM を再現性をもって取得する
- FC / SFC など複数機種へ拡張できる汎用カートリッジリーダーを構築する
- FPGA / MCU を用いてバス制御・トレース・簡易ロジックアナライザを実装する
- エミュレータから RAM・savestate・入力・frame を機械的に扱う
- ゲーム固有状態を Game Adapter として分離する
- RNG を含む確率的挙動を計測し、状態遷移モデルを構築する
- 戦闘、移動、寄り道、経験値計画などを局所最適ではなく全体最適として探索する
- 機械が得た方策を、人間が観測・実行可能な RTA チャートへ変換する
- 既存の人間チャートがどの程度 Pareto frontier に近いかを測定する
- DQ6 で得た手法を他タイトルへ再利用できる形に一般化する

## 基本アーキテクチャ

```text
Cartridge / Console
        ↓
Hardware acquisition
        ↓
ROM / SRAM / bus trace
        ↓
Emulator abstraction
        ↓
RAM / savestate / input / frame
        ↓
Game adapter
        ↓
Structured game state
        ↓
Optimization core
        ↓
Search / DP / scenario tree / Monte Carlo / Pareto
        ↓
Human policy compiler
        ↓
RTA chart / experimental result
```

詳細は [`docs/architecture.md`](docs/architecture.md) を参照してください。

## 最初の対象

- Platform: Super Famicom
- Game: ドラゴンクエストVI 幻の大地
- Category: Normal Ending RTA
- 最初のハードウェア目標: 自作 reader で同一 SFC ROM を独立に複数回 dump し、byte-for-byte および SHA-256 が一致すること
- 最初の最適化 benchmark: 夢見の洞窟周辺からアモール北の洞窟・ホラービースト周辺にかけての、移動・エンカウント・メタル・経験値・戦闘をまたぐ政策探索

## リポジトリ構成

```text
docs/                設計、ロードマップ、用語、実験方針
hardware/            reader、保護回路、各機種アダプタ、計測系
firmware/            MCU firmware
fpga/                 FPGA RTL、constraints、capture logic
host/                 PC 側 CLI / library
rom/                  dump、識別、hash、検証手順
emulator/             emulator abstraction / adapters
analysis/             RAM、RNG、trace、state diff
optimizer/            探索、DP、scenario tree、Pareto 等
games/                ゲーム固有 adapter / model
experiments/          再現可能な実験設定
results/              公開可能な集計結果
```

## 言語方針

本プロジェクトは日本版レトロゲームおよび日本の RTA コミュニティを主要な対象とするため、**README、docs、Issue、実験記録などは原則として日本語**で記述します。

一方、ソースコード上の識別子、API、ファイル形式、プロトコル名などは、可搬性と他プロジェクトとの互換性を考慮して英語を基本とします。

## ROM・著作物について

このリポジトリには、ゲーム ROM、BIOS、ゲームから抽出した著作物、配布権限のないデータを含めません。

ROM イメージが必要な実験では、利用者自身が適法に用意したローカルファイルを使用します。ROM 本体は Git 管理せず、再現性のため必要に応じてファイルサイズ、revision 情報、SHA-256 などの識別情報のみを実験 manifest に記録します。

Nintendo、Square Enix その他の権利者とは関係のない非公式の研究プロジェクトです。

## 安全方針

実機・カートリッジ・FPGA 等を扱う回路では、外部バスを高価なデバイスへ直接接続しないことを原則とします。レベル変換、バッファ、電流制限、保護回路を用い、電源・信号条件を計測してから段階的に接続します。

詳細な安全方針は [`hardware/README.md`](hardware/README.md) にまとめます。

## License

本リポジトリ内のソフトウェアは、特記のない限り **Apache License 2.0** の下で公開します。詳細は [`LICENSE`](LICENSE) を参照してください。

このライセンスは、本リポジトリに含まれる独自のソースコード等にのみ適用されます。ゲーム ROM、ゲームデータ、商標、その他第三者が権利を有する著作物に対する権利を付与するものではありません。

ハードウェア設計データのライセンスは、PCB・回路図等を本格公開する段階で別途明示します。
