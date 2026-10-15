# Mashiro Player Follower

指定したプレイヤーの方向・位置へオブジェクトを追従させるコンポーネント集。次の 3 系統を含む。

- `MashiroPlayerFollower`: UI の一覧から選択したプレイヤーへ対象オブジェクトを向ける。選択状態を全員で同期する。
- `MashiroPlayerNameFollower`: DisplayName が一致するプレイヤーへ対象オブジェクトを向ける。ローカル処理。
- `MashiroPlayerNameLookTarget`: DisplayName が一致するプレイヤーの位置へ自身を移動する。ローカル処理。

## 構成

| ファイル | 役割 |
| --- | --- |
| `MashiroPlayerFollower.cs` / `.asset` | 候補一覧の管理・選択状態の同期・対象オブジェクトの回転 |
| `MashiroPlayerFollowerButtonHandler.cs` / `.asset` | 候補一覧の 1 ボタン分（プレイヤー名表示・選択色・押下処理） |
| `MashiroPlayerNameFollower.cs` / `.asset` | DisplayName 指定で対象オブジェクトを回転させる |
| `MashiroPlayerNameLookTarget.cs` / `.asset` | DisplayName 指定で自身の位置を移動させる |
| `PlayerFollowerBoard.prefab` | `MashiroPlayerFollower` と UI（登録ボタン・候補一覧のスクロールビュー・対象名表示）を組み込んだボード |
| `PlayerButton.prefab` | 候補一覧に生成されるボタン（`MashiroPlayerFollowerButtonHandler` 付き） |

## 依存

- パッケージ `MashiroTheater-Utils`（VPM `com.mashirotheater.utils`）に同梱。
- `MashiroPlayerFollower` / `MashiroPlayerFollowerButtonHandler` は TextMeshPro（`TextMeshProUGUI`）を参照する。
- `PlayerFollowerBoard.prefab` は `_Common/Fonts/ZenKakuGothicNew-Regular SDF.asset` を参照する。

## 仕様

### MashiroPlayerFollower

- 同期方式: `BehaviourSyncMode.Manual`。
- 同期変数:

  | 変数 | 型 | 初期値 | 内容 |
  | --- | --- | --- | --- |
  | `registeredPlayerIds` | `int[]` | 要素数 32 | 登録済みプレイヤーの playerId |
  | `registeredPlayerCount` | `int` | `0` | 登録数 |
  | `selectedPlayerId` | `int` | `-1` | 選択中プレイヤーの playerId（`-1` は未選択） |

- 登録上限は 32 人（配列長）。上限超過の判定は行わない。
- `RegisterSelf()` は、ローカルプレイヤーが登録済みなら何もしない。未登録なら所有権を取得して末尾へ追加し、同期を要求する。
- `TogglePlayerSelection()` は所有権を取得し、選択中のプレイヤーなら選択解除、それ以外ならそのプレイヤーを選択して同期を要求する。
- `targetObject` の向き: 毎フレーム（`Update`）、`selectedPlayerId` のプレイヤーの頭位置（Head トラッキング）と足元位置（`GetPosition()`）を `0.1` で線形補間した点へ `Quaternion.LookRotation` で向ける。位置は変更しない。
- 補間比率 `0.1` は固定値（Inspector から変更不可）。
- `Start` 時の `targetObject` のワールド回転を元の回転として保持する。選択解除時・選択中プレイヤー退出時は、その処理を実行したクライアント（オーナー）でのみ元の回転へ戻す。同期受信（`OnDeserialization`）では回転を戻さない。
- 同期受信時は候補ボタンを再生成し、選択表示を更新する。
- 候補ボタンの再生成時は、`buttonParent` の子をすべて `Destroy` してから登録順に `playerButtonPrefab` を `VRCInstantiate` する。
- プレイヤー退出時、オーナーは退出者を登録一覧から除き、同期を要求する。
- 所有権を受け取ったクライアントは、無効になったプレイヤーを登録一覧から除き、同期を要求する。
- プレイヤー参加時、オーナーは同期を要求する。
- `targetObjectNameText` には `Start` 時に 1 回だけ `Object : <targetObject の名前>` を設定する（`targetObject` 未設定時は設定しない）。

### MashiroPlayerFollowerButtonHandler

- `[UdonBehaviourSyncMode]` の指定なし。同期変数なし。
- `Initialize()` でプレイヤーの `displayName` を `buttonText` に表示し、非選択色にする。
- `SetSelected()` は `buttonImage.color` を `selectedColor` / `normalColor` に設定する。
- `PlayerButton.prefab` の `Button.OnClick` は `SendCustomEvent("OnButtonClick")` に配線済み。

