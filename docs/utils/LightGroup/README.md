# Mashiro Light Group

子階層の `Light` とビームライト（名前に `BeamLight` を含む `MeshRenderer`）を 1 グループとして扱い、明るさ・色・サイズ・回転を適用する UdonSharpBehaviour（`MashiroLightGroup`）と、灯体の回転対象を示すマーカー（`MashiroLightFixture`）、配置・確認用のエディタ拡張。`MashiroLightGroup` は制御側から `Initialize` が呼ばれるまで実行時にライトを変更しない。

## 構成

| ファイル | 役割 |
| --- | --- |
| `MashiroLightGroup.cs` / `.asset` | グループ内のライト・ビームライトへ明るさ・色・サイズ・回転を適用し、目標値を同期する |
| `MashiroLightFixture.cs` | 回転対象の Transform を示す編集時マーカー（MonoBehaviour） |
| `Editor/MashiroLightGroupEditor.cs` | `MashiroLightGroup` のカスタムインスペクタ（ライトサイズ・回転・影・カリングマスク・点灯テスト）、点灯テストの状態管理（`MashiroLightGroupTestController`）、エディタ上のビーム開き角の反映（`MashiroBeamShapeRefresher`） |
| `Editor/MashiroLightFixtureEditor.cs` | `MashiroLightFixture` のカスタムインスペクタ |
| `Editor/MashiroLightRotationBuildBaker.cs` | シーン処理時に回転データを `MashiroLightGroup` へ転記する |
| `Editor/MashiroLightGroupWindow.cs` | シーン内の全 `MashiroLightGroup` を一覧・点灯テストするエディタウィンドウ |

## 依存

