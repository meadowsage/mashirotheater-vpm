# OnOffSwitches

任意の GameObject の ON/OFF をボタン操作で切り替えるためのスイッチ群です。
用途に応じて以下を使い分けてください。

| コンポーネント | 同期 | ボタン数 | 主な用途 |
| --- | --- | --- | --- |
| `MashiroGlobalOnOffSwitch` | 全プレイヤーで同期 | 1 | 1 つのボタンで全員に同じ状態を見せたい対象 |
| `MashiroLocalOnOffSwitch` | ローカルのみ | 1 | プレイヤーごとに ON/OFF を切り替えたい UI |
| `MashiroMultiGlobalOnOff` (+`MashiroMultiGlobalOnOffButton`) | 全プレイヤーで同期 | 複数 | 1 つの対象を複数ボタンから連動して制御したい場合 |

> **複数ボタンで 1 つの対象を制御したいとき**は `MashiroGlobalOnOffSwitch` を複数並べてはいけません。
> 各スイッチが独立した同期状態を持つため互いに競合し、特に後から Join したプレイヤーで
> 表示が食い違います。この用途では後述の `MashiroMultiGlobalOnOff` を使ってください。

## 共通の使い方

1. 対象 GameObject に各スイッチコンポーネントを追加します。
2. インスペクタで対象・初期状態・ボタン色を設定します。**フィールド名はコンポーネントごとに異なります**（下記「Inspector フィールド」を参照）。
3. 子に `TextMeshProUGUI` があると自動的にラベルとして扱われます。表示される文字列はコンポーネントごとに異なります（下記「ラベルの扱い」を参照）。

## Inspector フィールド

### MashiroGlobalOnOffSwitch

| フィールド | 既定値 | 内容 |
|---|---|---|
| `Target` | – | ON/OFF を切り替える GameObject |
| `On Color` | `(0.69, 0.239, 0.016)` | ON 時のボタン色 |
| `Off Color` | 黒 | OFF 時のボタン色 |
| `Initial State` | `false` | ワールド入室直後の ON/OFF |
| `Use Game Object Name For Label` | `true` | ON のとき、子ラベルに GameObject 名を表示する |

### MashiroLocalOnOffSwitch

初期状態のフィールド名だけ他と異なり、**`Start Enabled`**（Global 系の `Initial State` に相当）です。

| フィールド | 既定値 | 内容 |
|---|---|---|
| `Target` | – | ON/OFF を切り替える GameObject |
| `Start Enabled` | `false` | ワールド入室直後の ON/OFF |
| `Use Custom Labels` | `false` | ON のとき、ラベル文字列を ON/OFF で切り替える |
| `Enabled Label` | `ON` | `Use Custom Labels` が ON のときの ON 時ラベル |
| `Disabled Label` | `OFF` | `Use Custom Labels` が ON のときの OFF 時ラベル |
| `Enabled Color` | `(0.69, 0.239, 0.016)` | ON 時のボタン色 |
| `Disabled Color` | 黒 | OFF 時のボタン色 |
| `Update Button Color` | `true` | OFF にするとボタン色を書き換えない（見た目を自前で管理したいとき） |

### MashiroMultiGlobalOnOff（コントローラ）

| フィールド | 既定値 | 内容 |
|---|---|---|
| `Target` | – | ON/OFF を切り替える GameObject |
| `Buttons` | – | この対象を制御する全ボタン（見た目を揃えるため全て登録する） |
| `Initial State` | `false` | ワールド入室直後の ON/OFF |

### MashiroMultiGlobalOnOffButton（ボタン）

| フィールド | 既定値 | 内容 |
|---|---|---|
| `Controller` | – | 状態を管理する `MashiroMultiGlobalOnOff` |
| `On Color` | `(0.69, 0.239, 0.016)` | ON 時のボタン色 |
| `Off Color` | 黒 | OFF 時のボタン色 |
| `Use Game Object Name For Label` | `true` | ON のとき、子ラベルに GameObject 名を表示する |

## ラベルの扱い

子の `TextMeshProUGUI` は自動的に検出されますが、そこに入る文字列はコンポーネントによって異なります。

- **`MashiroGlobalOnOffSwitch` / `MashiroMultiGlobalOnOffButton`**: `Use Game Object Name For Label` が ON（既定）のとき、起動時にラベルへ **GameObject 名** を設定します。OFF にするとシーンで設定した文字列のままです。いずれの場合も ON/OFF で文字列は変わりません。
- **`MashiroLocalOnOffSwitch`**: GameObject 名は使いません。既定（`Use Custom Labels` が OFF）では**シーンで設定した文字列をそのまま保持**します。`Use Custom Labels` を ON にすると、ON 時は `Enabled Label`、OFF 時は `Disabled Label` に切り替わります。

## 操作方法

### MashiroGlobalOnOffSwitch（2 種類サポート）

以下のどちらの形態でも動作します。両者の併用も可能です。

#### A. UI ボタンとして使う

- 対象 GameObject に `Button` コンポーネントを付け、`OnClick()` から
  当該スクリプトの `OnButtonClick` を呼ぶように設定します。
- UI のクリック操作で ON/OFF が切り替わります。

#### B. Cube などの 3D オブジェクトとして使う

- 対象 GameObject に `Collider`（Cube の `BoxCollider` 等）を付けます。
  `Button` コンポーネントは不要です。
