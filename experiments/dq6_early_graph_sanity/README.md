# DQ6 early event graph sanity v0

## 目的

`games/sfc/dq6/model/early_event_graph.json` のmacro event graphが、探索器へ渡す前提として最低限の構造整合性を持つか確認する。

検査項目:

- node id重複なし
- start nodeが存在
- terminal nodeが存在
- actionの遷移先が存在
- terminalからactionが出ていない
- startから全nodeへ到達可能
- startからterminalへ到達可能

## 結果

- nodes: 8
- terminals: 1
- errors: 0
- PASS

この検査はgraphの**構造**だけを見る。各duration modelやtransition distributionの正しさは、公開資料・emulator実測で別途検証する。
