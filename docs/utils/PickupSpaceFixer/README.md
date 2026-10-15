# Mashiro Pickup Space Fixer

保持中の Pickup をダブルトリガーでその場に固定し、固定中に掴むと固定を解除する UdonSharp コンポーネント（`MashiroPickupSpaceFixer`）。固定状態を全プレイヤーで同期する。

## 構成

| ファイル | 内容 |
|---|---|
| `MashiroPickupSpaceFixer.cs` | 本体スクリプト（`MashiroTheater.MashiroPickupSpaceFixer`） |
| `MashiroPickupSpaceFixer.asset` | `MashiroPickupSpaceFixer` の UdonSharp ProgramAsset |

## 依存

- パッケージ: `MashiroTheater-Utils`（VPM `com.mashirotheater.utils`）
- 同じ GameObject 上の次のコンポーネント（`Start` で取得する。null チェックは行わない）
  - `VRC_Pickup`
  - `Rigidbody`
  - `Collider`（`GetComponents<Collider>()` で取得したすべて）
- `VRCObjectSync`（位置・回転の同期用。本コンポーネントからは参照しない）

## 仕様

### 固定

- `OnPickupUseDown` の発生時刻（`Time.time`）と前回の発生時刻の差が `doubleTriggerWindow` 秒以下のとき固定する。
- 固定が成立すると前回時刻を破棄する（3 回目の押下は 1 回目として扱う）。
- 固定中は固定処理を行わない。
- 固定時の処理順:
  1. オーナーでなければ `Networking.SetOwner` でオーナーになる。
  2. `VRC_Pickup.Drop()` する。
  3. `isFixed = true` にして物理状態を適用する。
  4. `audioSource` と `fixSound` が両方設定されていれば `audioSource.PlayOneShot(fixSound)` する。

### 解除

- 固定中に `OnPickup` が発生したとき、オーナーでなければオーナーになり、`isFixed = false` にして物理状態を適用する。

### 物理状態

| 状態 | `Rigidbody.useGravity` | `Rigidbody.isKinematic` | 全 `Collider.isTrigger` |
|---|---|---|---|
| 固定中 | `false` | `true` | `true` |
| 非固定 | `true` | `false` | `false` |

- 非固定時の値は固定値であり、元の設定値は保持しない。
- `Start` で `isFixed` の値（既定 `false`）の状態を適用するため、Inspector 上の `useGravity` / `isKinematic` / `isTrigger` の設定は上書きされる。
- `VRC_Pickup` の `pickupable` は変更しない。
- Transform の位置・回転は変更しない。

### 同期

- 同期モード: `BehaviourSyncMode.Continuous`
- 同期変数: `isFixed`（`bool`、`[UdonSynced]`）
- `OnDeserialization` と `OnOwnershipTransferred` で `isFixed` の物理状態を適用する。
- 効果音は固定操作を行ったクライアントのみで再生し、同期しない。
- 位置・回転の同期は行わない。

## Inspector

### MashiroPickupSpaceFixer

Add Component メニュー: `MashiroTheater/Mashiro Pickup Space Fixer`

| フィールド | 型 | 既定値 | 必須 | 内容 |
|---|---|---|---|---|
| `doubleTriggerWindow` | `float` | `0.3` | – | ダブルトリガーと判定する押下間隔の上限（秒） |
| `audioSource` | `AudioSource` | なし | – | 固定時の効果音を鳴らす `AudioSource`。未設定なら鳴らさない |
| `fixSound` | `AudioClip` | なし | – | 固定時に鳴らす音。未設定なら鳴らさない |

## API リファレンス

### MashiroPickupSpaceFixer

#### UI へ手配線するもの

なし。

#### 内部連携用（配線不要）

| シグネチャ | 用途 | 呼び出し種別 |
|---|---|---|
| `override void OnPickup()` | 固定中なら解除する | VRChat コールバック（内部専用） |
| `override void OnPickupUseDown()` | ダブルトリガーを判定して固定する | VRChat コールバック（内部専用） |
| `override void OnDeserialization()` | 同期された固定状態を物理へ適用する | VRChat コールバック（内部専用） |
| `override void OnOwnershipTransferred(VRCPlayerApi player)` | 固定状態を物理へ再適用する | VRChat コールバック（内部専用） |

## ライセンス

MIT License（リポジトリルートの `LICENSE.md`）。

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
