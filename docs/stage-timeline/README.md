# StageTimelineTools

公演進行を Unity Timeline で自動化するツールセット。Builder（エディタ拡張）が公演設定から TimelineAsset と AnimationClip を生成し、Manager（UdonSharp）が VRChat 上でその再生・シーン送り・配役登録・ワープを同期する。Builder の仕様は [Builder/README.md](Builder/README.md) に記載する。

- パッケージ名: `MashiroTheater-StageTimelineTools`（VPM: `com.mashirotheater.stagetimelinetools`）
- フォルダ名: `StageTimelineTools/`

## 構成

| パス | 内容 |
|---|---|
| `StageTimelineManager.prefab` | `StageTimelineManager`・操作パネル UI・`PlayableDirector`（子 GameObject `Timeline`。`timeline` に配線済み）・配役登録行 10 行・暗転用オブジェクト（`暗転Box`・`暗転中ガイド`）を含むプレハブ。Builder の初期設定でシーンに Manager が無い場合に配置される |
| `Manager/StageTimelineManager.cs` / `.asset` | 再生・シーン送り・配役登録・ワープ・タイムライン連動イベントを処理する UdonSharpBehaviour と ProgramAsset |
| `Manager/StageCharacterRegistrationRow.cs` / `.asset` | 配役登録 UI の 1 行分。登録・解除要求をネットワークイベントで送る UdonSharpBehaviour と ProgramAsset |
| `Prefabs/CharacterRegistrationRow.prefab` | 配役登録行のプレハブ |
| `Prefabs/CheckPointLIne.prefab` | プログレスバー上のチェックポイント線（`checkpointLinePrefab` 用） |
| `Prefabs/WarpPointMarker.prefab` | ワープ可視化マーカー（`StageTimelineConfig.warpMarkerPrefab` 用） |
| `Builder/` | エディタウィンドウ・タイムライン生成・`StageTimelineConfig`。詳細は [Builder/README.md](Builder/README.md) |
| `Example/` | サンプルシーン `StageTimelineToolsExample.unity`（`StageTimelineConfig` 設定済み）と、シーンが参照するアニメーション・音声・マテリアル・ライティングデータ・生成済みのタイムライン（`Example/Generated/`） |
| `LICENSE.md` / `VN3License_ja.pdf` | 利用規約 |

- `StageTimelineTools/Generated/` は配布対象外。Builder の既定出力先は `Assets/StageTimelineTools/Generated`。
- サンプルシーンの出力先（`generatedBaseFolder`）は `Assets/MashiroSmallTheater/StageTimelineTools/Example/Generated`。
- 名前空間: Manager は `MashiroTheater.StageTimeline`、Builder は `MashiroTheater.StageTimeline.Builder` / `MashiroTheater.StageTimeline.Builder.Editor`。

## 依存