### MashiroPlayerNameFollower

- `[UdonBehaviourSyncMode]` の指定なし。同期変数なし。各クライアントがローカルで同じ計算を行う。
- 対象プレイヤーの判定: `displayName` と `targetPlayerName` の完全一致。最初に一致したプレイヤーを対象とする。
- 対象探索のタイミング: `Start`、`OnEnable`（`Start` 後）、`_SetTargetPlayerName()` 呼び出し時、対象ロスト時。
- `OnPlayerJoined`: 参加者の名前が一致し、追従中の対象がいない（または無効・名前不一致）なら参加者を対象にする。
- 毎フレーム（`Update`）、頭位置と足元位置を `targetPositionRatio`（`Clamp01`）で補間した点へ `targetObject` を向ける。方向ベクトルの長さの二乗が `1e-6` 以下なら回転しない。
- `Start` 時の `targetObject` のワールド回転を元の回転として保持し、次の場合に元の回転へ戻す。
  - 対象が無効になったとき（直後に再探索する）。
  - 対象プレイヤーの退出時。
  - コンポーネントの無効化時（`OnDisable`）。
  - `_ResetRotation()` 呼び出し時。
- `targetObject` 未設定時は何もしない。

### MashiroPlayerNameLookTarget

- `[UdonBehaviourSyncMode]` の指定なし。同期変数なし。各クライアントがローカルで同じ計算を行う。
- 移動するのはこのコンポーネントが付いた GameObject 自身の `transform.position`。
- 対象プレイヤーの判定: `displayName` と `targetPlayerName` の完全一致。最初に一致したプレイヤーを対象とする。
- 対象探索のタイミング: `Start`、`_SetTargetPlayerName()` 呼び出し時。`OnPlayerJoined` では対象がいない場合のみ参加者を判定する。対象プレイヤーの退出で対象を解除する。
- 毎フレーム（`LateUpdate`）、目標点を次の順で決める。
  1. 対象が有効: 頭位置と足元位置を `targetPositionRatio`（`Clamp01`）で補間し、`worldOffset` を加えた点。
  2. 対象が無効で `fallbackPoint` 設定あり: `fallbackPoint.position`。
  3. それ以外: 現在位置。
- 平滑化: 前フレームの位置から目標点へ `smoothAlpha`（`Clamp01`）で `Vector3.Lerp` する。`maxStepPerFrame > 0` のとき 1 フレームの移動距離をその値で制限する。

## Inspector

### MashiroPlayerFollower

| フィールド | 型 | 既定値 | 必須 | 内容 |
| --- | --- | --- | --- | --- |
| `targetObject` | `GameObject` | なし | ○ | 選択プレイヤーへ向けるオブジェクト。未設定時は回転しない |
| `playerButtonPrefab` | `GameObject` | なし | ○ | 候補一覧に生成するボタン。`MashiroPlayerFollowerButtonHandler` を持つこと |
| `buttonParent` | `Transform` | なし | ○ | ボタンの生成先。子はすべて再生成時に破棄される |
| `targetObjectNameText` | `TextMeshProUGUI` | なし | – | `targetObject` の名前の表示先 |

`PlayerFollowerBoard.prefab` では `playerButtonPrefab`（`PlayerButton.prefab`）・`buttonParent`・`targetObjectNameText` と、登録ボタンの `Button.OnClick`（`RegisterSelf`）が設定済み。`targetObject` は未設定。

### MashiroPlayerFollowerButtonHandler

| フィールド | 型 | 既定値 | 必須 | 内容 |
| --- | --- | --- | --- | --- |
| `buttonText` | `TextMeshProUGUI` | なし | – | プレイヤー名の表示先 |
| `buttonImage` | `Image` | なし | – | 選択色の適用先 |
| `normalColor` | `Color` | `(0, 0, 0, 1)` | – | 非選択時の背景色 |
| `selectedColor` | `Color` | `(0.91, 0.35, 0, 1)` | – | 選択時の背景色 |

### MashiroPlayerNameFollower

| フィールド | 型 | 既定値 | 必須 | 内容 |
| --- | --- | --- | --- | --- |
| `targetObject` | `GameObject` | なし | ○ | プレイヤーへ向けるオブジェクト |
| `targetPlayerName` | `string` | 空 | ○ | 対象プレイヤーの DisplayName（完全一致） |
| `targetPositionRatio` | `float`（`[Range(0, 1)]`） | `0.02` | – | 狙う高さ。`0` = 頭、`1` = 足元 |

### MashiroPlayerNameLookTarget

