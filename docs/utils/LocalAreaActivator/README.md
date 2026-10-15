# MashiroLocalAreaActivator

ローカルプレイヤーが指定 Collider の内部にいる間だけ、対象 GameObject を有効化するコンポーネント。内外判定はポーリングで行い、状態は同期しない。

## 構成

| ファイル | 役割 |
| --- | --- |
| `MashiroLocalAreaActivator.cs` | 内外判定と対象 GameObject の `SetActive` |
| `MashiroLocalAreaActivator.asset` | `MashiroLocalAreaActivator` の UdonSharp ProgramAsset |

## 依存

- パッケージ: `MashiroTheater-Utils`（VPM `com.mashirotheater.utils`）
- エリア定義に `Collider`（Box / Sphere / Capsule / Convex MeshCollider）が必要。

## 仕様

### 内外判定

- 判定点は `Networking.LocalPlayer.GetPosition()`（ローカルプレイヤーの足元位置）。
- `area.ClosestPoint(判定点)` と判定点の距離の 2 乗が `1e-6` 以下（距離 1 mm 以下）のとき「内」とする。
- `OnPlayerTriggerEnter` / `OnPlayerTriggerExit` は使わない。
- 次の場合は「外」とする。
  - `area` が未設定
  - `area.enabled` が `false`
  - ローカルプレイヤーが取得できない
- `area` の GameObject のアクティブ状態は判定条件に含まない。
- Non-Convex の MeshCollider は `Collider.ClosestPoint` の対象外のため使用できない。

### タイミング

- `Start` で即時に判定し、結果を対象へ反映する。
- 以後は `Update` で `pollInterval` 秒ごとに判定する。`pollInterval` が `0` 以下のときは毎フレーム判定する。
- 最初のポーリング時刻は `Start` から `0` 〜 `pollInterval` 秒の乱数でずらす。
- ポーリング時は、内外が前回から変化したときのみ対象へ反映する。

### 反映

- `invert` が `false`: 内で `SetActive(true)`、外で `SetActive(false)`。
- `invert` が `true`: 内で `SetActive(false)`、外で `SetActive(true)`。
- `targets` の `null` 要素は無視する。
- `targets` の要素数は `Start` 時点の値を使う。

### 同期

- 同期モード: `[UdonBehaviourSyncMode(BehaviourSyncMode.NoVariableSync)]`
- 同期変数なし。判定・反映はプレイヤーごとにローカルで行う。

### 既知の干渉

- 対象の `SetActive` を直接呼ぶため、同じ GameObject を他のコンポーネント（`MashiroGlobalOnOffSwitch` 等）でも操作すると、内外が変化した時点で互いの状態を上書きする。

## Inspector

### MashiroLocalAreaActivator

| フィールド | 型 | 既定値 | 必須 | 内容 |
| --- | --- | --- | --- | --- |
| `area` | `Collider` | なし | ○ | エリア判定に使う Collider |
| `targets` | `GameObject[]` | 空 | ○ | 内外に応じて有効・無効を切り替える GameObject |
| `invert` | `bool` | `false` | — | `true` で内外を反転する（外で有効、内で無効） |
| `pollInterval` | `float` | `0.1` | — | 判定間隔（秒）。`0` 以下で毎フレーム |

## API リファレンス

### MashiroLocalAreaActivator

public 関数はない。配線は不要。

## ライセンス

MIT License（`MashiroTheater-Utils` 同梱の `LICENSE.md` を参照）。

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
