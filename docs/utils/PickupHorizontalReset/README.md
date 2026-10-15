# Mashiro Pickup Horizontal Reset

Pickup のドロップ時に、付与した GameObject のワールド回転の X/Z を 0 にする UdonSharp コンポーネント（`MashiroPickupHorizontalReset`）。

## 構成

| ファイル | 内容 |
|---|---|
| `MashiroPickupHorizontalReset.cs` | 本体スクリプト（`MashiroPickupHorizontalReset`） |
| `MashiroPickupHorizontalReset.asset` | `MashiroPickupHorizontalReset` の UdonSharp ProgramAsset |

## 依存

- パッケージ: `MashiroTheater-Utils`（VPM `com.mashirotheater.utils`）
- `VRC_Pickup`: 同じ GameObject に付いている場合に `OnDrop` を受け取る。

## 仕様

- 水平化の対象は、このコンポーネントが付いた GameObject の Transform に固定。
- 水平化は、ワールド回転（`transform.eulerAngles`）を `(0, 現在の Y, 0)` に設定する。位置は変更しない。
- `OnDrop` で水平化する。
- `desktopModeOnly` が `true` のとき、`OnDrop` を受け取ったクライアントのローカルプレイヤーが VR（`IsUserInVR()` が `true`）、または `Networking.LocalPlayer` が null なら何もしない。
- `ResetHorizontal` は `desktopModeOnly` を判定せずに水平化する。
- `[UdonBehaviourSyncMode]` は指定していない。
- 同期変数を持たない。
- Transform の変更は実行したクライアントのみで行う。

## Inspector

### MashiroPickupHorizontalReset

| フィールド | 型 | 既定値 | 必須 | 内容 |
|---|---|---|---|---|
| `desktopModeOnly` | `bool` | `true` | – | `true` のとき、`OnDrop` での水平化をデスクトップモードのプレイヤーに限定する |

## API リファレンス

### MashiroPickupHorizontalReset

#### UI へ手配線するもの

| シグネチャ | 用途 | 呼び出し種別 |
|---|---|---|
| `void ResetHorizontal()` | この GameObject を水平化する | `Button.OnClick` から `SendCustomEvent("ResetHorizontal")` で配線 / 他の Udon から `SendCustomEvent` |

#### 内部連携用（配線不要）

| シグネチャ | 用途 | 呼び出し種別 |
|---|---|---|
| `override void OnDrop()` | `desktopModeOnly` の条件を満たせば水平化する | VRChat コールバック（内部専用） |

## ライセンス

MIT License（リポジトリルートの `LICENSE.md`）。

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
