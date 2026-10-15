# OnOffSwitches

GameObject の有効・無効をボタン押下・Interact・長押しで切り替えるスイッチ群。全プレイヤー同期版、ローカル版、複数ボタンで 1 つの同期状態を共有する版、3D オブジェクトの長押しで切り替える同期版を含む。

## 構成

| ファイル | 役割 |
| --- | --- |
| `MashiroGlobalOnOffSwitch.cs` | 1 ボタンで対象を切り替える。状態を全プレイヤーで同期する |
| `MashiroGlobalOnOffSwitch.asset` | `MashiroGlobalOnOffSwitch` の UdonSharp ProgramAsset |
| `MashiroLocalOnOffSwitch.cs` | 1 ボタンで対象を切り替える。状態はローカルのみ |
| `MashiroLocalOnOffSwitch.asset` | `MashiroLocalOnOffSwitch` の UdonSharp ProgramAsset |
| `MashiroMultiGlobalOnOff.cs` | 対象と同期状態を保持するコントローラ。複数の `MashiroMultiGlobalOnOffButton` から操作される |
| `MashiroMultiGlobalOnOff.asset` | `MashiroMultiGlobalOnOff` の UdonSharp ProgramAsset |
| `MashiroMultiGlobalOnOffButton.cs` | 押下を `MashiroMultiGlobalOnOff` へ転送し、ボタン色を状態に合わせる |
| `MashiroMultiGlobalOnOffButton.asset` | `MashiroMultiGlobalOnOffButton` の UdonSharp ProgramAsset |
| `MashiroGlobalHoldOnOffSwitch.cs` | 3D オブジェクトの長押しで対象を切り替える。状態を全プレイヤーで同期する |
| `MashiroGlobalHoldOnOffSwitch.asset` | `MashiroGlobalHoldOnOffSwitch` の UdonSharp ProgramAsset |

## 依存

- パッケージ: `MashiroTheater-Utils`（VPM `com.mashirotheater.utils`）
- ボタン色の反映には、スイッチ（`MashiroMultiGlobalOnOffButton` を含む）と同じ GameObject の `UnityEngine.UI.Button` が必要。
- ラベルの反映には、自身または子の `TextMeshProUGUI`（TextMeshPro）が必要。
- `Interact()` による操作には、スイッチと同じ GameObject の Collider が必要。
- `MashiroGlobalHoldOnOffSwitch` の色表示には、自身または子の `Renderer` が必要（未取得時は色を変更しない）。Pickup として使う場合は同じ GameObject の `VRC_Pickup` が必要。

## 仕様

### 共通（`MashiroGlobalOnOffSwitch` / `MashiroLocalOnOffSwitch` / `MashiroMultiGlobalOnOff` / `MashiroMultiGlobalOnOffButton`）

`ボタン色` / `ラベル` の節も同じ 4 コンポーネントが対象。

| 項目 | 内容 |
| --- | --- |
| 対象の切替 | `target.SetActive(状態)`。`target` 未設定時は何もしない |
| ボタン参照 | 自身の `GetComponent<Button>()` で取得する。未取得時は色を変更しない |
| ラベル参照 | `GetComponentInChildren<TextMeshProUGUI>()` で取得する（自身を含む） |
| 入力 | `OnButtonClick()`（`Button.OnClick` から配線）と `Interact()`（VRChat の Use 操作）の両方で同じ処理を行う |

### ボタン色

`ColorBlock` の各項目を次の値にする。`disabledColor` は変更しない。

| 項目 | 値 |
| --- | --- |
| `normalColor` | 基準色 |
| `selectedColor` | 基準色 |
| `highlightedColor` | `Color.Lerp(基準色, Color.white, 0.1f)` |
| `pressedColor` | `Color.Lerp(基準色, Color.black, 0.1f)` |

基準色は ON 時と OFF 時でコンポーネントごとのフィールド（下記 Inspector）を使う。`MashiroLocalOnOffSwitch` は `updateButtonColor` が `false` のとき色を変更しない。

### ラベル

| コンポーネント | 挙動 |
| --- | --- |
| `MashiroGlobalOnOffSwitch` / `MashiroMultiGlobalOnOffButton` | `useGameObjectNameForLabel` が `true` のとき、参照取得時（`Start`。`MashiroMultiGlobalOnOffButton` は `Start` 前に `ApplyVisual` が呼ばれた場合はその時点）にラベルへ `gameObject.name` を設定する。状態による変更はしない |
| `MashiroLocalOnOffSwitch` | `useCustomLabels` が `true` のとき、ON で `enabledLabel`、OFF で `disabledLabel` を設定する。`false` のときは `Start` 時点のラベル文字列を ON / OFF 共通で使う |

