# Mashiro Custom Station

演劇イベントの観客席向けに拡張したカスタム VRCStation ギミックです。

## 主な機能

- 通常通り Interact で着席
- 空席時にマーカー Sprite を表示（着席で非表示、全プレイヤーに同期）
- 右スティック左右で連続的に回転（VR 専用・ローカル・メニュー表示中も操作可）
- A ボタン長押し（VR）、Space キー長押し（PC）で降車（1 秒）。スティック / WASD による降車は無効化（フライングカメラ操作中の誤降車防止）
- 着席でフルメニューが自動オープン（注意事項タブ）
- タブ切り替え（注意事項 / 公演案内 / 広告）と Sprite スライドのページ送り（端でループ、PC は ←→ キー）
- イスの高さ調整（上下ボタン＋リセット）
- 字幕の有効/無効トグル（観客ごとにローカル・**別途字幕システムが必要**。後述）
- 「席を立つ」ボタン、メニュー折りたたみ / 展開（折りたたみ時はミニパネル表示）
- 操作説明テキストを自動付与（VR / デスクトップで自動切り替え）
- 座席番号を親オブジェクト名＋ヒエラルキー順で自動生成（例: `A-3`）
- 降車時に高さ・回転・メニュー状態を自動リセット

## 同梱ファイル

- `MashiroCustomStation.cs` — メインスクリプト
- `MashiroUnlitBillboardCutout.shader` — 空席マーカー用ビルボードシェーダー（Unlit + Cutout）
- `ソファーアイコン.png` / `ソファーアイコン.mat` — 空席マーカー用アイコン
- `StationPrefab.prefab` — 構成例プレハブ
- `MashiroCustomStationGroup.cs` — 複数席の共有参照を一括注入する任意コンポーネント。
  **配布パッケージには含まれません**（劇場内部の字幕・パンフレットシステムとの連携用。後述）

## 同期設計

- 同期するのは `syncedIsOccupied`（着席中フラグ）のみ
- 回転と高さはローカル処理（VRChat のアバター位置同期で他者にも自然に反映）
- `BehaviourSyncMode.Manual` を使用するため、Late Joiner にも最新の着席状態が自動配信される

---

## プレハブ構成

`StationPrefab.prefab` を参考にしてください。最小構成は以下です。

```
StationPrefab (root)
├── MashiroCustomStation … MashiroCustomStation + VRCStation + BoxCollider（Interact 判定）
│   └── DummySeat（椅子モデル）
├── MainPanel（Canvas, Render Mode = World Space）
│   ├── Header … 席番号ラベル・折りたたみボタン
│   ├── SideBar … タブ・高さ調整
│   ├── Main … スライド表示・ページ ◀ ▶・ページ数
│   └── Footer … 操作説明・「席を立つ」ボタン
├── MiniPanel（Canvas, Render Mode = World Space）
│   └── Footer … 席番号・操作説明・「展開する」ボタン
├── EmptyMarker（Quad + MeshRenderer + ビルボードマテリアル）
├── EnterLocation（着席アンカー Transform）
│   └── ExitHoldGauge（降車ゲージ用 Canvas）
└── ExitLocation（降車位置 Transform）
```

`MainPanel` / `MiniPanel` はそれぞれ独立した World Space Canvas です。座席番号の自動生成は「スクリプトのある GameObject の親＝席プレハブのルート、その親＝行オブジェクト」という 2 階層を前提とするため、`StationPrefab` を行ごとの GameObject（`A`, `B`, …）の下に並べてください。

## VRCStation の設定

| 項目 | 推奨値 |
|---|---|
| `Player Mobility` | `ImmobilizeForVehicle` |
| `Station Enter Location` | `EnterLocation` の Transform |
| `Station Exit Location` | `ExitLocation` の Transform（降車時の立ち位置。不要なら未設定でも可） |
| `Disable Station Exit` | スクリプトが `Start()` で `true` に上書きします |
| `Animator Controller` | 用途に応じて設定（座りモーションなど） |

