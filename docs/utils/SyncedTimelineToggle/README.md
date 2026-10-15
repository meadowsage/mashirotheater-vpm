# SyncedTimelineToggle

`PlayableDirector` の再生をトグル操作で制御し、ON/OFF 状態を全プレイヤーで同期するコンポーネント。ON でタイムラインの先頭から中央まで再生して停止し、OFF で中央から末尾まで再生する。`MashiroTimelineToggleExclusiveGroup` で複数のトグルを排他（同時に ON は 1 つ）にできる。

## 構成

| ファイル | 役割 |
| --- | --- |
| `MashiroTimelineToggle.cs` / `.asset` | 1 本のタイムラインの ON/OFF 再生・ボタン色・同期 |
| `MashiroTimelineToggleExclusiveGroup.cs` / `.asset` | 子階層のトグルの排他制御・同期 |

## 依存

- パッケージ `MashiroTheater-Utils`（VPM `com.mashirotheater.utils`）に同梱。
- `MashiroTimelineToggle` は `PlayableDirector` の参照を必要とする。
- ボタン色の適用先は同じ GameObject の `UnityEngine.UI.Button`、ラベルの表示先は `TextMeshProUGUI`（いずれも任意）。

## 仕様

### タイムラインの区間

- `Start` 時に `PlayableDirector.duration / 2` を中央時刻とし、`time = 0` にして `Stop()` する。
- ON: `time = 0` から再生し、`time >= 中央時刻` になったフレームで `time = 中央時刻` に設定して `Evaluate()` し、`Pause()` する。
- OFF: `time = 中央時刻` から再生し、`time >= 中央時刻 × 2` または `time == 0` になったフレームで `Stop()` する。

### MashiroTimelineToggle

- 同期方式: `BehaviourSyncMode.Manual`。
- 同期変数: `state`（`bool`、初期値 `false`、`FieldChangeCallback` → `State`）。同期受信で値が変わると `SetState()` と同じ処理を行う。
- 単独使用時（グループ未所属）の操作:
  - 再生中（ON/OFF の遷移中）は操作を無視する。
  - 操作したプレイヤーが所有権を取得し、`state` を反転して同期を要求する。
- グループ所属時の操作: グループの `OnToggleClicked()` へ委譲する。再生中の操作も受け付ける。トグル自身の `state` は送信しない。
- 操作の入力:
  - `OnButtonClick()`（`Button.OnClick` からの配線用）。
  - `Interact()`（VRChat の Use 操作）。同じ GameObject に `Button` がある場合は何もしない。
- ボタン色: 同じ GameObject の `Button.colors` を書き換える。`Button` がない場合は何もしない。
  - `normalColor` / `selectedColor` に指定色を設定する。
  - `highlightedColor` = 指定色と白を `0.1` で補間した色、`pressedColor` = 指定色と黒を `0.1` で補間した色。
  - ON 遷移中は `inactiveColor` → `activeColor`、OFF 遷移中は `activeColor` → `inactiveColor` を再生位置に応じて補間する。
  - `Start` 時は `inactiveColor`（`timeline` 設定時のみ）。
- ラベル: `useGameObjectNameForLabel` が `true` のとき、`Start` 時に `GetComponentInChildren<TextMeshProUGUI>(true)` で得たテキストへ GameObject 名を設定する。
- `timeline` 未設定で `SetState()` が実行されると例外になる（null チェックなし）。
- `AddComponentMenu`: `MashiroTheater/Mashiro Timeline Toggle`。

### MashiroTimelineToggleExclusiveGroup

- 同期方式: `BehaviourSyncMode.Manual`。
- 同期変数: `activeIndex`（`int`、初期値 `-1`、`FieldChangeCallback` → `ActiveIndex`）。ON のトグルの番号。`-1` は全 OFF。
- 所属トグル: `Start` 時に `GetComponentsInChildren<MashiroTimelineToggle>(true)`（非アクティブを含む）で収集し、各トグルに `InitializeWithGroup(this)` を呼ぶ。番号はこの取得順。
- `OnToggleClicked()`: 所有権を取得し、押されたトグルが ON 中なら `activeIndex = -1`、それ以外なら押されたトグルの番号を設定して同期を要求する。
- `ActiveIndex` 設定時の動作:
  - 現在 ON のトグルがある場合: そのトグルを `SetState(false)` し、新しい番号が有効なら `crossFadeDelay` 秒後（`SendCustomEventDelayedSeconds`）に新しいトグルを `SetState(true)` する。
  - 現在 ON のトグルがない場合: 新しい番号が有効なら即時に `SetState(true)` する。
- `Start` 時に `ActiveIndex = activeIndex` を実行し、同期を要求する。
- `AddComponentMenu`: `MashiroTheater/Mashiro Timeline Toggle Exclusive Group`。

## Inspector

### MashiroTimelineToggle

| フィールド | 型 | 既定値 | 必須 | 内容 |
| --- | --- | --- | --- | --- |
| `timeline` | `PlayableDirector` | なし | ○ | 制御するタイムライン |
| `activeColor` | `Color` | `(0.69, 0.239, 0.016, 1)` | – | ON 時のボタン色 |
| `inactiveColor` | `Color` | `(0, 0, 0, 1)` | – | OFF 時のボタン色 |
| `useGameObjectNameForLabel` | `bool` | `true` | – | 自身または子の `TextMeshProUGUI` に GameObject 名を表示する |

### MashiroTimelineToggleExclusiveGroup

| フィールド | 型 | 既定値 | 必須 | 内容 |
| --- | --- | --- | --- | --- |
| `crossFadeDelay` | `float` | `0.1` | – | ON のトグルを OFF にしてから新しいトグルを ON にするまでの秒数 |

`toggles`（`MashiroTimelineToggle[]`）は `[HideInInspector]`。`Start` 時に子階層から収集した値で上書きされる。

## API リファレンス

### MashiroTimelineToggle

UI へ手配線するもの:

| シグネチャ | 用途 | 呼び出し種別 |
| --- | --- | --- |
| `void OnButtonClick()` | ON/OFF を切り替える（グループ所属時はグループへ委譲） | `Button.OnClick` から配線 |

内部連携用（配線不要）:

| シグネチャ | 用途 | 呼び出し種別 |
| --- | --- | --- |
| `void Interact()` | `OnButtonClick()` と同じ。`Button` がある場合は何もしない | VRChat が呼ぶ（Use 操作） |
| `void SetState(bool value)` | `state` を設定し、ON/OFF の区間を再生する。同期は要求しない | グループ・他 Udon が呼ぶ |
| `bool State { get; set; }` | `state` の取得。設定は `SetState(value)` と同じ | 同期変数の `FieldChangeCallback`（内部専用） |
| `void InitializeWithGroup(MashiroTimelineToggleExclusiveGroup exclusiveGroup)` | 所属グループを設定する | グループが `Start` 時に呼ぶ |

### MashiroTimelineToggleExclusiveGroup

内部連携用（配線不要）:

| シグネチャ | 用途 | 呼び出し種別 |
| --- | --- | --- |
| `void OnToggleClicked(MashiroTimelineToggle toggle)` | 押されたトグルに応じて `activeIndex` を更新し同期する | 所属トグルが呼ぶ |
| `int ActiveIndex { get; set; }` | `activeIndex` の取得。設定時に排他切替を実行する | 同期変数の `FieldChangeCallback`（内部専用） |
| `void _DelayedActivate()` | `activeIndex` のトグルを ON にする | `SendCustomEventDelayedSeconds` から呼ばれる（内部専用） |

## ライセンス

MIT License（リポジトリルートの `LICENSE.md` を参照）。

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
