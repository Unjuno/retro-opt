# DQ6 early state-dependent policy experiment v0

## 目的

追加戦闘を「常に狩る / 常に逃げる」という固定ruleにせず、現在EXPと後続価値に応じてsolverが条件付きpolicyを選べるか確認する。

実測前の sensitivity test であり、実ゲームの最適チャートを主張しない。

## 仮説モデル

- target EXP: 847
- Metal Slime EXP: 1350
- 非Metal EXP候補: 19, 19, 21, 23, 24（仮に等確率）
- Metal確率: 5%（仮定）
- 追加戦闘の正味コスト: 10秒（仮定）
- 閾値847未達による後続penaltyを 15 / 30 / 60秒で感度分析
- 追加戦闘機会は1回

公開値のprovenance:

- https://togoblo25.fc2.net/blog-entry-131.html
- https://mamemommm.com/dq6_chart_mmm

## 結果

仮説モデルでは、追加戦闘を選び始めるEXP境界は以下になった。

| 後続penalty | fightを選ぶ最初のEXP |
| ---: | ---: |
| 15 s | 828 |
| 30 s | 824 |
| 60 s | 823 |

つまり、同じ敵・同じ追加戦闘コストでも、現在EXPと「そのEXPが将来どれだけ価値を持つか」でactionが変わる。

この実験の意味は数値そのものではなく、将来emulator実測値を投入した際に、solverがこの種の**状態依存境界**を自動的に出せることを確認した点にある。

## 次段階

- 追加戦闘機会を複数回に増やす
- 敵編成ごとに fight / flee actionを分ける
- fight時間を確率分布化する
- Metalの「遭遇」だけでなく「撃破成功 / 逃走」まで分岐させる
- target EXPを単一閾値ではなく、後続boss / movement / recoveryの連続的value functionへ置換する
