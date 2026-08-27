# DQ6 RAM event flags

## 1. 現状

SFC版DQ6については、恒久イベントフラグ領域 `$7E3D2A-$7E3DFF` と多数の名前付きbitが公開解析されている。

そのため `retro-opt` では、story modelを次の3層で扱う。

```text
semantic gate
  ↕
external chart_event_id (1..225)
  ↕
RAM address + bit mask
```

`chart_event_id` と RAM bit は同一番号だと仮定しない。

公開解析から対応が明確なprogression-relevant bitは
`games/sfc/dq6/data/ram_progression_flags_reference.json` に収録する。

## 2. 例

| Semantic state | RAM reference |
| --- | --- |
| 夢見のしずく入手 | `7E3D35 & 0x20` |
| 鏡の鍵入手 | `7E3D35 & 0x40` |
| ラーの鏡入手 | `7E3D35 & 0x80` |
| 王の書状入手 | `7E3D36 & 0x01` |
| 黄金のつるはし入手 | `7E3D36 & 0x04` |
| 勇気のかけら入手 | `7E3D36 & 0x08` |
| 水門の鍵入手 | `7E3D36 & 0x10` |
| マーメイドハープ入手 | `7E3D36 & 0x20` |
| 砂の器入手 | `7E3D36 & 0x40` |
| 錆びた剣入手 | `7E3D36 & 0x80` |
| スフィーダの盾 | `7E3D37 & 0x01` |
| セバスの兜 | `7E3D37 & 0x02` |
| オルゴーの鎧 | `7E3D37 & 0x04` |
| 牢獄の鍵 | `7E3D37 & 0x08` |
| 主人公融合 | `7E3D39 & 0x08` |
| グラコスイベント完了 | `7E3D38 & 0x04` |
| 本気ムドー撃破 | `7E3D60 & 0x01` |
| 魔法の鍵取得 | `7E3D6C & 0x10` |
| 狭間へ行けるペガサス | `7E3D71 & 0x20` |
| デスタムーア撃破 | `7E3D6C & 0x40` |

## 3. bitではない進行state

すべてを恒久event bitへ押し込めない。

公開RAM解析では、例えば以下が別領域に存在する。

- `$7E3D29`: ベストドレッサーコンテストのランク
- `$7E3E08`: 試練の塔でミスした回数
- `$7E3E0C`: 魔王の使いに負けた回数
- `$7E3E18-$7E3E27`: map変更で消えるtemporary flags
- `$7E3E28-$7E3E3F`: 地域データ変更で消えるtemporary flags

したがってabstract stateでも

- permanent flags
- counters
- stage enums
- temporary flags
- key items/equipment

を分離する。

## 4. Validation policy

公開RAM表は非常に有用だが、Competition modelに採用する重要flagは最終的にemulatorでcross-checkする。

最低限、対象イベント直前/直後のsavestateを比較して、

1. 対応bitが期待通り変化する
2. 他の候補bitと混同していない
3. reload後も恒久状態として残る
4. そのbitを満たさない状態では実際にgateを通れない

を確認する。

この検証は「RAMを見て行動を変える」ためではない。RAMはモデル検証に使い、Competition policyは人間から観測可能な状態だけで分岐する。

## 5. Sources

- https://w.atwiki.jp/dq_binary/pages/22.html
- https://w.atwiki.jp/dq_binary/pages/7.html
- https://showa-yojyo.github.io/dqbook/dq6_search.html
