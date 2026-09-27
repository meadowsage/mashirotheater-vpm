# LightingControlSystem

ステージ照明を VRChat 上で操作するためのツール群です。Light（実ライト）とビームライト
（円錐メッシュ）をグループ単位でまとめ、明るさ・色・スポット角をオペレーションボードから
同期操作します。

## 主なコンポーネント

| ファイル | 役割 |
| --- | --- |
| `MashiroLightGroup.cs` | 1 グループ分の Light / ビームライトを保持し、明るさ・色・サイズを適用・同期する |
| `MashiroLightFixture.cs` | 灯体 1 台分の回転対象（アーム部 / 本体部）を示す編集時マーカー |
| `MashiroLightingManager.cs` | 複数グループの統括・プリセット適用 |
| `MashiroIntensitySlidersHandler.cs` | 明るさスライダー UI のハンドラ |
| `MashiroColorButtonHandler.cs` | 色選択ボタンのハンドラ |
| `MashiroFadeDurationButtonHandler.cs` | 遅延実行モードの反映秒数選択ボタンのハンドラ |
| `MashiroLightScenePreset.cs` | 照明シーンプリセット 1 件分のデータ・呼出ボタン |
| `MashiroLightPresetSlotHandler.cs` | ランタイムプリセットスロット 1 個分の UI ハンドラ（読込・登録・削除） |
| `MashiroBlackoutButtonHandler.cs` | 完全暗転ボタン 1 個分のハンドラ（トグル） |
| `MashiroConsoleFoldToggle.cs` | オペレーター UI をまとめて折りたたむローカルトグル（SetPassCall 削減） |
| `Editor/MashiroLightGroupEditor.cs` | `MashiroLightGroup` のカスタムインスペクタ（点灯テスト機能） |
| `Editor/MashiroLightFixtureEditor.cs` | `MashiroLightFixture` のカスタムインスペクタ（基準姿勢の保存・注意書き） |
| `Editor/MashiroLightRotationBuildBaker.cs` | 回転対象・基準姿勢を `MashiroLightGroup` へ転記する自動処理（Play 開始時・ビルド時） |
| `Editor/MashiroLightingControlWindow.cs` | シーン内の照明グループを一覧制御する照明コントロールウィンドウ |

## 導入

`Prefabs/` に配置用のプレハブが同梱されています。

| プレハブ | 内容 |
| --- | --- |
| `MashiroLightingManager.prefab` | 卓一式。`MashiroLightingManager` と操作 UI（フェーダー列・色ボタン・A/B クロスフェード・遅延実行モード・プリセットスロット・暗転ボタン・折りたたみトグル）、暗転用の黒箱までを含みます |
| `FaderGroup.prefab` | フェーダーグループ 1 列分。`sliderPrefab` に割り当てます（卓プレハブでは設定済み） |
| `ColorButton.prefab` | 色選択ボタン 1 個分。`colorButtonPrefab` に割り当てます（同上） |
| `PresetSlot.prefab` | ランタイムプリセットスロット 1 個分。`presetSlotPrefab` に割り当てます（同上） |
| `PresetButton.prefab` | シーンプリセット呼出ボタンの雛形。OnClick に `MashiroLightScenePreset.OnButtonClick` を割り当てて使います |
| `StageLights_Preset.prefab` | ステージ照明の配置サンプル（Spot ライトと `BeamLightCone` メッシュ一式）。`MashiroLightGroup` は付いていないため、グループ化したい単位のオブジェクトに自分で付与します |

### 最短の手順

1. 照明（Spot ライトやビームライト）を 1 つの親オブジェクトの下にまとめ、グループにしたい
   単位のオブジェクトへ `MashiroLightGroup` を付与します（配下の Light / `BeamLight` を含む
   MeshRenderer は自動スキャンされます）。`StageLights_Preset.prefab` を配置サンプルとして
   流用できます。
2. `MashiroLightingManager.prefab` をシーンに配置します。
3. 配置した `MashiroLightingManager` の `lightGroupParent` に、手順 1 の親オブジェクトを
   割り当てます（**唯一の必須設定**。ここを起点に配下の `MashiroLightGroup` が自動収集され、
   フェーダー列が実行時に生成されます）。
4. 必要に応じて、暗転用の黒箱の位置調整や、シーンプリセット・プレビューパネルなどの
   任意機能を後述の各節に従って設定します。

## MashiroLightGroup

- `lights` / `beamLights` は子階層から**自動スキャン**されるため、手動設定は不要です。
  - `lights`: 子階層のすべての `Light`
  - `beamLights`: 子階層の `MeshRenderer` のうち、名前に `BeamLight` を含むもの
- `initialColor`: ライトの初期色（デフォルトは白）。

実際の `Light.intensity` は `スライダー値 × intensityMultiplier` として求められます。
`intensityMultiplier` は既定 1 の内部値で、インスペクタには表示されません。

### ライトサイズ（エディタ機能）

Spot ライトの **Size（Angle）**・**Range**・ビームライトの **Y スケール** をグループ単位で
まとめて変更する永続的な機能です（テストではなく実データを書き換えます。Undo 可）。
インスペクタの **「ライトサイズ」** セクションから操作します。

- **Size**: スライダー（1〜179）。ドラッグに連動して即時反映され、グループ内の全 Spot ライトの
  `spotAngle` と、全ビームライトの `localScale.y`（自動計算）に適用されます（X/Z スケールは
  変更しません）。1 回のドラッグは 1 ステップの Undo にまとまります。
- **Range**: スライダー（0〜200）。ドラッグに連動して即時反映され、グループ内の全ライトの
  `range` に適用されます。ビームライトの形状は **Size のみに追従**し、Range には追従しません。

ビーム Y スケールは内部で `0.75 × cot(Size / 2)` として自動計算されます（ビームメッシュは
頂点幅が固定の円錐で、長さ＝Y で開き角を合わせる構造のため）。

> ランタイムのサイズ操作はビームを `_ConeWidth`（マテリアル）で調整し、transform スケールには
> 触れません。そのためここで設定した Y スケールは実行時に上書きされず、そのまま維持されます。

### 回転（エディタ機能）

灯体の横回転（パン）・縦回転（チルト）を、グループ単位でまとめて回転する永続的な機能です
（Undo 可）。インスペクタの **「回転」** セクションから操作します。

回転対象は `MashiroLightFixture` コンポーネントで指定します（名前マッチングではなく、Prefab 側で
手動付与する方式）。

#### セットアップ（MashiroLightFixture）

**回転させたいオブジェクト自体**（アーム部・本体部など）に `MashiroLightFixture` を付与します。
コンポーネントは自身の Transform を回転させます。

- **横回転（パン）**: `allowHorizontal`（許容するか）。**パンはワールドの垂直軸まわり**に回るため、
  軸の指定は不要です。
- **縦回転（チルト）**: `allowVertical`（許容するか）、`verticalAxis`（蝶番のローカル軸。通常 X 軸）。

アーム（ハンガー）に付けてパンのみ許可、本体に付けてパン＋チルト許可、のように構成します。
どの方向を許容するかは `allowHorizontal` / `allowVertical` で指定し、許容しない方向はスキップされます。

- **デフォルト（基準姿勢）**: コンポーネントを**付与した時点の向き**を自動的に基準（パン/チルト 0）
  として記録します。天吊り・三脚反転など、その取り付け姿勢を 0 として扱います。
- **回転は LightGroup のスライダーで**行ってください。`Transform` を手で直接回すのは非推奨です
  （スライダーの表示と実際の向きがずれます）。Fixture のインスペクタにも注意書きを表示します。

#### 回転の適用（MashiroLightGroup インスペクタ）

