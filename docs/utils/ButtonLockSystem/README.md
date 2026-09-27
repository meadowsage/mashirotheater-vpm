# Mashiro Button Lock System

UI ボタン群を一括でロック（押せない状態に）するギミックです。公演の操作卓などで、本番中に触ってほしくないボタンをまとめて保護する用途を想定しています。

## 主な機能・仕様

- ロック ON 中は対象ボタンの `interactable` が false になり押せません
- ロック切替用トグルボタンは、状態に応じて色が変わります（ON: 暗いオレンジ / OFF: 黒）。全ステート同色にしてあるため、フォーカスが外れても色が戻りません
- `Use Global Lock` を ON にするとロック状態が全プレイヤーで同期されます（OFF なら各自ローカル）

## セットアップ

1. 空の GameObject などに `MashiroButtonLockSystem` を追加します
2. `Target Buttons` にロック対象のボタン群、`Lock Toggle Button` に切替ボタンを割り当てます
3. 切替ボタンの `OnClick` から `ToggleLock` を呼ぶよう配線します

| フィールド | 既定値 | 内容 |
|---|---|---|
| `Use Global Lock` | `false` | ロック状態を全員で共有する |
| `Is Locked` | `true` | シーン開始時のロック状態 |
| `Target Buttons` | – | ロック対象の UI ボタン群 |
| `Lock Toggle Button` | – | ロック状態を切り替えるボタン |
| `Locked Color` / `Unlocked Color` | 暗いオレンジ / 黒 | トグルボタンの状態色 |

## API リファレンス

### MashiroButtonLockSystem

| メソッド | 用途 | 呼び出し種別 |
|---|---|---|
| `ToggleLock()` | ロック状態を切り替える | `Button.OnClick` から配線 |
| `OnDeserialization()` | 同期受信処理 | 内部専用（配線不要） |

## ライセンス

このフォルダの内容は MIT License で提供します（リポジトリルートの `LICENSE.md` を参照）。

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