### MashiroGlobalOnOffSwitch

- 同期モード: `[UdonBehaviourSyncMode(BehaviourSyncMode.Manual)]`
- 同期変数: `state`（`bool`、`[FieldChangeCallback(nameof(State))]`）
- `Start`:
  - マスター: `State` に `initialState` を設定して反映し、`RequestSerialization()` する。
  - マスター以外: `state` に `initialState` を代入して反映する。
- `OnButtonClick()` / `Interact()`: 操作者がオーナーでなければ `Networking.SetOwner` でオーナーを取得し、`State` を反転して反映・`RequestSerialization()` する。
- 受信時: `FieldChangeCallback` 経由で反映する。`OnDeserialization()` でも `Start` 完了後であれば反映する。
- `OnPlayerJoined`: マスターが `RequestSerialization()` する。
- 操作できるプレイヤーの制限はない。
- 同じ `target` を複数の `MashiroGlobalOnOffSwitch` で操作した場合、各スイッチは独立した同期変数を持ち、スイッチ間で状態は連動しない。

### MashiroLocalOnOffSwitch

- `[UdonSynced]` フィールドを持たず、`[UdonBehaviourSyncMode]` も指定していない。状態はローカルのみ。
- `Start` で `startEnabled` を状態として反映する（対象・ボタン色・ラベル）。
- `Toggle()` / `OnButtonClick()` / `Interact()` は状態を反転して反映する。
- `SetState(bool)` は現在の状態と異なる場合のみ反映する。

### MashiroMultiGlobalOnOff / MashiroMultiGlobalOnOffButton

- 同期状態はコントローラ（`MashiroMultiGlobalOnOff`）の `state` 1 つのみ。ボタンは同期状態を持たない。
- `MashiroMultiGlobalOnOff`:
  - 同期モード: `[UdonBehaviourSyncMode(BehaviourSyncMode.Manual)]`
  - 同期変数: `state`（`bool`、`[FieldChangeCallback(nameof(State))]`）
  - `Start`: マスターは `State` に `initialState` を設定して反映し、`RequestSerialization()` する。マスター以外は `state` に `initialState` を代入して反映する。
  - `Toggle()`: 操作者がオーナーでなければ `Networking.SetOwner` でオーナーを取得し、`State` を反転して反映・`RequestSerialization()` する。
  - 受信時: `FieldChangeCallback` 経由で反映する。`OnDeserialization()` でも `Start` 完了後であれば反映する。
  - `OnPlayerJoined`: マスターが `RequestSerialization()` する。
  - 反映時は `target.SetActive` と、`buttons` に登録された各ボタンの `ApplyVisual(bool)` を呼ぶ。`buttons` に未登録のボタンには状態変化を通知しない。
- `MashiroMultiGlobalOnOffButton`:
  - 同期モード: `[UdonBehaviourSyncMode(BehaviourSyncMode.NoVariableSync)]`
  - `OnButtonClick()` / `Interact()`: `controller.Toggle()` を呼ぶ。`controller` 未設定時は何もしない。
  - `Start` で `controller.GetState()` を取得してボタン色に反映する。
  - `ApplyVisual(bool)` が `Start` より前に呼ばれた場合は、その時点でボタン・ラベルの参照を取得する。

### MashiroGlobalHoldOnOffSwitch

- 同期モード: `[UdonBehaviourSyncMode(BehaviourSyncMode.Continuous)]`
- 同期変数: `state`（`bool`、`[UdonSynced]`）
- 入力:

| イベント | 動作 |
| --- | --- |
| `Interact()` | 長押しの計測を開始する |
| `InputUse(false, …)`（Use 入力の解放） | 長押しを中断する |
| `OnPickupUseDown()` | 長押しの計測を開始する |
| `OnPickupUseUp()` / `OnDrop()` | 長押しを中断する |