- **横回転（パン）/ 縦回転（チルト）**: スライダー（−90〜90）。各灯体の**取付時のデフォルト姿勢
  からのパン/チルト角**を指定します。
  - **パンはワールドの垂直軸**まわり、**チルトはローカルの蝶番軸**まわりに回ります。デフォルトが
    傾いていても、パン時に首振り（X/Z の傾き）が発生しません。
  - 回転は各灯体の**自分の原点**まわりに行います（パン軸が原点を通る前提でモデルを組んでください）。
- **現在値の表示**: スライダーは選択時に各灯体に記録されたパン/チルト角を読み戻して表示します
  （他の照明を選んでから戻ってきても保持されます）。
- **Undo**: 1 回のドラッグ操作が 1 ステップの Undo にまとまります。
- **現在の向きをデフォルトに保存**: 各灯体の現在の向きを基準として保存し、パン/チルトを 0 にします。
- **デフォルトに戻す**: 各灯体を保存済みデフォルトの向きへ戻します。

> 回転は編集時に Transform へ直接焼き込む永続操作です。`MashiroLightFixture` は実行時には
> 何もしない編集時メタデータで、VRChat ビルド時には除去されます。

### 影（エディタ機能）

グループ内の全 `Light` の影設定をまとめて変更する永続的な機能です（Undo 可・即時反映）。
インスペクタの **「影」** セクションから操作します。

- **影タイプ**: `None`（影なし）/ `Hard` / `Soft` を選択し、全ライトの `shadows` に適用します。
- **影の濃さ**: スライダー（0〜1）。全ライトの `shadowStrength` に適用します（ドラッグ連動・
  1 ドラッグ 1 Undo）。**影タイプが `None` のときは表示されません。**

### カリングマスク（エディタ機能）

グループ内の全 `Light` の `cullingMask` をまとめて変更する永続的な機能です（Undo 可・即時反映）。
インスペクタの **「カリングマスク」** セクションから操作します。

- **対象レイヤー**: ライトが照らす対象レイヤーを選択します。
- **アバターのみ（Player / PlayerLocal / MirrorReflection）**: カリングマスクを
  アバター関連レイヤーのみに一括設定する簡易ボタンです（VRChat の標準レイヤー名で解決します）。

### 点灯テスト（エディタ機能）

Play モードに入らずに、配置中の照明を Scene ビューで確認するためのエディタ専用機能です。

`MashiroLightGroup` を選択するとインスペクタ下部に **「点灯テスト」** セクションが表示されます。

- **テスト明るさ**: スライダー（0〜1）。ランタイムと同じく `明るさ × intensityMultiplier` が
  `Light.intensity` に適用されます。テスト中にスライダーを動かすと即時反映されます。
- **色**: グループの `initialColor` を使用します。点灯中に `initialColor` を変更すると、
  プレビューへ動的に反映されます（テスト専用の色設定は廃止しました）。
- **点灯テストボタン**: クリックすると、子階層の **Light とビームライトを同時にスキャン**して
  点灯します。点灯中はボタンがオレンジ色（選択時カラー）で強調表示されます。
  **もう一度クリックするまで点灯したまま**になり、別オブジェクトを選択しても消えません。
- **自動 全解除**: 次のタイミングでは、点灯中のすべてのグループが自動的に消灯し、点灯前の
  状態に復元されます。
  - Play モードへの突入時
  - Unity 終了時
  - スクリプトの再コンパイル時

#### 非破壊プレビューについて

点灯テストはシーンを汚さないことを優先しています。

- 非アクティブな Light / ビームライトも対象にするため、`includeInactive` でスキャンします。
- Light は点灯前のアクティブ状態・明るさ・色を記憶し、消灯時にそのまま復元します。
- ビームライトのマテリアルは直接書き換えず `MaterialPropertyBlock` で上書きするため、
  共有マテリアルやマテリアルインスタンスを汚しません。消灯時に上書きを解除します。

> 注意: あくまで「点灯時の見た目」を簡易確認するプレビューです。スポット角（サイズ）や
> 色フェードなどランタイム固有の挙動は再現しません。

## ランタイムのサイズ・回転調整（ランタイム機能）

選択中の照明グループに対して、VRC 内でスポット角（サイズ）と縦横回転を調整できます
（オーナーのみ操作可・全員に同期）。いずれも**ビルド時の状態を基準（0）とした相対調整**です。

### サイズ

- `sizeSlider` は**ビルド時のスポット角からの ±30 度オフセット**として扱います
  （範囲は起動時に自動設定）。
- 実際の `spotAngle` は `ビルド時の角度 + オフセット` を **SpotAngle の有効範囲（1〜179 度）で
  クランプ**します。ビルド時が 170 度なら +30 に振っても 179 度で頭打ちになり、ライト自体の
  制限を超えません。ビーム形状も追従します。

### 回転（縦回転チルト / 横回転パン）

- `panSlider`（横回転）/ `tiltSlider`（縦回転）で、**ビルド時の向きから ±30 度**回転します。
- 回転対象はエディタの回転機能と同じく `MashiroLightGroup` 配下の `MashiroLightFixture` に
  倣います（`allowHorizontal` / `allowVertical` / `verticalAxis`）。パンはワールド垂直軸、
  チルトはローカル蝶番軸まわりで、デフォルトが傾いていても首振りが出ない計算です。
- 回転は遅延実行モードの保留対象外で、常に即時反映・同期します。

#### 回転対象の解決について（自動・操作不要）

`MashiroLightFixture` は VRChat ビルド時に除去されるため、ランタイム回転は回転対象・基準姿勢・
許容軸を `MashiroLightGroup` へ転記したデータを参照します。この転記は
**Play 開始時・ビルド時に自動で行われます**（`MashiroLightRotationBuildBaker`）。

- オペレータの操作は不要です。処理はビルド用の一時シーンに対して行われるため、元シーンは
  変更されません。処理時点の各灯体の向きが、ランタイムのパン/チルト 0 の基準になります。

> 補足: 自動処理は UdonSharp のシーン処理の後に走らせて proxy→Udon を確定させています。
> UdonSharp を大きくバージョンアップした際は、Play で回転が効くことを一度確認してください。

### UI セットアップ

`MashiroLightingManager` に以下を割り当てます（回転は任意機能。未割り当てなら何もしません）。

- `sizeSlider` / `sizeSliderGameObject`（既存）
- `panSlider` / `tiltSlider` … 回転スライダー（OnValueChanged に `OnPanSliderValueChanged` /
  `OnTiltSliderValueChanged` を割り当て）
- `panSliderGameObject` / `tiltSliderGameObject` … グループ選択中のみ表示する行オブジェクト

## 遅延実行モード（ランタイム機能）

フェーダーを動かしても即時にはライトへ反映せず、**「確定」ボタンを押した時点の値へ、
全プレイヤーのローカルで規定秒数かけてフェード**させるモードです。
本番中に複数のフェーダーをあらかじめ仕込んでおき、キッカケで一斉に転換する用途を想定しています。

- **モード切替**: **2 値スライダー**（`delayedModeSlider`。0=OFF / 1=ON、起動時に
  WholeNumbers・0〜1 へ自動設定）で ON/OFF を切り替えます（オーナーのみ操作可、状態は全員に同期）。
  OnValueChanged に `OnDelayedModeSliderChanged` を割り当てます。
  - ON 中はフェーダー操作・シーンプリセット呼出に加え、**色・サイズの変更や設定リセットも
    ライトへ反映されず、確定待ち**になります（確定時: 明るさは設定秒数フェード、色は約 2 秒
    フェード、サイズは即時反映）。
  - ON 中も A/B クロスフェードは使用できます。クロスフェードは常に**現在の表示値**から
    新アクティブ系統のフェーダー値へフェードするため、未確定の仕込みがあっても点灯が
    飛びません（確定フェードとクロスフェードは同時には実行できず、実行中はもう一方の
    操作が無視されます）。
  - OFF に戻すと、未確定のフェーダー値・保留中のプリセット色が即時反映されます。