---

## MashiroCustomStation のフィールド設定

Inspector は機能ごとに `■` 見出しのセクションに分かれています。

### ■ ステーション基本設定

| フィールド | 内容 |
|---|---|
| `Station` | 対象 VRCStation |
| `Station Enter Location` | VRCStation に指定したものと同じ Transform |
| `Empty Marker` | 空席マーカーの GameObject |

### ■ メニューパネル

| フィールド | 内容 |
|---|---|
| `Menu Panel` | 着席時に開くフルメニューの GameObject |
| `Mini Panel` | 折りたたみ時に表示するミニパネルの GameObject |

### ■ 座席番号ラベル（自動生成）

| フィールド | 内容 |
|---|---|
| `Seat Label` | フルメニュー上の座席番号 TextMeshProUGUI |
| `Mini Seat Label` | ミニパネル上の座席番号 TextMeshProUGUI |

座席番号は `Start()` で **親の親オブジェクト名＋ヒエラルキー順** から自動生成されます（例: 祖父 `A` の 3 番目 → `A-3`）。Inspector での手動入力は不要です。

### ■ タブ

| フィールド | 内容 |
|---|---|
| `Tab Buttons` | タブ0〜2 の `Button` 配列（順番通りに3要素） |
| `Tab Button Labels` | タブボタン上の `TextMeshProUGUI` 配列（同順） |
| `Tab 0 Slides` | 注意事項タブのスライド Sprite 配列 |
| `Tab 1 Slides` | 公演案内タブのスライド Sprite 配列 |
| `Tab 2 Slides` | 広告タブのスライド Sprite 配列 |

スライド配列が空のタブでは `Slide Area` が非表示になります。

### ■ スライド表示

| フィールド | 内容 |
|---|---|
| `Slide Area` | スライドとページナビ全体の GameObject |
| `Slide Image` | スライド表示用の `Image` |
| `Page Count Text` | "1 / 5" 形式のページ数表示 |

### ■ 操作説明テキスト（自動付与）

| フィールド | 内容 |
|---|---|
| `Sub Text VR` / `Sub Text PC` | フルメニューの操作説明 TextMeshProUGUI |
| `Mini Sub Text VR` / `Mini Sub Text PC` | ミニパネルの操作説明 TextMeshProUGUI |

文面は `MashiroCustomStation.cs` 冒頭の定数で定義され、`Start()` で自動付与・VR/PC 自動切り替えされます。アサインしたフィールドだけが書き換えられるため、自動付与したくない箇所は未割り当て（None）のままにしてください。

### ■ 字幕（任意・別システム連携）

| フィールド | 内容 |
|---|---|
| `Subtitle Display` | この椅子に紐づく字幕表示コンポーネント（`UdonSharpBehaviour`）。未設定なら字幕機能はオフ |
| `Subtitle Settings Overlay` | フルメニュー内の字幕設定オーバーレイ GameObject。タブ切替・折りたたみ・降車時に自動で閉じる |

字幕トグルは、割り当てたコンポーネントの `ToggleSubtitle` / `SetLangOFF` を `SendCustomEvent` で呼び出します。この2つのイベントを持つ UdonSharpBehaviour であれば何でも接続できます（ましろ小劇場内部では `SubtitleSystem` の `SubtitleDisplay` を使用。同システムは現在未配布です）。字幕を使わない場合は未設定のままで問題ありません。

### ■ 動作パラメータ

| フィールド | 既定値 | 内容 |
|---|---|---|
| `Rotation Speed Deg Per Sec` | `90` | 最大入力時の角速度（VR 専用） |
| `Exit Hold Duration` | `1` 秒 | 長押し降車の必要長押し時間 |
| `Height Step` | `0.05` m | 1段あたりの高さ変化量 |
| `Height Max Level` | `10` | 上方向最大段階数 |
| `Height Min Level` | `-6` | 下方向最大段階数（負値で指定） |

