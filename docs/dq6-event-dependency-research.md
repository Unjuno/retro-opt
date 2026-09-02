# DQ6イベント依存関係の調査と最適化用モデル

## 1. 目的

SFC版DQ6 Normal Ending RTAを最適化問題として扱うため、通常の攻略チャートの順番をそのまま探索器へ入れるのではなく、**ゲーム内部で実際に必要な依存関係だけ**を抽出する。

最適化器が必要とするのは「一般的な攻略順」ではなく次の区別である。

- hard event dependency: 先行イベントなしでは後続イベントが発生しない
- reachability dependency: map edge / vehicle / door / world stateがないと場所へ行けない
- item/resource dependency: key item, gold, equipment等が必要
- capability dependency: 呪文、特技、party member、能力条件等が必要
- unordered set / counter dependency: 複数対象を全部処理すればよく順番自体は自由
- knowledge-only dependency: ヒントを聞かなくても答え・場所を知っていれば省略可能
- uncertain hidden dependency: 公開資料間で食い違いがありRAM/emulator検証が必要

## 2. 基準資料

### フラグチャート

hori3948のSFC版フラグチャートはイベント1〜225について「そのイベントを発生させるために必要な先行番号」を持つため、dependency graphの一次基準として使用する。

- http://hori3948.g2.xrea.com/dq6/dq6-event1.html
- http://hori3948.g2.xrea.com/dq6/dq6-event2.html
- http://hori3948.g2.xrea.com/dq6/dq6-event3.html

ただし、この表をそのまま「最小hard dependency DAG」とはみなさない。次の理由がある。

1. item / command / equipmentのような非イベント条件が別途存在する
2. 攻略情報を知っていれば飛ばせる情報イベントがある
3. 複数NPC会話など、本来setとして扱うべきものが1イベント行に圧縮されている
4. world stateや到達可能性が暗黙条件になっている場合がある
5. 公開資料間に矛盾する箇所がある

そのため原表はprovenanceとして保持し、`story_dependency_evidence.json`で最適化用の意味付けを追加する。

## 3. 検証できた重要な依存関係

### 3.1 知識で飛ばせないhard gate

#### 川の抜け道

木こりイベントを完了して「川の抜け道を発見可能」にする必要がある。入口位置をプレイヤーが知っていても先行イベントなしでは入れない。

したがってこれはknowledgeではなくhard event dependencyとして固定してよい。

#### 氷の洞窟

入口の答えを暗記しているだけでは不十分で、ザム神官のイベント後でなければ封印扉を突破できないというSFC攻略資料がある。

したがって chart event 148 -> 149 はhard dependencyとして扱う。

### 3.2 knowledge-onlyで削除できるもの

#### グレイス城の過去イベント

通常攻略では過去の儀式を見てオルゴーの鎧の隠し場所を知るが、場所を既知なら過去イベントを見ずに現在のグレイス城で黄金のつるはしを使い、直接オルゴーの鎧へ到達できる。

したがって過去儀式はNormal Endingのhard progression graphへ追加しない。

#### 不思議な洞窟のヒントNPC

各地のNPCがパズルの解法を教えるが、既知解を入力・歩行できるrunnerならヒント回収は不要。チャートイベント178にもヒントイベントは先行条件として現れない。

#### 秘密の湖の場所情報

欲望の町の炭鉱・モルガンへの5000G支払いは場所を知るための情報取得であり、場所を知っていれば省略可能。

この種の情報行動はCompetition runnerの知識を許すNormal RTAではhard dependencyにしない。

## 4. 「一本道」ではなくset/counterとして扱うイベント

イベント系の計算量を減らす上で重要なのは、複数処理を無意味に順列化しないことである。

### アモールの4会話

chart event 52は4人のNPCへの会話を全部要求するが、順不同。

optimizerでは4!個のstory sequenceを作るのではなく、

```text
required_npc_talks: bitset[4]
```

として扱う。実際の会話順はmap/path solverが決める。

### カルカドの5会話

chart event 95も5人への会話が順不同。夜になる条件はset completionとして扱う。

### 月鏡の塔の4つの玉

4個を全部破壊することが必要。story側は `moon_mirror_orbs_destroyed=4` を条件とし、どの順に壊すかはmap solverへ渡す。

### ライフコッドの9敵グループ

9グループ全撃破をcounter/set gateとする。撃破順は移動距離、戦闘終了位置、HP/MP状態との局所最適化対象。

### レイドックの6記憶ポイント