- **確定**: 現在のアクティブ側フェーダー値を確定し、全プレイヤーのローカルで
  設定秒数かけてフェードします。フェード完了時にオーナーが同期値を書き込むため、
  後から入ったプレイヤーにも最終状態が反映されます。フェード中の再確定も可能です
  （現在の表示値から新しい目標へ滑らかに繋がります）。
- **変更前に戻す**: 確定前に仕込んだフェーダー・色・サイズの保留を破棄し、**実際に照明へ
  反映されている状態へフェーダーを戻します**（確定はしません）。仕込みをやり直したいときの
  キャンセル用です。ボタンの OnClick に `OnDelayedRevertButtonClicked` を割り当て、
  `delayedRevertButton` に設定します（`delayedControlsPanel` 内に置けばモード ON 時のみ表示）。
- **反映秒数**: `MashiroFadeDurationButtonHandler` を付けたボタンで選択します（例: 1 / 3 / 5 / 10 秒）。
  選択中のボタンは UI カラー規約（#E85900）でハイライトされます。

### UI セットアップ

1. モード切替用の 2 値スライダーを配置し、OnValueChanged に
   `MashiroLightingManager.OnDelayedModeSliderChanged`（UdonBehaviour → SendCustomEvent）を
   割り当て、`delayedModeSlider` に設定します。
2. 確定用の Button を配置し、OnClick に `OnDelayedCommitButtonClicked` を割り当て、
   `delayedCommitButton` に設定します。「変更前に戻す」用 Button は `OnDelayedRevertButtonClicked`
   を割り当て、`delayedRevertButton` に設定します。
3. 秒数ボタンをオペレーションボード配下に必要な数だけ配置し、それぞれに
   `MashiroFadeDurationButtonHandler` を付与して `lightingManager` と `durationSeconds` を設定、
   OnClick にハンドラの `OnClick` を割り当てます（ラベルは自動で「◯秒」になります）。
4. 確定・変更前に戻す・秒数ボタンをまとめた GameObject を `delayedControlsPanel` に設定すると、
   モード ON のときだけ表示されます。`delayedDurationLabel` を設定すると現在の秒数が表示されます。

## シーンプリセット

エディタで作った点灯状態（各グループの明るさ・色）を `MashiroLightScenePreset` として登録し、
VRC 内でボタンひとつでフェーダーへ呼び出せる機能です。

- **登録（エディタ）**: 照明コントロールウィンドウ（後述）で各グループをテスト点灯させ、
  プリセット名を入力してから「現在の状態を登録」を押すと、`MashiroLightingManager` の子に
  プリセットオブジェクトが作成されます（名前が空のあいだ、登録ボタンは非活性です）。
  テスト点灯中のグループはその明るさ・色、消灯中のグループは明るさ 0 で保存されます。
- **呼出（VRC 内）**: UI ボタンの OnClick に `MashiroLightScenePreset.OnButtonClick` を割り当てると、
  アクティブ側フェーダーがプリセット値に変わり、色も適用されます（オーナーのみ操作可）。
  - **通常モード**: フェーダーが `presetFadeDuration`（既定 2 秒）かけて目標値まで動き、
    照明もフェーダーに追従してフェードします。**アニメーション中はフェーダーが非活性**になり、
    完了すると操作可能に戻ります（クロスフェード中の呼出は無視されます）。
  - **遅延実行モード中**: フェーダーだけが即時に動き、**確定で反映**されます。
- プリセットはグループ名で照合します。グループをリネームした場合は該当エントリがスキップされ、
  Console に Warning が出ます（プリセットの上書き保存で追従できます）。

## ランタイムプリセットスロット（VRC 内で登録・読込・削除）

VRC 内で**現在の照明状態を空きスロットに登録**し、あとから**読込**・**削除**できる機能です。
本番中に作った状態をその場で保存しておく用途を想定しています。

- **スロット構成**: `presetSlotCount` で総数を決めます。`MashiroLightingManager` の子階層にある
  `MashiroLightScenePreset` が**件数ぶん先頭から「保護スロット」を占有**し、残りがランタイム
  登録用の空きスロットになります（プリセット 3 件・`presetSlotCount` 5 なら、保護 3 + 空き 2）。
  プリセット件数が `presetSlotCount` を超えると Console に Warning が出て、超過分は
  読み込まれません。
- **登録は共通ボタン**（`registerPresetButton`）で行い、**最小の空きスロットへ新規保存**します。
  スロットが満杯だと登録ボタンは非活性になります（スロット数以上は登録不可）。色は
  **パレット番号**で保存し、登録時に各グループの色を最も近いパレット色へ丸めます。
- **各スロットのボタンは「読込・削除」の 2 種**で、**使わないボタンは非表示**になります。
  - **空きスロット**: 何も表示しません。
  - **ランタイム登録済**: 読込・削除を表示。
  - **保護スロット（アップロード時に設定済み）**: **読込のみ表示**、削除は非表示。
- **削除は前詰め**: スロットを削除すると、それ以降のランタイム登録スロットが 1 つ前へ詰まり、
  途中に空きの穴ができません（保護スロットは先頭に固定されたまま動きません）。
- **登録スロットの自動命名**: 点灯中（明るさ > 0）のグループのうち**先頭のライト名**をとり、
  **「〇〇 他N灯」**（N＝先頭以外の点灯数）と自動で名付けます（1 灯だけなら「〇〇」、
  全消灯なら「（消灯）」）。名前は同期せず各クライアントで同じ内容から算出されます。
- **読込**: 「読込」で全グループのフェーダー・色へ反映します（通常モードは
  `presetFadeDuration` でフェード、遅延実行モード中は確定まで保留、という呼出仕様は
  シーンプリセットと同じ）。
- 操作はオーナーのみ・全員に同期します。**登録内容はインスタンス内でのみ有効**で、全員が
  退出してインスタンスが消えると失われます（保護スロットは毎回復活します）。

### UI セットアップ

`MashiroLightingManager` に以下を割り当てます（未割り当てなら機能は無効）。

- `presetSlotCount` … 総スロット数（保護＋空きの合計）
- `presetSlotPrefab` … スロット 1 個分のプレハブ。`MashiroLightPresetSlotHandler` を付け、
  `loadButton`（読込）/ `deleteButton`（削除）/ `label` を設定。各ボタンの OnClick には
  ハンドラの `OnLoadClick` / `OnDeleteClick` を割り当てます。
- `presetSlotParent` … スロットを並べる親（実行時にスロット数ぶん自動生成）
- `registerPresetButton` … 共通の登録ボタン。OnClick に `RegisterCurrentToSlot` を割り当て
- `presetSlotStatusLabel` … 使用状況（例: 3/8）を表示する任意ラベル

## 照明コントロールウィンドウ（エディタ機能）

メニュー **Tools > Mashiro Theater > Lighting Control** から開きます。
シーン内の全 `MashiroLightGroup` を一覧化し、Play モードに入らずにまとめて制御できます。

- **プレビュー**: 色選択パネル風のタイルで各グループの現在の点灯色（色 × 明るさ）を一覧表示します。
  タイルをクリックするとヒエラルキー上で選択されます。
- **一覧行**: 現在色スウォッチ / グループ名（クリックで選択）/ テスト明るさスライダー /
  色（`initialColor` の編集、点灯中は即時反映）/ 点灯テストのトグル。
- **全点灯 / 全消灯**: ツールバーから一括操作できます。
- **シーンプリセット**: 登録・選択・読込（テスト点灯で再現）・上書き・削除ができます。
  「選択」を押すとそのプリセットオブジェクトがヒエラルキーで選択・Ping されます。
  一覧の名前欄はそのまま編集でき、**プリセット名をいつでも変更**できます
  （表示名と GameObject 名の両方が更新されます。呼出はグループ名照合のため、
  プリセット名の変更は動作に影響しません）。