### ■ 降車ゲージ

長押し降車の進捗を椅子の正面に表示する円形ゲージです。長押し中のみ表示されます。

| フィールド | 内容 |
|---|---|
| `Exit Hold Gauge Root` | 長押し降車中のみ表示するゲージのルート GameObject。**未割り当てなら機能オフ** |
| `Exit Hold Gauge` | 長押し進捗を表す `Image`。`Image Type = Filled` に設定する |

- `ExitHoldGauge` を `EnterLocation`（着席アンカー）の子にすると、回転・高さ調整をしても常にプレイヤーの正面に表示されます
- パネルとは独立した Canvas にすると、パネルを閉じていても表示されます
- 配置の目安: プレイヤー正面方向へ 0.5〜0.7m、目線の少し下
- 円形リングの透過 PNG（512px 程度）を用意し、`Fill Method = Radial 360` を設定。fill をオレンジ `(0.91, 0.35, 0)`、背景を暗色にすると既存 UI と馴染みます

---

## API リファレンス

### MashiroCustomStation（UI へ配線するもの）

以下は **UI の `Button.OnClick` から配線**して使います。

| メソッド | 用途 |
|---|---|
| `OnTab0Button` / `OnTab1Button` / `OnTab2Button` | タブ切り替え（注意事項 / 公演案内 / 広告） |
| `OnPagePrevButton` / `OnPageNextButton` | スライドのページ送り |
| `OnHeightUpButton` / `OnHeightDownButton` | 高さを 1 段階調整 |
| `OnResetHeightButton` | 高さを初期位置へ戻す |
| `OnSubtitleToggleButton` | 字幕の有効/無効を切替（ローカル） |
| `OnOpenSubtitleSettings` / `OnCloseSubtitleSettings` | 字幕設定オーバーレイの開閉 |
| `OnExitSeatButton` | 降車 |
| `OnToggleMenuButton` | フルメニュー ⇔ ミニパネル切り替え（フルの「折りたたむ」とミニの「展開する」の両方に配線） |

### MashiroCustomStation（内部専用・配線不要）

以下は VRChat が呼ぶイベントのオーバーライドです。public ですが **UI からは配線しません**。

| メソッド | 用途 |
|---|---|
| `Interact()` | 座席の Interact。VRCStation へ着席させる |
| `OnStationEntered(VRCPlayerApi)` / `OnStationExited(VRCPlayerApi)` | 着席・降車時の初期化とリセット、着席フラグの同期 |
| `OnDeserialization()` | 同期受信時に空席マーカー表示を更新 |
| `OnOwnershipTransferred(VRCPlayerApi)` | 着席者が退出した際に着席フラグをリセット |
| `InputJump(bool, UdonInputEventArgs)` | VR の A ボタン長押し降車の入力受け取り |
| `InputLookHorizontal(float, UdonInputEventArgs)` | 右スティック左右による向き変更の入力受け取り |

### MashiroCustomStationGroup（配布パッケージ非同梱）

public 関数はありません。UI からの配線は不要です（`Start` 時に自動でスキャン・注入する内部連携用コンポーネント）。

UI ボタンの配色規約: 通常時背景 `#000000`、選択時背景 `#E85900`、選択時テキスト `#FFFFFF`、非選択時テキスト `#999999`。タブボタンの選択色はスクリプトが自動で切り替えます。

---

## 空席マーカーのセットアップ（ビルボードシェーダー）

`MashiroUnlitBillboardCutout.shader` はシェーダー側でカメラへ自動追従するため、CPU 負荷ゼロで複数マーカーを描画できます。