6地点を処理すると最後の玉座ポイントが出現する。これもset completionであり固定sequenceにしない。

## 5. 大きな並行区間

### Mermaid Harp後

chart event 142以降は一本道ではない。少なくとも次の枝が独立して開始可能である。

```text
143  最後の鍵
144  マウントスノー -> 錆びた剣 -> サリイ
159  ベストドレッサー -> 綺麗な絨毯
160  主人公本体 -> ライフコッド -> セバスの兜
170  砂の器
171  グラコス
178  スフィーダの盾
```

重要なjoinは以下。

```text
170 + 171 -> 172 -> 173
159 + 173 -> 174 魔法の絨毯
158 + 169 + 177 + 178 -> 179 ラミアスの剣
143 + 188 -> 189 天馬の塔
```

この区間は攻略サイトの記載順を固定せず、global optimizerへ順序自由度を露出すべきである。

## 6. event dependency以外のhard gate

フラグDAGだけでは合法性を判定できない。

例:

- 魔術師の塔: story進行に加えて `インパス` が必要
- カルベローナ: 砂の器、グラコス撃破、バーバラが必要
- 魔法の絨毯: 綺麗な絨毯 + カルベローナ進行
- 聖なるほこら: 伝説4装備を主人公が装備し、正しいsymbol配置
- 天馬の塔: ゼニス側進行 + 最後の鍵
- 真実のオーブ移動: 真実のオーブ所持が必要

したがってlegal action判定は

```text
story prerequisites
AND spatial reachability
AND resources
AND capabilities
AND temporary/world state
```

で行う。

## 7. 未解決: 狭間世界の能力回復と湖ルート

外部フラグチャートでは、狭間突入後のイベント198が191だけを前提とする形になっており、エンデ防具・能力回復イベント197との依存が明示されない。

一方、複数の通常攻略資料は「エンデの防具を作るまでシナリオが進まない」と説明している。

この差は最適化上重要である。もし湖側へ能力回復前に進めるなら、通常チャートにない順序がlegalになる可能性がある。

現段階では

```text
status = uncertain_hidden_gate
optimizer = fail closed
```

とし、RAM watch / emulatorで以下を確認する。

1. event 191直後、197未完了で欲望の町・秘密の湖へ入れるか
2. 湖のNPC event 199が発生するか
3. event 198相当RAM bitが197前に立つか
4. 197前後でNPC/object script条件が変化するか

## 8. 最適化用の縮約原則

イベントDAGは事前計算できるが、**イベント列全体を雑に1本のmacroへ潰してはいけない**。

安全に縮約できるのは、途中に

- optional pickup
- shop
- recovery
- encounter region
- branchable movement
- resource consumption
- externally visible event edge

がなく、単純にprogression stateだけを更新するforced sequenceである。

したがって2段階にする。

```text
Raw chart-event graph (1..225)
        ↓
Semantic progression automaton
        ↓
Contract deterministic progression-only chains
        ↓
Expose only decision/join/set/reachability boundaries to global optimizer
```

一方、物理的な移動・アイテム回収・戦闘が挟まる区間はlocal macro solverがcost/state distributionを計算する。

## 9. 次の検証優先順位

1. 狭間197 vs 198/199のhidden gateを実機/エミュレータなしで追加解析できる資料がないか探索
2. 225 event edgeを `hard / reachability / resource / capability / set / knowledge / uncertain` に全件分類
3. 各hard edgeについてRAM bitまたはscript条件との対応率を上げる
4. indegree/outdegreeだけでなくresource/map side-effectを考慮した安全なchain contractionを実装
5. contraction後のprogression automatonをglobal optimizerへ接続

## 10. 主な参照先

- SFC DQ6 フラグチャート その1〜3
  - http://hori3948.g2.xrea.com/dq6/dq6-event1.html
  - http://hori3948.g2.xrea.com/dq6/dq6-event2.html
  - http://hori3948.g2.xrea.com/dq6/dq6-event3.html
- DQ6RTA実験室 ストーリーフラグ解説
  - https://dqrta.com/chart/story01/
- SFC版攻略チャート
  - https://way78.com/dq6/sfc/chart2.html
  - https://way78.com/dq6/sfc/chart3.html
- グレイス城イベント省略確認
  - https://gamewith.jp/dq6/560687
- 狭間世界通常進行確認
  - https://dq6.pidlio.com/dq6sfc/story09.html
  - https://gamewith.jp/dq6/560689