- 点灯操作はインスペクタの「点灯テスト」と同じ非破壊プレビューの仕組みを共有しています
  （テスト明るさも共有。Play 突入時などに自動で全解除されます）。

## プレビューパネル（ランタイム機能）

各照明グループについて、**編集中系統（A/B）の想定明るさ・色**をタイル風の見た目で表示する
機能です。「今どう点いているか」ではなく「編集している系統がどう点く予定か」を示すため、
**待機系統を編集していても、遅延実行モード中でも、色・明るさの変更が即座にプレビューへ
反映されます**（実際の点灯状態は下記の実明るさメーターで別途確認できます）。
表示方法は 2 通りあり、併用もできます（どちらもタイル色は「編集系統の色 × 編集系統フェーダー値」で、
編集系統の切替・色変更時に即時、通常時は約 0.1 秒ごとに更新されます）。

### A. フェーダーグループ内タイル（推奨）

FaderGroup プレハブ内にプレビュータイルを組み込む方式です。

1. FaderGroup プレハブ内の任意の位置に `Image` を追加します（**Raycast Target は OFF 推奨**）。
2. その Image を `MashiroIntensitySlidersHandler` の `previewImage` に設定します
   （**明るさ × 色**を反映）。未設定のグループでは何も表示されません（任意機能）。
3. 別途「色のみ」を反映する小さな丸インジケーターを置きたい場合は、その Image を
   `colorIndicatorImage` に設定します。**明るさは反映せず色だけ**を表示します
   （明るさ 0 でも色が見えます。任意）。

### 待機系統・遅延実行モード中の表示

プレビューは常に**編集中系統の想定値**（`GetBankColor(編集系統) × 編集系統フェーダー値`）を
表示します。したがって、ライブ系統（点灯中）とは別の待機系統を編集していても、また遅延実行
モードで確定前でも、色・明るさの変更がそのままプレビューに出ます。実際の点灯状態（ライブ）は
下記の実明るさメーターで確認してください。色・フェーダー値は A/B 系統ごとに全員へ同期される
ため、非オーナーのプレビューも同じ想定値を表示します。

### 実明るさメーター（任意）

フェーダーの隣に「実際の明るさ」を表示するメーターです。遅延実行モード中に、
現在の明るさ（メーター）と次の明るさ（フェーダー）を見比べる用途を想定しています。

1. FaderGroup プレハブ内に縦のバー用 `Image` を追加し、**Image Type = Filled /
   Fill Method = Vertical** に設定して `MashiroIntensitySlidersHandler` の
   `meterFillImageA` に割り当てます（バーの色はプレハブ側で自由に設定）。
2. 任意で数値表示用の TextMeshProUGUI を `meterValueLabelA` に割り当てると、
   実際の明るさが 0〜100 の整数で表示されます。
3. レイアウトの都合で A/B 両方のコンテナにメーターを置きたい場合は、
   `meterFillImageB` / `meterValueLabelB` にもう 1 組を割り当てます
   （**両方とも同じ実明るさ**を表示します。片方だけの設定でも動作します）。
4. いずれもクロスフェード・確定フェードの途中経過に約 0.1 秒周期で追従します。

### フェーダー値の数値表示（A/B 共通・任意）

「実際の明るさ」ではなく、**編集系統のフェーダーが指す値（設定値, 0〜100）**を表示するラベルです。
A/B で 1 つの TMP を共通利用したいとき（レイアウトの都合で数値の位置を固定したいとき）に使います。

- `MashiroIntensitySlidersHandler` の `intensityValueLabel` に TextMeshProUGUI を割り当てます。
- 表示内容は**編集系統のフェーダー値**で、編集系統を切り替えると自動的にその系統の値へ
  切り替わります（フェーダー操作・プリセット呼出・同期でも更新）。
- 実際の点灯明るさ（上記メーター）とは別物です。遅延実行モード中は「次の値（仕込み）」に
  相当し、実明るさはメーターで確認できます。

#### 縦グラデーション表示（任意）

バーを下から上へグラデーションさせたい場合は、同梱の
`MashiroUIVerticalGradient.shader`（シェーダー名 **Mashiro Theater/UI/Vertical Gradient**）
を使ったマテリアルを作成し、バー用 Image の **Material** に割り当てます。
オレンジ系のマテリアル `MashiroUIVerticalGradientOrange.mat` を同梱しており、`FaderGroup.prefab`
では既定でこれを使っています。

- UI/Default にグラデーション乗算を 1 つ足しただけの軽量シェーダーで、
  Mask / RectMask2D にも標準どおり対応します。
- 色はマテリアルの **Bottom Color / Top Color** で指定します（既定はオレンジ系）。
- グラデーションはバー全体に固定され、フィルが増えるほど上側の色が現れます。
- 注意: スプライトを SpriteAtlas に入れると UV がずれてグラデーション位置が
  崩れます。スプライトなし（None）か、アトラス化していないスプライトで使ってください。

### B. 独立パネル（自動生成）

1. タイルのプレハブを作成します（ルートに `Image`、任意で子に TextMeshProUGUI のラベル。
   Button は不要です）。
2. `MashiroLightingManager` の `previewTilePrefab` にプレハブ、`previewTileParent` に
   タイルを並べる親（Grid Layout Group 推奨）を設定します。
3. 実行時にグループ数ぶんのタイルが自動生成され、ラベルにはグループ名が入ります。

## 完全暗転（ランタイム機能）

黒箱（`_Common/Shaders/TwoSidedOverlay` シェーダー）の透明度 `_Alpha` を上げて画面を暗転
させる機能です。Timeline ではなく Udon の Update でローカル制御し、**複数の黒箱を 1 つの
制御でまとめて動かす**ため多重暗転になりません。

- **動作（トグル）**: ボタンを押すとフェードして暗転、もう一度押すとフェードして復帰します。
  暗転の保持時間は自由（次のキッカケまで暗転のままにできます）。フェード秒数はボタンごとに設定。
- **多重防止**: 暗転中は**暗転を開始したボタンのみ**が操作可能（復帰用）で、他の暗転ボタンは
  無効化されます。フェード中は全ボタン無効。
- オーナー操作・全員に同期します。後から入ったプレイヤーは、暗転中ならフェードなしで即座に
  暗転状態で参加します。
- **暗転中表示**: `blackoutIndicators`（GameObject 配列・複数可）を設定すると、**完全に
  暗転している間のみ**表示されます（フェードイン/アウト中は非表示。オペレータ向けの状態表示）。

### UI セットアップ

1. 暗転用の黒箱（`TwoSidedOverlay` マテリアルの Renderer）をシーンに用意し、
   `MashiroLightingManager` の `blackoutBoxes` に複数まとめて割り当てます
   （透明度は同シェーダーの `_Alpha` を決め打ちで制御します）。
2. 暗転ボタンをボードに必要な数だけ配置し、それぞれに `MashiroBlackoutButtonHandler` を付与、
   `lightingManager` と `fadeDuration`（フェード秒数。「一瞬」は 0 に近い値）・`displayName` を
   設定します。OnClick にハンドラの `OnClick` を割り当てます（ラベルは自動で表示名になります）。
3. 任意で `blackoutIndicators` に暗転中表示オブジェクトを（複数）割り当てます。

## Realtime ライト数の表示（ランタイム機能）

現在使用中（Intensity が 0 でない＝ライトの GameObject が有効化されている）の Realtime ライトの
合計数を表示し、しきい値を超えたら色で注意・警告を出す機能です。負荷の目安として使います。

