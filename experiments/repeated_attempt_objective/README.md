# Repeated-attempt objective demo v0

## 目的

RTAのroute比較を「成功runのタイム」だけでなく、**目標successを1回得るまでの期待壁時計時間**でも評価できるようにする。

IID attemptを成功まで繰り返すとし、

- success probability: `p`
- 成功attemptの平均時間: `Ts`
- 失敗attemptの平均時間: `Tf`

なら、成功までの期待壁時計時間は

```text
Ts + ((1 - p) / p) * Tf
```

となる。

## Synthetic example

| policy | success p | success mean | failure mean | expected wall-clock to success |
| --- | ---: | ---: | ---: | ---: |
| stable | 0.25 | 400 s | 180 s | 940 s |
| aggressive | 0.10 | 380 s | 120 s | 1460 s |
| tail-heavy | 0.05 | 360 s | 60 s | 1500 s |

成功時の最速値だけを見ると`tail-heavy`が最も速いが、繰り返しattempt全体では`stable`が最も早く目標successへ到達する。

## DQ6への用途

将来、successを以下のように定義して同じ指標を使える。

- 完走
- current WR未満
- 6:xx:xx未満
- 特定区間を所定タイム・所定状態で突破

failure durationにはreset判断までに消費した時間を含める。policyごとにreset位置が違う場合、その差も評価へ入る。

この指標は単独で唯一の目的関数に固定せず、平均タイム・完走率・target突破率・実行難度等とともにChart Atlasへ載せる。