| 依存 | 区分 | 用途 |
|---|---|---|
| VRChat SDK - Worlds 3.8.1 以上 / UdonSharp | 必須 | Manager 全体。`StageCharacterRegistrationRow` は引数付きの `[NetworkCallable]`（`VRC.SDK3.UdonNetworkCalling`）を使用する |
| TextMeshPro | 必須 | UI テキスト・ワープマーカー |
| Unity Timeline | 必須 | `PlayableDirector` / 生成される TimelineAsset |
| `MashiroTheater-Utils`（`com.mashirotheater.utils`） | 必須 | `MashiroLightGroup`（Builder の「LightGroup をスキャン」・照明プリセットのドラッグ＆ドロップ追加）、`MashiroButtonLockSystem`（`StageTimelineManager.prefab`）、共有フォント・アイコン・`BlackOut.mat` |
| Cinemachine | 任意 | カメラトラック生成。型はリフレクションで解決し、未導入時はカメラトラックの生成をスキップする |
| Post Processing Stack v2 | 任意 | Builder のポストプロセストラック生成。型はリフレクションで解決し、未導入時はポストプロセスの生成をスキップする |
| [NoribenBeamlightShader](https://booth.pm/ja/items/1637978)（シェーダー `Noriben/noribenBeamLight`） | 任意 | 照明フェードの対象に含めるビームライト。未導入時は `Light` コンポーネントのみが対象 |

- サンプルシーン（`Example/`）は Cinemachine（`CinemachineVirtualCamera` ×4・`CinemachineBrain`）と、Utils の `MashiroLightGroup` / `MashiroLightFixture` を使用する。
- サンプルシーンのビームライト（名前に `BeamLight` を含む GameObject）は、サンプル用に新規作成したマテリアル `Example/Materials/Example_BeamLight.mat` を使う。このマテリアルのシェーダー・テクスチャと、ビームのメッシュは [NoribenBeamlightShader](https://booth.pm/ja/items/1637978) のものを参照しており、本パッケージには同梱しない（未導入の環境では Missing になる）。

## 仕様

### 同期

- `StageTimelineManager` / `StageCharacterRegistrationRow` とも `BehaviourSyncMode.Manual`。
- `StageTimelineManager` の同期変数はすべて Owner が書き込み、`RequestSerialization()` で送る。

| 同期変数 | 型 | 初期値 | 内容 |
|---|---|---|---|
| `ownerName` | `string` | `""` | Owner の表示名 |
| `currentTime` | `double` | `0` | Owner 側の再生位置（秒） |
| `sceneNumber` | `int` | `1` | 現在の表示シーン番号（1 始まり） |
| `isPlaying` | `bool` | `false` | 再生中か |
| `nextCheckPointTime` | `double` | `0` | 次のチェックポイント時刻（秒） |
| `syncState` | `int` | `0` | 状態更新カウンタ。値が変わったときだけ受信側が再生状態を適用する |
| `scheduledBaseTimelineTime` | `double` | `0` | 再生開始時のタイムライン位置（秒） |
| `scheduledStartServerTime` | `double` | `0` | 再生開始予定のサーバー時刻（`Networking.GetServerTimeInSeconds()` 基準） |
| `playSessionId` | `int` | `0` | 再生セッション番号。再生開始・Reset・自動再生のたびに 1 増える |
| `serializedCharacterAssignments` | `string` | `""` | 配役登録。`キャラindex:playerId:表示名` を `\|` 区切りで連結（`%` `\|` `:` は `%25` `%7C` `%3A` にエスケープ） |
| `registryVersion` | `int` | `0` | 配役登録の更新カウンタ |
| `isTimelineOperationLocked` | `bool` | `false` | タイムライン操作ロック |
| `isRegistrationLocked` | `bool` | `false` | 配役登録ロック |

### 再生

- 再生開始時、Owner は `scheduledStartServerTime = サーバー時刻 + max(0.1, scheduledStartLeadTime)` を同期する。各クライアントはサーバー時刻がこの値に達した時点で、`scheduledBaseTimelineTime + 経過時間` からローカル再生を開始する。
- 受信側は `syncState` が変わったとき、`PlayableDirector` を一時停止して同期位置へシークし `Evaluate()` する。
- チェックポイント配列 `checkPointSeconds` は Builder が書き込む整数秒の配列で、先頭が `0`、以降が各シーングループの終了時刻。
- 再生中に次のチェックポイントへ達すると停止する。`enableCheckpointHardStop` が ON のときの停止判定時刻は `チェックポイント - checkpointSafetyMargin`、OFF のときはチェックポイント時刻。
- Owner は停止後、再生位置をチェックポイント時刻ちょうどに合わせて同期する。非 Owner は停止判定時刻で停止し、次の同期受信まで保持する。
- `Start()` 時、Owner は再生を停止状態にする。`syncState == 0` の場合は 2 つのロックを OFF にする。
- `autoPlayToFirstCheckpointOnInstanceStart` が ON のとき、`Start()` 時に次の条件をすべて満たせば時刻 0 から再生を開始し、最初のチェックポイントで停止する: ローカルが Owner / `playSessionId == 0` / プレイヤー数 1 / `checkPointSeconds` の要素数が 2 以上。

### 操作

| 操作 | 実行条件 | 動作 |
|---|---|---|
| Play（`PlayTimeline`） | Owner | 現在位置から新しい再生セッションを開始する |
| Pause（`PauseTimeline`） | Owner | 一時停止する |
| Next（`Next`） | Owner かつ操作ロック OFF | 一時停止し、次のシーンの開始チェックポイントへ移動する |
| Back（`Back`） | Owner かつ操作ロック OFF | 一時停止し、現在位置より前の直近チェックポイントへ移動する（チェックポイント上にいる場合は 1 つ前） |
| +1s / -1s（`Plus1s` / `Minus1s`） | Owner かつ操作ロック OFF | 一時停止し、1.0 秒進める / 戻す（-1s は 0 未満にしない） |
| Reset（`ResetTimeline`） | Owner かつ操作ロック OFF | 時刻 0・シーン 1 に戻し、新しい再生セッションで再生を開始する |
| Set Owner（`OnClickSetOwner`） | なし | ローカルプレイヤーが所有権を取得する |
| 操作ロック切替（`OnClickToggleTimelineOperationLock`） | なし（非 Owner は所有権を取得してから実行） | `isTimelineOperationLocked` を反転する |
| 登録ロック切替（`OnClickToggleRegistrationLock`） | なし（非 Owner は所有権を取得してから実行） | `isRegistrationLocked` を反転する |

### ボタンの活性状態

Owner 状態・`isPlaying`・`isTimelineOperationLocked` のいずれかが変わったときに更新する。

| 対象 | Owner | 非 Owner |
|---|---|---|
| `playButton` | 再生中は非活性、停止中は活性 | 非活性 |
| `pauseButton` | 活性 | 非活性 |
| `setOwnerButton` | 非活性 | 操作ロック OFF のとき活性、ON のとき非活性 |
| `ownerOnlyButtons` の各ボタン | 操作ロック OFF のとき活性、ON のとき非活性（`timelineLockToggleButton` は常に活性） | 非活性 |

- `ownerOnlyButtons` に含まれる `playButton` / `pauseButton` / `setOwnerButton` は上表の個別ルールに従う。
- `timelineLockToggleButton` / `registrationLockToggleButton` は、ロック ON の間 `targetGraphic` の色を `#E85900`、子の TextMeshProUGUI の色を `#FFFFFF` にする。ロック OFF で初期色に戻す。

### 表示

| UI フィールド | 表示内容 |
|---|---|
| `currentTimeText` | ローカルの再生位置（`0.0s` 形式） |
| `infoText` | `Synced Time` / `Next Checkpoint` / `Owner` の 3 行 |
| `sceneNameText` | `#番号 シーン名`。シーン名が空の場合は `#番号 シーン 番号` |
| `nextCueText` | 次のシーングループの先頭シーンの `cue`（キッカケ） |
| `progressBar` | 再生位置 / 全長。`Image.Type.Filled`・水平・左起点に設定し、色は `progressBarColor` |
| `checkpointContainer` | `Start()` 時に `checkPointSeconds` の各時刻へ `checkpointLinePrefab` を生成する（幅 2） |
| `registrationWarningText` | 未登録のキャラクターがあるとき `未登録のキャラクターがあります。` |

- 番号はシーングループ単位（Builder で「次のシーンを統合」により連結されたシーンは 1 番号）。

### 配役登録

- `registrationRows` の先頭からキャラクター数分の行を表示し、残りの行は非アクティブにする。キャラクター名が空の場合は `Character 番号` を表示する。
- 行の `Submit()` は `SendCustomNetworkEvent(NetworkEventTarget.All, BroadcastRequest, ...)` を送る。各クライアントの行が `StageTimelineManager` の `ReceiveRegistrationRequest` / `ReceiveUnregisterRequest` を呼び、Owner のみが処理する。
- 登録要求の処理（Owner）:
  - `isRegistrationLocked` が ON の場合は無視する。
  - 要求者がすでにそのキャラクターに登録済みの場合は登録を解除する。
  - 要求者が他のキャラクターに登録済みの場合はその登録を解除してから登録する（1 プレイヤー 1 キャラクター）。
  - 表示名が空の場合は `Player playerId` を記録する。
- 解除要求（`unregisterMode` が ON の行）は、登録者本人の要求のみ処理する。
- 登録ロック ON の間、各行の `registrationButton` は非活性。
- `OnPlayerJoined`（Owner のみ）: 登録中の playerId が無効になっており、記録された表示名が参加者の表示名と一致する場合、その登録を参加者の playerId に付け替える。

### ワープ

- Builder が書き込むワープ配列（キャラクター index・発火時刻・座標・Y 回転）を時刻順に処理する。
- 再生中のみ、前フレームから現フレームまでの区間に入った発火時刻のワープを実行する。同じ再生セッション内で各ワープは 1 回のみ実行する。再生セッション開始時は区間を現在位置から取り直す。
- 対象キャラクターに登録されたプレイヤー本人のクライアントでのみ実行する。未登録のキャラクターのワープは何もしない。
- 実行内容: `SetVelocity(Vector3.zero)` → `Immobilize(true)` → `TeleportTo(座標, Y 回転, SpawnOrientation.AlignPlayerWithSpawnPoint)`。`Immobilize` は次フレーム以降の `Update` で解除する。

### タイムライン連動イベント

Builder が書き込む配列に従い、各クライアントがローカルで実行する。

| 種別 | 実行 | 再生停止中 | 巻き戻し時 |
|---|---|---|---|
| Animator パラメータ | 発火時刻を過ぎたイベントの値を `Animator.SetInteger` で適用する。対象ごとに最後に適用した値と同じ場合は再適用しない | 処理する | キャッシュを破棄し、現在時刻までの値を再適用する |
| Animator トリガー | 区間に入った発火時刻で `Animator.SetTrigger` を 1 回呼ぶ | 処理しない | 現在時刻より後のイベントを未発火に戻す |
| Udon イベント | 区間に入った発火時刻で `SendCustomEvent` を 1 回呼ぶ。OwnerOnly 指定のイベントは、対象 GameObject の Owner のクライアントのみが呼ぶ | 処理しない | 現在時刻より後のイベントを未発火に戻す |

- Animator トリガー / Udon イベントは、再生セッション開始時に区間を現在位置から取り直す。区間より前の未発火イベントは発火せず消化する。

## Inspector

### StageTimelineManager

| フィールド | 型 | 既定値 | 必須 | 内容 |
|---|---|---|---|---|
| `timeline` | `PlayableDirector` | なし | 必須 | 制御対象。未設定時は `Start()` でエラーを出して動作しない。Builder の生成時に適用先 `PlayableDirector` が書き込まれる（未設定の場合は Manager 自身・子孫の `PlayableDirector`、無ければ子に作成した `Timeline` の `PlayableDirector`。解決順は [Builder/README.md](Builder/README.md#タイムライン生成)） |
| `currentTimeText` | `TextMeshProUGUI` | なし | 任意 | 再生位置表示 |
| `infoText` | `TextMeshProUGUI` | なし | 任意 | 同期情報表示 |
| `sceneNameText` | `TextMeshProUGUI` | なし | 任意 | シーン名表示 |
| `nextCueText` | `TextMeshProUGUI` | なし | 任意 | 次のキッカケ表示 |
| `progressBar` | `Image` | なし | 任意 | プログレスバー |
| `registrationWarningText` | `TextMeshProUGUI` | なし | 任意 | 未登録警告表示 |
| `playButton` | `Button` | なし | 任意 | 再生ボタン |
| `pauseButton` | `Button` | なし | 任意 | 一時停止ボタン |
| `setOwnerButton` | `Button` | なし | 任意 | 所有権取得ボタン |
| `timelineLockToggleButton` | `Button` | なし | 任意 | 操作ロック切替ボタン |
| `registrationLockToggleButton` | `Button` | なし | 任意 | 登録ロック切替ボタン |
| `ownerOnlyButtons` | `Button[]` | 空 | 任意 | Owner のみ操作可能にするボタン |
| `progressBarColor` | `Color` | `#3B82F6` | 任意 | プログレスバーの色 |
| `registrationRows` | `StageCharacterRegistrationRow[]` | 空 | 任意 | 配役登録行。表示できるキャラクター数の上限は要素数（プレハブは 10） |
| `checkpointContainer` | `RectTransform` | なし | 任意 | チェックポイント線の親 |
| `checkpointLinePrefab` | `GameObject` | なし | 任意 | チェックポイント線のプレハブ |
| `scheduledStartLeadTime` | `float` | `0.5` | 任意 | 再生開始を予約する先行時間（秒）。実効値は 0.1 以上 |
| `checkpointSafetyMargin` | `float` | `0.05` | 任意 | チェックポイント手前で停止するマージン（秒） |
| `enableCheckpointHardStop` | `bool` | `true` | 任意 | マージン手前で停止するか |
| `autoPlayToFirstCheckpointOnInstanceStart` | `bool` | `true` | 任意 | インスタンス最初の参加者の `Start()` で最初のチェックポイントまで自動再生する |

Inspector に表示しないシリアライズフィールド（Builder の生成時に書き込まれる）:

| フィールド | 型 | 内容 |
|---|---|---|
| `checkPointSeconds` | `int[]` | チェックポイント（秒） |
| `sceneDisplayNames` / `sceneNextCues` | `string[]` | シーングループごとの表示名・次のキッカケ |
| `sceneRangeStarts` / `sceneRangeEnds` | `int[]` | シーングループに含まれる最初・最後のシーン番号（1 始まり） |
| `characterDisplayNames` | `string[]` | キャラクター表示名 |
| `warpCharacterIndices` / `warpTriggerTimes` / `warpDestinations` / `warpYawDegrees` | `int[]` / `float[]` / `Vector3[]` / `float[]` | ワープ |
| `animatorParamAnimators` / `animatorParamNames` | `Animator[]` / `string[]` | Animator パラメータの対象（Animator とパラメータ名の組） |
| `animatorParamEventTargets` / `animatorParamEventTimes` / `animatorParamEventValues` | `int[]` / `float[]` / `int[]` | Animator パラメータのイベント（時刻昇順） |
| `animatorTriggerAnimators` | `Animator[]` | Animator トリガーの対象 |
| `animatorTriggerEventTargets` / `animatorTriggerEventTimes` / `animatorTriggerEventNames` | `int[]` / `float[]` / `string[]` | Animator トリガーのイベント（時刻昇順） |
| `udonEventTargets` | `UdonSharpBehaviour[]` | Udon イベントの対象 |
| `udonEventEventTargets` / `udonEventEventTimes` / `udonEventEventNames` / `udonEventEventOwnerOnly` | `int[]` / `float[]` / `string[]` / `bool[]` | Udon イベント（時刻昇順） |
| `characterRegistryText` | `TextMeshProUGUI` | 配役一覧テキスト（任意） |

### StageCharacterRegistrationRow

| フィールド | 型 | 既定値 | 必須 | 内容 |
|---|---|---|---|---|
| `characterNameText` | `TextMeshProUGUI` | なし | 任意 | キャラクター名表示 |
| `registeredPlayerNameText` | `TextMeshProUGUI` | なし | 任意 | 登録者名表示（未登録時 `未登録`） |
| `registrationButton` | `Button` | なし | 任意 | 登録ロック中に非活性にするボタン |
| `unregisterMode` | `bool` | `false` | 任意 | ON の場合、`Submit()` は解除要求を送る |

## API リファレンス

### StageTimelineManager

#### UI へ手配線するもの（`Button.OnClick` → `UdonBehaviour.SendCustomEvent`）

| シグネチャ | 用途 |
|---|---|
| `void OnClickPlay()` | 再生（Owner のみ） |
| `void OnClickPause()` | 一時停止（Owner のみ） |
| `void OnClickNext()` | 次のシーンへ（Owner のみ） |
| `void OnClickBack()` | 前のチェックポイントへ（Owner のみ） |
| `void OnClickPlus1s()` | 1 秒進める（Owner のみ） |
| `void OnClickMinus1s()` | 1 秒戻す（Owner のみ） |
| `void OnClickReset()` | 先頭から再生（Owner のみ） |
| `void OnClickSetOwner()` | 所有権を取得する |
| `void OnClickToggleTimelineOperationLock()` | 操作ロックを切り替える |
| `void OnClickToggleRegistrationLock()` | 登録ロックを切り替える |

- `StageTimelineManager.prefab` では Play / Pause / Next / Back / +1s / -1s / Reset / Set Owner の各ボタンが配線済み。

#### 他コンポーネントから呼ぶもの（配線不要）

| シグネチャ | 用途 |
|---|---|
| `void PlayTimeline()` / `void PauseTimeline()` | 再生 / 一時停止。Owner のクライアントでのみ動作する |
| `void Next()` / `void Back()` / `void Plus1s()` / `void Minus1s()` / `void ResetTimeline()` | 進行操作。Owner かつ操作ロック OFF のクライアントでのみ動作する |
| `int GetCurrentScene()` | `sceneNumber` を返す |
| `float GetCurrentTime()` | ローカルの再生位置（秒）を返す |
| `float GetSyncedTime()` | `currentTime` を返す |
| `float GetProgress()` | 再生位置 / 全長（0–1）を返す |
| `float GetNextCheckpointTime()` | `nextCheckPointTime` を返す |
| `string GetOwnerName()` | `ownerName` を返す |
| `string GetSceneDisplayName(int sceneIndex)` | `#番号 シーン名` を返す（`sceneIndex` は 1 始まり。0 以下はその数値の文字列） |
| `string GetSceneNextCue(int sceneIndex)` | 指定シーングループ表示中の次のキッカケを返す（範囲外は空文字） |
| `int GetCharacterCount()` | キャラクター数を返す |
| `string GetCharacterDisplayNameAt(int index)` | キャラクター表示名を返す（範囲外は空文字） |
| `string[] GetCharacterDisplayNames()` | キャラクター表示名配列（内部配列の参照）を返す |
| `int GetAssignedPlayerId(int characterIndex)` | 登録プレイヤーの playerId を返す（未登録・範囲外は -1） |

#### 内部専用（配線不要）

| シグネチャ | 用途 |
|---|---|
| `void ReceiveRegistrationRequest(int characterIndex, int playerId, string displayName)` | 配役登録要求の処理。`StageCharacterRegistrationRow.BroadcastRequest` が呼ぶ |
| `void ReceiveUnregisterRequest(int characterIndex, int playerId)` | 配役解除要求の処理。同上 |
| `override void OnDeserialization()` | VRChat コールバック。同期状態を適用する |
| `override void OnPlayerJoined(VRCPlayerApi player)` | VRChat コールバック。再参加者の配役を付け替える |

### StageCharacterRegistrationRow

#### UI へ手配線するもの（`Button.OnClick` → `UdonBehaviour.SendCustomEvent`）

| シグネチャ | 用途 |
|---|---|
| `void Submit()` | 登録（`unregisterMode` が ON の場合は解除）要求を送る。`CharacterRegistrationRow.prefab` では配線済み |

#### 内部専用（配線不要）

| シグネチャ | 用途 |
|---|---|
| `void Configure(StageTimelineManager manager, int characterIndex, string characterName)` | 行の初期化。`StageTimelineManager` が呼ぶ |
| `void SetRegisteredPlayerName(string registeredPlayerName)` | 登録者名表示の更新。`StageTimelineManager` が呼ぶ |
| `void SetInteractable(bool interactable)` | `registrationButton` の活性切替。`StageTimelineManager` が呼ぶ |
| `void SendBroadcastRequest(int requestedCharacterIndex, int requesterPlayerId, string requesterDisplayName, bool requestUnregisterMode)` | `BroadcastRequest` を全員へ送る。`Submit()` が呼ぶ |
| `[NetworkCallable] void BroadcastRequest(int requestedCharacterIndex, int requesterPlayerId, string requesterDisplayName, bool requestUnregisterMode)` | ネットワークイベントハンドラ。`StageTimelineManager` へ要求を渡す |

### Builder

UI へ手配線するものはない。エディタ API は [Builder/README.md](Builder/README.md) に記載する。

## ライセンス

MIT License ではない。[LICENSE.md](LICENSE.md)（ましろ小劇場 ツール・ギミック汎用利用規約）に基づいて提供する。規約の正本は [VN3License_ja.pdf](VN3License_ja.pdf)（VN3 ライセンス様式）。

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