| フィールド | 型 | 既定値 | 必須 | 内容 |
| --- | --- | --- | --- | --- |
| `targetPlayerName` | `string` | `"PlayerName"` | ○ | 対象プレイヤーの DisplayName（完全一致） |
| `targetPositionRatio` | `float`（`[Range(0, 1)]`） | `0.35` | – | 追従する高さ。`0` = 頭、`1` = 足元 |
| `worldOffset` | `Vector3` | `(0, 0.1, 0)` | – | 補間後に加えるワールドオフセット（m） |
| `smoothAlpha` | `float`（`[Range(0, 1)]`） | `0.25` | – | 平滑化係数。`0` = 移動しない、`1` = 即時 |
| `maxStepPerFrame` | `float` | `0` | – | 1 フレームの最大移動距離（m）。`0` = 無制限 |
| `fallbackPoint` | `Transform` | なし | – | 対象不在時の目標点。未設定時は現在位置を維持 |

## API リファレンス

### MashiroPlayerFollower

UI へ手配線するもの:

| シグネチャ | 用途 | 呼び出し種別 |
| --- | --- | --- |
| `void RegisterSelf()` | ローカルプレイヤーを候補一覧に登録する | `Button.OnClick` から配線（`SendCustomEvent`） |

内部連携用（配線不要）:

| シグネチャ | 用途 | 呼び出し種別 |
| --- | --- | --- |
| `void TogglePlayerSelection(VRCPlayerApi player)` | 指定プレイヤーの選択／選択解除を切り替えて同期する | `MashiroPlayerFollowerButtonHandler` が呼ぶ |
| `void OnPlayerJoined(VRCPlayerApi player)` | オーナーが同期を要求する | VRChat が呼ぶ（内部専用） |
| `void OnPlayerLeft(VRCPlayerApi player)` | オーナーが退出者を一覧から除く | VRChat が呼ぶ（内部専用） |
| `void OnDeserialization()` | 候補ボタンを再生成し選択表示を更新する | VRChat が呼ぶ（内部専用） |
| `void OnOwnershipTransferred(VRCPlayerApi newOwner)` | 新オーナーが無効なプレイヤーを一覧から除く | VRChat が呼ぶ（内部専用） |

### MashiroPlayerFollowerButtonHandler

UI へ手配線するもの:

| シグネチャ | 用途 | 呼び出し種別 |
| --- | --- | --- |
| `void OnButtonClick()` | 担当プレイヤーの選択を切り替える | `Button.OnClick` から配線（`PlayerButton.prefab` で配線済み） |

内部連携用（配線不要）:

| シグネチャ | 用途 | 呼び出し種別 |
| --- | --- | --- |
| `void Initialize(MashiroPlayerFollower follower, VRCPlayerApi player)` | 担当プレイヤーと親コンポーネントを設定する | `MashiroPlayerFollower` が呼ぶ |
| `void SetSelected(bool isSelected)` | 背景色を選択色／非選択色に切り替える | `MashiroPlayerFollower` が呼ぶ |
| `int PlayerId { get; }` | 担当プレイヤーの playerId。未設定時は `-1` | `MashiroPlayerFollower` が参照する |

### MashiroPlayerNameFollower

内部連携用（配線不要）:

| シグネチャ | 用途 | 呼び出し種別 |
| --- | --- | --- |
| `void _SetTargetPlayerName(string newName)` | 対象の DisplayName を変更して再探索する | 他 Udon から呼ぶ |
| `void _ResetRotation()` | 元の回転へ戻し、対象を解除する | 他 Udon から呼ぶ |
| `void OnPlayerJoined(VRCPlayerApi player)` | 参加者が対象名なら対象にする | VRChat が呼ぶ（内部専用） |
| `void OnPlayerLeft(VRCPlayerApi player)` | 対象の退出時に元の回転へ戻す | VRChat が呼ぶ（内部専用） |

### MashiroPlayerNameLookTarget

内部連携用（配線不要）:

| シグネチャ | 用途 | 呼び出し種別 |
| --- | --- | --- |
| `void _SetTargetPlayerName(string newName)` | 対象の DisplayName を変更して再探索する | 他 Udon から呼ぶ |
| `void OnPlayerJoined(VRCPlayerApi player)` | 対象がいなければ参加者を判定する | VRChat が呼ぶ（内部専用） |
| `void OnPlayerLeft(VRCPlayerApi player)` | 対象の退出時に対象を解除する | VRChat が呼ぶ（内部専用） |

## ライセンス

MIT License（リポジトリルートの `LICENSE.md` を参照）。

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
