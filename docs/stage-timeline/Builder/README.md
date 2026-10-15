# StageTimelineTools Builder

`StageTimelineConfig` に記述した公演設定（シーン・幕場の区切り・プリセット・演出指示）から、TimelineAsset・AnimationClip・設定バックアップを生成し、`StageTimelineManager` へシーン境界・配役・ワープ・連動イベントを書き込むエディタ拡張。Q シートウィンドウ（Q シート・遷移表・CSV 出力）、設定バックアップからの復元、外れた参照の再割り当てを持つ。ランタイムの仕様は [StageTimelineTools](../README.md) に記載する。

## 構成

| パス | 内容 |
|---|---|
| `Runtime/StageTimelineConfig.cs` | 公演設定コンポーネント（`MonoBehaviour`）と、シーン・幕場の区切り・プリセット・各演出エントリ・参照の控えのデータクラス |
| `Runtime/MashiroWarpPointGizmo.cs` | ワープ先 Transform に付く編集時専用の Gizmo コンポーネント（実行時は何もしない） |
| `Editor/StageTimelineBuilderWindow.cs` | エディタウィンドウ「Stage Timeline Builder」の本体（メニュー・ツールバー・タブ切替・Config の作成と読み込み・生成の呼び出し） |
| `Editor/StageTimelineBuilderWindow.Setup.cs` | 初期設定画面 |
| `Editor/StageTimelineBuilderWindow.Settings.cs` | 設定タブ |
| `Editor/StageTimelineBuilderWindow.Backups.cs` | 設定タブ「バックアップ」 |
| `Editor/StageTimelineBuilderWindow.References.cs` | 設定タブ「参照の再割り当て」 |
| `Editor/StageTimelineBuilderWindow.Presets.cs` | プリセットタブ |
| `Editor/StageTimelineBuilderWindow.Scenes.cs` | シーンタブ（一覧・詳細・幕場の区切り・タイムライン生成ボタン） |
| `Editor/StageTimelineBuilderWindow.SceneEntries.cs` | シーン詳細の演出の表 |
| `Editor/StageTimelineBuilderWindow.SceneActive.cs` | シーン詳細の継続中の演出の行 |
| `Editor/StageTimelineBuilderWindow.SceneState.cs` | シーン開始時点の継続状態の集計 |
| `Editor/StageTimelineBuilderWindow.SceneTable.cs` | シーン詳細の表の列幅・共通部品 |
| `Editor/StageTimelineBuilderWindow.SceneHelpers.cs` | シーン編集の補助（選択肢・ワープ地点の作成・ワープ先 Gizmo の付与と除去） |
| `Editor/StageTimelineBuilderWindow.Camera.cs` | カメラタブ |
| `Editor/StageTimelineBuilderStyles.cs` | ビルダーと Q シートウィンドウの色・スタイル・描画ヘルパー（`BuilderStyles`）と演出カテゴリ（`EffectCategory`） |
| `Editor/StageTimelineSceneListView.cs` | シーンタブ左のシーン一覧（`TreeView`） |
| `Editor/StageTimelineQSheetWindow.cs` | エディタウィンドウ「Q シート」 |
| `Editor/StageTimelineQSheetModel.cs` | Q シート・遷移表の集計 |
| `Editor/StageTimelineQSheetExporter.cs` | Q シート CSV 出力 |
| `Editor/StageTimelineDividers.cs` | 幕・場の区切りの番号付け・ページ分け・付け替え |
| `Editor/StageTimelineGenerator.cs` | タイムライン生成の本体。`StageTimelineManager` への書き込み・ワープマーカー・可視化トラック |
| `Editor/StagePlanning.cs` | シーン列から演出ごとの有効区間・シーン別指示・必要シーン尺を組み立てる |
| `Editor/TimelineWriter.cs` | トラック・クリップの書き込み（`TimelineWriters` クラス） |
| `Editor/AssetUtils.cs` | AnimationClip 生成・フォルダ作成・PostProcessVolume / CinemachineVirtualCamera 型解決などのユーティリティ |
| `Editor/StageTimelineConfigBackupWriter.cs` | 要約バックアップ・全項目バックアップの書き出しと読み込み・履歴管理 |
| `Editor/StageTimelineDirectorResolver.cs` | 適用先 `PlayableDirector` と生成物の親の解決 |
| `Editor/StageTimelineReferenceHints.cs` | 参照の控えの記録・候補の推測・参照の割り当て |
| `Editor/StageTimelineReferenceValidator.cs` | シーンの演出エントリの参照切れ判定 |

- 名前空間: `Runtime/` は `MashiroTheater.StageTimeline.Builder`、`Editor/` は `MashiroTheater.StageTimeline.Builder.Editor`。

## 依存