- 各 `MashiroLightGroup` が自グループの Light 数をスキャン時に保持し、マネージャが
  「点灯中グループのライト数の合計」を約 0.1 秒ごとに集計します（クロスフェード・
  遅延フェード中の点灯/消灯もリアルタイムに追従。表示の書き換えは値が変化した時のみ）。
- しきい値は `lightCountCautionThreshold`（既定 3、この数以上で注意色）/
  `lightCountWarningThreshold`（既定 4、この数以上で警告色）で変更できます。
- 表示例: `Realtimeライト: 2`（通常色・白）/ `Realtimeライト: 3（注意）`（黄）/
  `Realtimeライト: 4（警告）`（赤）。各色は `lightCountNormalColor` /
  `lightCountCautionColor` / `lightCountWarningColor` で変更できます。

### UI セットアップ

TextMeshProUGUI のラベルをボード上に配置し、`MashiroLightingManager` の
`realtimeLightCountLabel` に設定するだけです（未設定なら何もしません）。

## フェーダーグループ全体の選択ボタン化

照明グループの選択は、**フェーダー列そのものを押して行います**。FaderGroup のルートに
Button + Image を置き、`MashiroIntensitySlidersHandler` の `selectButton` に割り当てて
**グループ全体をボタン化**する構成です（OnClick には `OnSelectButtonClicked` を割り当てます）。
グループ選択用の独立したボタン列はありません。

- **非選択時の配色は Button に設定した初期状態（ColorBlock）を起動時に自動取得**し、
  そのまま使います（Inspector の専用フィールドはありません）。選択時のみ選択色
  （マネージャの `faderSelectedColor`。規約どおり #E85900）を適用し、hover / press 色は
  選択色から自動派生させるため、黒ベースでも白く光りません。非選択に戻ると初期の配色へ
  まるごと復元されます。ルートの Image は白 1 色のスプライトにして、Button の
  Color Tint（Normal Color = #000000 など）で着色してください。
- **選択中アウトライン（任意）**: ルートの Image に `Outline` コンポーネントを付けて
  `selectionOutline` に割り当てると、**選択中のみ**アウトライン
  （マネージャの `faderSelectionOutlineColor`。規約どおり #E85900）でハイライトされます。
  非選択時は Outline が無効化され通常の見た目のままです。太さ（Effect Distance）は
  プレハブ側の設定値がそのまま使われるため、Outline コンポーネント上で調整してください。
- **選択中の背景色（任意）**: `selectionImage` に背景の Image を割り当てると、
  Button の Color Tint とは独立に、選択中のみその Image を選択色で
  直接着色します（非選択時は初期色へ自動復元）。Button の Target Graphic が背景以外
  （小さなインジケータ等）を向いている構成でも背景色を変えられます。
  Target Graphic と同じ Image を指定すると Tint と乗算になるため避けてください。
  `selectionImage` を設定した場合、Button の ColorBlock には触れません。

### テーマカラーの集約

デザイン統一のため、指定可能な色は `MashiroLightingManager` に集約されています。
フェーダーグループ（生成プレハブ）側の色フィールドは廃止し、起動時にマネージャから
一括配布されます。

| Manager のフィールド | 用途 |
| --- | --- |
| `faderSelectedColor` | フェーダーグループ選択時のボタン/背景色 |
| `faderSelectionOutlineColor` | フェーダーグループ選択時のアウトライン色 |
| `activeImageColor` / `inactiveImageColor` | A/B 丸インジケータの点灯/消灯色 |
| `editBankColorA` / `editBankColorB` | 編集中アウトラインの色（A=オレンジ / B=シアン） |
| `lightCountNormalColor` / `lightCountCautionColor` / `lightCountWarningColor` | Realtime ライト数の表示色 |

UI カラー規約で固定の配色（通常ボタン #000000 / 選択 #E85900 / テキスト #FFFFFF・#999999）は
規約どおり各所でハードコードされており、テーマカラーの対象外です。

## A/B 系統（1 列表示・編集系統の切替）

フェーダーは **1 列表示**で、表示・編集する系統（A / B）を切り替えて使います。A/B には
明るさ・**色**・**サイズ**を別々に保持し、クロスフェードで系統ごと転換します。用語は 2 つ:

- **編集系統**: いま UI に表示・編集している系統。編集系統スライダーで切り替え。
- **ライブ系統**: いま実際に点灯している系統。クロスフェード実行で切り替え（＝転換）。

### 編集系統の切替（`editBankSlider`）

- `editBankSlider`（**0=A / 1=B**、起動時に WholeNumbers・0〜1 へ自動設定）を割り当て、
  OnValueChanged に `OnEditBankSliderChanged` を設定します（オーナーのみ操作可・全員に同期）。
- 切り替えると、フェーダー・**色・サイズ**の編集対象がその系統の値に切り替わります
  （A/B で別々に保持）。編集系統が**ライブ系統**のときは変更が即座に照明へ反映され、
  **待機系統**のときは保持のみ（点灯は変わりません）。
- FaderGroup プレハブ側で、各スライダーを包むオブジェクトを
  `MashiroIntensitySlidersHandler` の `sliderAContainer` / `sliderBContainer` に設定すると、
  編集系統のフェーダーだけが表示されます。

### 編集中の明示（アウトライン）

- `editFaderAreaOutline`（フェーダーエリア）に `Outline` を割り当てると、**編集系統に応じて
  色が切り替わります**（A=`editBankColorA`／既定オレンジ、B=`editBankColorB`／既定シアン）。
  常時表示で色のみ変化、太さはプレハブ側の Effect Distance を使います。
- クロスフェードボタン（`A → B` などの実行ボタン）の枠色は**色替えの対象外**です（演出上
  固定にするため）。枠の色はプレハブ側の `Outline` で自由に設定してください。

### ライブ系統の明示 & クロスフェード（点灯切替）

- `sliderAImage` / `sliderBImage`（クロスフェード枠の丸インジケータ）が、ライブ系統側だけ
  `activeImageColor`（点灯）になります。切り替えは**クロスフェード開始時点**で即時反映。
- `bankALiveLabel` / `bankBLiveLabel`（任意）は**ライブ系統の行にのみ**「LIVE」表記を表示します。
- `crossfadeButtonLabel` は **「A → B」/「B → A」**（ライブ → 待機）を自動表示します。
- **クロスフェード実行**（`crossfadeButton` → `OnCrossfadeButtonClicked`）で、ライブ系統が
  切り替わり、**明るさに加えて色・サイズも新ライブ系統の値へ**切り替わります
  （色は約 2 秒フェード、サイズは即時）。
- **クロスフェードの秒数**は `crossfadeDuration`（既定 1.5 秒）で設定します。明るさはこの秒数
  かけて各クライアントのローカルで補間されます。

### 運用

- 編集系統はクロスフェードしても自動では切り替わりません（明示操作のみ）。
  - 待機系統を編集 → **クロスフェード**で転換（従来の卓運用）
  - ライブ系統を編集（遅延実行モード）→ **確定**で転換

## オペレーター UI の折りたたみ（ランタイム機能）

`MashiroConsoleFoldToggle` は、フェーダー等のオペレーター UI グラフィックをまとめて
表示/非表示できるトグルです。**SetPassCall 削減**が目的で、オペレーターや卓を見たい
スタッフは展開、それ以外の観客はデフォルト折りたたみ、という運用を想定しています。

- **ローカル専用**: 折りたたみ状態は同期しません。各自が自分の視界だけを畳みます
  （同期すると一人が畳んだだけで全員から消えてしまうため）。
- **初期状態**: `startExpanded`（既定 false ＝折りたたみ）で決めます。観客中心の世界では
  false のままにしておくと、入室時点では畳まれた状態になります。
