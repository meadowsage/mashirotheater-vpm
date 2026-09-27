# Mashiro Station Auto Seat (By Display Name)

DisplayName が一致するプレイヤーを、指定の Station（椅子）へ自動的に座らせるギミックです。「この役の人は必ずこの席」という割り当てに使います。

## 主な機能・仕様

- Arm（起動）中、`Target Display Name` に一致する**ローカルプレイヤー**を対象 Station へ着席させます
- Disarm（解除）時、このギミックが座らせたプレイヤーは降車します
- 起動・解除は **Switch プロキシの GameObject を Timeline の Activation Track 等でトグル**して行うのが標準の使い方です

**Station 本体の GameObject を直接 SetActive しないでください。** `VRC_Station` 付き GameObject のトグルは、稀に他プレイヤーの描画・音声・名札が壊れる症状が報告されています。本体は常時 Active のまま、Switch プロキシ側をトグルする構成にしてあります。

## セットアップ

1. Station 側に `StationAutoSeatByDisplayName` を付け、`Station`（`VRCStation` コンポーネント）と `Target Display Name` を設定します
2. 別の GameObject に `StationAutoSeatByDisplayNameSwitch` を付け、対象の本体を割り当てます
3. Timeline の Activation Track などで **Switch 側の GameObject** をトグルします（Active = 着席試行、Inactive = 降車）

### StationAutoSeatByDisplayName のフィールド

| フィールド | 既定値 | 内容 |
|---|---|---|
| `Station` | – | 着席先の `VRCStation` コンポーネント |
| `Target Display Name` | 空 | 着席対象の displayName（完全一致・大文字小文字を区別） |
| `Initial Delay` | `0` 秒 | Arm 直後の判定遅延。0 で即時判定 |
| `Retry Count` | `4` | 再試行回数。0 なら 1 回のみ |
| `Retry Interval` | `0.25` 秒 | 再試行の間隔 |

再試行は `Station` などの参照が未準備だった場合にのみ行われます。参照が揃っていて displayName が一致しなかったときは、再試行せずにその Arm 期間の判定を終えます（displayName は途中で変わらないため）。

## API リファレンス

### StationAutoSeatByDisplayName

| メソッド | 用途 | 呼び出し種別 |
|---|---|---|
| `ArmGimmick()` / `DisarmGimmick()` | 起動 / 解除 | Switch が呼ぶ内部連携用（通常は手配線不要） |
| `TrySeatOnce()` | 着席を 1 回試行 | 内部連携用 |

### StationAutoSeatByDisplayNameSwitch

public 関数はありません。GameObject の Active/Inactive で本体を制御します（配線不要）。

## ライセンス

このフォルダの内容は MIT License で提供します（リポジトリルートの `LICENSE.md` を参照）。

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
