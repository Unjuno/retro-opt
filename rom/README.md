# ROM acquisition / validation

この directory は ROM イメージそのものではなく、**取得方法・識別・hash・検証手順**を管理する。

## 原則

- ROM file は repository に含めない
- 実験には利用者自身が適法に用意した local ROM を使用する
- dump device / firmware / cartridge 情報を可能な範囲で記録する
- 同一 cartridge から複数回 dump して一致を確認する
- SHA-256 を実験 manifest に記録する

## 初期 validation procedure

1. cartridge / connector の orientation を確認
2. power condition と current limit を確認
3. dump #1
4. power cycle
5. dump #2
6. power cycle
7. dump #3
8. 3 file を byte-for-byte 比較
9. SHA-256 比較
10. emulator で起動確認

3 dump が一致しない場合、その ROM は optimizer / reverse engineering の基準データとして使用しない。

## 将来の CLI

```text
retro-opt rom dump --platform sfc
retro-opt rom inspect <file>
retro-opt rom hash <file>
retro-opt rom compare <a> <b>
```