- **レイアウトのプライミング**: 動的生成フェーダーは「最初の 1 回だけ」レイアウトが組み直る
  ため、そのまま表示すると初回だけ表示がガタッと動きます。`primeLayoutOnStart`（既定 true）が
  ON のとき、**初期状態（ON/OFF）にかかわらず**読込中（操作前）に一度だけ対象を展開して
  レイアウトを確定させます。
  - **初期折りたたみ**: 展開 →（確定）→ `primeFrames` フレーム後に畳む。
  - **初期展開**: 展開 →（確定）→ 一瞬畳む → 次フレームで開き直す（＝クリーンな状態で表示）。
    最初から表示したい場合でも初回レイアウトずれが残りません（開き直しの一瞬の畳みは、
    スポーン地点の目前でなければ通常気になりません）。
  - `primeFrames`（既定 3）は Manager 側のレイアウト再構築（生成の次フレーム）が走り終わる
    猶予を確保する値で、通常は既定のままで問題ありません。プライミング自体が不要な
    （動的生成でない）UI では `primeLayoutOnStart` を false にできます。

### 安全な対象の選び方（重要）

`foldTargets` には **純粋な UI グラフィックのオブジェクトだけ**を割り当ててください。
非表示（SetActive(false)）にした GameObject は毎フレームの `Update()` が回らず、Udon の
`OnDeserialization`（同期受信）も取りこぼします。そのため次のものは**絶対に対象へ含めない**
でください（含めるとフェード停止・暗転解除・同期漏れの事故になります）。

- `MashiroLightingManager` … クロスフェード・遅延・暗転フェードをローカル Update で駆動
- ライト本体（`MashiroLightGroup` / `Light`）… 消灯・色トランジション停止
- 暗転の黒箱（`blackoutBoxes` の Renderer）… その視点だけ暗転が解除される

これらはトグル対象の階層の外（常時アクティブ）に置いてください。

### UI セットアップ

1. フェーダー群などの UI グラフィックを、Manager・ライト・黒箱を含まない親オブジェクトに
   まとめ、`MashiroConsoleFoldToggle` の `foldTargets` に割り当てます（複数可）。
2. トグルボタンを**折りたたみ対象の外**に置き（畳んでもボタンは残す必要があるため）、
   OnClick にハンドラの `OnToggleClick` を割り当てます。
3. 任意で状態ラベル（`stateLabel`）と文言（`expandedLabel` / `collapsedLabel`）を設定します。
4. 観客向けに畳んだ状態で始めるなら `startExpanded` を false のままにします。

## 同期の仕組み（仕様）

明るさ・色のフェードは**各クライアントのローカルで実行**され、ネットワークには
**確定値・目標値のみ**を同期します（フェードの途中値は同期しません）。

- **明るさ**: 同期されるのは確定値のみで、**全グループ分を `MashiroLightingManager` が
  まとめて保持**します（`MashiroLightGroup` は明るさを同期しません）。確定値は
  **フェード開始の時点**で書き込まれ、クロスフェード・確定フェードは各クライアントが
  ローカルで補間して同じ値へ着地します。フェード実行中は同期で届いた確定値を適用しません。
- **色**: 同期されるのは目標色のみ。色の変化（約 2 秒フェード）は各クライアントの
  ローカルで実行します。
- **サイズ・回転・A/B 系統の保持値・フェーダー値**: 値そのものを同期し、受信時に即時反映します。
- 後から入ったプレイヤーは、受信した確定値・目標色をフェードなしで即時反映して現在の
  状態に合流します（暗転中なら即座に真っ暗になります）。フェード進行中に入室した場合は
  フェード後の確定値で合流します。

> 明るさの確定値とフェード開始の合図を同じコンポーネントで同期しているため、両者は必ず
> 同一パケットで届きます。片方だけが先に届いて「フェードせず切り替わる」「フェード後に
> 古い値で一瞬戻る」といったことは起きません。

## API リファレンス

### `MashiroLightingManager`

**UI へ手配線するもの**

| シグネチャ | 用途 | 配線先 |
| --- | --- | --- |
| `OnCrossfadeButtonClicked()` | ライブ系統を転換（クロスフェード実行） | `crossfadeButton` の OnClick |
| `OnEditBankSliderChanged()` | 編集系統 A/B の切替 | `editBankSlider` の OnValueChanged |
| `OnDelayedModeSliderChanged()` | 遅延実行モードの ON/OFF | `delayedModeSlider` の OnValueChanged |
| `OnDelayedModeToggleClicked()` | 遅延実行モードのトグル（ボタン式で組む場合の代替） | Button の OnClick |
| `OnDelayedCommitButtonClicked()` | 仕込んだ変更を確定し全員へフェード反映 | `delayedCommitButton` の OnClick |
| `OnDelayedRevertButtonClicked()` | 仕込みを破棄して実際の状態へ戻す | `delayedRevertButton` の OnClick |
| `OnSizeSliderValueChanged()` | 選択中グループのサイズ変更 | `sizeSlider` の OnValueChanged |
| `OnPanSliderValueChanged()` | 選択中グループの横回転（パン） | `panSlider` の OnValueChanged |
| `OnTiltSliderValueChanged()` | 選択中グループの縦回転（チルト） | `tiltSlider` の OnValueChanged |
| `ResetSelectedLightGroup()` | 選択中グループの色・サイズ・回転をリセット | `resetButton` の OnClick |
| `OnTakeOwnershipButtonClicked()` | 操作権（オーナー）を取得 | `takeOwnershipButton` の OnClick |
| `RegisterCurrentToSlot()` | 現在の照明状態を空きスロットへ登録 | `registerPresetButton` の OnClick |

**内部連携用（配線不要）**

| シグネチャ | 用途 |
| --- | --- |
| `SelectLightGroup(int index)` | グループ選択のトグル（フェーダー列のハンドラが呼ぶ） |
| `OnColorPresetSelected(int index)` | 色プリセットの選択（色ボタンハンドラが呼ぶ） |
| `UpdateSelectedLightGroupColor(Color color)` | 選択中グループへ色を反映（遅延実行モード中は保留） |
| `UpdateSelectedLightGroupSize(float sizeOffset)` | 選択中グループへサイズを反映（遅延実行モード中は保留） |
| `CanLocalPlayerControl()` | ローカルプレイヤーが操作可能（=オーナー）かを返す |
| `GetColorPreset(int index)` | パレット番号から色を取得 |
| `ApplyScenePreset(MashiroLightScenePreset preset)` | シーンプリセットを適用（プリセットボタンが呼ぶ） |
| `LoadPresetSlot(int slot)` / `DeletePresetSlot(int slot)` | ランタイムスロットの読込・削除（スロットハンドラが呼ぶ） |
| `ToggleBlackout(float fadeDuration, int buttonIndex)` | 完全暗転のトグル（暗転ボタンハンドラが呼ぶ） |
| `SetDelayedFadeDuration(float seconds)` | 確定フェードの反映秒数を設定（秒数ボタンハンドラが呼ぶ） |
| `SetLiveIntensity(int index, float value)` | 1 グループの明るさ確定値を設定・反映・同期（フェーダー/プリセットから呼ぶ） |
| `UpdateColorSelectionUI()` | 色選択ハイライトの再描画 |
| `RefreshBankLayout()` | 起動時のレイアウト組み直し（遅延イベント用） |
| `IsSliderAActive` / `IsDelayedModeEnabled` | ライブ系統が A か／遅延実行モード中か（プロパティ） |
| `OnDeserialization()` | 同期受信時のコールバック。フェード開始判定と UI 反映（VRChat が呼ぶ／内部専用） |
| `OnOwnershipTransferred(VRCPlayerApi player)` | オーナー変更時のコールバック。操作権 UI の更新（VRChat が呼ぶ／内部専用） |

