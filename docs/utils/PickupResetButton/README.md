# Mashiro Pickup Reset Button

指定ルートの直下にある `VRC_Pickup` 付きオブジェクトを、Interact で一括して初期配置へ戻す UdonSharp コンポーネント（`MashiroPickupResetButton`）。

## 構成

| ファイル | 内容 |
|---|---|
| `MashiroPickupResetButton.cs` | 本体スクリプト（`MashiroTheater.MashiroPickupResetButton`） |
| `MashiroPickupResetButton.asset` | `MashiroPickupResetButton` の UdonSharp ProgramAsset |

## 依存

- パッケージ: `MashiroTheater-Utils`（VPM `com.mashirotheater.utils`）
- 対象オブジェクトの `VRC_Pickup`（必須）、`VRCObjectSync`（任意）、`Rigidbody`（任意）

## 仕様

### 対象

- `targetRoot`（未設定ならこの GameObject の Transform）の直下の子のうち、子自身に `VRC_Pickup` が付いているもの。孫以降は対象外。
- 対象は `Start` で確定する。`Start` 以降に追加した子は対象にならない。
- 子自身に `VRCObjectSync` が付いているかで、リセット方法が分かれる。

### リセット方法

| 対象 | 処理 | 反映範囲 |
|---|---|---|
| `VRCObjectSync` あり | オーナーでなければ `Networking.SetOwner` でオーナーになり、`VRCObjectSync.Respawn()` を呼ぶ | `VRCObjectSync` の同期に従う |
| `VRCObjectSync` なし | `Start` 時点の `localPosition` / `localRotation` へ戻す | 実行したクライアントのみ |

- `VRCObjectSync` ありの対象の戻り先は `VRCObjectSync` が保持するスポーン位置。
- `VRCObjectSync` なしの対象は、戻す前に次を行う。
  - `VRC_Pickup.IsHeld` が `true` なら `Drop()` する。
  - 同じ GameObject の `Rigidbody` が非キネマティックなら、`velocity` と `angularVelocity` を 0 にする。
- 戻し先はローカル座標で保持するため、`targetRoot` の移動・回転に追従する。

### 同期・権限

- 同期モード: `BehaviourSyncMode.NoVariableSync`
- 同期変数を持たない。
- `Interact` を実行できるプレイヤーの制限はない。

## Inspector

### MashiroPickupResetButton

Add Component メニュー: `MashiroTheater/Mashiro Pickup Reset Button`

| フィールド | 型 | 既定値 | 必須 | 内容 |
|---|---|---|---|---|
| `targetRoot` | `Transform` | なし | – | 直下の子をリセット対象にする Transform。未設定ならこの GameObject 自身 |

## API リファレンス

### MashiroPickupResetButton

#### UI へ手配線するもの

| シグネチャ | 用途 | 呼び出し種別 |
|---|---|---|
| `void ResetAll()` | 全対象をリセットする | `Button.OnClick` から `SendCustomEvent("ResetAll")` で配線 / 他の Udon から `SendCustomEvent` |

#### 内部連携用（配線不要）

| シグネチャ | 用途 | 呼び出し種別 |
|---|---|---|
| `override void Interact()` | `ResetAll()` を呼ぶ | VRChat コールバック（内部専用） |

## ライセンス

MIT License（リポジトリルートの `LICENSE.md`）。

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