- 計測中は 1 フレームごとに `_HoldTick` を実行する（`SendCustomEventDelayedFrames(…, 1)`）。計測していない間は実行しない。
- 進捗: `Mathf.Clamp01((Time.time - 開始時刻) / Mathf.Max(0.1f, holdSeconds))`
- 進捗が 1 に達すると計測を終了して状態を反転する。1 回の押下で反転は 1 回。
- 反転時、ローカルプレイヤーがオーナーでなければ `Networking.SetOwner` でオーナーになる。
- `Start`: オーナー、または同期を未受信の非オーナーは `state = initialState` とし、状態を反映する。
- `OnDeserialization`: 初回受信時、または受信値が反映済みの状態と異なるときだけ状態を反映する。
- 状態の反映: `target.SetActive(state)`（`target` 未設定時は省略）。計測中でなければ色も更新する。
- 色: `Renderer`（自身の `GetComponent<Renderer>()`、なければ `GetComponentInChildren<Renderer>()`）に `MaterialPropertyBlock` で `_Color` を設定する。

| 状態 | `_Color` |
| --- | --- |
| OFF | `(1, 1, 1, 1)` |
| ON | `(0.91, 0.35, 0, 1)` |
| 計測中 | `Color.Lerp(現在の状態の色, 反転後の色, Mathf.Lerp(0.2, 1, 進捗))` |
| 中断時 | 現在の状態の色に戻す |

- ON / OFF の色はコード内の固定値で、Inspector からは変更できない。

## Inspector

### MashiroGlobalOnOffSwitch

| フィールド | 型 | 既定値 | 必須 | 内容 |
| --- | --- | --- | --- | --- |
| `target` | `GameObject` | なし | ○ | 有効・無効を切り替える対象 |
| `onColor` | `Color` | `(0.69, 0.239, 0.016, 1)` | — | ON 時のボタン基準色 |
| `offColor` | `Color` | `Color.black`（`(0, 0, 0, 1)`） | — | OFF 時のボタン基準色 |
| `initialState` | `bool` | `false` | — | 開始時の状態 |
| `useGameObjectNameForLabel` | `bool` | `true` | — | `true` でラベルに GameObject 名を設定する |

### MashiroLocalOnOffSwitch

| フィールド | 型 | 既定値 | 必須 | 内容 |
| --- | --- | --- | --- | --- |
| `target` | `GameObject` | なし | ○ | 有効・無効を切り替える対象 |
| `startEnabled` | `bool` | `false` | — | 開始時の状態 |
| `useCustomLabels` | `bool` | `false` | — | `true` でラベルを `enabledLabel` / `disabledLabel` で切り替える |
| `enabledLabel` | `string` | `"ON"` | — | ON 時のラベル |
| `disabledLabel` | `string` | `"OFF"` | — | OFF 時のラベル |
| `enabledColor` | `Color` | `(0.69, 0.239, 0.016, 1)` | — | ON 時のボタン基準色 |
| `disabledColor` | `Color` | `Color.black`（`(0, 0, 0, 1)`） | — | OFF 時のボタン基準色 |
| `updateButtonColor` | `bool` | `true` | — | `false` でボタン色を変更しない |

### MashiroMultiGlobalOnOff

| フィールド | 型 | 既定値 | 必須 | 内容 |
| --- | --- | --- | --- | --- |
| `target` | `GameObject` | なし | ○ | 有効・無効を切り替える対象 |
| `buttons` | `MashiroMultiGlobalOnOffButton[]` | 空 | — | 状態変化時に `ApplyVisual` を呼ぶボタン |
| `initialState` | `bool` | `false` | — | 開始時の状態 |

### MashiroMultiGlobalOnOffButton

| フィールド | 型 | 既定値 | 必須 | 内容 |
| --- | --- | --- | --- | --- |
| `controller` | `MashiroMultiGlobalOnOff` | なし | ○ | 状態を管理するコントローラ |
| `onColor` | `Color` | `(0.69, 0.239, 0.016, 1)` | — | ON 時のボタン基準色 |
| `offColor` | `Color` | `Color.black`（`(0, 0, 0, 1)`） | — | OFF 時のボタン基準色 |
| `useGameObjectNameForLabel` | `bool` | `true` | — | `true` でラベルに GameObject 名を設定する |

### MashiroGlobalHoldOnOffSwitch

Add Component メニュー: `MashiroTheater/Mashiro Global Hold On Off Switch`

| フィールド | 型 | 既定値 | 必須 | 内容 |
| --- | --- | --- | --- | --- |
| `target` | `GameObject` | なし | ○ | 有効・無効を切り替える対象 |
| `holdSeconds` | `float` | `1`（`[Min(0.1)]`） | — | 切り替わるまでに押し続ける秒数 |
| `initialState` | `bool` | `false` | — | 開始時の状態 |