### `MashiroLightGroup`

すべて内部連携用（UI からの手配線は不要）。

| シグネチャ | 用途 |
| --- | --- |
| `SetColorWithFade(Color newColor)` | 目標色を設定しローカルでフェード（同期は目標色のみ） |
| `SetBankColor(bool isA, Color color)` / `GetBankColor(bool isA)` | A/B 系統別の保持色の設定・取得 |
| `SetSizeOffset(float offset)` / `GetSizeOffset()` | サイズオフセットの適用・取得 |
| `SetBankSizeOffset(bool isA, float offset)` / `GetBankSizeOffset(bool isA)` | A/B 系統別の保持サイズの設定・取得 |
| `SetPan(float pan)` / `SetTilt(float tilt)` / `GetPan()` / `GetTilt()` | 回転の適用・取得 |
| `GetMaxSizeOffset()` / `GetMaxRotationAngle()` | 可動範囲定数の取得（スライダー範囲の設定用） |
| `Initialize(int index)` | 起動時初期化（ライトのスキャン・初期値適用） |
| `SetSliderHandler(MashiroIntensitySlidersHandler handler)` | フェーダーハンドラの関連付け |
| `UpdateFromSlider(float value, bool isSliderA)` | フェーダー値の保持・同期 |
| `ApplyIntensityDirect(float intensity)` | 明るさを実ライトへ適用する唯一の入口（マネージャが呼ぶ。同期はしない） |
| `ResetToInitialValues()` | サイズ・回転・色を初期値へ戻す（現在は呼び出し元がない予約 API。卓の「リセット」は `MashiroLightingManager.ResetSelectedLightGroup()` が担当） |
| `GetName()` | グループ名（GameObject 名） |
| `GetDisplayIntensity()` / `GetDisplayColor()` | 現在表示中の明るさ・色（フェード途中値を含む） |
| `GetInitialSize()` | ビルド時のスポット角（現在は呼び出し元がない予約 API） |
| `GetRealtimeLightCount()` / `AreLightsEnabled()` | Realtime ライト数／点灯中か |
| `OnDeserialization()` | 同期受信時のコールバック。確定値の反映と色フェードの開始（VRChat が呼ぶ／内部専用） |

### `MashiroIntensitySlidersHandler`

**UI へ手配線するもの（FaderGroup プレハブ内で設定）**

| シグネチャ | 用途 | 配線先 |
| --- | --- | --- |
| `OnSliderAValueChanged()` / `OnSliderBValueChanged()` | A/B フェーダーの操作 | `sliderA` / `sliderB` の OnValueChanged |
| `OnSelectButtonClicked()` | グループ選択 | `selectButton` の OnClick |

**内部連携用（配線不要）**

| シグネチャ | 用途 |
| --- | --- |
| `Initialize(MashiroLightingManager mgr, MashiroLightGroup group, int index)` | 生成時初期化 |
| `SetThemeColors(Color selectedColor, Color outlineColor)` | 選択時テーマカラーの配布 |
| `SetValueFromPreset(float value)` | プリセット呼出によるフェーダー値の設定 |
| `SetSlidersInteractable(bool interactable)` / `SetOwnerControlEnabled(bool enabled)` | 操作可否の切替 |
| `UpdateSelectButtonUI(bool isSelected)` / `UpdateBankVisibility(bool showSliderA, bool showSliderB)` | 選択・系統表示の更新 |
| `UpdatePreviewColor(Color color)` / `UpdateColorIndicator(Color color)` / `UpdateMeter(float intensity)` | プレビュー・メーターの更新 |
| `UpdateSliderUI(float valueA, float valueB)` | 同期受信時のスライダー表示更新 |

### ボタン・スロット系ハンドラ

| コンポーネント | UI へ手配線するもの | 内部連携用（配線不要） |
| --- | --- | --- |
| `MashiroColorButtonHandler` | `OnClick()` → プレハブ内 Button の OnClick | `Initialize(mgr, color, index)` |
| `MashiroBlackoutButtonHandler` | `OnClick()` → 暗転ボタンの OnClick | `Initialize(mgr, index)` / `SetInteractable(bool)` |
| `MashiroFadeDurationButtonHandler` | `OnClick()` → 秒数ボタンの OnClick | `UpdateSelectedUI(bool)` / `SetInteractable(bool)` |
| `MashiroLightPresetSlotHandler` | `OnLoadClick()` / `OnDeleteClick()` → プレハブ内 Button の OnClick | `Initialize(mgr, index)` / `UpdateDisplay(...)` |
| `MashiroLightScenePreset` | `OnButtonClick()` → プリセット呼出ボタンの OnClick | （データ保持のみ） |
| `MashiroConsoleFoldToggle` | `OnToggleClick()` → 折りたたみトグルの OnClick | `FinishPrimeLayout()` / `ReopenAfterPrime()`（遅延イベント用） |

### `MashiroLightFixture`（エディタ専用）

エディタ拡張から呼ばれる編集時マーカーです（手配線不要）:
`SaveDefaultRotation()` / `EnsureDefaultRotation()` / `RestoreDefaultRotation()` /
`SetPanTilt(float pan, float tilt)`、プロパティ `HasDefaultRotation` / `DefaultRotation` /
`PanAngle` / `TiltAngle`。

## 付録: UI 参照フィールド早見表（レイアウト対応）

インスペクタの参照名が実際の画面上のどの部品か分かりにくいため、対応をまとめます。
「種別」は割り当てる Unity コンポーネント、「画面上」は見た目・位置の目安です。

「必須／任意」は次の意味です。同梱の `MashiroLightingManager.prefab` を使う場合、**必須の
うち自分で設定するのは `lightGroupParent` だけ**で、残りはプレハブ側で配線済みです。

- **必須**: 未設定だと起動時の初期化が例外で止まり、卓が一切動かなくなります。
- **任意**: 未設定なら、その機能だけが無効になります。

### A. `MashiroLightingManager`（ボード全体の統括）

#### 基本参照

| フィールド | 必須/任意 | 種別 | 画面上 | 役割 |
| --- | --- | --- | --- | --- |
| `lightGroupParent` | 必須 | GameObject | （非表示・シーン上の親） | 配下の `MashiroLightGroup` を自動収集する起点 |
| `sliderPrefab` | 必須 | GameObject | （プレハブ） | フェーダーグループ 1 列分の生成元 |
| `sliderParent` | 必須 | Transform | フェーダーが横に並ぶ列の親 | 生成したフェーダーグループの配置先 |
| `colorButtonPrefab` / `colorButtonParent` | 必須 | GameObject / Transform | 色ボタンの並ぶ領域 | 色選択ボタンの生成元／配置先 |
| `ownerNameText` | 任意 | TMP | 「オペレーター名」表示 | 現在のオーナー名 |
| `selectedGroupLabel` | 必須 | TMP | 選択中グループ名表示 | いま選択中の照明グループ名 |
| `selectedColorLabel` | 任意 | TMP | 選択中の色名表示 | いま選択中の色プリセット名 |
| `takeOwnershipButton` | 任意 | Button | 「操作権を取得」ボタン | 押すと操作権を自分に。自分がオーナーの時は自動で非表示 |

#### サイズ・回転（選択中グループへ適用）

| フィールド | 必須/任意 | 種別 | 画面上 | 役割 |
| --- | --- | --- | --- | --- |
| `sizeSlider` / `sizeSliderGameObject` | 任意 | Slider / GameObject | 「サイズ」スライダーとその行 | スポット角 ±30 度オフセット。行は選択中のみ表示 |
| `panSlider` / `panSliderGameObject` | 任意 | Slider / GameObject | 「横回転」スライダーとその行 | パン ±30 度。行は選択中のみ表示 |
| `tiltSlider` / `tiltSliderGameObject` | 任意 | Slider / GameObject | 「縦回転」スライダーとその行 | チルト ±30 度。行は選択中のみ表示 |
| `resetButton` / `resetButtonGameObject` | 任意 | Button / GameObject | 「リセット」ボタンとその行 | 色を `initialColor` へ戻し、サイズ・回転を 0 に戻す |