1. `Create > Material` で新規マテリアルを作成
2. Shader を `MashiroTheater/UnlitBillboardCutout` に変更
3. `_MainTex` にアイコンテクスチャをアサイン（Sprite の場合は `Texture Type = Default` に変更）
4. **Enable GPU Instancing にチェック**（多数の席を 1 ドローコールで描画するため必須）
5. `Quad` GameObject に貼り付けて `Empty Marker` にアサイン

| プロパティ | 内容 |
|---|---|
| `_MainTex` | アイコンテクスチャ |
| `_Color` | 乗算カラー（Tint） |
| `_Cutoff` | アルファカットオフ閾値（既定 0.5） |
| `Lock Y Axis` | ON で円柱型ビルボード（Y軸固定）、OFF で球状ビルボード（常に正対） |

## Canvas の配置目安

- `Render Mode = World Space`
- `StationPrefab` では `MainPanel` / `MiniPanel` を root 直下に置いているため、右スティックで向きを変えてもパネルは動きません。パネルを回転に追従させたい場合は `EnterLocation`（着席アンカー）の子に配置します
- VR を考慮して 30〜50 cm 程度の見やすいサイズを推奨
- ミニパネルはフルメニューより小さく、画面端に置くと邪魔になりにくい

## 操作フロー

| 操作 | 挙動 |
|---|---|
| Interact | 着席。フルメニュー自動オープン、空席マーカー消去（全員に同期） |
| タブボタン | タブ切り替え（ページはリセット） |
| ページ ◀ / ▶ | スライドのページ送り。端まで行くと反対側へループ（先頭で ◀ → 最終ページ、最終で ▶ → 先頭）。PC は ← → キーでも操作可 |
| 右スティック左右 | 向き変更（VR 専用・メニュー表示中も操作可） |
| A ボタン長押し 1 秒（VR）/ Space 長押し 1 秒（PC）| 降車 |
| ↑ / ↓ / リセット | 高さ調整 |
| 字幕トグル | 字幕の有効/無効（ローカル）。OFF→ON は前回の言語で復帰。ラベル（`OFF`/`JP`/`EN`）自動更新 |
| 折りたたむ / 展開 | フルメニュー ⇔ ミニパネル |
| 降車時 | 高さ・回転・タブ・ページ・字幕（OFF）をリセット、両パネル非表示 |

## ローカル処理の注意点

- 高さ・回転は同期しないため、他プレイヤーから見たアバター位置・向きは VRChat 側のアバター同期に従います。座席自体（メッシュ・コライダー）は動きません。
- 「他から見て少しズレた位置に体がある」程度の見た目差異は仕様上許容します。

---

## MashiroCustomStationGroup（劇場内部向け・配布パッケージ非同梱）

複数の席プレハブを束ねるルートに付ける軽量マネージャです。`Start` 時に配下をスキャンし、椅子全体で共有する参照（字幕システム・パンフレットローダー）を各席のコンポーネントへ自動注入します。席数分の参照を Inspector で個別にアサインする手間を省くためのものです。

| フィールド | 内容 |
|---|---|
| `Subtitle System` | 配下の `SubtitleDisplay` に注入する `SubtitleSystem`。未設定なら字幕注入はスキップ |
| `Pamphlet Loader` | 配下の `MashiroPamphletViewer` に注入する `MashiroPamphletLoader`。未設定ならスキップ |
| `Target Roots` | スキャン起点の Transform 配列。空なら自身の配下を再帰スキャン。席列の中間 GameObject（`A`, `B`, …）を個別指定すると取りこぼしが少ない |
| `Debug Log` | 注入結果の詳細をコンソールへ出力（失敗警告は常に出力） |

- 対象側で既に参照が設定済みの場合はそちらが優先されます
- このコンポーネントは任意です。参照を 1 個ずつ手動アサインする運用も従来通り可能です
- 依存先（`SubtitleSystem` / `Pamphlet`）が存在するプロジェクトでのみコンパイルできます

## ライセンス

このフォルダの内容は MIT License で提供します（リポジトリルートの `LICENSE.md` を参照）。

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
