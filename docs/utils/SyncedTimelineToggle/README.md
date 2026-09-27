# SyncedTimelineToggle

タイムライン（`PlayableDirector`）の再生をトグルボタンで制御し、状態を全プレイヤーで同期するツールです。
ボタンを押すとタイムライン前半（OFF→ON）が再生されて**中央で停止**し、もう一度押すと
後半（ON→OFF）が再生されて先頭へ戻ります。複数のトグルを排他グループにまとめることもできます。

| コンポーネント | 同期 | 主な用途 |
| --- | --- | --- |
| `MashiroTimelineToggle` | 全プレイヤーで同期 | 1 つのタイムラインを ON/OFF トグルで制御する |
| `MashiroTimelineToggleExclusiveGroup` | 全プレイヤーで同期 | 複数のトグルを「同時に 1 つだけ ON」に排他制御する |

## タイムラインの作り方（重要）

このツールは **1 本のタイムラインを前半・後半の 2 区間** として扱います。

- **前半（0 〜 中央）**: OFF から ON への遷移アニメーション
- **中央（タイムライン全長の半分）**: ON 状態の見せたいポーズ。ここで停止します
- **後半（中央 〜 末尾）**: ON から OFF への遷移アニメーション

そのため、タイムラインは「**先頭＝OFF の見た目**」「**ちょうど中央＝ON の見た目**」「**末尾＝再び OFF の見た目**」に
なるよう作成してください。中央が ON のポーズになるように尺を調整するのがポイントです。

## 使い方

1. 対象のボタン GameObject に `MashiroTimelineToggle` を追加します。
2. インスペクタで以下を設定します。
   - **Timeline**: 制御したい `PlayableDirector`
   - **Active Color / Inactive Color**: ON 時 / OFF 時のボタン色（遷移中はこの 2 色を補間します）。色が反映されるのは同じ GameObject に `Button` コンポーネントがある場合のみです
   - **Use GameObject Name For Label**: 子の `TextMeshProUGUI` に GameObject 名を自動表示するか
3. ラベルを表示したい場合は、子に `TextMeshProUGUI` を置いておきます。

### 操作方法（2 種類サポート）

`MashiroTimelineToggle` は以下のどちらの形態でも動作します。

#### A. UI ボタンとして使う

- GameObject に `Button` コンポーネントを付け、`OnClick()` から当該スクリプトの
  `OnButtonClick` を呼ぶように設定します。

#### B. 3D オブジェクトとして使う

- `Button` コンポーネントを付けず、`Collider` を付けます。
- VRChat の「Use（インタラクト）」操作でトグルできます。
- この形態では `Active Color` / `Inactive Color` は反映されません（色の適用先が `Button` のため）。見た目の変化はタイムライン側で付けてください。

## 排他グループ（MashiroTimelineToggleExclusiveGroup）

複数のトグルを「**同時に ON になるのは 1 つだけ**」に制御したい場合に使います。

### セットアップ

1. 親 GameObject に `MashiroTimelineToggleExclusiveGroup` を付けます。
2. その子階層に複数の `MashiroTimelineToggle` を配置します
   （`GetComponentsInChildren` で自動的に収集・登録されます）。
3. **Cross Fade Delay**（既定 `0.1` 秒）: 既に ON のトグルを OFF にしてから、新しいトグルを ON にするまでの
   待機秒数。古いタイムラインの戻りと新しいタイムラインの立ち上がりが重ならないよう調整します。

### 挙動

- 既に ON のトグルがある状態で別のトグルを押すと、現在の ON を OFF にしてから
  `Cross Fade Delay` 秒後に新しいトグルを ON にします。
- 同じトグルをもう一度押すと、そのトグルが OFF になります（全て OFF の状態）。
- 状態（`activeIndex`）はコントローラに 1 つだけ同期され、後から Join したプレイヤーにも反映されます。
- 操作したプレイヤーが自動的にオーナーになります。

## 中央停止の精度について

ON にしたときの停止位置は、フレームレートに依存せず**常にタイムラインの中央**になるよう、
中央時刻へスナップしてから停止しています。これにより、端末性能の差で停止位置が
プレイヤーごとに微妙にずれることを防いでいます。

## API リファレンス

### MashiroTimelineToggle

| メソッド／プロパティ | 用途 | 呼び出し種別 |
|---|---|---|
| `OnButtonClick()` | 再生状態をトグル（全員同期） | `Button.OnClick` から配線 |
| `Interact()` | 同上 | オブジェクトへの Interact（配線不要）。`Button` が付いている場合は二重発火防止のため何もしません |
| `SetState(bool)` | 再生状態を直接設定 | 他の Udon・グループが呼ぶ内部連携用 |
| `State`（`bool`） | 同期状態の取得／設定。設定時は `SetState(bool)` と同じ | 内部専用（同期変数の受け口・配線不要） |
| `InitializeWithGroup(...)` | 排他グループへの登録 | グループが呼ぶ内部連携用 |

### MashiroTimelineToggleExclusiveGroup

| メソッド／プロパティ | 用途 | 呼び出し種別 |
|---|---|---|
| `ActiveIndex`（`int`） | ON にするトグルの番号（`-1` で全 OFF）。設定すると排他切替を実行する | 内部専用（同期変数の受け口・配線不要） |
| `OnToggleClicked(...)` / `_DelayedActivate()` | 排他制御の内部処理 | 内部専用（配線不要） |

## ライセンス

このフォルダの内容は MIT License で提供します（リポジトリルートの `LICENSE.md` を参照）。

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
