# Mashiro Button Lock System

複数の UI `Button` の `interactable` を一括で切り替え、押下できない状態（ロック）にするコンポーネント。ロック状態はローカル管理と全プレイヤー同期を切り替えられる。

## 構成

| ファイル | 役割 |
| --- | --- |
| `MashiroButtonLockSystem.cs` | ロック状態の管理と対象ボタン・切替ボタンへの反映 |
| `MashiroButtonLockSystem.asset` | `MashiroButtonLockSystem` の UdonSharp ProgramAsset |

## 依存

- パッケージ: `MashiroTheater-Utils`（VPM `com.mashirotheater.utils`）
- ロック対象・切替ボタンは `UnityEngine.UI.Button`。

## 仕様

### ロックの反映

- ロック中は `targetButtons` の各要素の `interactable` を `false`、解除中は `true` にする。`null` 要素は無視する。
- `lockToggleButton` の `ColorBlock` の `normalColor` / `highlightedColor` / `pressedColor` / `selectedColor` / `disabledColor` をすべて同じ色にする。
  - ロック中: `lockedColor`
  - 解除中: `unlockedColor`
- `lockToggleButton` の `interactable` は変更しない（`targetButtons` に含めた場合を除く）。
- 反映は `Start`・`ToggleLock()`・`OnDeserialization()`（`useGlobalLock` が `true` のとき）で行う。

### 同期

- 同期モード: `[UdonBehaviourSyncMode(BehaviourSyncMode.Manual)]`
- 同期変数: `syncedIsLocked`（`bool`、初期値 `true`）
- `useGlobalLock` が `false` のとき:
  - `isLocked` をローカルで反転する。同期変数は使わない。
  - `OnDeserialization()` では何もしない。
- `useGlobalLock` が `true` のとき:
  - `Start`: GameObject のオーナーは `syncedIsLocked` に `isLocked` を代入して `RequestSerialization()` する。オーナー以外は `isLocked` に `syncedIsLocked` を代入する。
  - `ToggleLock()`: 操作者がオーナーでなければ `Networking.SetOwner` でオーナーを取得し、`syncedIsLocked` を反転して反映・`RequestSerialization()` する。
  - `OnDeserialization()`: `isLocked` に `syncedIsLocked` を代入して反映する。
- 操作できるプレイヤーの制限はない。

## Inspector

### MashiroButtonLockSystem

| フィールド | 型 | 既定値 | 必須 | 内容 |
| --- | --- | --- | --- | --- |
| `useGlobalLock` | `bool` | `false` | — | `true` でロック状態を全プレイヤーで同期する |
| `isLocked` | `bool` | `true` | — | 開始時のロック状態（`true` = ロック） |
| `targetButtons` | `Button[]` | 空 | ○ | ロック対象のボタン群 |
| `lockToggleButton` | `Button` | なし | — | 状態色を反映する切替ボタン |
| `lockedColor` | `Color` | `(0.69, 0.239, 0.016, 1)` | — | ロック中の切替ボタン色 |
| `unlockedColor` | `Color` | `Color.black`（`(0, 0, 0, 1)`） | — | 解除中の切替ボタン色 |

## API リファレンス

### MashiroButtonLockSystem

#### UI へ手配線するもの

| シグネチャ | 用途 | 呼び出し種別 |
| --- | --- | --- |
| `void ToggleLock()` | ロック状態を反転する | `Button.OnClick` から配線 |

#### 内部連携用（配線不要）

| シグネチャ | 用途 | 呼び出し種別 |
| --- | --- | --- |
| `void OnDeserialization()` | 同期受信時に `syncedIsLocked` を反映する | VRChat コールバック（内部専用） |

## ライセンス

MIT License（`MashiroTheater-Utils` 同梱の `LICENSE.md` を参照）。

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
