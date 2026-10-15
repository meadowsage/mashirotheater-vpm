# Mashiro Pickup Hold SFX

Pickup の Use 中（または保持中）に `AudioSource` をループ再生する UdonSharp コンポーネント（`MashiroPickupHoldSfx`）。再生状態を同期し、全プレイヤーで再生・停止する。

## 構成

| ファイル | 内容 |
|---|---|
| `MashiroPickupHoldSfx.cs` | 本体スクリプト（`MashiroPickupHoldSfx`） |
| `MashiroPickupHoldSfx.asset` | `MashiroPickupHoldSfx` の UdonSharp ProgramAsset |
| `footsteps-on-wooden-floor-6803.mp3` | 効果音素材（配布対象外） |

## 依存

- パッケージ: `MashiroTheater-Utils`（VPM `com.mashirotheater.utils`）
- `VRC_Pickup`: `pickup` 未設定時は同じ GameObject のものを取得する。
- `AudioSource`: 再生する AudioClip は `AudioSource.clip` に設定する。

## 仕様

### 初期化（`Start`）

- `audioSource` 未設定のとき、`Debug.LogError` を出してコンポーネントを無効化（`enabled = false`）する。
- `pickup` 未設定のとき、同じ GameObject の `VRC_Pickup` を取得する。取得できなければ `Debug.LogError` を出してコンポーネントを無効化する。
- `audioSource` に次を設定する。
  - `playOnAwake = false`
  - `loop = true`
  - `spatialBlend` が 1 未満なら `1`
- `audioSource` を停止して音量を 0 にし、同期変数 `_playingSynced` の値を反映する。

### 再生条件

- `playWhileHeldWithoutUse` が `false`: 保持中かつ Use 押下中（`OnPickupUseDown` 〜 `OnPickupUseUp`）に再生する。
- `playWhileHeldWithoutUse` が `true`: 保持中（`OnPickup` 〜 `OnDrop`）に再生する。
- `OnDrop` で Use 押下状態も解除する。

### 同期

- 同期モード: `BehaviourSyncMode.Manual`
- 同期変数: `_playingSynced`（`bool`、`[UdonSynced]`）
- `OnPickup` で拾ったプレイヤーが `Networking.SetOwner` でオーナーになる。
- 再生条件の評価と `_playingSynced` の更新はオーナーのみが行い、値が変わったときに `RequestSerialization` する。
- `OnDeserialization` と `OnOwnershipTransferred` で `_playingSynced` を反映する。
- `OnPlayerLeft` で、自分がオーナーならローカルの保持・Use 状態から再生条件を再評価する。

### 音量フェード

- 目標音量は `_playingSynced` が `true` なら `targetVolume`、`false` なら `0`。
- `fadeSeconds` が 0 より大きいとき、`Mathf.SmoothDamp`（`smoothTime = fadeSeconds`）で音量を目標へ近づけ、差が `0.002` 未満で目標値に確定する。
- `fadeSeconds` が 0 以下のとき、目標音量を即時適用する。
- 停止時は音量が 0 に確定した時点で `AudioSource.Stop()` する。
- 音量は 0〜1 に制限して `AudioSource.volume` へ設定する。
- フェード中のみコンポーネントを有効にし、確定後は `enabled = false` にする。

## Inspector

### MashiroPickupHoldSfx

| フィールド | 型 | 既定値 | 必須 | 内容 |
|---|---|---|---|---|
| `audioSource` | `AudioSource` | なし | ○ | 再生に使う `AudioSource` |
| `pickup` | `VRC_Pickup` | なし | – | 対象の Pickup。未設定なら同じ GameObject から取得する |
| `playWhileHeldWithoutUse` | `bool` | `false` | – | `true` で保持中に再生、`false` で保持中かつ Use 押下中に再生 |
| `fadeSeconds` | `float` | `0.10` | – | 音量フェードの `SmoothDamp` の smoothTime（秒）。0 以下で即時切り替え |
| `targetVolume` | `float`（`[Range(0, 1)]`） | `1` | – | 再生時の音量 |

## API リファレンス

### MashiroPickupHoldSfx

#### UI へ手配線するもの

なし。

#### 内部連携用（配線不要）

| シグネチャ | 用途 | 呼び出し種別 |
|---|---|---|
| `override void OnPickup()` | オーナーを取得し、保持状態にして再評価する | VRChat コールバック（内部専用） |
| `override void OnDrop()` | 保持・Use 状態を解除して再評価する | VRChat コールバック（内部専用） |
| `override void OnPickupUseDown()` | Use 押下状態にして再評価する | VRChat コールバック（内部専用） |
| `override void OnPickupUseUp()` | Use 押下状態を解除して再評価する | VRChat コールバック（内部専用） |
| `override void OnDeserialization()` | 同期された再生状態を反映する | VRChat コールバック（内部専用） |
| `override void OnOwnershipTransferred(VRCPlayerApi player)` | 再生状態を反映する | VRChat コールバック（内部専用） |
| `override void OnPlayerLeft(VRCPlayerApi player)` | オーナーなら再生条件を再評価する | VRChat コールバック（内部専用） |

## ライセンス

MIT License（リポジトリルートの `LICENSE.md`）。

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
