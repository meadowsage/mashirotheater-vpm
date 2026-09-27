# Mashiro Station Auto Seat (On Active)

起動時に、指定エリア内にいるプレイヤーを Station（椅子）へ自動的に座らせるギミックです。「開演時にエリア内の観客を一斉着席させる」ような使い方を想定しています。

## 主な機能・仕様

- Arm（起動）中、`Target Zones` のコライダー内にいる**ローカルプレイヤー**を対象 Station へ着席させます
- Disarm（解除）時、このギミックが座らせたプレイヤーは降車します
- 判定は座標ベース（ClosestPoint）で行い、OnTrigger 系イベントは使用しません
- 判定に使うプレイヤーの座標は既定で**頭の位置**です（`Tracking Data Type` で変更可）。足元基準ではないため、床に貼り付けた薄いゾーンでは判定されません。ゾーンは頭の高さを含む厚みで作ってください
- 起動・解除は **Switch プロキシの GameObject を Timeline の Activation Track 等でトグル**して行うのが標準の使い方です

**Station 本体の GameObject を直接 SetActive しないでください。** `VRC_Station` 付き GameObject のトグルは、稀に他プレイヤーの描画・音声・名札が壊れる症状が報告されています。本体は常時 Active のまま、Switch プロキシ側をトグルする構成にしてあります。

## セットアップ

1. Station 側に `StationAutoSeatOnActive` を付け、`Station`（`VRCStation` コンポーネント）と判定エリア `Target Zones` を設定します
2. 別の GameObject に `StationAutoSeatOnActiveSwitch` を付け、対象の本体を割り当てます
3. Timeline の Activation Track などで **Switch 側の GameObject** をトグルします（Active = 着席試行、Inactive = 降車）

### StationAutoSeatOnActive のフィールド

| フィールド | 既定値 | 内容 |
|---|---|---|
| `Station` | – | 着席先の `VRCStation` コンポーネント |
| `Target Zones` | – | 判定エリアの BoxCollider 群 |
| `Tracking Data Type` | `Head` | 判定に使うトラッキング座標。既定は頭の位置 |
| `Initial Delay` | `0` 秒 | Arm 直後の判定遅延。0 で即時判定 |
| `Retry Count` | `0` | 同一 Arm 期間中の再試行回数。0 なら 1 回のみ判定 |
| `Retry Interval` | `0.25` 秒 | 再試行の間隔 |

### 着席ポーズ用の AnimatorController

同梱の `StationAutoSeatOnActive.controller` は、`VRCStation` の `Animator Controller` に割り当てるための**雛形**です。モーションは入っていないため、着席ポーズのアニメーションクリップは利用者が設定してください。

## API リファレンス

### StationAutoSeatOnActive

| メソッド | 用途 | 呼び出し種別 |
|---|---|---|
| `ArmGimmick()` / `DisarmGimmick()` | 起動 / 解除 | Switch が呼ぶ内部連携用（通常は手配線不要） |
| `TrySeatOnce()` | 着席を 1 回試行 | 内部連携用 |

### StationAutoSeatOnActiveSwitch

public 関数はありません。GameObject の Active/Inactive で本体を制御します（配線不要）。

## ライセンス

このフォルダの内容は MIT License で提供します（リポジトリルートの `LICENSE.md` を参照）。

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