#### A/B クロスフェード（点灯系統の切替）※名前に注意

| フィールド | 必須/任意 | 種別 | 画面上 | 役割 |
| --- | --- | --- | --- | --- |
| **`crossfadeButton`** | 任意 | Button | **「A → B」/「B → A」実行ボタンそのもの** | 押すとライブ系統を切り替える（＝転換） |
| `crossfadeButtonLabel` | 任意 | TMP | 上記ボタン内の文字 | 「A → B」「B → A」を自動表示 |
| `sliderAImage` / `sliderBImage` | 必須 | Image | A / B の丸インジケータ | ライブ系統側が点灯色（`activeImageColor`）になる |
| `bankALiveLabel` / `bankBLiveLabel` | 任意 | GameObject | ライブ系統行の「LIVE」表記 | ライブ側の行にのみ表示 |
| `crossfadeDuration` | （設定値） | float | — | クロスフェードの秒数（既定 1.5） |

> **紛らわしさの注意**: 「クロスフェードボタン」＝ `crossfadeButton`（上の実行ボタン本体）です。
> 以前あった `editCrossfadeAreaOutline`（クロスフェード“エリア”を囲う枠）は削除済みで、
> **実行ボタンの枠色はスクリプト管理外**になりました。枠色はボタンの `Outline` で直接設定します。

#### 編集系統の切替（1 列表示）

| フィールド | 必須/任意 | 種別 | 画面上 | 役割 |
| --- | --- | --- | --- | --- |
| `editBankSlider` | 任意 | Slider | 「編集系統」2 値スライダー（0=A / 1=B） | 表示・編集する系統を切り替える |
| `editFaderAreaOutline` | 任意 | Outline | **フェーダーエリアを囲う枠** | 編集系統で色が変わる（A=`editBankColorA` / B=`editBankColorB`） |

#### 遅延実行モード

| フィールド | 必須/任意 | 種別 | 画面上 | 役割 |
| --- | --- | --- | --- | --- |
| `delayedModeSlider` | 任意 | Slider | 「遅延実行」2 値スライダー（0=OFF / 1=ON） | 遅延実行モードの ON/OFF |
| `delayedControlsPanel` | 任意 | GameObject | 確定・秒数ボタンを含むパネル | 遅延実行モード中のみ表示 |
| `delayedCommitButton` | 任意 | Button | 「確定 / GO」ボタン | 仕込んだ変更を全員へフェード反映 |
| `delayedRevertButton` | 任意 | Button | 「変更前に戻す」ボタン | 仕込み（保留）を破棄して現状へ戻す |
| `delayedDurationLabel` | 任意 | TMP | フェード秒数の表示 | 現在の反映秒数 |

#### プレビューパネル（独立パネル）

| フィールド | 必須/任意 | 種別 | 画面上 | 役割 |
| --- | --- | --- | --- | --- |
| `previewTilePrefab` / `previewTileParent` | 任意 | GameObject / Transform | 色プレビューのタイル群 | 各グループの明るさ×色タイルの生成元／配置先 |

#### ランタイムプリセットスロット

| フィールド | 必須/任意 | 種別 | 画面上 | 役割 |
| --- | --- | --- | --- | --- |
| `presetSlotPrefab` / `presetSlotParent` | 任意 | GameObject / Transform | プリセットスロットの並ぶ領域 | スロット UI の生成元／配置先 |
| `registerPresetButton` | 任意 | Button | 「登録」共通ボタン | 現在の状態を最小の空きスロットへ登録（満杯で自動無効化） |
| `presetSlotStatusLabel` | 任意 | TMP | 「3/8」等の使用状況 | 使用スロット数の表示 |

#### 完全暗転 / Realtime ライト数

| フィールド | 必須/任意 | 種別 | 画面上 | 役割 |
| --- | --- | --- | --- | --- |
| `blackoutBoxes` | 任意 | Renderer[] | シーン中の黒箱（画面を覆う板） | まとめて `_Alpha` を上げ下げして暗転 |
| `blackoutIndicators` | 任意 | GameObject[] | 「暗転中」オペレータ表示 | 完全暗転中のみ表示（フェード中は非表示） |
| `realtimeLightCountLabel` | 任意 | TMP | 「Realtimeライト: N」表示 | 点灯中の Realtime ライト合計。しきい値で色変化 |

#### テーマカラー（色はここに集約）

| フィールド | 用途 |
| --- | --- |
| `faderSelectedColor` | フェーダーグループ選択時のボタン/背景色 |
| `faderSelectionOutlineColor` | フェーダーグループ選択時のアウトライン色 |
| `activeImageColor` / `inactiveImageColor` | A/B 丸インジケータの点灯/消灯色 |
| `editBankColorA` / `editBankColorB` | 編集系統アウトライン色（A=オレンジ / B=シアン） |
| `lightCountNormalColor` / `lightCountCautionColor` / `lightCountWarningColor` | Realtime ライト数の表示色 |

### B. `MashiroIntensitySlidersHandler`（フェーダーグループ 1 列＝動的生成）

`sliderPrefab` 側に付けるハンドラ。1 グループ分の縦 1 列に対応します。

| フィールド | 必須/任意 | 種別 | 画面上 | 役割 |
| --- | --- | --- | --- | --- |
| `sliderA` / `sliderB` | 必須 | Slider | A / B 系統の明るさフェーダー | 系統ごとの明るさ。1 列表示では編集系統のみ見える |
| `sliderAContainer` / `sliderBContainer` | 任意 | GameObject | A / B フェーダーを包む枠 | 編集系統のコンテナだけ表示（1 列表示の切替単位） |
| `labelText` | 任意 | TMP | 列の下のグループ名 | グループ名（例: ピンスポット上手） |
| `selectButton` | 任意 | Button | 列全体（グループ選択ボタン化） | 押すとそのグループを選択。未設定だとグループ選択ができなくなる |
| `selectionImage` | 任意 | Image | 選択時に着色する背景 | 選択中のみ選択色。Button の Tint とは独立 |
| `selectionOutline` | 任意 | Outline | 選択時のハイライト枠 | 選択中のみ表示 |
| `previewImage` | 任意 | Image | 列内のプレビュータイル | **明るさ × 色**を反映 |
| `colorIndicatorImage` | 任意 | Image | 小さい丸インジケータ | **色のみ**反映（明るさは無視） |
| `meterFillImageA` / `meterFillImageB` | 任意 | Image(Filled) | 実明るさメーター | 実際の明るさをバー表示（A/B どちらの列にも置ける） |
| `meterValueLabelA` / `meterValueLabelB` | 任意 | TMP | 実明るさの数値 | 実際の明るさ 0〜100 |
| `intensityValueLabel` | 任意 | TMP | フェーダー下の設定値（A/B 共通） | 編集系統フェーダーの設定値 0〜100。系統切替で表示も切替 |

### C. `MashiroConsoleFoldToggle`（オペレーター UI の折りたたみ）

| フィールド | 種別 | 画面上 | 役割 |
| --- | --- | --- | --- |
| `foldTargets` | GameObject[] | 折りたたむ UI グラフィック群 | まとめて表示/非表示。Manager・ライト・黒箱は含めない |
| `stateLabel` | TMP | トグルボタンの文字 | 展開/折りたたみで文言切替 |
| `startExpanded` / `primeLayoutOnStart` / `primeFrames` | bool / bool / int | （設定値） | 初期状態・レイアウトプライミングの制御 |

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