- パッケージ `MashiroTheater-Utils`（VPM `com.mashirotheater.utils`）に同梱。
- エディタ拡張は UdonSharp のエディタ API（`UdonSharpEditor`）を使用する。
- ビームライトのマテリアルに書き込むプロパティ: `_Color`、`_Intensity`、`_ConeWidth`。
- ビームの開き角の計算は、ビームのメッシュが [NoribenBeamlightShader](https://booth.pm/ja/items/1637978) の `BeamLightConeModel`（根元を原点に -Y 方向へ長さ 5m）であることを前提とする。
- `LightingConsole` と `StageTimelineTools` のコードが `MashiroLightGroup` を参照する。

## 仕様

### MashiroLightGroup（実行時）

- クラスは名前空間に属さない（グローバル名前空間）。
- 同期方式: `BehaviourSyncMode.Continuous`。
- 同期変数:

  | 変数 | 型 | 初期値 | 内容 |
  | --- | --- | --- | --- |
  | `_color` | `Color` | 白 | 目標色 |
  | `_colorA` / `_colorB` | `Color` | 白 | 系統 A / B の保持色 |
  | `_sizeOffset` | `float` | `0` | サイズオフセット（度） |
  | `_sizeOffsetA` / `_sizeOffsetB` | `float` | `0` | 系統 A / B の保持サイズオフセット（度） |
  | `_sliderAValue` / `_sliderBValue` | `float` | `0` | フェーダー A / B の値 |
  | `_pan` / `_tilt` | `float` | `0` | パン / チルト角（度） |

- 明るさは同期しない。`ApplyIntensityDirect()` で渡された値をローカルで適用する。
- 所有権の取得・移譲は行わない。`Set*` 系メソッド・`UpdateFromSlider()`・`ResetToInitialValues()` は `RequestSerialization()` を呼ぶ。
- `Initialize()` が呼ばれるまで、`Update`（色フェード）と `OnDeserialization` は何もしない。
- 固定値:

  | 定数 | 値 |
  | --- | --- |
  | `MaxSizeOffset` | `30`（サイズオフセットのクランプ範囲 ±30 度） |
  | `MaxRotationAngle` | `30`（パン / チルトのクランプ範囲 ±30 度） |
  | `MinSpotAngle` / `MaxSpotAngle` | `1` / `179` |
  | 色フェード時間 | `2` 秒 |
  | `DeserializedEventName` | `"OnLightGroupDeserialized"` |
  | `BeamMeshLength` | `5`（ビームメッシュの長さ m） |
  | `BeamBaseSlope` | `1.02` |
  | `BeamConeWidthSlope` | `14` |
  | `MinBeamSlope` | `0.01` |
  | `MaxBeamHalfAngle` | `85`（ビームの半角の上限 度） |

#### Initialize(int index)

1. `GetComponentsInChildren<Light>()` で子階層の Light を取得する（非アクティブは含まない）。
2. `GetComponentsInChildren<MeshRenderer>()` のうち、名前に `BeamLight` を含むものをビームライトとして取得する（非アクティブは含まない）。
3. Light が 1 つ以上あれば、先頭の Light の `spotAngle` を基準サイズとする。
4. サイズオフセット（A/B 含む）・パン・チルト・フェーダー値を `0`、色（A/B・表示色含む）を `initialColor` にする。
5. `ApplyIntensityDirect(0)` を実行する（全ライト・ビームの GameObject を非アクティブにする）。
6. 色・サイズ・回転を適用する。

#### 明るさ

- 適用値 = `intensity × intensityMultiplier`。
- 適用値 `> 0`: Light とビームの GameObject を `SetActive(true)` にし、`Light.intensity` = 適用値、ビームの `_Intensity` = 適用値 × `0.05`。
- 適用値 `<= 0`: Light とビームの GameObject を `SetActive(false)` にする。

#### 色

- `SetColorWithFade()` は目標色を設定し、現在の表示色から目標色へ 2 秒で線形補間する（`Update`）。同期するのは目標色（`_color`）のみ。
- 適用先: `Light.color` とビームの `_Color`。

#### サイズ

- Spot ライトの `spotAngle` = `Clamp(基準サイズ + _sizeOffset, 1, 179)`。Spot 以外の Light は変更しない。
- ビームの開き角 = `spotAngle × beamAngleScale × beamWidthMultiplier`。Transform のスケールは変更しない。
- ビームごとに `_ConeWidth` を次の式で設定する。
  - `halfTan` = `tan(Clamp(開き角 × 0.5, 0.1, MaxBeamHalfAngle))`
  - `slope` = `Max(halfTan × length / width, MinBeamSlope)`。`width` / `length` はビームのローカル X / Y 単位ベクトルのワールドでの長さ。`width` が `0.0001` 未満のビームは変更しない
  - `_ConeWidth` = `(slope − BeamBaseSlope) / BeamConeWidthSlope`

#### 回転

- 回転対象は `rotationTargets`（`MashiroLightRotationBuildBaker` が転記した配列）。
- 各対象の `localRotation` を次の式で設定する。
  - `AngleAxis(_pan, ワールド上方向を親のローカルへ変換した軸) × rotationDefaults[i] × AngleAxis(_tilt, rotationVerticalAxis[i])`
  - パン項は `rotationAllowHorizontal[i]`、チルト項は `rotationAllowVertical[i]` が `true` の場合のみ掛ける。
  - 軸ベクトルの長さの二乗が `0.0001` 以下のとき、チルト軸は `(1, 0, 0)`、パン軸は `(0, 1, 0)` を使う。

#### 系統 A/B・フェーダー値

- `SetBankColor()` / `SetBankSizeOffset()` / `UpdateFromSlider()` は値の保持と同期のみを行い、ライトへは適用しない。

#### 同期受信（OnDeserialization）

- 初回受信時は目標色を表示色へ即時反映する（フェードしない）。
- 2 回目以降は、受信した目標色が現在の目標色と異なる場合に色フェードを開始する。
- サイズと回転を適用する。
- `SetDeserializationListener()` で通知先が設定されていれば、通知先へ `SendCustomEvent("OnLightGroupDeserialized")` を送る。

#### マテリアル

- 実行時は `MeshRenderer.material`（インスタンス）へ書き込む。

### MashiroLightFixture

- `MonoBehaviour`（Udon ではない）。実行時の処理はない。
- `[DisallowMultipleComponent]`。`AddComponentMenu`: `Mashiro Theater/Mashiro Light Fixture`。
- 付与時（`Reset`）に現在の `localRotation` を基準姿勢として記録し、パン / チルト角を `0` にする。
- 非表示のシリアライズ値: `hasDefaultRotation`、`defaultRotation`、`panAngle`、`tiltAngle`。

### ランタイム回転データの転記（MashiroLightRotationBuildBaker）

- `IProcessSceneWithReport` の実装。`callbackOrder` は `1000`。ビルド時および Play 開始時のシーン処理で実行する。
- シーン内の全 `MashiroLightGroup`（非アクティブ含む）について、子階層の `MashiroLightFixture`（非アクティブ含む）から次の配列を作成して設定し、`UdonSharpEditorUtility.CopyProxyToUdon()` を呼ぶ。`allowHorizontal` と `allowVertical` が両方 `false` の Fixture は除外する。

  | 設定先 | 値 |
  | --- | --- |
  | `rotationTargets` | Fixture の Transform |
  | `rotationDefaults` | 処理時点の `localRotation` |
  | `rotationAllowHorizontal` | `allowHorizontal` |
  | `rotationAllowVertical` | `allowVertical` |
  | `rotationVerticalAxis` | `verticalAxis` |

- 処理時点の向きが実行時のパン / チルト `0` の基準になる。
- グループが 1 つ以上あれば、グループ数と回転対象数を Console にログ出力する。

### MashiroLightGroup インスペクタ

`DrawDefaultInspector()` の下に次のセクションを表示する。ライトサイズ・回転・影・カリングマスクの操作は Undo に記録する。スライダーは 1 回のドラッグを 1 つの Undo にまとめる。対象の Light / ビーム / Fixture は子階層から非アクティブを含めて取得する。

| セクション | コントロール | 範囲 | 動作 |
| --- | --- | --- | --- |
| ライトサイズ | `Size` スライダー | `1`〜`179` | 全 Spot ライトの `spotAngle` を設定し、ビームの開き角を反映する。ビームの Transform は変更しない |
| ライトサイズ | `Range` スライダー | `0`〜`200` | 全 Light の `range` を設定する。ビームは変更しない |
| ライトサイズ | `ビームの長さ (m)` スライダー | `0.1`〜`10` | 全ビームのワールドでの長さ（`BeamMeshLength` × Y 方向のワールドスケール）が指定値になるよう `localScale.y` を設定する。X / Z スケールは変更しない |
| ライトサイズ | `ビームの太さ補正` スライダー | `0`〜`5` | このグループの `beamWidthMultiplier` を設定する |
| ライトサイズ | `ビームの見た目係数` スライダー | `0.3`〜`2` | シーン内の全 `MashiroLightGroup`（非アクティブ含む）の `beamAngleScale` を同じ値に設定する |
| 回転 | `横回転（パン）` スライダー | `-90`〜`90` | 下記「回転セクション」参照 |
| 回転 | `縦回転（チルト）` スライダー | `-90`〜`90` | 下記「回転セクション」参照 |
| 回転 | `現在の向きをデフォルトに保存` ボタン | – | 全 Fixture の現在の `localRotation` を基準姿勢として保存し、パン / チルト角を `0` にする |
| 回転 | `デフォルトに戻す` ボタン | – | 基準姿勢を記録済みの全 Fixture を基準姿勢へ戻し、パン / チルト角を `0` にする |
| 影 | `影タイプ` | `None` / `Hard` / `Soft` | 全 Light の `shadows` を設定する |
| 影 | `影の濃さ` スライダー | `0`〜`1` | 全 Light の `shadowStrength` を設定する。`影タイプ` が `None` のとき非表示 |
| カリングマスク | `対象レイヤー` | 名前付きレイヤー | 全 Light の `cullingMask` を設定する |
| 点灯テスト | `テスト明るさ` スライダー | `0`〜`1` | 点灯テストの明るさ。点灯中は即時反映する |
| 点灯テスト | `点灯テスト` / `点灯テスト中（クリックで OFF）` ボタン | – | 点灯テストの開始 / 終了。点灯中は背景色 `#E85900` |

- 初期表示値: `Size` は最初の Spot ライトの `spotAngle`（なければ `30`）、`Range` は最初の Light の `range`（なければ `10`）、`ビームの長さ (m)` は最初のビームの長さ（なければ `5`）、`ビームの見た目係数` はこのグループの `beamAngleScale`、影・カリングマスクは最初の Light の値。Undo / Redo 時にシーンの値から読み直す。
- 回転セクション:
  - 子階層に `MashiroLightFixture` がない場合は案内の HelpBox のみ表示する。
  - スライダー変更時、`allowHorizontal` または `allowVertical` が `true` の各 Fixture について、基準姿勢が未記録なら現在の向きを記録し、`localRotation` を `AngleAxis(パン, ワールド上方向を親のローカルへ変換した軸) × 基準姿勢 × AngleAxis(チルト, verticalAxis)` に設定する。パン項・チルト項は各 Fixture の許可フラグが `true` の場合のみ掛ける。適用した角度を Fixture に記録する。
  - スライダーの初期表示値は、基準姿勢を記録済みでその軸を許可する最初の Fixture の記録角度。
  - `対象: 横 n 個 / 縦 n 個` に、`allowHorizontal` / `allowVertical` が `true` の Fixture 数を表示する。
- 点灯テスト:
  - 適用する明るさ = `テスト明るさ × intensityMultiplier`。色は `initialColor`。点灯中に `initialColor` が変わると即時反映する。
  - `テスト明るさ` は `SessionState` にグループ単位（`GlobalObjectId`）で保存し、ライトグループウィンドウと共有する。既定値は `1`。
  - 点灯中は点灯対象の Light 数・ビーム数を表示する。

### エディタ上のビーム開き角（MashiroBeamShapeRefresher）

- `[InitializeOnLoad]` の静的クラス。編集モードで、全 `MashiroLightGroup` のビームへ「サイズ」と同じ式の `_ConeWidth` を `MaterialPropertyBlock` で設定する。マテリアルアセットは変更しない。グループに属するビームでは、マテリアルの `_ConeWidth` の値は使われない。
- 開き角の基準は子階層（非アクティブ含む）の最初の Spot ライトの `spotAngle`。Spot ライトがないグループは変更しない。
- 再計算のタイミング: スクリプトのロード時、シーンを開いたとき、Undo / Redo、編集モードへの復帰時、グループ配下の Light・Transform・MeshRenderer・GameObject または `MashiroLightGroup` の変更時、GameObject の破棄・親の変更時。1 フレームに 1 回にまとめる。
- Play モード突入時（`ExitingEditMode`）に全グループの点灯テストを終了し、全ビームの `MaterialPropertyBlock` を解除する。

### 点灯テスト（MashiroLightGroupTestController）

- `[InitializeOnLoad]` の静的クラス。点灯状態はインスペクタの選択状態と独立して保持し、もう一度操作するまで点灯を続ける。
- 開始時に子階層（非アクティブ含む）の Light とビームを取得し、次を記録する。
  - Light: GameObject の `activeSelf`、`intensity`、`color`。
  - ビーム: GameObject の `activeSelf`、既存の `MaterialPropertyBlock`。
- 点灯時:
  - Light: GameObject を `SetActive(true)`、`intensity` と `color` を設定する。
  - ビーム: GameObject を `SetActive(true)`、`MaterialPropertyBlock` で `_Color` と `_Intensity`（明るさ × `0.05`）を設定する。マテリアルアセットは変更しない。
- 終了時は記録した状態へ戻す。ビームは既存の `MaterialPropertyBlock` があればそれを戻し、なければ解除する。 その後ビームの開き角を再計算する。
- 次のタイミングで全グループの点灯テストを終了する: Play モード突入時（`ExitingEditMode`）、Unity 終了時、アセンブリリロード前。
- 点灯前の状態を `SessionState` に保存する。編集モードでのアセンブリリロード後、保存値が残っていれば Light の `intensity`・`color`・アクティブ状態とビームのアクティブ状態を戻し、ビームの `MaterialPropertyBlock` を解除して、保存値を削除し、ビームの開き角を再計算する。

### MashiroLightFixture インスペクタ

- 回転は `MashiroLightGroup` の「回転」スライダーで調整する旨の HelpBox を表示する。
- 基準姿勢を記録済みの場合、`現在: パン n° / チルト n°（取付時を基準）` を表示する。
- その下に既定のインスペクタを表示する。

### ライトグループウィンドウ（MashiroLightGroupWindow）

- メニュー: `Tools/Mashiro Theater/Light Groups`。ウィンドウ名: `ライトグループ`。
- 対象: `FindObjectsOfType<MashiroLightGroup>(true)` で取得したシーン内の全グループ。ヒエラルキー順に並べる。
- 一覧の再取得: ウィンドウ有効化時、フォーカス時、ヒエラルキー変更時、`更新` ボタン押下時。
- Play モード中（遷移中を含む）は案内の HelpBox のみ表示する。
- 点灯操作は `MashiroLightGroupTestController` を使用し、インスペクタの点灯テストと状態・テスト明るさを共有する。

| 領域 | コントロール | 動作 |
| --- | --- | --- |
| ツールバー | `更新` ボタン | 一覧を再取得する |
| ツールバー | `照明グループ: n 件` | グループ数を表示する |
| ツールバー | `全点灯` ボタン | 点灯テスト中でない全グループの点灯テストを開始する（明るさ = テスト明るさ × `intensityMultiplier`、色 = `initialColor`） |
| ツールバー | `全消灯` ボタン | 全グループの点灯テストを終了する |
| プレビュー | タイル（76 × 48） | 点灯テスト中は適用色 × 明るさ（`intensityMultiplier` で正規化し `0`〜`1` にクランプ）、それ以外は黒を表示する。グループ名を表示する。クリックでグループを選択して Ping する |
| 照明グループ | 色スウォッチ | プレビュータイルと同じ色を表示する |
| 照明グループ | グループ名 | クリックでグループを選択して Ping する |
| 照明グループ | 明るさスライダー（`0`〜`1`） | テスト明るさを設定する。点灯中は即時反映する |
| 照明グループ | カラーフィールド | `initialColor` を変更する（Undo 記録・`CopyProxyToUdon`・シーンを変更済みにする）。点灯中は即時反映する |
| 照明グループ | `点灯` / `点灯中` ボタン | 点灯テストの開始 / 終了。点灯中は背景色 `#E85900` |

## Inspector

### MashiroLightGroup

| フィールド | 型 | 既定値 | 必須 | 内容 |
| --- | --- | --- | --- | --- |
| `initialColor` | `Color` | `(1, 1, 1, 1)` | – | `Initialize` 時の色。点灯テストの色 |

次のフィールドはインスペクタに表示しない。

| フィールド | 型 | 既定値 | 内容 |
| --- | --- | --- | --- |
| `intensityMultiplier` | `float`（private、`[SerializeField]`） | `1` | 明るさのゲイン |
| `beamAngleScale` | `float` | `1` | ビームの見た目係数。インスペクタの `ビームの見た目係数` で設定する |
| `beamWidthMultiplier` | `float` | `1` | ビームの太さ補正。インスペクタの `ビームの太さ補正` で設定する |
| `lights` | `Light[]` | なし | `Initialize` 時に取得した Light |
| `beamLights` | `MeshRenderer[]` | なし | `Initialize` 時に取得したビーム |
| `rotationTargets` | `Transform[]` | なし | 回転対象（転記値） |
| `rotationDefaults` | `Quaternion[]` | なし | 回転対象の基準 `localRotation`（転記値） |
| `rotationAllowHorizontal` | `bool[]` | なし | パン許可（転記値） |
| `rotationAllowVertical` | `bool[]` | なし | チルト許可（転記値） |
| `rotationVerticalAxis` | `Vector3[]` | なし | チルト軸（転記値） |

### MashiroLightFixture

| フィールド | 型 | 既定値 | 必須 | 内容 |
| --- | --- | --- | --- | --- |
| `allowHorizontal` | `bool` | `true` | – | パン（ワールド上方向まわりの回転）を適用する |
| `allowVertical` | `bool` | `true` | – | チルトを適用する |
| `verticalAxis` | `Vector3` | `(1, 0, 0)` | – | チルトの回転軸（このオブジェクトのローカル軸） |

## API リファレンス

### MashiroLightGroup

UI へ手配線するものはない。すべて内部連携用（配線不要）。

| シグネチャ | 用途 | 呼び出し種別 |
| --- | --- | --- |
| `void Initialize(int index)` | ライトを取得し、初期値を適用して制御を開始する | 制御側コンポーネントが呼ぶ |
| `void SetDeserializationListener(UdonSharpBehaviour listener)` | 同期受信時に `OnLightGroupDeserialized` を送る通知先を設定する | 制御側コンポーネントが呼ぶ |
| `void ApplyIntensityDirect(float intensity)` | 明るさをライトへ適用する（同期しない） | 制御側コンポーネントが呼ぶ |
| `void SetColorWithFade(Color newColor)` | 目標色を設定し、2 秒でフェードする | 制御側コンポーネントが呼ぶ |
| `void SetBankColor(bool isA, Color color)` | 系統 A / B の保持色を設定する | 制御側コンポーネントが呼ぶ |
| `Color GetBankColor(bool isA)` | 系統 A / B の保持色を返す | 制御側コンポーネントが呼ぶ |
| `void SetSizeOffset(float offset)` | サイズオフセットを ±30 にクランプして適用する | 制御側コンポーネントが呼ぶ |
| `float GetSizeOffset()` | サイズオフセットを返す | 制御側コンポーネントが呼ぶ |
| `void SetBankSizeOffset(bool isA, float offset)` | 系統 A / B の保持サイズオフセットを ±30 にクランプして設定する | 制御側コンポーネントが呼ぶ |
| `float GetBankSizeOffset(bool isA)` | 系統 A / B の保持サイズオフセットを返す | 制御側コンポーネントが呼ぶ |
| `float GetMaxSizeOffset()` | `MaxSizeOffset`（`30`）を返す | 制御側コンポーネントが呼ぶ |
| `void SetPan(float pan)` | パン角を ±30 にクランプして適用する | 制御側コンポーネントが呼ぶ |
| `void SetTilt(float tilt)` | チルト角を ±30 にクランプして適用する | 制御側コンポーネントが呼ぶ |
| `float GetPan()` | パン角を返す | 制御側コンポーネントが呼ぶ |
| `float GetTilt()` | チルト角を返す | 制御側コンポーネントが呼ぶ |
| `float GetMaxRotationAngle()` | `MaxRotationAngle`（`30`）を返す | 制御側コンポーネントが呼ぶ |
| `void UpdateFromSlider(float value, bool isSliderA)` | フェーダー A / B の値を設定する（ライトへは適用しない） | 制御側コンポーネントが呼ぶ |
| `float GetSliderAValue()` | フェーダー A の値を返す | 制御側コンポーネントが呼ぶ |
| `float GetSliderBValue()` | フェーダー B の値を返す | 制御側コンポーネントが呼ぶ |
| `void ResetToInitialValues()` | サイズオフセット・パン・チルトを `0`、色を `initialColor`（フェード）にする | 制御側コンポーネントが呼ぶ |
| `string GetName()` | GameObject 名を返す | 制御側コンポーネントが呼ぶ |
| `float GetDisplayIntensity()` | 最後に `ApplyIntensityDirect()` へ渡した値を `0`〜`1` にクランプして返す | 制御側コンポーネントが呼ぶ |
| `Color GetDisplayColor()` | 表示中の色（フェード途中の値を含む）を返す | 制御側コンポーネントが呼ぶ |
| `float GetInitialSize()` | 基準サイズ（`Initialize` 時の先頭 Light の `spotAngle`）を返す | 制御側コンポーネントが呼ぶ |
| `int GetRealtimeLightCount()` | `Initialize` 時に取得した Light の数を返す | 制御側コンポーネントが呼ぶ |
| `bool AreLightsEnabled()` | 最後に適用した明るさ（`× intensityMultiplier`）が `0` より大きいかを返す | 制御側コンポーネントが呼ぶ |
| `void OnDeserialization()` | 色フェードの開始・サイズと回転の適用・通知先への送信 | VRChat が呼ぶ（内部専用） |
| `const string DeserializedEventName` | `"OnLightGroupDeserialized"` | 定数 |
| `const float BeamMeshLength` / `BeamBaseSlope` / `BeamConeWidthSlope` / `MinBeamSlope` / `MaxBeamHalfAngle` | ビームの開き角の計算に使う定数（値は「固定値」を参照） | 定数（エディタ拡張が参照する） |

### MashiroLightFixture

UI へ手配線するものはない。すべてエディタ拡張から呼ぶ内部連携用（配線不要）。メソッドは `UNITY_EDITOR` 時のみ定義する。

| シグネチャ | 用途 | 呼び出し種別 |
| --- | --- | --- |
| `void SaveDefaultRotation()` | 現在の `localRotation` を基準姿勢として保存し、パン / チルト角を `0` にする | エディタ拡張が呼ぶ |
| `void EnsureDefaultRotation()` | 基準姿勢が未記録なら `SaveDefaultRotation()` を実行する | エディタ拡張が呼ぶ |
| `void RestoreDefaultRotation()` | 基準姿勢が記録済みなら `localRotation` を基準姿勢へ戻し、パン / チルト角を `0` にする | エディタ拡張が呼ぶ |
| `void SetPanTilt(float pan, float tilt)` | 適用したパン / チルト角を記録する | エディタ拡張が呼ぶ |
| `bool HasDefaultRotation { get; }` | 基準姿勢を記録済みか | エディタ拡張が参照する |
| `Quaternion DefaultRotation { get; }` | 基準姿勢（`localRotation`） | エディタ拡張が参照する |
| `float PanAngle { get; }` | 記録したパン角 | エディタ拡張が参照する |
| `float TiltAngle { get; }` | 記録したチルト角 | エディタ拡張が参照する |

### MashiroLightGroupWindow（エディタ専用）

| シグネチャ | 用途 | 呼び出し種別 |
| --- | --- | --- |
| `static void Open()` | ライトグループウィンドウを開く | メニュー `Tools/Mashiro Theater/Light Groups` |

## ライセンス

MIT License（`MashiroTheater-Utils` 同梱の `LICENSE.md` を参照）。