## API リファレンス

### MashiroGlobalOnOffSwitch

#### UI へ手配線するもの

| シグネチャ | 用途 | 呼び出し種別 |
| --- | --- | --- |
| `void OnButtonClick()` | 状態を反転して同期する | `Button.OnClick` から配線 |

#### 内部連携用（配線不要）

| シグネチャ | 用途 | 呼び出し種別 |
| --- | --- | --- |
| `void Interact()` | `OnButtonClick()` を呼ぶ | VRChat コールバック（内部専用） |
| `bool State { get; private set; }` | 現在の状態。setter は対象とボタン色へ反映する | 取得は他の Udon から可。設定は内部専用 |
| `void OnDeserialization()` | 同期受信時に状態を反映する | VRChat コールバック（内部専用） |
| `void OnPlayerJoined(VRCPlayerApi player)` | マスターが同期を送信する | VRChat コールバック（内部専用） |

### MashiroLocalOnOffSwitch

#### UI へ手配線するもの

| シグネチャ | 用途 | 呼び出し種別 |
| --- | --- | --- |
| `void OnButtonClick()` | 状態を反転する | `Button.OnClick` から配線 |

#### 内部連携用（配線不要）

| シグネチャ | 用途 | 呼び出し種別 |
| --- | --- | --- |
| `void Interact()` | 状態を反転する | VRChat コールバック（内部専用） |
| `void Toggle()` | 状態を反転する | 他の Udon から呼ぶ |
| `void SetState(bool newState)` | 状態を設定する。現在と同じ値なら何もしない | 他の Udon から呼ぶ |
| `bool GetState()` | 現在の状態を返す | 他の Udon から呼ぶ |

### MashiroMultiGlobalOnOff

#### UI へ手配線するもの

なし。

#### 内部連携用（配線不要）

| シグネチャ | 用途 | 呼び出し種別 |
| --- | --- | --- |
| `void Toggle()` | 状態を反転して同期する | `MashiroMultiGlobalOnOffButton` が呼ぶ。他の Udon からも呼べる |
| `bool GetState()` | 現在の状態を返す | `MashiroMultiGlobalOnOffButton` が呼ぶ。他の Udon からも呼べる |
| `bool State { get; private set; }` | 現在の状態。setter は対象と全ボタンへ反映する | 取得は他の Udon から可。設定は内部専用 |
| `void OnDeserialization()` | 同期受信時に状態を反映する | VRChat コールバック（内部専用） |
| `void OnPlayerJoined(VRCPlayerApi player)` | マスターが同期を送信する | VRChat コールバック（内部専用） |

### MashiroMultiGlobalOnOffButton

#### UI へ手配線するもの

| シグネチャ | 用途 | 呼び出し種別 |
| --- | --- | --- |
| `void OnButtonClick()` | `controller.Toggle()` を呼ぶ | `Button.OnClick` から配線 |

#### 内部連携用（配線不要）

| シグネチャ | 用途 | 呼び出し種別 |
| --- | --- | --- |
| `void Interact()` | `OnButtonClick()` を呼ぶ | VRChat コールバック（内部専用） |
| `void ApplyVisual(bool isOn)` | ボタン色を状態に合わせる | `MashiroMultiGlobalOnOff` が呼ぶ |

### MashiroGlobalHoldOnOffSwitch

#### UI へ手配線するもの

なし。

#### 内部連携用（配線不要）

| シグネチャ | 用途 | 呼び出し種別 |
| --- | --- | --- |
| `void Interact()` | 長押しの計測を開始する | VRChat コールバック（内部専用） |
| `void InputUse(bool value, UdonInputEventArgs args)` | Use 入力の解放で長押しを中断する | VRChat コールバック（内部専用） |
| `void OnPickupUseDown()` | 長押しの計測を開始する | VRChat コールバック（内部専用） |
| `void OnPickupUseUp()` | 長押しを中断する | VRChat コールバック（内部専用） |
| `void OnDrop()` | 長押しを中断する | VRChat コールバック（内部専用） |
| `void OnDeserialization()` | 受信した状態を反映する | VRChat コールバック（内部専用） |
| `void _HoldTick()` | 長押しの進捗を 1 フレーム分進める | `SendCustomEventDelayedFrames` で自身が呼ぶ（内部専用） |

## ライセンス

MIT License（`MashiroTheater-Utils` 同梱の `LICENSE.md` を参照）。

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