| 依存 | 区分 | 用途 |
|---|---|---|
| Unity Timeline | 必須 | TimelineAsset / ActivationTrack / AnimationTrack / GroupTrack |
| TextMeshPro | 必須 | ワープマーカーのテキスト |
| UdonSharp | 必須 | Udon イベントの対象型 `UdonSharpBehaviour` |
| `StageTimelineManager`（同パッケージ Runtime） | 必須 | 生成結果の書き込み先・適用先 `PlayableDirector` の解決元。`StageTimelineManager.prefab` は初期設定でシーンに配置される |
| `MashiroLightGroup`（`MashiroTheater-Utils`） | 必須（コンパイル） | 「LightGroup をスキャン」・照明プリセットのドラッグ＆ドロップ追加 |
| Cinemachine | 任意 | カメラトラック。`Cinemachine.CinemachineVirtualCamera` / `Cinemachine.CinemachineBrain` と、`CinemachineTrack` / `CinemachineShot`（`Cinemachine.Timeline` / `Unity.Cinemachine.Timeline` / `Unity.Cinemachine` 名前空間）をリフレクションで解決する |
| Post Processing Stack v2（`UnityEngine.Rendering.PostProcessing.PostProcessVolume`） | 任意 | ポストプロセストラック。型をリフレクションで解決し、未導入時はポストプロセスの生成をスキップする |
| [NoribenBeamlightShader](https://booth.pm/ja/items/1637978)（シェーダー `Noriben/noribenBeamLight`） | 任意 | 照明フェードの対象 MeshRenderer |

## 仕様

### エディタウィンドウ

- メニュー: `Tools/Mashiro Theater/Stage Timeline Builder`。タイトル `Stage Timeline Builder`、最小サイズ 760×560。
- ウィンドウを開いたとき・アクティブシーンを切り替えたときに、アクティブシーン内の `StageTimelineConfig` を検索して読み込む。
- 描画時に `StageTimelineConfig.UpgradeBuilderDataIfNeeded()` を呼ぶ。
- `setupCompleted` が `false` の間は初期設定画面のみを表示し、タブを表示しない。
- ツールバー:

| 項目 | 内容 |
|---|---|
| 設定 | 設定タブ。生成を妨げる条件（下記「タイムライン生成」）があるとき橙の点を付ける |
| プリセット | プリセットタブ |
| シーン | シーンタブ |
| カメラ | カメラタブ。`showCameraFeatures` が ON のときのみ表示する |
| Q シート ↗ | Q シートウィンドウを開く |
| 閲覧モード | ON の間は編集を受け付けない（ウィンドウ上部に「閲覧モード中は編集できません」と「解除」を表示） |

### 初期設定

- Config が無い、または `title` が空の場合: 「公演名」入力欄と「はじめる」を表示する。Config が無い場合は「作成済みの Config を使う」（Config 欄・「シーンから読み込み」）も表示する。
- 「はじめる」（Enter キーでも可）:
  - Config が無い場合は下記「Config の作成」を行う。
  - `title` が空の場合のみ、入力した公演名を `title` に設定する。
- 続けて 3 ステップを表示する: 1「出力先」（出力先フォルダ）/ 2「登場人物」（`characters`）/ 3「高度な機能」（機能スイッチ）。
- `stageTimelineManager` が未設定の場合、フッターに「StageTimelineManager が未設定です（設定タブで指定できます）」を表示する。進行は妨げない。
- 「完了」で `setupCompleted = true` にし、設定タブに完了案内を表示する。

Config の作成:

1. アクティブシーンに `StageTimelineConfig` が既にある場合は作成せず、それを読み込む（ダイアログを表示）。
2. GameObject `StageTimelineConfig` を作成し、`StageTimelineConfig` を追加して `InitializeAsNewBuilderData()` を呼ぶ。
3. シーン内の `StageTimelineManager` を検索する。無い場合は `StageTimelineManager.prefab`（GUID `d6039a8e2ad4bb94ebb38f0482116a81` で参照）をシーンのルートに配置する。Prefab が見つからない場合は Warning。
4. Manager がある場合:
   - Config の GameObject を Manager の子にする。
   - `stageTimelineManager` に Manager を設定する。
   - Manager 配下で名前に `暗転Box` または `暗転用オブジェクト` を含む GameObject を `blackoutBoxRoots` に、`暗転中ガイド` を含む GameObject を `blackoutGuideRoots` に追加する。
5. `blackoutBoxRoots` が空の場合は未割り当ての要素を 1 つ追加する。

- `title` を変更すると、GameObject 名が `StageTimelineConfig - {タイトル}`（タイトルが空なら `StageTimelineConfig`）に追従する（変更前の名前がこの形式と一致している場合のみ）。

### 設定タブ

左の一覧でページを切り替える。必須項目が空のページには橙の点を付ける。

| グループ | ページ | 内容 | 橙の点の条件 |
|---|---|---|---|
| 基本 | Config | `StageTimelineConfig` 欄、「タイトル」、「標準シーン尺」 | `title` が空 |
| 基本 | シーン連携 | 「StageTimelineManager」（未設定時「シーンから検索」）、「出力先フォルダ」（「選択…」は `Assets` 配下のみ受け付ける） | `stageTimelineManager` が未設定 |
| 基本 | 登場人物 | `characters` の一覧（「＋ 登場人物を追加」「−」）、「マーカー Prefab」 | — |
| 基本 | 高度な機能 | 機能スイッチ（カメラ / Animator / Udon イベント / ポストプロセス）。カメラ ON 時は「CinemachineBrain」欄（「シーンから検索」は型名 `CinemachineBrain` のコンポーネントを探し、複数あれば選択メニューを出す） | カメラ ON かつ `cinemachineBrain` が未設定 |
| 演出 | 暗転 | 「暗転用Cube」（`blackoutBoxRoots`）、「暗転中ガイド」（`blackoutGuideRoots`） | 削除されたオブジェクトへの参照がある、または「暗転用Cube」に未割り当ての要素がある |
| バックアップ・復元 | バックアップ | 下記「バックアップ」 | — |
| バックアップ・復元 | 参照の再割り当て | 下記「参照の再割り当て」 | — |

機能スイッチ:

| スイッチ | フィールド | OFF 時に表示しないもの |
|---|---|---|
| カメラ | `showCameraFeatures` | カメラタブ、Q シートのカメラ列 |
| Animator | `showAnimatorFeatures` | Animator パラメータ / Animator トリガーのプリセットとシーンの演出 |
| Udon イベント | `showUdonEventFeatures` | Udon イベントのプリセットとシーンの演出 |
| ポストプロセス | `showPostProcessFeatures` | ポストプロセスのプリセットとシーンの演出 |

- スイッチは表示のみを切り替える。OFF でもデータは保持し、生成に反映する。

「Config を初期化…」（左の一覧の下）:

- Config がプレハブインスタンスに含まれる（追加コンポーネントのオーバーライドでない）場合は実行しない。
- 確認ダイアログの後、全項目バックアップ（種類 `BeforeInitialize`）を書き出す。書き出せない場合は中止する。
- Config コンポーネントを削除して追加し直し、`InitializeAsNewBuilderData()` を呼ぶ（Undo 1 回で戻る）。
- GameObject 名が `StageTimelineConfig` で始まる場合は `StageTimelineConfig` に戻す。
- シーン内の `StageTimelineManager` を `stageTimelineManager` に設定し、暗転オブジェクトを Config の作成と同じ規則で登録する。
- シーンに配置したワープ地点は削除しない。

### プリセットタブ

- 左の一覧: 照明 / オブジェクト / アニメーション / BGM / SE。`showAnimatorFeatures` ON で Animator パラメータ / Animator トリガー、`showUdonEventFeatures` ON で Udon イベント、`showPostProcessFeatures` ON でポストプロセスを追加表示する。カメラのプリセットはカメラタブで扱う。
- 各カテゴリに参照切れのプリセット数を表示する。

| カテゴリ | 表の列 |
|---|---|
| 照明 | 表示名 / Light Root / Intensity / Color / 使用 |
| オブジェクト | 表示名 / GameObject / 使用 |
| アニメーション | 表示名 / 対象 / Clip / 使用 |
| BGM / SE | 表示名 / AudioSource / 音量 / 使用 |
| Animator パラメータ | 表示名 / Animator / パラメータ名 (Int) / 使用 |
| Animator トリガー | 表示名 / Animator / 使用 |
| Udon イベント | 表示名 / 対象 Udon / 使用 |
| ポストプロセス | 表示名 / Volume / 使用 |

- 対象を割り当てたとき、表示名が空なら対象の名前を表示名に入れる。
- ツールバー: 検索、絞り込み（すべて / 未使用 / 参照切れ）、「⚠ 参照切れ N」（参照切れの絞り込みを切り替える）、「この順番で保存」（見出しで並べ替えた表示順を保存順にする。番号順以外で並べ替えている場合のみ表示）。
- 行の「⋯」メニュー: 「デフォルト設定を反映」（照明・BGM・SE のみ）/「複製」（新しい `id` を採番して直後に挿入）/「削除」（使用中の場合は使用数を示して確認する）。
- 表の下: 「＋ {カテゴリ}を追加」（ポストプロセスは「＋ Volume を追加」）。照明カテゴリのみ「LightGroup をスキャン」を併置する。
- ドラッグ＆ドロップ欄: Hierarchy のオブジェクトをまとめて追加する。表示名はオブジェクト名。登録済みの対象とカテゴリに合わない対象は除外する。

| カテゴリ | 受け付ける対象 |
|---|---|
| 照明 | `MashiroLightGroup` を持つ、または子孫に `Light` を持つ GameObject（`MashiroLightGroup` があれば `initialColor` を `defaultColor` にする） |
| オブジェクト / アニメーション | GameObject |
| BGM / SE | `AudioSource` |
| Animator パラメータ / Animator トリガー | `Animator` |
| Udon イベント | `UdonSharpBehaviour` |
| ポストプロセス | PostProcessVolume を持つ GameObject（PPv2 未導入時は GameObject） |

- 右の欄「使うシーン」: 選択中のプリセットを使用しているシーンを一覧する。
- ポストプロセスの行: GameObject に PostProcessVolume が無い場合、または Is Global でない場合に警告を表示する。Is Global でない場合は「Is Global にする」で `isGlobal` を ON にする。
- 「LightGroup をスキャン」: アクティブシーン内の `MashiroLightGroup` のうち、どの照明プリセットの `lightRoot` にもなっていないものを照明プリセットとして追加する（`displayName` = GameObject 名、`defaultColor` = `MashiroLightGroup.initialColor`）。
- 「デフォルト設定を反映」:
  - 照明 / BGM: そのプリセットを参照し、`action` が `FadeIn`、または `Change` かつ `useDefaultValues` が ON のエントリに、プリセットの既定値（照明: `defaultIntensity` / `defaultColor`、BGM: `defaultVolume`）を書き込む。BGM の `Change` + `useDefaultValues` エントリは `pitch` を 1 にする。
  - SE: そのプリセットを参照するすべてのエントリの `volume` に `defaultVolume` を書き込む。
  - 対象エントリが無い場合はダイアログを表示して何もしない。

### シーンタブ

左にシーン一覧、右に選択したシーン（または区切り）の詳細を表示する。

シーン一覧:

- ツールバー: 検索、「絞り込み」（詳細に表示する演出カテゴリの切替・「すべて表示」・「すべて隠す」）、一覧を閉じるボタン（閉じた状態では前後のシーンへ移動するボタンを表示）。
- フッター: キュー数（`Cue N`）、「＋ シーン」（末尾に追加）。
- ドラッグで並べ替える。統合されたシーンはまとめて移動する。
- 右クリック（詳細の「⋯」も同じ）メニュー:

| 項目 | 動作 |
|---|---|
| 上に挿入 / 下に挿入 | 空のシーンを挿入する |
| 複製 | 直後に複製を挿入する。`sceneUid` は新しく採番し、ワープ先は同じ位置・向きのワープ地点を新規作成して差し替える |
| 次のシーンを統合 | `autoAdvance` を切り替える（最終シーンでは無効） |
| 統合を解除 | 前のシーンと自身の `autoAdvance` を OFF にする（統合グループ内のシーンのみ表示） |
| この上に場の区切りを入れる / この上に幕の区切りを入れる | 区切りを追加する（下記「幕・場の区切り」） |
| 削除 | シーンを削除する。そのシーンの上にある区切りは次のシーンへ移す（次のシーンが無い、または同じ種類の区切りが既にある場合は削除する） |

シーン詳細:

| 欄 | 内容 |
|---|---|
| 番号 | `#{シーングループ番号}`。グループ内 2 番目以降は `#{グループ番号}-{グループ内の順番}` |
| シーン名 | `sceneName` |
| キッカケ | `cue`。前のシーンが `autoAdvance` ON の場合は入力欄の代わりに「↳ 前のシーン（#N）から続けて進みます」を表示する |
| 尺 | 空欄は標準尺（`useCustomDuration = false`、`durationSeconds = 0`）。数値を入れると `useCustomDuration = true`、`durationSeconds` = 入力値（0 以上） |
| 次のシーンを統合 | `autoAdvance`。最終シーンでは OFF の間は操作できない |

- 演出はカテゴリごとの表に表示する。表は「このシーンで追加した演出」と「前のシーンから継続中の演出」（「#N から」の行）を含む。
- 参照切れのエントリは行に警告を表示する（判定は `StageTimelineReferenceValidator`）。
- フッター: 警告の要約（`⚠ 警告 N 件（シーン #…）`）または生成を妨げる条件の 1 件目、「タイムライン生成」。

演出の追加（「＋ 演出を追加 ▼」→ カテゴリ、または各表の追加ボタン）:

| 種別 | プリセット選択で作成するエントリ | 自由指定の項目名 → 作成するエントリ | 継続中の行の選択肢 → 作成するエントリ |
|---|---|---|---|
| 照明 | `LightFadeEntry`（`FadeIn`、`targetIntensity` / `targetColor` = プリセットの既定値） | 自由指定（Light を直接指定）→ `FadeIn` | 維持 / 変更 → `Change` / デフォルト（Preset のみ）→ `Change` + `useDefaultValues`（値 = プリセットの既定値）/ フェードアウト → `FadeOut` |
| オブジェクト | `ToggleEntry`（`Appear`） | 自由指定（GameObject を直接指定）→ `Appear` | 維持 / OFF → `Disappear` |
| アニメーション | `ObjectAnimationEntry`（`Play`） | 自由指定（GameObject と Clip を直接指定）→ `Play` | 維持 / 終了 → `Stop` |
| BGM | `BgmEntry`（`FadeIn`、`volume` = `defaultVolume`） | 自由指定（AudioSource を直接指定）→ `FadeIn` | 維持 / 変更 → `Change` / デフォルト（Preset のみ）→ `Change` + `useDefaultValues`（`volume` = `defaultVolume`、`pitch` = 1）/ フェードアウト → `FadeOut` |
| SE | `SeEntry`（`volume` = `defaultVolume`） | 自由指定（AudioSource を直接指定） | — |
| 暗転 | 「暗転を追加」→ `BlackoutEntry`（`FadeIn`） | — | 維持 / 解除 → `FadeOut` |
| ワープ | 登場人物を選択 → `WarpEntry`（`characterIndex`） | — | — |
| Animator パラメータ | `AnimatorParameterEntry`（`valueId` / `intValue` = 先頭の値） | 自由指定（Animator を直接指定） | — |
| Animator トリガー | `AnimatorTriggerEntry`（`triggerId` / `triggerName` = 先頭の Trigger） | 自由指定（Animator を直接指定） | — |
| Udon イベント | `UdonEventEntry`（`eventId` / `eventName` = 先頭のイベント） | 自由指定（UdonBehaviour を直接指定） | — |
| ポストプロセス | `PostProcessEntry`（`presetId`） | なし（Volume を解除）→ `presetId` が空のエントリ（直前に有効な Volume がある場合のみ表示） | — |

- プリセット選択は `bindingMode = Preset`、自由指定は `bindingMode = Direct`。
- 照明・オブジェクト・BGM は、前のシーンから継続中の対象と、このシーンで既に追加した対象のプリセットを選択肢から除く。
- 暗転は、前のシーンから暗転中の場合と、このシーンに `FadeIn` がある場合は追加できない。
- ポストプロセスは 1 シーン 1 件まで追加できる。
- ワープの行の「新規作成」はワープ地点を作成して `destinationTransform` に設定する（下記「ワープ地点と Gizmo」）。

### 幕・場の区切り

- `sceneDividers` の各要素（`SceneDivider`）は、すぐ下のシーンを `sceneUid` で指す。シーンの並び・番号・タイムラインには影響しない。
- 区切りの用途: シーン一覧の表示、Q シートウィンドウのページ分け、Q シート CSV の `幕` / `場` 列。
- 追加: シーンの右クリックメニュー「この上に場の区切りを入れる」/「この上に幕の区切りを入れる」。統合グループの 2 番目以降のシーン、および同じ種類の区切りが既にあるシーンには追加できない。
- 番号: 区切りを上から並べ、同じシーンの上では幕を場より上にする。幕は通し番号、場は幕の区切りを越えるたびに 1 から振り直す。表記は `N幕` / `N場`。
- 一覧の区切り行: クリックで選択、ドラッグで移動（統合グループの途中に移した場合はグループの先頭へ寄せる。移動先に同じ種類の区切りがある場合は移動しない）、右クリックで「名前を変える」/「削除」。
- 区切りの詳細: 表記、名前（`name`）、「削除」、「範囲」（場は次の区切りの手前まで、幕は次の幕の手前までのシーン番号）。
- シーンの並べ替え後も、区切りは並べ替え前と同じ行位置に残す（統合グループの途中になった場合はグループの先頭へ寄せる。同じシーンに同じ種類が重なった場合は削除する）。

### カメラタブ

- `showCameraFeatures` が ON のときのみ表示する。
- `cinemachineBrain` が未設定の場合は「CinemachineBrain が未設定です。設定タブの「高度な機能」で割り当ててください。」を表示する。
- 左「カット割り」: シーンごとの `CameraEntry`。列は No / シーン / アングル / タイミング（最初 / 最後）/ 遅延 / ✕。タイミングが「最後」の場合、遅延は 0 にする。「＋ 切り替えを追加」と右クリックメニュー（切り替えを追加 / カットを追加 / このカットを削除）で編集する。
- 右「アングル」: `cameraPresets`。「＋ アングルを追加」、選択中のアングルの「Scene ビューで見る」（Scene ビューを vcam の位置と向きに合わせる）・「選択」（Hierarchy で vcam を選択）、「⋯」メニュー（複製 / 削除）、使用シーンの一覧。
- アングルの表示色は並び順で決まる（`colorSlot` は使用しない）。

### タイムライン生成

- シーンタブの「タイムライン生成」で `StageTimelineGenerator.Generate` を呼ぶ。
- 押せる条件: `stageTimelineManager` 設定済み、`title` が空でない、シーン 1 件以上、閲覧モード OFF。
- 生成結果の Warning は Console に `[StageTimeline]` 付きで出し、続けて集計（`TimelineBuildResult.LogSummary`）を出す。

`Generate` の処理順:

1. `stageTimelineManager` が未設定ならシーン内を検索して設定する。
2. 適用先 `PlayableDirector` を解決する（下表）。解決できない場合は Error を出して終了する。
3. シーンが 0 件なら Error を出して終了する。
4. `{出力先}/{タイトル}` を作成し、要約バックアップ・参照の控え（`referenceHints`）・全項目バックアップ（種類 `Generate`）を書き出す。
5. `Anim/` 内の既存アセットをすべて削除する。
6. 演出の計画・シーン尺を求め、トラック・クリップを書き込み、`StageTimelineManager` へ書き込む。
7. `PlayableDirector` に TimelineAsset を割り当て、再生位置を生成前の位置（全長内に収める）にする。`Evaluate()` は Timeline ウィンドウのプレビュー中（`AnimationMode.InAnimationMode()`）のみ行う。

適用先 `PlayableDirector` の解決順:

| 順 | 条件 | 適用先 |
|---|---|---|
| 1 | `playableDirector` が設定済み | `playableDirector` |
| 2 | `stageTimelineManager` の `timeline` が設定済み | `timeline` |
| 3 | Manager 自身に `PlayableDirector` がある | そのコンポーネント |
| 4 | Manager の子孫に `PlayableDirector` がある | 最初に見つかったもの |
| 5 | いずれも無い | Manager の子に GameObject `Timeline` を作成し、`PlayableDirector`（`playOnAwake = false`）を追加する |

- 3〜5 で解決した場合は Manager の `timeline` に設定する。
- `stageTimelineManager` が未設定の場合は 1 のみ。

### シーンとシーングループ

- `autoAdvance` が ON のシーンは次のシーンと同じシーングループになる。グループ内のシーン境界にはチェックポイントを置かない（自動で次のシーンへ進む）。
- グループの表示名 = 先頭シーンの `sceneName`（空なら `シーン {グループ番号}`）。
- グループの「次のキッカケ」 = 次のグループの先頭シーンの `cue`。
- チェックポイント = `[0, グループ1の終了時刻, グループ2の終了時刻, …]`（整数秒に切り上げ。直前の値以下の場合は直前 + 1）。

### シーン尺

標準尺のシーン（`useCustomDuration` が OFF かつ `durationSeconds` が 0 以下）: 次の最大値。

| 対象 | 必要秒数 |
|---|---|
| 標準 | `defaultSceneDuration`（下限 0.1） |
| 照明 | `FadeIn` / `FadeOut`: `delaySeconds + fadeSeconds`。`Change`: `fadeSeconds` |
| 暗転 | `FadeIn`: `max(0.1, delaySeconds) + fadeSeconds`。`FadeOut`: `delaySeconds + fadeSeconds` |
| BGM | `playDelaySeconds`（0 の場合は 1/60）+ `fadeSeconds` |
| アニメーション | `ceil(遅延 + クリップ長)`（遅延は `Play` の `playDelaySeconds`、`Stop` は 0） |
| SE | `delaySeconds + AudioSource.clip の長さ` |
| カメラ（「最初」） | `max(0.1, delaySeconds) + 0.2` |
| ポストプロセス（先頭 1 件） | `max(0.1, delaySeconds) + max(1/60, fadeSeconds)` |

秒数指定のシーン（`useCustomDuration` が ON、または `durationSeconds > 0`）:

- 尺 = `durationSeconds`（0 以下なら `defaultSceneDuration`）。
- 次の必要秒数の最大値が尺を 0.001 秒超える場合、尺をその値へ延長する。

| 対象 | 必要秒数 | 判定に使う入力秒数 |
|---|---|---|
| 照明 | `max(リード, delaySeconds) + fadeSeconds`（リード: `FadeIn` / `Change` は 0.1、`FadeOut` は 0） | `delaySeconds + fadeSeconds` |
| 暗転 | `max(0.1, delaySeconds) + fadeSeconds` | `delaySeconds + fadeSeconds` |
| BGM | `max(リード, playDelaySeconds) + fadeSeconds`（リード: `FadeIn` は 1/60、それ以外は 0） | `playDelaySeconds + fadeSeconds` |
| アニメーション `Stop`（「最初」） | `stopDelaySeconds` | `stopDelaySeconds` |
| アニメーション `Play`（`SingleShot`） | `playDelaySeconds + クリップ長` | 同左 |
| カメラ（「最初」） | `max(0.1, delaySeconds) + 0.2` | `delaySeconds` |
| ポストプロセス（先頭 1 件） | `max(0.1, delaySeconds) + max(1/60, fadeSeconds)` | `delaySeconds + fadeSeconds` |

- 延長時、入力秒数の最大値も尺を 0.001 秒超える場合は Warning を出す。
- SE・アニメーション `Hold` は延長の対象外。

共通:

1. 各シーン尺の下限は 0.1 秒。
2. 各シーンの終了時刻（累積）を整数秒へ切り上げる。結果として各シーン尺は 1 秒以上の整数秒になる。
3. タイムライン全長 = `max(最終シーン終了時刻, SE・SingleShot アニメのクリップ終端の最大値) + 0.1`。

### 生成物

| 出力 | パス |
|---|---|
| TimelineAsset | `{出力先}/{タイトル}/{タイトル}_AllScenes.playable` |
| AnimationClip | `{出力先}/{タイトル}/Anim/` |
| 要約バックアップ | `{出力先}/{タイトル}/StageTimelineConfigBackup.json` |
| 全項目バックアップ | `{出力先}/{タイトル}/StageTimelineConfigBackup_{種類}_{yyyyMMdd_HHmmss}.json` |

- `{出力先}` = `generatedBaseFolder`。空、または `Assets` で始まらない場合は `Assets/StageTimelineTools/Generated`（後者は Warning を出す）。
- `{タイトル}` = `title` のファイル名に使えない文字を `_` に置換した値（`title` が空の場合は `Show`）。
- 既存の `.playable` がある場合は、ルートの GroupTrack `Generated` のみを削除して作り直す。それ以外のトラック（ユーザー追加トラック）は保持し、そのクリップを前回生成時のシーン内相対位置へ移動する（所属シーンが削除された場合は、前回順で直前に残っているシーンの終了時刻、無ければ 0 秒）。
- TimelineAsset: フレームレート 60、`DurationMode.FixedLength`。
- `PlayableDirector`: `playableAsset` に生成した TimelineAsset、`playOnAwake = false`、`extrapolationMode = Hold`、`timeUpdateMode = GameTime`、`initialTime = 0`。
- 照明ルート・BGM / SE の AudioSource・暗転オブジェクト・ワープマーカー・ポストプロセス Volume の GameObject に `Animator` が無ければ追加する。
- BGM / SE の AudioSource の `playOnAwake` が OFF なら ON にする。
- ポストプロセスの対象 Volume の `weight` を 0 にする。

AnimationClip のファイル名（`NNN` はシーン番号 3 桁）:

| 種別 | ファイル名 |
|---|---|
| 照明 | `{タイトル}_SceneNNN_{照明ルート名}_{FadeIn\|Change\|Hold\|FadeOut}.anim` |
| 照明（タイムライン末尾の保持） | `{タイトル}_Tail_SceneNNN_{照明ルート名}_Hold.anim` |
| BGM | `{タイトル}_Bgm_{AudioSource名}_SceneNNN_SceneNNN_{連番2桁}.anim` |
| SE | `{タイトル}_Se_{AudioSource名}_SceneNNN.anim`（同シーン 2 件目以降は `_{番号2桁}` を付加） |
| 暗転 | `{タイトル}_SceneNNN_Blackout_{オブジェクト名}_{FadeIn\|Hold\|FadeOut}.anim` |
| ワープマーカー | `{タイトル}_WarpMarker_{キャラクター名}.anim` |
| ポストプロセス | `{タイトル}_PP{Volume の登場順2桁}_{Volume名}_SceneNNN.anim` |

### 生成トラック

すべてルートの GroupTrack `Generated` の下に作成する。

| グループ | トラック | 内容 |
|---|---|---|
| `Objects` | ActivationTrack `{オブジェクト名}` | 表示区間 |
| `Animations` | AnimationTrack `{オブジェクト名} Animation` | AnimationClip の再生区間 |
| `Lights` | GroupTrack `{照明ルート名}` 内に ActivationTrack `Light Active - {名前}`（`Light` / ビーム MeshRenderer を持つ GameObject ごと）と AnimationTrack `Light Anim - {照明ルート名}` | 点灯区間と強度・色のカーブ |
| `BGM` | ActivationTrack `{AudioSource名} (Active)`、AnimationTrack `BGM - {AudioSource名}` | 有効区間と `m_Volume` / `m_Pitch` / `m_PlayOnAwake` のカーブ |
| `SE` | ActivationTrack `{AudioSource名} (SE Active)`、AnimationTrack `SE - {AudioSource名}` | 有効区間と `m_Volume` / `m_PlayOnAwake` のカーブ |
| `Blackout` | ActivationTrack `暗転 (アクティブ) - {名前}`、AnimationTrack `暗転アニメーション - {名前}`、ActivationTrack `暗転中ガイド - {名前}` | 暗転オブジェクトの有効区間・不透明度、ガイドの表示区間 |
| `Warp Markers` | ActivationTrack `Warp Marker Active - {キャラクター名}`、AnimationTrack `Warp Marker Move - {キャラクター名}` | ワープマーカーの表示と移動 |
| `Cameras` | CinemachineTrack `Cinemachine` | CinemachineShot。`cinemachineBrain` の CinemachineBrain にバインド |
| `Post Process` | AnimationTrack `PostProcess - {Volume名}` | Volume の `weight` のクリップ（名前 `SceneNNN {ON\|OFF\|FadeIn\|FadeOut}`） |
| `Animator Params` | AnimationTrack `{Animator名}.{パラメータ名}`（muted） | 値ごとの区間クリップ（名前 `{値の名前} (= {値})` または `= {値}`） |
| `Animator Triggers` | AnimationTrack `{Animator名} (Trigger)`（muted） | 発火位置のクリップ（名前 `▶ {Trigger名}`） |
| `Udon Events` | AnimationTrack `{Behaviour名} (Udon)`（muted） | 発火位置のクリップ（名前 `▶ {関数名}()`） |
| （直下） | AnimationTrack `Scene Markers`（muted） | シーングループごとのクリップ（名前 `#{番号} {表示名}`） |

- `Objects` 〜 `Cameras` の GroupTrack は常に作成する。`Post Process` は対象 Volume がある場合のみ、`Animator Params` / `Animator Triggers` / `Udon Events` は対象がある場合のみ作成する。
- muted のトラックは表示用で、再生に影響しない。Animator パラメータ / トリガー / Udon イベントの実行は `StageTimelineManager` が行う。

### 発火タイミング

S = シーン開始時刻、E = シーン終了時刻、d = エントリの遅延秒数。

| 演出 | 「最初」 / 開始 | 「最後」 / その他 |
|---|---|---|
| オブジェクト表示（`Appear`） | S + 0.1 + d（先頭シーンは S。d を無視） | E − 0.1 |
| オブジェクト非表示（`Disappear`） | S + 0.1 + d（E 以下） | E − 0.1 |
| アニメーション再生（`Play`） | S + `playDelaySeconds` | — |
| アニメーション停止（`Stop`） | S + `stopDelaySeconds`（シーン尺未満） | E |
| 照明 `FadeIn` / `Change` | S + max(0.1, d) からフェード開始 | — |
| 照明 `FadeOut` | S + d からフェード開始 | — |
| BGM `FadeIn` | S + d（d = 0 のときは S + 1/60）で有効化しフェード開始 | — |
| BGM `Change` | S + p + d からフェード開始（p = 同じ BGM の `FadeIn` 時の再生開始遅延。0 のときは 1/60） | — |
| BGM `FadeOut` | S + d からフェード開始 | — |
| SE | S + d + 1/60 | — |
| 暗転 `FadeIn` / `FadeOut` | S + max(0.1, d) からフェード開始 | — |
| ポストプロセス | S + max(0.1, d) からフェード開始 | — |
| ワープ | S + d | E − 0.2 |
| カメラ | S + max(0.1, d)（E − 0.2 を超える場合は E − 0.2 に寄せ、Warning） | E − 0.2 |
| Animator パラメータ | S + max(0.1, d)（E 以下） | — |
| Animator トリガー | S + max(0.1, d)（E 以下） | — |
| Udon イベント | S + max(0.1, d) | E − 0.1 |

- 「最後」指定のワープ・カメラ・Udon イベントでは d を使わない。
- オブジェクト・ワープ・Animator パラメータ・Animator トリガー・Udon イベントの発火時刻はシーン範囲 [S, E] に収める。
- 「最後」指定のワープ・カメラ・Udon イベントで、シーン尺がリード時間より短い場合は Warning を出す。

リード時間定数:

| 定数 | 値（秒） | 定義 | 対象 |
|---|---|---|---|
| `WarpSceneEndLeadSeconds` | 0.2 | `StageTimelineGenerator.cs` | ワープ「最後」 |
| `AnimatorParamSceneStartLeadSeconds` | 0.1 | `StageTimelineGenerator.cs` | Animator パラメータ |
| `AnimatorTriggerSceneStartLeadSeconds` | 0.1 | `StageTimelineGenerator.cs` | Animator トリガー |
| `UdonEventSceneStartLeadSeconds` | 0.1 | `StageTimelineGenerator.cs` | Udon イベント「最初」 |
| `UdonEventSceneEndLeadSeconds` | 0.1 | `StageTimelineGenerator.cs` | Udon イベント「最後」 |
| `CameraSceneStartLeadSeconds` | 0.1 | `TimelineWriter.cs` | カメラ「最初」 |
| `CameraSceneEndLeadSeconds` | 0.2 | `TimelineWriter.cs` | カメラ「最後」・「最初」の上限 |
| `LightFadeInMinLeadSeconds` | 0.1 | `StagePlanning.cs` | 照明 `FadeIn` / `Change` |
| `BlackoutFadeInMinLeadSeconds` / `BlackoutFadeOutMinLeadSeconds` | 0.1 | `StagePlanning.cs` | 暗転 |
| `PostProcessSceneStartLeadSeconds` | 0.1 | `StagePlanning.cs` | ポストプロセス |
| `ActivationTailPadding` | 0.1 | `TimelineWriter.cs` | オブジェクト表示・非表示のずらし幅、暗転中ガイドの前後余白、末尾延長 |

- `PostProcessMinFadeSeconds`（1/60 秒、`StagePlanning.cs`）: ポストプロセスのフェード秒数の下限。フェード 0 秒は 1/60 秒のフェードになる。

### 演出ごとの仕様

- オブジェクト: 同一シーン・同一対象のエントリは先頭 1 件のみ有効。表示中の `Appear`・非表示中の `Disappear` は無視する。
- アニメーション:
  - `Hold`: 同じ対象の `Stop` またはタイムライン末尾まで再生する。再生中の対象に新しい `Play` がある場合は、そのシーン開始で前の再生を終える。
  - `SingleShot`: 次のシーン開始（最終シーンではシーン終了）までクリップを配置する。クリップ長がその区間より長い場合はクリップ全長（タイムライン末尾まで）配置する。
- 照明:
  - 対象は `lightRoot` 配下の `Light` と、シェーダー `Noriben/noribenBeamLight` のマテリアルを持つ `MeshRenderer`。
  - `Light`: `m_Intensity` / `m_Color` を、MeshRenderer: `material._Intensity`（強度 × 0.05）/ `material._Color` をアニメーションする。
  - 点灯区間外は対象 GameObject を非アクティブにする。
  - `FadeIn` は強度 0・色 (0,0,0,0) から、`Change` は現在値から目標値へ、`FadeOut` は強度を 0 へフェードする（色は変えない）。
  - 消灯中の `Change` は `FadeIn` として扱う。
- BGM: `AudioSource.clip` を再生する。`FadeIn` は音量 0 から、ピッチ 1 で開始する。音量は 0–1、ピッチは −3–3 に制限する。`Change` で区切られた区間の有効化は連続させる。
- SE: `AudioSource.clip` を 1 回再生する。音量は 0–1 に制限する。同じ AudioSource の次の SE と重なる場合は、前の有効区間を次の開始 1/60 秒前で切る。クリップがシーン終了を超える場合はタイムライン末尾まで延長する。
- 暗転:
  - 1 シーンにつき先頭 1 件のみ有効。暗転中の `FadeIn`・非暗転中の `FadeOut` は無視する。
  - `blackoutBoxRoots` 配下の各 Renderer のマテリアル `_Color.a` / `_BaseColor.a`（`_Alpha` プロパティがあればそれも）と、各 `CanvasGroup` の `m_Alpha` をアニメーションする。
  - `blackoutGuideRoots` は不透明度 1 の区間の前後 0.1 秒を含めて表示する。
- ポストプロセス:
  - 1 シーンにつき先頭 1 件のみ有効（2 件以上は Warning）。
  - 有効な Volume は常に 0 または 1 つ。`presetId` が空のエントリは「なし」（現在の Volume を外す）。
  - 切り替えは、前の Volume の `weight` を 1→0、次の Volume の `weight` を 0→1 へ同じ時刻・同じ秒数で線形に変化させる。
  - 直前と同じ Volume への切り替えはスキップする（Warning）。
  - 対象 Volume ごとに全シーン分のクリップを並べる。`weight` が一定のシーンが続く場合は 1 クリップにまとめる。最後のクリップは `max(最終シーン終了 + 0.1, タイムライン全長)` まで延ばす。
  - 対象は PostProcessVolume を持ち、Is Global の Volume のみ。
- ワープ:
  - `StageTimelineManager` に `destinationTransform` の `position` と `eulerAngles.y` を書き込む。
  - `warpMarkerPrefab` 設定時、生成物の親（下記）の子 `_WarpMarkers` にキャラクターごとのインスタンス `WarpMarker_{番号2桁}_{キャラクター名}` を作成・更新する。タグ `EditorOnly`、非アクティブ、色はキャラクター順の固定 10 色。ワープ時刻から 2.0 秒間表示する。
- カメラ:
  - 全シーンのカメラ指定を時刻順に並べ、各指定の切替時刻から次の切替時刻（最後はタイムライン末尾）まで、そのプリセットの `virtualCamera` の CinemachineShot を置く。
  - `presetId` が空の指定は無視する。
  - `cameraPresets` が空、または有効な指定が 1 件も無い場合は CinemachineTrack を作成しない（`cameraPresets` が空の場合は `cinemachineBrain` 等の Warning も出さない）。
  - `CameraEntry` の `blendSeconds` / FOV / チルト・パン関連フィールドと、`CameraPresetEntry` の `activePriority` / `inactivePriority` / `defaultFov` / `colorSlot` は生成に使用しない。
- Animator パラメータ / トリガー: 対象 Animator の AnimatorController（`AnimatorOverrideController` は元のコントローラー）に同名パラメータがあり、型が Int / Trigger であることを検証する。AnimatorController に解決できない場合は検証を省略する（Warning）。
- Udon イベント: 対象型に public・引数なしの同名メソッドが無い場合は Warning のみ出して生成する。`ownerOnly` は Preset 指定時は選択肢の値、Direct 指定時はエントリの値を使う。

生成物の親（ワープマーカー `_WarpMarkers`・ワープ地点 `_WarpPoints`）:

- 適用先 `PlayableDirector` の GameObject。適用先が無い場合は Config の GameObject。
- 適用先の下に同名の子が無く、Config の下に同名の子がある場合は Config の GameObject。

### プリセットの参照方式

プリセットの `id` は GUID（`N` 形式）で自動採番する。エントリはプリセットを `presetId` で参照する。

| 方式 | プリセット | 生成時に参照する値 |
|---|---|---|
| 対象指定型 | オブジェクト（`TogglePresetEntry`）、アニメーション（`ObjectAnimationPresetEntry`）、カメラ（`CameraPresetEntry`）、ポストプロセス（`PostProcessPresetEntry`） | 対象（`target` / `clip` / `virtualCamera` / `volumeObject`）をプリセットから取得する |
| 初期値テンプレート型 | 照明（`LightPresetEntry`）、BGM（`BgmPresetEntry`）、SE（`SePresetEntry`） | 対象（`lightRoot` / `source`）はプリセットから取得する。強度・色・音量・ピッチはエントリの値を使う（プリセットの既定値は、追加時・「デフォルト」選択時・「デフォルト設定を反映」でのみエントリへ書き込む） |
| 選択肢列挙型 | Animator パラメータ（`values`）、Animator トリガー（`triggers`）、Udon イベント（`events`） | 対象はプリセットから取得する。値・Trigger 名・関数名はエントリの `valueId` / `triggerId` / `eventId` で選択肢を引く |

- オブジェクト・アニメーション・照明・BGM・SE は、プリセットが見つからない場合にエントリの Direct 用フィールド（`target` / `clip` / `lightRoot` / `source`）を使う。
- Animator トリガー / Udon イベントは、ID で選択肢が見つからない場合、エントリの `triggerName` / `eventName` と同名の選択肢で解決する。
- 選択肢を解決できないエントリは Warning を出してスキップする。

### StageTimelineManager への書き込み

`stageTimelineManager` 設定時、`SerializedObject` 経由で次を書き込む（未設定時は Warning を出して書き込まない）。

| 書き込み先 | 内容 |
|---|---|
| `checkPointSeconds` | チェックポイント（整数秒） |
| `sceneDisplayNames` / `sceneNextCues` / `sceneRangeStarts` / `sceneRangeEnds` | シーングループの表示名・次のキッカケ・シーン範囲 |
| `characterDisplayNames` | `characters` の `displayName`（空なら `Character {番号}`） |
| `warp*` | ワープ（時刻昇順） |
| `animatorParam*` / `animatorTrigger*` / `udonEvent*` | 連動イベント（時刻昇順） |
| `timeline` | 適用先 `PlayableDirector` |

### Warning / Error

Console に `[StageTimeline]` 付きで出力する。

| 条件 | 結果 |
|---|---|
| Config 未設定 / 適用先 `PlayableDirector` を解決できない / シーン 0 件 | Error。生成しない |
| `generatedBaseFolder` が `Assets` で始まらない | Warning。既定の出力先を使う |
| `stageTimelineManager` 未設定（`playableDirector` 設定済みで生成した場合） | Warning。Manager への書き込みをスキップ |
| 秒数指定のシーンで入力秒数が尺を超え、尺を延長した | Warning |
| オブジェクト: 同一シーン重複 / 表示中の表示 / 非表示中の非表示 | Warning。該当エントリを無視 |
| アニメーション: 対象またはクリップ未設定 / 再生していない対象の停止 / 再生中の対象の再生 | Warning |
| 照明: プリセット参照切れ / 同一シーン重複 / 消灯中の `Change`・`FadeOut` | Warning |
| BGM: 同一シーン重複 / 再生中の `FadeIn` / 停止中の `Change`・`FadeOut` / AudioSource にクリップ無し | Warning |
| SE: AudioSource にクリップ無し | Warning |
| 暗転: 同一シーン重複 / 暗転中の暗転 / 非暗転中の解除 | Warning |
| ポストプロセス: PPv2 パッケージが見つからない | Warning。ポストプロセス全体をスキップ |
| ポストプロセス: 1 シーンに 2 件以上 | Warning。先頭 1 件のみ使用 |
| ポストプロセス: プリセット参照切れ / Volume 未割り当て / PostProcessVolume が無い / Is Global でない / 直前と同じ Volume | Warning。該当エントリをスキップ |
| ポストプロセス: 1 つの GameObject に PostProcessVolume が複数 / Profile 未割り当て / Color Grading の Mode・Tonemapper が Global Volume 間で不一致 | Warning。生成は継続 |
| ワープ: `characters` が空 / `destinationTransform` 未設定 | Warning。スキップ |
| Animator パラメータ: Animator 未設定 / パラメータ名未設定 / 値の選択肢を解決できない / パラメータが無い・Int 型でない | Warning。スキップ |
| Animator トリガー: Animator 未設定 / Trigger 名を解決できない / パラメータが無い・Trigger 型でない | Warning。スキップ |
| Udon イベント: 対象未設定 / 関数名を解決できない | Warning。スキップ |
| Udon イベント: public・引数なしのメソッドが見つからない | Warning。生成は継続 |
| カメラ: プリセット参照切れ / `virtualCamera` 未設定 / vcam に CinemachineVirtualCamera が無い | Warning。該当指定をスキップ |
| カメラ: `cinemachineBrain` 未設定 / Cinemachine 未導入 / CinemachineBrain コンポーネントが無い / Cinemachine Timeline 型を解決できない | Warning。カメラトラック全体をスキップ |
| ワープ・カメラ・Udon イベントの「最後」: シーン尺がリード時間未満 / カメラ「最初」: 遅延がシーン尺を超える | Warning |

### Q シートウィンドウ

- ビルダーのツールバー「Q シート ↗」で開く。タイトル `Q シート`、最小サイズ 640×320。
- 表示対象は開いている Stage Timeline Builder の Config。Config の変更とビルダーで選択中のシーンに追従する（選択中のシーンを含むページを開く）。
- 1 キュー = 1 シーングループ。尺はシーン尺の計算（整数秒への切り上げ前）の合計。
- ツールバー: 「Q シート」/「遷移表」の切替、検索、「CSV を出力」（下記 CSV）。
- ページ: 幕・場の区切りで分ける。区切りが無い場合は 1 ページ。最初の区切りより前のキューは「はじめ」のページ。統合グループの途中にある区切りはそのキューの先頭にあるものとして扱う。ページ見出しは幕の区切りがある場合 `A幕B場`、無い場合 `N場` / `N幕`。
- キューのクリックでビルダーのそのシーンを選択し、ダブルクリックでそのシーン（カメラはカメラタブ）を開いて演出の行を示す。

| 表示 | 内容 |
|---|---|
| Q シート | 列: Cue / きっかけ / シーン / 照明 / 暗転 / BGM / オブジェクト / SE / アニメ / ワープ / カメラ（カメラ列は `showCameraFeatures` ON のときのみ）。各演出は時刻（`0.0s` / `+X.Xs` / `end`）・操作・対象・フェード秒・付加情報で表示する。ポストプロセスは照明列に操作 `Volume` で表示する（`presetId` が空なら `解除`） |
| 遷移表 | キューを横軸に、照明・暗転・BGM・オブジェクトの各対象が有効な範囲を表示する。SE・ワープは発生位置、カメラは切替を表示する |

- 状態が変わらない操作（点いていない対象の消灯・点いている対象の点灯・鳴っていない BGM の `Change`）は区別して表示する。

### Q シート CSV

Q シートウィンドウの「CSV を出力」で保存先を選んで出力する。読み込み機能は無い。

- 既定ファイル名: `{タイトル}_QSheet.csv`（タイトルが空なら `QSheet.csv`）。
- 文字コード UTF-8（BOM 付き）、区切り `,`、行区切り CRLF、セル内改行 LF。空セルは `-`。
- 先頭行 `# Stage Timeline Builder Export`、続いて `タイトル,…` と `出力日時,yyyy-MM-dd HH:mm`、空行、表。
- 列: `Cue` / `幕` / `場` / `シーン` / `キッカケ` / `照明` / `暗転` / `BGM` / `SE` / `オブジェクト` / `アニメーション` / `ワープ` / `カメラ` / `尺`。
- 1 行 = 1 シーングループ。`Cue` はグループ番号、`シーン` はグループ内の `sceneName` を ` / ` で連結、`キッカケ` は先頭シーンの `cue`。
- `幕` / `場`: そのグループの最後のシーンまでに現れた区切りのうち直近の幕・場の `N幕` / `N場`（名前があれば半角スペースに続けて名前）。幕の区切りが 1 つも無い場合、`幕` 列は `-`。幕の区切りが現れると `場` 列を空に戻す。
- `尺` はグループ内のシーン尺（タイムライン生成と同じ計算、整数秒への切り上げ前）の合計。書式 `X.Xs`。
- グループ内 2 番目以降のシーンの演出は、グループ先頭からの経過秒をオフセットに加える。
- `暗転` 列は、そのグループに暗転エントリが無く暗転継続中の場合 `暗転中`。
- `カメラ` 列は `showCameraFeatures` に関わらず出力する。

セル内の 1 行の書式: `[オフセット][タグ] 対象 フェード秒 付加情報`

| 要素 | 書式 |
|---|---|
| オフセット | `[+X.Xs]`。0 秒は省略。「最後」指定でグループ末尾ちょうどは `[end]`、超過分は `[end+X.Xs]` |
| タグ | 照明・BGM・暗転: `[FI]` / `[FO]`（フェード 0 秒は `[CI]` / `[CO]`）/ `[Change]`。ポストプロセス: `[PP]`。オブジェクト: `[ON]` / `[OFF]`。アニメーション: `[Play]` / `[Stop]`。カメラ: `[Cam]`。SE・ワープはタグ無し |
| フェード秒 | `X.Xs`。0 秒は省略 |
| 照明 | 色 `{カテゴリ}(#RRGGBB)`（`targetColor`。彩度 < 0.05 かつ明度 > 0.95 は省略）、強度 `i=` は 1 以外のとき |
| 色カテゴリ | 明度 < 0.1: `暗`、彩度 < 0.15: `白`、それ以外は色相で `赤` / `橙` / `黄` / `黄緑` / `緑` / `水色` / `青` / `紫` / `桃` |
| ポストプロセス | `[PP] {プリセット表示名}`（`presetId` が空なら `解除`）。照明列に出力する |
| BGM | `vol=`（`FadeOut` 以外）、`pitch=`（`Change` のみ） |
| SE | `vol=`（1 以外のとき） |
| アニメーション | `[Play] 対象 (クリップ, Hold)` / `[Play] 対象 (クリップ, SingleShot, シーン終了で停止)` / `[Stop] 対象` |
| ワープ | `キャラクター名 → ワープ先Transform名`（キャラクター名が空なら `キャラ{番号}`） |
| カメラ | `[Cam] プリセット名` に `blend=X.Xs` または `cut`、`useFovOverride` ON 時 `fov=X.X`（`fovSeconds` > 0 なら `(X.Xs)`）、`useTiltPanOverride` ON 時 `tilt=X.X° pan=X.X°`（`tiltPanSeconds` > 0 なら `(X.Xs)`） |
| プリセット削除済み | `{最後に設定されていた対象名}（プリセット削除済み）`、対象も無い場合 `(プリセット未設定)` |

### バックアップ

要約バックアップ:

- 生成のたびに `StageTimelineConfigBackup.json` を上書きする（`JsonUtility`、UTF-8）。読み込み・復元には使わない。
- オブジェクト参照は `GlobalObjectId` 文字列で記録する。
- 記録する項目: 出力日時、`title`、`defaultSceneDuration`、`playableDirector`、`stageTimelineManager`、暗転オブジェクト・ガイド、照明プリセット、カメラプリセット、ポストプロセスプリセット、`cinemachineBrain`、各シーンの `sceneName` / `cue` / 尺設定 / `autoAdvance` / オブジェクト / アニメーション / 照明 / BGM / 暗転 / カメラ / ポストプロセス。

全項目バックアップ:

- Config のシリアライズ対象をすべて `EditorJsonUtility` で書き出す。オブジェクト参照は `instanceID` に `globalObjectId` を添えて記録する。
- ファイル名: `StageTimelineConfigBackup_{種類}_{yyyyMMdd_HHmmss}.json`。
- 保存先: `{出力先}/{タイトル}`（`title` が空の場合は `{出力先}`）。
- 種類ごとに新しいものから 20 件（`HistoryLimit`）を残し、古いものを削除する。

| 種類 | 一覧の表記 | 書き出すタイミング |
|---|---|---|
| `Generate` | タイムライン生成時 | タイムライン生成 |
| `Manual` | 手動 | 「いまの内容をバックアップ」 |
| `BeforeInitialize` | Config を初期化する前 | 「Config を初期化…」 |
| `BeforeRestore` | バックアップから戻す前 | 「このバックアップに戻す…」 |

設定タブ「バックアップ」:

- 「いまの内容をバックアップ」、「フォルダを開く」。
- 保存先の全項目バックアップを新しい順に一覧する（日時・種類）。
- 選択したバックアップの公演名・シーン数・プリセット数・登場人物数を表示する。読み込めないファイルは「このバックアップは読み込めません。」。
- 「このバックアップに戻す…」:
  1. 確認後、現在の内容を全項目バックアップ（種類 `BeforeRestore`）に書き出す。書き出せない場合は中止する。
  2. バックアップを一時的な Config に読み込み、設定値を現在の Config へ写す（GameObject と有効状態は変えない。Undo で戻せる）。
  3. オブジェクト参照は `globalObjectId` で現在開いているシーン・プロジェクトから解決できたもののみ戻し、解決できない参照は未設定にする。
  4. 戻した後に未設定の参照（下記「参照の再割り当て」の対象）がある場合は件数を示し、「参照の再割り当てを開く」を提示する。
- 「削除…」: 確認後にファイルを削除する。

### 参照の再割り当て

- 対象: Config 内のシーン内オブジェクト（GameObject / Component）への参照のうち、未設定のもの。`SerializedObject` で全フィールドを走査する。
- 対象外: `m_Script`、`referenceHints`、`previousSceneSnapshots`、`warpMarkerPrefab`、`_deprecated*`、プロジェクト内のアセット、ワープ（`warps`）の参照、`bindingMode = Preset` のエントリの参照。
- 一覧に出す条件: 参照の控え（`referenceHints`）がある、プリセットの表示名がある、または候補がある。
- 参照の控え: 参照ごとのキー（配列の添字をプリセット `id` / シーン `sceneUid` に置き換えたパス）と、対象 GameObject のシーンルートからの名前の並び（`path`）・同名兄弟内の順番（`order`）。タイムライン生成時と割り当て時に更新する。外れている参照の控えは保持し、Config から無くなった参照の控えは削除する。
- 一覧は種類ごとに分ける: 設定 / `{種別}のプリセット` / シーン（自由指定）。列は 名前 / 割り当て / 候補。削除されたオブジェクトを参照していた行は ⚠ を付ける。
- 「候補をスキャン」: 読み込み済みの全シーンから候補を探す。

| 順 | 方法 | 候補の理由の表記 |
|---|---|---|
| 1 | 控えの `path` / `order` で階層をたどる | 階層が一致 |
| 2 | 控えの末尾の名前と一致するオブジェクト（複数ある場合は親の名前の一致数、次に種類で絞る） | 名前が一致 |
| 3 | プリセットの表示名と一致するオブジェクト（同上） | 名前が一致 |
| 4 | プリセットの表示名の部分一致（NFKC 正規化・小文字化し、空白・`_`・`-`・`・`・`.`・`(`・`)` を除いて比較。2 文字以上。完全一致 → 末尾一致 → 部分一致の順、余分な文字が最少で 1 件に決まる場合のみ。割り当て済み・他の候補のオブジェクトは除く） | 名前がほぼ一致 / 名前の一部が一致 |

- 種類で絞る条件: カメラのプリセットは `CinemachineVirtualCamera`、ポストプロセスのプリセットは `PostProcessVolume` を持つもの、照明は子孫に `Light` または `MeshRenderer` を持つもの。
- 「候補をまとめて割り当てる（N 件）」、行ごとの「割り当てる」・「✕」（候補を取り下げる）、割り当て欄への直接指定で割り当てる。割り当てた行は一覧から外す。

### ワープ地点と Gizmo

- ワープの行の「新規作成」: 生成物の親の子 `_WarpPoints/Char_{キャラクター名}/` に GameObject `{シーン名}`（空なら `warppoint`。Hierarchy に使えない `/ \ : * ? " < > |` は `_` に置換。同名がある場合は `_2`、`_3` … を付加）を Scene ビューの注視点に作成し、`destinationTransform` に設定する。キャラクター名が空の場合は `character_{番号}`。
- ウィンドウ表示中（閲覧モード OFF）、いずれかのワープの `destinationTransform` になっている Transform に `MashiroWarpPointGizmo` を追加し、Config と同じシーン内でどのワープにも使われていない `MashiroWarpPointGizmo` を削除する。
- Scene ビューに位置（半径 0.07 の円）と Y 回転方向（長さ 0.18 の矢印）を描画する。

## Config

### StageTimelineConfig

| フィールド | 型 | 既定値 | 必須 | 内容 |
|---|---|---|---|---|
| `title` | `string` | `""` | 必須 | UI「タイトル」（初期設定は「公演名」）。出力サブフォルダ名・アセット名の接頭辞 |
| `defaultSceneDuration` | `float` | `2.0` | — | UI「標準シーン尺」（秒）。最小 0.1 |
| `scenes` | `List<ShowScene>` | 空 | 必須（1 件以上） | シーン一覧 |
| `sceneDividers` | `List<SceneDivider>` | 空 | 任意 | 幕・場の区切り |
| `lightPresets` | `List<LightPresetEntry>` | 空 | 任意 | 照明プリセット |
| `togglePresets` | `List<TogglePresetEntry>` | 空 | 任意 | オブジェクトプリセット |
| `objectAnimationPresets` | `List<ObjectAnimationPresetEntry>` | 空 | 任意 | アニメーションプリセット |
| `bgmPresets` | `List<BgmPresetEntry>` | 空 | 任意 | BGM プリセット |
| `sePresets` | `List<SePresetEntry>` | 空 | 任意 | SE プリセット |
| `animatorParameterPresets` | `List<AnimatorParameterPresetEntry>` | 空 | 任意 | Animator パラメータプリセット |
| `animatorTriggerPresets` | `List<AnimatorTriggerPresetEntry>` | 空 | 任意 | Animator トリガープリセット |
| `udonEventPresets` | `List<UdonEventPresetEntry>` | 空 | 任意 | Udon イベントプリセット |
| `cameraPresets` | `List<CameraPresetEntry>` | 空 | 任意 | カメラプリセット（UI「アングル」） |
| `cinemachineBrain` | `GameObject` | なし | カメラ使用時 | UI「CinemachineBrain」。CinemachineBrain を持つ GameObject |
| `postProcessPresets` | `List<PostProcessPresetEntry>` | 空 | 任意 | ポストプロセスプリセット |
| `setupCompleted` | `bool` | `false` | — | 初期設定の完了 |
| `showCameraFeatures` | `bool` | `false` | — | 機能スイッチ「カメラ」 |
| `showAnimatorFeatures` | `bool` | `false` | — | 機能スイッチ「Animator」 |
| `showUdonEventFeatures` | `bool` | `false` | — | 機能スイッチ「Udon イベント」 |
| `showPostProcessFeatures` | `bool` | `false` | — | 機能スイッチ「ポストプロセス」 |
| `characters` | `List<CharacterEntry>` | 空 | ワープ使用時 | UI「登場人物」 |
| `warpMarkerPrefab` | `GameObject` | なし | 任意 | UI「マーカー Prefab」。ワープマーカーのプレハブ |
| `generatedBaseFolder` | `string` | `Assets/StageTimelineTools/Generated` | 任意 | UI「出力先フォルダ」（`Assets` 配下） |
| `playableDirector` | `PlayableDirector` | なし | 任意 | 旧バージョン用の適用先。設定時は適用先として最優先する。UI には表示しない |
| `stageTimelineManager` | `StageTimelineManager` | なし | 必須 | UI「StageTimelineManager」。生成結果の書き込み先・適用先の解決元 |
| `blackoutBoxRoots` | `List<GameObject>` | 空 | 暗転使用時 | UI「暗転用Cube」 |
| `blackoutGuideRoots` | `List<GameObject>` | 空 | 任意 | UI「暗転中ガイド」 |

Inspector に表示しないフィールド:

| フィールド | 型 | 内容 |
|---|---|---|
| `builderDataVersion` | `int`（private） | ビルダーのデータ版数。既定 `0`。`CurrentBuilderDataVersion` は `1` |
| `showAdvancedFeatures` | `bool` | 旧バージョンの「高度な機能を表示」。`UpgradeBuilderDataIfNeeded()` でのみ参照する |
| `previousSceneSnapshots` | `List<GeneratedSceneSnapshot>`（private） | 前回生成時の各シーンの `sceneUid` / `startTime` / `endTime` |
| `referenceHints` | `List<ReferenceHint>` | 参照の控え。要素は `key`（`string`）/ `path`（`string[]`）/ `order`（`int[]`） |

- `Reset()`（Add Component 時）で `InitializeAsNewBuilderData()` を呼ぶ。

### ShowScene

| フィールド | 型 | 既定値 | 必須 | 内容 |
|---|---|---|---|---|
| `sceneUid` | `string`（非表示） | 採番 | — | シーン識別 ID（GUID `N` 形式） |
| `sceneName` | `string` | なし | 任意 | シーン名 |
| `cue` | `string` | なし | 任意 | UI「キッカケ」 |
| `useCustomDuration` | `bool` | `false` | — | 秒数指定 |
| `durationSeconds` | `float` | `0` | — | UI「尺」（秒） |
| `autoAdvance` | `bool` | `false` | — | UI「次のシーンを統合」 |
| `toggles` / `objectAnimations` / `lightFades` / `bgmEntries` / `seEntries` / `blackouts` / `warps` / `animatorParameters` / `animatorTriggers` / `udonEvents` / `cameras` / `postProcesses` | 各エントリの `List` | 空 | 任意 | 演出エントリ |

### SceneDivider

| フィールド | 型 | 既定値 | 必須 | 内容 |
|---|---|---|---|---|
| `isAct` | `bool` | `false` | — | `true`: 幕の区切り、`false`: 場の区切り |
| `sceneUid` | `string` | `""` | 必須 | 区切りのすぐ下のシーンの `sceneUid`。一致するシーンが無い区切りは無視する |
| `name` | `string` | `""` | 任意 | 区切りの名前 |

### プリセット

全プリセット共通（`CharacterEntry` を除く）: `id`（`string`、自動採番）、`displayName`（`string`、UI「表示名」）。

| クラス | フィールド | 型 | 既定値 | 内容 |
|---|---|---|---|---|
| `LightPresetEntry` | `lightRoot` | `GameObject` | なし | UI「Light Root」 |
| | `defaultIntensity` | `float` | `1.0` | UI「Intensity」 |
| | `defaultColor` | `Color` | 白 | UI「Color」 |
| `TogglePresetEntry` | `target` | `GameObject` | なし | UI「GameObject」 |
| `ObjectAnimationPresetEntry` | `target` | `GameObject` | なし | UI「対象」 |
| | `clip` | `AnimationClip` | なし | UI「Clip」 |
| `BgmPresetEntry` / `SePresetEntry` | `source` | `AudioSource` | なし | UI「AudioSource」 |
| | `defaultVolume` | `float` | `1.0` | UI「音量」 |
| `AnimatorParameterPresetEntry` | `targetAnimator` | `Animator` | なし | UI「Animator」 |
| | `parameterName` | `string` | `""` | UI「パラメータ名 (Int)」 |
| | `values` | `List<AnimatorParameterValueLabel>` | 空 | 値の選択肢。要素は `id`（自動採番）/ `value`（`int`）/ `name`（`string`） |
| `AnimatorTriggerPresetEntry` | `targetAnimator` | `Animator` | なし | UI「Animator」 |
| | `triggers` | `List<AnimatorTriggerOption>` | 空 | 送れる Trigger。要素は `id`（自動採番）/ `triggerName` / `displayName`（空なら `triggerName` を表示） |
| `UdonEventPresetEntry` | `targetBehaviour` | `UdonSharpBehaviour` | なし | UI「対象 Udon」 |
| | `events` | `List<UdonEventOption>` | 空 | 呼べるイベント。要素は `id`（自動採番）/ `eventName` / `displayName`（空なら `eventName` を表示）/ `ownerOnly`（`bool`、既定 `false`） |
| `CameraPresetEntry` | `virtualCamera` | `GameObject` | なし | CinemachineVirtualCamera を持つ GameObject |
| | `activePriority` / `inactivePriority` / `defaultFov` | `int` / `int` / `float` | `20` / `0` / `60` | 生成では使用しない |
| | `colorSlot` | `int`（非表示） | `0` | 使用しない |
| `PostProcessPresetEntry` | `volumeObject` | `GameObject` | なし | UI「Volume」。PostProcessVolume を持つ GameObject |
| `CharacterEntry` | `displayName` | `string` | `""` | キャラクター名（`id` は無い） |

### 演出エントリ

`bindingMode`（`Direct` / `Preset`）と `presetId`（`string`）を持つエントリ: `ToggleEntry` / `ObjectAnimationEntry` / `LightFadeEntry` / `BgmEntry` / `SeEntry` / `AnimatorParameterEntry` / `AnimatorTriggerEntry` / `UdonEventEntry`。Direct 用の対象フィールドは Preset 指定時、プリセットが見つからない場合のみ使う。

| クラス | フィールド | 型 | 既定値 | 内容 |
|---|---|---|---|---|
| `ToggleEntry` | `bindingMode` | enum | `Direct` | |
| | `target` | `GameObject` | なし | 対象（Direct） |
| | `action` | `Appear` / `Disappear` | `Appear` | |
| | `appearTiming` / `disappearTiming` | `SceneStart` / `SceneEnd` | `SceneStart` | 「最初」/「最後」 |
| | `appearDelaySeconds` / `disappearDelaySeconds` | `float` | `0` | 遅延（`SceneStart` のみ） |
| `ObjectAnimationEntry` | `bindingMode` | enum | `Direct` | |
| | `target` / `clip` | `GameObject` / `AnimationClip` | なし | 対象・クリップ（Direct） |
| | `action` | `Play` / `Stop` | `Play` | |
| | `playDelaySeconds` | `float` | `0` | 再生遅延 |
| | `playMode` | `Hold` / `SingleShot` | `Hold` | UI「維持」/「単発」 |
| | `stopTiming` | `SceneStart` / `SceneEnd` | `SceneStart` | |
| | `stopDelaySeconds` | `float` | `0` | 停止遅延（`SceneStart` のみ） |
| `LightFadeEntry` | `bindingMode` | enum | `Direct` | |
| | `lightRoot` | `GameObject` | なし | 照明ルート（Direct） |
| | `action` | `FadeIn` / `FadeOut` / `Change` | `FadeIn` | |
| | `targetIntensity` | `float` | `1.0` | 目標強度 |
| | `targetColor` | `Color` | 白 | 目標色 |
| | `fadeSeconds` | `float` | `1.0` | フェード秒数 |
| | `delaySeconds` | `float` | `0` | 遅延 |
| | `useDefaultValues` | `bool` | `false` | 「デフォルト」指定（`Change` かつ Preset） |
| `BgmEntry` | `bindingMode` | enum | `Direct` | |
| | `source` | `AudioSource` | なし | 対象（Direct） |
| | `action` | `FadeIn` / `FadeOut` / `Change` | `FadeIn` | |
| | `volume` | `float` | `1.0` | 目標音量 |
| | `pitch` | `float` | `1.0` | 目標ピッチ（`Change` のみ使用） |
| | `fadeSeconds` | `float` | `1.0` | フェード秒数 |
| | `playDelaySeconds` | `float` | `0` | `FadeIn`: 再生開始遅延、`Change` / `FadeOut`: フェード開始遅延 |
| | `useDefaultValues` | `bool` | `false` | 「デフォルト」指定（`Change` かつ Preset） |
| `SeEntry` | `bindingMode` | enum | `Direct` | |
| | `source` | `AudioSource` | なし | 対象（Direct） |
| | `volume` | `float` | `1.0` | 音量 |
| | `delaySeconds` | `float` | `0` | 遅延 |
| `BlackoutEntry` | `action` | `FadeIn` / `FadeOut` | `FadeIn` | 暗転 / 解除 |
| | `fadeSeconds` | `float` | `1.0` | フェード秒数 |
| | `delaySeconds` | `float` | `0` | 遅延 |
| `WarpEntry` | `characterIndex` | `int` | `0` | `characters` の index |
| | `timing` | `SceneStart` / `SceneEnd` | `SceneStart` | |
| | `delaySeconds` | `float` | `0` | 遅延（`SceneStart` のみ） |
| | `destinationTransform` | `Transform` | なし | ワープ先 |
| `AnimatorParameterEntry` | `bindingMode` | enum | `Preset` | |
| | `targetAnimator` / `parameterName` | `Animator` / `string` | なし / `""` | Direct 用 |
| | `valueId` | `string` | `""` | 選択肢 ID（Preset） |
| | `intValue` | `int` | `0` | Direct: 適用値。Preset: 表示用キャッシュ |
| | `delaySeconds` | `float` | `0` | 遅延 |
| `AnimatorTriggerEntry` | `bindingMode` | enum | `Preset` | |
| | `targetAnimator` | `Animator` | なし | Direct 用 |
| | `triggerId` | `string` | `""` | 選択肢 ID（Preset） |
| | `triggerName` | `string` | `""` | Direct: Trigger 名。Preset: 表示用キャッシュ |
| | `delaySeconds` | `float` | `0` | 遅延 |
| `UdonEventEntry` | `bindingMode` | enum | `Preset` | |
| | `timing` | `SceneStart` / `SceneEnd` | `SceneStart` | |
| | `targetBehaviour` | `UdonSharpBehaviour` | なし | Direct 用 |
| | `eventId` | `string` | `""` | 選択肢 ID（Preset） |
| | `eventName` | `string` | `""` | Direct: 関数名。Preset: 表示用キャッシュ |
| | `ownerOnly` | `bool` | `false` | Direct 時の Owner のみ実行（UI「全員」/「Owner」） |
| | `delaySeconds` | `float` | `0` | 遅延（`SceneStart` のみ） |
| `CameraEntry` | `presetId` | `string` | `""` | カメラプリセット ID |
| | `timing` | `SceneStart` / `SceneEnd` | `SceneStart` | 「最初」/「最後」 |
| | `delaySeconds` | `float` | `0` | 遅延（`SceneStart` のみ） |
| | `blendSeconds` | `float` | `1.0` | 生成では使用しない（Q シートに出力） |
| | `useFovOverride` / `targetFov` / `fovSeconds` / `fovDelaySeconds` | `bool` / `float` ×3 | `false` / `60` / `1.0` / `0` | 生成では使用しない（Q シート CSV に出力） |
| | `useTiltPanOverride` / `targetTiltDegrees` / `targetPanDegrees` / `tiltPanSeconds` / `tiltPanDelaySeconds` | `bool` / `float` ×4 | `false` / `0` / `0` / `1.0` / `0` | 生成では使用しない（Q シート CSV に出力） |
| `PostProcessEntry` | `presetId` | `string` | `""` | ポストプロセスプリセット ID。空は「なし」 |
| | `fadeSeconds` | `float` | `1.0` | フェード秒数 |
| | `delaySeconds` | `float` | `0` | 遅延 |

### MashiroWarpPointGizmo

Inspector フィールドは無い。`[DisallowMultipleComponent]`、`AddComponentMenu`: `Mashiro Theater/Mashiro Warp Point Gizmo`。

## API リファレンス

UI へ手配線するものは無い。以下はすべてエディタまたは他コンポーネントから呼ばれる内部連携用（配線不要）。

### StageTimelineBuilderWindow

| シグネチャ | 用途 |
|---|---|
| `static void Open()` | ウィンドウを開く。メニュー `Tools/Mashiro Theater/Stage Timeline Builder` から呼ばれる |

### StageTimelineQSheetWindow

| シグネチャ | 用途 |
|---|---|
| `static void Open()` | Q シートウィンドウを開く。ビルダーのツールバー「Q シート ↗」から呼ばれる |

### StageTimelineGenerator

| シグネチャ | 用途 |
|---|---|
| `static TimelineBuildResult Generate(StageTimelineConfig config)` | タイムラインを生成する。「タイムライン生成」ボタンから呼ばれる。Config 未設定、適用先 `PlayableDirector` を解決できない、シーン 0 件のときは `null` を返す |

`TimelineBuildResult`: `SceneCount` / `ObjectTrackCount` / `LightRootCount` / `BgmTrackCount` / `BlackoutSceneCount`（`int`）、`Warnings`（`List<string>`）、`void LogSummary(string title)`（集計を Console に出力）。

### StageTimelineConfig

| シグネチャ | 用途 |
|---|---|
| `LightPresetEntry FindLightPresetById(string presetId)` | ID でプリセットを返す（無ければ `null`） |
| `TogglePresetEntry FindTogglePresetById(string presetId)` | 同上 |
| `ObjectAnimationPresetEntry FindObjectAnimationPresetById(string presetId)` | 同上 |
| `BgmPresetEntry FindBgmPresetById(string presetId)` | 同上 |
| `SePresetEntry FindSePresetById(string presetId)` | 同上 |
| `AnimatorParameterPresetEntry FindAnimatorParameterPresetById(string presetId)` | 同上 |
| `AnimatorTriggerPresetEntry FindAnimatorTriggerPresetById(string presetId)` | 同上 |
| `UdonEventPresetEntry FindUdonEventPresetById(string presetId)` | 同上 |
| `CameraPresetEntry FindCameraPresetById(string presetId)` | 同上 |
| `PostProcessPresetEntry FindPostProcessPresetById(string presetId)` | 同上 |
| `List<GameObject> GetResolvedBlackoutBoxRoots()` | 重複・null を除いた暗転オブジェクト一覧を返す |
| `List<GameObject> GetResolvedBlackoutGuideRoots()` | 重複・null を除いた暗転中ガイド一覧を返す |
| `List<GeneratedSceneSnapshot> PreviousSceneSnapshots { get; }` | 前回生成時のシーン位置を返す |
| `void SetPreviousSceneSnapshots(List<GeneratedSceneSnapshot> snapshots)` | 前回生成時のシーン位置を設定する。Generator が呼ぶ |
| `bool UpgradeBuilderDataIfNeeded()` | `builderDataVersion` が `CurrentBuilderDataVersion` 未満の場合、`setupCompleted = true`、`showCameraFeatures = true`、`showAnimatorFeatures` / `showUdonEventFeatures` / `showPostProcessFeatures` = `showAdvancedFeatures` にして版数を更新し `true` を返す。ビルダー・Q シートウィンドウが呼ぶ |
| `void InitializeAsNewBuilderData()` | 版数を `CurrentBuilderDataVersion` にし、`setupCompleted` と機能スイッチ 4 つを `false` にする。Config の作成・初期化・`Reset()` で呼ばれる |
| `const int CurrentBuilderDataVersion` | ビルダーのデータ版数（`1`） |

### エントリ・プリセットクラス

| シグネチャ | 用途 |
|---|---|
| `ShowScene.SceneUid { get; }` / `string ShowScene.EnsureSceneUid()` | シーン ID を返す / 未採番なら採番して返す |
| `void ShowScene.RegenerateSceneUid()` | シーン ID を新しく採番する。シーンの複製で呼ばれる |
| `GameObject ToggleEntry.ResolveTarget(StageTimelineConfig config)` | 対象を解決する（Preset はプリセットの対象、見つからなければ `target`） |
| `GameObject ObjectAnimationEntry.ResolveTarget(StageTimelineConfig config)` / `AnimationClip ResolveClip(StageTimelineConfig config)` | 対象・クリップを解決する |
| `GameObject LightFadeEntry.ResolveLightRoot(StageTimelineConfig config)` | 照明ルートを解決する |
| `AudioSource BgmEntry.ResolveSource(StageTimelineConfig config)` / `AudioSource SeEntry.ResolveSource(StageTimelineConfig config)` | AudioSource を解決する |
| `bool AnimatorParameterEntry.TryResolveIntValue(StageTimelineConfig config, out int value)` | 適用値を解決する。Preset で選択肢が見つからない場合 `false` |
| `Animator AnimatorParameterEntry.ResolveAnimator(StageTimelineConfig config)` / `string ResolveParameterName(StageTimelineConfig config)` | 対象 Animator・パラメータ名を解決する |
| `AnimatorParameterValueLabel AnimatorParameterPresetEntry.FindValueById(string valueId)` / `FindFirstValueByInt(int value)` | 値の選択肢を ID / 値で検索する |
| `bool AnimatorTriggerEntry.TryResolveTriggerName(StageTimelineConfig config, out string trigger)` / `Animator ResolveAnimator(StageTimelineConfig config)` | Trigger 名・対象 Animator を解決する |
| `AnimatorTriggerOption AnimatorTriggerPresetEntry.FindTriggerById(string triggerId)` / `FindTriggerByName(string name)` / `ResolveTrigger(string triggerId, string cachedTriggerName)` | Trigger 選択肢を検索する（`ResolveTrigger` は ID → 名前の順） |
| `bool UdonEventEntry.TryResolveEventName(StageTimelineConfig config, out string resolved)` / `UdonSharpBehaviour ResolveTarget(StageTimelineConfig config)` / `bool ResolveOwnerOnly(StageTimelineConfig config)` | 関数名・対象・OwnerOnly を解決する |
| `UdonEventOption UdonEventPresetEntry.FindEventById(string eventId)` / `FindEventByName(string name)` / `ResolveEvent(string eventId, string cachedEventName)` | イベント選択肢を検索する（`ResolveEvent` は ID → 名前の順） |

### その他

- `TimelineWriters` / `StagePlanning` / `AssetUtils` の public static メンバーは Generator・ビルダーの内部処理用。
- `StageTimelineConfigBackupWriter` / `StageTimelineDirectorResolver` / `StageTimelineDividers` / `StageTimelineQSheetExporter` / `StageTimelineQSheetModel` / `StageTimelineReferenceHints` / `StageTimelineReferenceValidator` / `StageTimelineSceneListView` / `BuilderStyles` / `EffectCategory` は `internal`。

## ライセンス

MIT License ではない。[LICENSE.md](../LICENSE.md)（ましろ小劇場 ツール・ギミック汎用利用規約）に基づいて提供する。規約の正本は [VN3License_ja.pdf](../VN3License_ja.pdf)（VN3 ライセンス様式）。

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
