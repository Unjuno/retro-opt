# SFC DQ6 emulator readout design

## 1. 目的

SFC版DQ6の最適化では、公開されているゲーム仕様を可能な限り解析的・静的に扱い、emulator readoutは次の用途へ限定する。

1. 公開RAM表と実ゲーム状態のcross-check
2. 公開資料に無い状態遷移・タイミングの測定
3. event dependency / map gate / encounter / battle modelの反証
4. 同一savestate + 同一入力によるdeterministic replay検証
5. local solverが返す分布を実エミュレーションで検証

readoutしたhidden stateを、そのままCompetition向け人間policyの入力にしてはならない。hidden RAMはモデル構築・検証用であり、最終policyはhuman-observable stateへdistillする。

## 2. 推奨構成

### BizHawk: automation/execution harness

第一候補。現在のBizHawkはSNESを含む複数systemを扱い、Lua/C#制御、memory tools、savestate、frame stepping、input recordingを持つ。

今回の用途では、Luaから明示的なmemory domainを指定してRAMを読む。BizHawk 2.11系では `memory.read_bytes_as_binary_string` 等も利用できる。

自動化を進めるときは、同一hostならmemory-mapped file IPC (`--mmf`, Lua `comm.mmf*`) とsocket IPC (`--socket-ip`, `--socket-port`, Lua `comm.socket*`) を比較する。

### MesenCE: reverse-engineering microscope

未知のflagや書込元を追う用途ではMesenCEを併用する。Mesen系Lua APIにはmemory read/write、memory callback、event callback、access counterなどがあり、特定WRAM addressを書き換える処理を追跡しやすい。

方針は「BizHawkで大量自動実験、MesenCEで未知部分の原因追跡」。重要候補は後にcross-coreで再現確認する。

## 3. SNES CPU address と WRAM domain offset

SNESのdirect WRAMはCPU address `$7E0000-$7FFFFF` に割り当てられる。emulatorが128 KiB WRAMをzero-based domainとして公開する場合、offsetは単純に `$7E0000` を引く。

例:

```text
CPU $7E3D2A -> WRAM offset $03D2A
CPU $7F0000 -> WRAM offset $10000
CPU $7FFFFF -> WRAM offset $1FFFF
```

`retro_opt.emulator.snes.snes_wram_offset()` でこの変換を一元化する。

low-bank mirror等はこのhelperでは扱わず、direct WRAM mappingだけを受け付ける。

## 4. 最初に読むべきDQ6 RAM

公開RAM解析をそのまま全部streamするのではなく、目的別のregistryに分ける。

### Tier A: story / event

- `$7E3D2A-$7E3DFF`: 恒久イベントフラグ
- `$7E3E08`: 試練の塔ミス回数
- `$7E3D29`: ベストドレッサー関連rank
- 必要に応じてtemporary/map-scoped flags

既存の `retro_opt.games.dq6.ram_progression` がCPU-style addressからsemantic gateをdecodeできるため、BizHawk bridgeはCPU address -> WRAM offsetの変換後にbyteを渡せばよい。

### Tier B: map / encounter

公開RAM mapで確認されている主要値:

- `$7E3B8F`: 0を切るとrandom encounterになる値（まずraw byteとして観測）
- `$7E5EC3-$7E5EC4`: encounter番号
- `$7E5ED7-$7E5ED8`: 地域データ2
- `$7E5ED9-$7E5EDA`: map No.
- `$7E5EED-$7E5EF0`: 直前座標

encounter counterのbit width / signedness / decrement ruleは、公開解析と実run traceを突き合わせてからsemantic decoderへ固定する。

### Tier C: persistent party / resources

- `$7E3EA2-$7E3EA4`: gold（公開解析では一部byteにXOR encodingあり）
- `$7E3EAA`: small medal count
- `$7E3F0B-$7E400A`: bag item counts
- `$7E400D-$7E4024`: join order character IDs
- `$7E4025-$7E4414`: persistent character data
- `$7E4415-$7E45DC`: proficiency
- `$7E45DD-$7E47BC`: learned data

ここはpacked bitfield / XOR encodingを含むため、raw dumpとsemantic decoderを分離する。

### Tier D: battle

