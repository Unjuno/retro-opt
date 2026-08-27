# DQ6 story event / gating model

## 1. 目的

SFC版DQ6のRTA探索では、地理的に到達できる場所であっても、ストーリー上のイベント条件を満たしていなければ通行・会話・戦闘・アイテム取得・乗り物利用などが発生しない場合がある。

したがって optimizer は「現在位置 + 資源」だけではなく、**進行イベント状態**を明示的に持つ。

重要なのは、攻略チャートに書かれているイベントをすべて必須扱いしないことである。DQ6には次の両方が存在する。

- ゲーム内部のフラグが立たない限り絶対に先へ進めないイベント
- 情報を聞くためだけのイベントで、プレイヤーが答えや場所を知っていれば飛ばせるイベント

例:

- 木こりから話を聞く前は、場所を知っていても川の抜け道を発見できない → **hard gate**
- グレイス城の過去イベントは、隠し階段の場所を知っていれば見なくてもオルゴーの鎧を取得できる → **knowledge-only / skippable**

この違いを探索器に反映する。

## 2. 3層のフラグ表現

### Layer A: semantic event state

optimizer が使用するゲーム意味上の状態。

例:

- `river_passage_discovery_enabled`
- `dream_dew_obtained`
- `mirror_key_obtained`
- `moon_mirror_orbs_destroyed = 0..4`
- `mudo_real_defeated`
- `magic_key_obtained`
- `flying_bed_unlocked`
- `mermaid_harp_obtained`
- `gracos_defeated`
- `plush_rug_obtained`
- `magic_carpet_unlocked`
- `legendary_equipment_count`
- `zenith_castle_restored`
- `pegasus_harness_upgraded`
- `hazama_power_restored`
- `deathmore_defeated`

### Layer B: chart event reference

公開されているSFC版「フラグチャート」では、進行イベントを 1〜225 の番号で整理し、それぞれの発生に必要な先行イベント番号を記載している。

この番号は本repoでは `chart_event_id` と呼ぶ。

**RAMのbit番号だとは仮定しない。**

### Layer C: RAM mapping

SFC版の解析資料では恒久イベントフラグ領域として `$7E3D2A-$7E3DFF` が報告されている。

将来 emulator/RAM解析を行った時点で、

```text
semantic event
    ↓
chart_event_id
    ↓
RAM address + bit
```

をcross-checkして対応付ける。

RAM mappingが未同定でもsemantic modelとsolverは構築できる。

## 3. Event classification

各event/actionには以下の分類を付ける。

### `hard_progression`

Normal Endingへ進むためにゲーム内部状態として必要。場所や答えを知っていても代替不能。

### `reachability_gate`

扉、関所、井戸、船、水門、ベッド、絨毯、天馬など、到達可能なmap edgeを変える。

### `forced_sequence`

複数の会話・追跡・一時同行などを順番に踏む必要があるstate machine。

例: ホルス王子、ペスカニのロブ、牢獄の町。

### `mandatory_combat`

勝利または規定結果が次eventの前提になる戦闘。

### `item_gate`

story flagではなくkey item / equipment / command所持がlegal actionの前提になる。

例: ラーの鏡、黄金のつるはし、魔法の鍵、古びたパイプ、牢獄の鍵、真実のオーブ。

### `capability_gate`

キャラクター能力・習得コマンド・装備条件が必要。

例: 魔術師の塔への侵入に必要な `インパス`、ベストドレッサーのかっこよさ条件。

### `temporary_state`

一時同行、夜/昼、姿が見えない、狭間世界の能力低下など、次のlegal actionを変える一時状態。

### `knowledge_only`

NPC情報・ヒント等。ゲーム内部のhard gateではなく、解答を知っているcompetition runnerなら省略可能。

### `optional_resource`

宝箱、種、金、装備、回復など。completionには不要だが最適routeでは候補になる。

### `optional_party`

アモス、ピエール、ドランゴ等の任意加入。

### `world_state`

町の復活、NPC配置変化、店解禁、敵出現変化など複数箇所へ作用する状態。

## 4. Booleanだけにしない

イベント状態は単純なboolだけでは足りない。

例:

```text
trial_tower_mistake_count: 0..3+
moon_mirror_orbs_destroyed: 0..4
best_dresser_rank_cleared: 0..8
hols_escort_stage: enum
rob_follow_stage: enum
legendary_equipment: set
prison_town_stage: enum
```

同一event chainの途中状態を保持することで、「どこまで処理済みか」を探索器が正しく判定できる。

## 5. Event graph と resource graph の接続

story eventはresourceとは別レイヤではあるが、相互作用する。

```text
story requirements
 + key items
 + party/capability requirements
 + temporary state
        ↓
      legal action
        ↓
 time + resource effects + event effects
        ↓
      next state
```

例:

- ホルストック南西の井戸へ入るには `magic_key_obtained` が必要。
- 魔術師の塔はstory上フォーン王の依頼だけでなく `インパス` が必要。
- ベストドレッサーランク3は `coolness >= threshold` を要求し、成功すると `plush_rug_obtained`。
- `plush_rug_obtained` だけでは魔法の絨毯にならず、グラコス撃破→カルベローナ復活→砂の器→マダンテ伝授イベントまで必要。
- 伝説の剣完成は、サリイへ錆びた剣を渡しただけでは足りず、兜・鎧・盾の取得も前提になる。

## 6. 情報イベントの扱い

攻略サイトの通常チャートをそのままdependency graphにすると不要なイベントを強制してしまう。

したがって各候補について次を確認する。

1. イベントを発生させずに対象object/door/routeへアクセスできるか
2. 正解・場所を知っていてもゲーム側が拒否するか
3. event flagがNPC/door/object配置条件になっているか
4. key item/commandだけで代替できるか
5. RTAの既存チャートが実際に省略しているか

確認できないものは `gate_status = uncertain` とし、hard gateと決め打ちしない。

## 7. 現時点の主要source

- SFC版フラグチャート その1〜3
  - http://hori3948.g2.xrea.com/dq6/dq6-event1.html
  - http://hori3948.g2.xrea.com/dq6/dq6-event2.html
  - http://hori3948.g2.xrea.com/dq6/dq6-event3.html
- DQ6 攻略・解析 story chart
  - https://gcgx.games/dq6/chart1.html 〜 chart8.html
- SFC-DQ6 RAM解析
  - https://w.atwiki.jp/dq_binary/pages/7.html
- DQ6 `しらべる` / flag ID解析
  - https://showa-yojyo.github.io/dqbook/dq6_search.html
- RTA向けストーリーフラグ解説
  - https://dqrta.com/chart/story01/
  - https://dqrta.com/chart/story02/

重要なgateは最終的に複数sourceとemulator/RAMでcross-checkする。
