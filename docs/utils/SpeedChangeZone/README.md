# Mashiro Speed Change Zone

指定した BoxCollider の範囲内にローカルプレイヤーがいる間、移動速度（Walk / Run / Strafe）に倍率を掛けるコンポーネント。

## 構成

| ファイル | 役割 |
| --- | --- |
| `MashiroSpeedChangeZone.cs` / `.asset` | エリア判定と移動速度の設定 |
| `SpeedChangeZone.prefab` | `MashiroSpeedChangeZone`、Trigger の BoxCollider（サイズ `(1, 1, 1)`）、無効化した MeshRenderer を持つ GameObject |

## 依存

- パッケージ `MashiroTheater-Utils`（VPM `com.mashirotheater.utils`）に同梱。

## 仕様

- 同期方式: `BehaviourSyncMode.NoVariableSync`。同期変数なし。ローカルプレイヤーにのみ作用する。
- 基準速度: `Start` 時に `GetWalkSpeed()` / `GetRunSpeed()` / `GetStrafeSpeed()` で取得した値。以後は更新しない。
- 判定タイミング: `Start` 時に 1 回、以後 `updateInterval` 秒ごと（`Update` で経過時間を加算）。
- 判定位置: ローカルプレイヤーの `GetPosition()`（足元）。
- 判定方式: 各 BoxCollider の `ClosestPoint()` と判定位置の距離が `0.02` m 以下ならエリア内とする。BoxCollider の回転を反映する。
- 判定から除外する BoxCollider: `null`、`enabled == false`、GameObject が `activeInHierarchy == false` のもの。
- 目標速度: いずれかのエリア内なら「基準速度 × `speedRatio`」、エリア外なら基準速度。Walk / Run / Strafe の 3 種に同じ倍率を掛ける。
- 速度の設定: 現在値と目標値の差が `applyEpsilon` を超える種別だけ `SetWalkSpeed()` / `SetRunSpeed()` / `SetStrafeSpeed()` を呼ぶ。
- エリア内外にかかわらず毎判定で目標速度へ設定するため、他のコンポーネントが変更した移動速度は次の判定で上書きされる。
- `OnDisable` / `OnDestroy` 時は基準速度へ戻す（差が `applyEpsilon` を超える種別のみ）。
- `speedZones` が未設定（空）のときは常にエリア外として扱う。

## Inspector

| フィールド | 型 | 既定値 | 必須 | 内容 |
| --- | --- | --- | --- | --- |
| `speedZones` | `BoxCollider[]` | 空 | ○ | 倍率を適用するエリア |
| `updateInterval` | `float` | `1.0` | – | 判定間隔（秒） |
| `speedRatio` | `float`（`[Range(0.05, 10)]`） | `0.44` | – | エリア内の速度倍率 |
| `applyEpsilon` | `float` | `0.01` | – | 現在値と目標値の差がこの値を超えたときだけ速度を設定する |

`SpeedChangeZone.prefab` では `speedZones` は未設定。

## API リファレンス

### MashiroSpeedChangeZone

public メソッド・プロパティはない。UI への配線は不要。

## ライセンス

MIT License（リポジトリルートの `LICENSE.md` を参照）。

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