- VRChat の「Use（インタラクト）」操作で ON/OFF が切り替わります。
- A と B を併用することもできます（例: ワールドスペースの UI ボタンに
  3D Collider を重ねて、ポインタクリックと近接インタラクトの両方を
  受け付ける構成）。

### MashiroLocalOnOffSwitch（2 種類サポート）

`MashiroGlobalOnOffSwitch` と同様に、以下のどちらの形態でも動作します（併用も可能）。
切り替えはローカルのみで、他プレイヤーには同期されません。

#### A. UI ボタンとして使う

- 対象 GameObject に `Button` コンポーネントを付け、`OnClick()` から
  当該スクリプトの `OnButtonClick` を呼ぶように設定します。
- UI のクリック操作で ON/OFF が切り替わります。

#### B. Cube などの 3D オブジェクトとして使う

- 対象 GameObject に `Collider`（Cube の `BoxCollider` 等）を付けます。
  `Button` コンポーネントは不要です。
- VRChat の「Use（インタラクト）」操作で ON/OFF が切り替わります。
- A と B を併用することもできます。

## MashiroGlobalOnOffSwitch 固有の挙動

- 状態はマスタークライアントが初期化し、`UdonSynced` により全員に同期されます。
- 後から Join したプレイヤーには現在の状態が反映されます。
- 操作したプレイヤーが自動的にオーナーになります。

## MashiroMultiGlobalOnOff（複数ボタン連動）

1 つの対象 GameObject を、複数のボタンから連動して ON/OFF する構成です。
**同期状態をコントローラ 1 箇所だけに集約する**ことで、複数ボタン間の競合や
Join 時の表示食い違いを構造的に防ぎます。

### 構成

- **`MashiroMultiGlobalOnOff`（コントローラ）**: 対象 GameObject と同期状態（唯一の真実）を
  保持します。状態を持つのはこのコンポーネントだけです。
- **`MashiroMultiGlobalOnOffButton`（ボタン）**: 押下をコントローラへ転送し、見た目は
  コントローラの状態をミラーするだけ。同期状態は持ちません。1 つの対象に対して複数並べられます。

### セットアップ

1. 空の GameObject（または任意のオブジェクト）に `MashiroMultiGlobalOnOff` を付け、
   **Target** に制御対象、**Initial State** に初期状態を設定します。
2. 各ボタンの GameObject に `MashiroMultiGlobalOnOffButton` を付け、**Controller** に 1. の
   コントローラを指定します。ボタン色・ラベルは各ボタンで設定します。
3. コントローラの **Buttons** 配列に、2. で作った全ボタンを登録します
   （見た目を全ボタンで同期させるために必要）。
4. 各ボタンは `MashiroGlobalOnOffSwitch` と同様、UI `Button`（`OnClick` から
   `OnButtonClick` を呼ぶ）と 3D `Collider`（インタラクト）の両形態に対応します。

### 挙動

- どのボタンから押しても、コントローラの 1 つの同期状態が反転し、対象と全ボタンの見た目が
  一致して更新されます。
- 同期変数はコントローラに 1 つだけなので、後から Join したプレイヤーでも状態が競合しません。
- 操作したプレイヤーがコントローラのオーナーになります。

## API リファレンス

### MashiroLocalOnOffSwitch（ローカル）

| メソッド | 用途 | 呼び出し種別 |
|---|---|---|
| `OnButtonClick()` | 状態をトグル | `Button.OnClick` から配線 |
| `Interact()` | 状態をトグル | オブジェクトへの Interact（配線不要） |
| `Toggle()` / `SetState(bool)` / `GetState()` | 外部からの制御・参照 | 他の Udon から呼ぶ内部連携用 |

### MashiroGlobalOnOffSwitch（全体同期）

| メソッド | 用途 | 呼び出し種別 |
|---|---|---|
| `OnButtonClick()` | 状態をトグル（全員同期） | `Button.OnClick` から配線 |
| `Interact()` | 状態をトグル（全員同期） | オブジェクトへの Interact（配線不要） |
| `State`（プロパティ） | 現在状態の取得（設定は内部からのみ） | 内部専用（配線不要） |
| `OnDeserialization()` / `OnPlayerJoined()` | 同期処理 | 内部専用（配線不要） |

### MashiroMultiGlobalOnOff（複数ボタン連動・コントローラ）

| メソッド | 用途 | 呼び出し種別 |
|---|---|---|
| `Toggle()` | 状態をトグル（全員同期） | ボタン側が呼ぶ内部連携用。他の Udon からも呼び出し可 |
| `GetState()` | 現在状態の取得 | 他の Udon から呼ぶ内部連携用 |
| `State`（プロパティ） | 現在状態の取得（設定は内部からのみ） | 内部専用（配線不要） |
| `OnDeserialization()` / `OnPlayerJoined()` | 同期処理 | 内部専用（配線不要） |

### MashiroMultiGlobalOnOffButton（複数ボタン連動・ボタン）

| メソッド | 用途 | 呼び出し種別 |
|---|---|---|
| `OnButtonClick()` | コントローラへトグルを転送 | `Button.OnClick` から配線 |
| `Interact()` | 同上 | オブジェクトへの Interact（配線不要） |
| `ApplyVisual(bool)` | 表示更新 | コントローラが呼ぶ内部連携用 |

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
