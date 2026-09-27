# MashiroChairHeightAdjuster

`MashiroChairHeightAdjuster` は、VRCStation の椅子高さを段階的に上下させる UdonSharp ギミックです。
椅子に連動して操作パネルの高さも移動できます。

## 同梱ファイル

- `MashiroChairHeightAdjuster.cs`
  - 椅子と任意の操作パネルを段階調整するメインコンポーネント
- `MashiroAdjustableChair.prefab`
  - 椅子・操作パネル・上下ボタンを配線済みの構成例プレハブ

## セットアップ

1. 任意の GameObject に `MashiroChairHeightAdjuster` をアタッチ
2. Inspector で以下を設定
   - `Chair`: 高さを動かしたい `VRCStation`
   - `Control Panel`（任意）: 椅子と一緒に動かしたい `Transform`
   - `Height Step`: 1段あたりの高さ変化量（デフォルト `0.05`）
   - `Max Level`: 最大調整段階数（デフォルト `8`）
   - `Initial Level`: 初期段階数（デフォルト `4`）
3. UIボタン等から以下メソッドを呼び出し
   - 上げる: `OnUpButton()`
   - 下げる: `OnDownButton()`

## 動作仕様

- 段階は `0` ～ `Max Level` の範囲にクランプされます。
- `Initial Level` は**変位 0 の基準となる段階**です。起動時は椅子・操作パネルともシーンに配置したままの位置で、移動は起きません。
- 起動後は `Initial Level` を基準に、上へ `Max Level - Initial Level` 段、下へ `Initial Level` 段まで調整できます（1 段あたり `Height Step` m）。
- `Initial Level` が `Max Level` を超える場合は、`Max Level` までに制限されます。
- **高さ変更はローカル処理**です。同期しないため、他プレイヤーの画面では椅子・操作パネルは動きません。

## API リファレンス

### MashiroChairHeightAdjuster

| メソッド | 用途 | 呼び出し種別 |
|---|---|---|
| `OnUpButton()` | 高さを 1 段階上げる | `Button.OnClick` から配線 |
| `OnDownButton()` | 高さを 1 段階下げる | `Button.OnClick` から配線 |

## ライセンス

このフォルダ内の `.cs` ファイルは MIT License で提供します。

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