- `$7E2000-$7E2007`: group enemy IDs
- `$7E2008-$7E200F`: group counts
- `$7E2011`: preemptive / surprise / no-escape / boss flags等
- `$7E2030-$7E250F`: 24 combatants x 0x52-byte battle records
- `$7E2514`: battle-end stateとescape-attempt countを含むpacked byte
- `$7E2529-$7E2540`: action order
- `$7E2541`: turn
- `$7E254D-$7E2554`: earned EXP / gold
- `$7E255F`: action/technique ID
- `$7E2563`: damage
- `$7E2565`: consumed MP
- `$7E265F-$7E268E`: randomized per-turn speed

戦闘ML/DP用traceでは、full RAMではなくこのblockとpersistent battle-entry stateを中心に保存する。

## 5. Probe strategy

`tools/bizhawk/dq6_probe.lua` はread-onlyの最小probeである。

- memory domain名 `WRAM` を明示する
- domainが存在しなければ即停止する
- map / encounter / battle controlをframe単位で読む
- 値が変化したframeだけconsoleへ出力する
- permanent event blockはhashが変わった時だけ全214 byteをhexで出力する
- packed fieldは最初から解釈し過ぎずraw値も保存する

最初から128 KiB WRAM全量を毎frame保存しない。未知値探索が必要な局所実験だけ、対象範囲を広げる。

## 6. 外部processとの接続

段階的に進める。

### Phase 1: console probe

Lua Consoleへchange-driven TSVを出す。目的はaddress/domainのcross-checkだけ。

### Phase 2: machine-readable stream

Python hostへ次のどちらかで送る。

- socket IPC
- memory-mapped file IPC

payloadには最低限:

```text
frame
core/version
rom hash
savestate/experiment id
map/encounter state
selected RAM registry values
input applied that frame
```

を含める。

### Phase 3: deterministic experiment harness

Issue #7 の要件へ接続する。

```text
load savestate
-> inject input
-> advance N frames
-> read registered RAM fields
-> emit TransitionOutcome / trace
-> repeat from identical start state
```

同一start state + 同一inputから一致しなければ、solver用datasetへ入れない。

## 7. Correctness / contamination rules

### Emulator-side

- domain名をruntimeで確認する
- CPU addressとdomain offsetを混同しない
- raw bytesを必ず保存可能にし、semantic decoderの誤りを後から検証できるようにする
- emulator/core/version/ROM hashをexperiment provenanceに含める
- read-only probeから開始し、write/injectionとは権限・code pathを分ける

BizHawkではcore reload中の`event.onexit`からmemory APIを呼ぶことでcrashする報告があるため、readout cleanupでRAMを読まない。

### RTA policy-side

RAMからしか分からないRNG/internal counterを最終チャートの条件にしない。

```text
hidden emulator state -> model/debug only
human-observable state -> competition policy input
```

同じ人間観測を持つhidden statesでは、Competition policyは同じactionを選ばなければならない。

## 8. BizHawk と MesenCE の使い分け

| Purpose | BizHawk | MesenCE |
| --- | --- | --- |
| frame advance / savestate experiment | primary | secondary |
| input sequence automation | primary | possible |
| known WRAM field logging | primary | possible |
| unknown flag writer tracing | possible | primary |
| memory access callbacks / debugger investigation | secondary | primary |
| large experimental dataset | primary | secondary |
| cross-core reproduction | yes | yes |

## 9. 直近の検証

最初の実験はstory flagでよい。

1. event直前savestateを作る
2. `$7E3D2A-$7E3DFF` をread
3. eventを一つだけ発生させる
4. block差分を取る
5. 公開event flag表のbitと一致するか確認する
6. 同じsavestateから再実行して再現するか確認する

その後にmap transition、encounter counter、battle start/endへ広げる。

## 10. Public references

- BizHawk: https://github.com/TASEmulators/BizHawk
- BizHawk Lua API: https://tasvideos.org/Bizhawk/LuaFunctions
- BizHawk command line / IPC source: https://github.com/TASEmulators/BizHawk/blob/master/src/BizHawk.Client.Common/ArgParser.cs
- MesenCE: https://github.com/nesdev-org/MesenCE
- DQ6 RAM map: https://w.atwiki.jp/dq_binary/pages/7.html
- DQ6 event flags: https://w.atwiki.jp/dq_binary/pages/22.html

公開RAM情報はreferenceであり、Normal Ending optimizerへ確定仕様として昇格させる前にemulator traceでcross-checkする。
