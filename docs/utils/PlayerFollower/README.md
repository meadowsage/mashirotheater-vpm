# Mashiro Player Follower

オブジェクトをプレイヤーに追従させるコンポーネント集です。独立した 3 つの機能が入っています。

| コンポーネント | 用途 | 同期 |
|---|---|---|
| `MashiroPlayerFollower`（+ ButtonHandler） | UI でプレイヤーを選んでオブジェクトを追従させる | 全員同期（Manual） |
| `MashiroPlayerNameFollower` | DisplayName 指定のプレイヤーへオブジェクトを**向ける**（スポットライト等） | ローカル一致方式 |
| `MashiroPlayerNameLookTarget` | DisplayName 指定のプレイヤー位置へ自身を**移動**（Cinemachine LookAt 用ダミー） | ローカル一致方式 |

## 1. MashiroPlayerFollower — UI 選択式の追従

プレイヤーが「登録」ボタンで自分を候補一覧に載せ、一覧のボタンで選ばれたプレイヤーに `Target Object` が追従します。選択状態は全員で同期されます。

### 同梱プレハブ

| プレハブ | 内容 |
|---|---|
| `PlayerFollowerBoard.prefab` | `MashiroPlayerFollower` と UI（登録ボタン・候補一覧のスクロールビュー・対象名表示）が組み込み済みのボード |
| `PlayerButton.prefab` | 一覧に並ぶボタン。`MashiroPlayerFollowerButtonHandler` 付きで、`OnClick` から `OnButtonClick` を呼ぶ配線済み |

### セットアップ

1. `PlayerFollowerBoard.prefab` をシーンに配置します。`Player Button Prefab` / `Button Parent` / `Target Object Name Text` と、登録ボタンの `OnClick`（`RegisterSelf`）は配線済みです。
2. ボード上の `MashiroPlayerFollower` の `Target Object` に、追従させたいオブジェクト（スポットライト等）を割り当てます。プレハブでは未設定です。
3. UI を自作する場合は、`Player Button Prefab` に同梱の `PlayerButton.prefab` を指定し、`Button Parent` に一覧の親 Transform を割り当て、登録ボタンの `OnClick` に `RegisterSelf` を配線します。

### MashiroPlayerFollower のフィールド

| フィールド | 内容 |
|---|---|
| `Target Object` | 追従させるオブジェクト |
| `Player Button Prefab` | 一覧に並べるボタンの prefab（同梱の `PlayerButton.prefab`） |
| `Button Parent` | ボタンを生成する親 Transform |
| `Target Object Name Text` | `Target Object` の名前を `Object : <名前>` 形式で表示する TextMeshProUGUI（任意）。起動時に一度だけ設定され、以後は更新されません |

### MashiroPlayerFollowerButtonHandler のフィールド

| フィールド | 既定値 | 内容 |
|---|---|---|
| `Button Text` | – | プレイヤー名を表示する TextMeshProUGUI（prefab で配線済み） |
| `Button Image` | – | 配色を適用する Image（prefab で配線済み） |
| `Normal Color` | `#000000` | 非選択時のボタン背景色 |
| `Selected Color` | `#E85900` | 選択時のボタン背景色 |

### API リファレンス

| メソッド／プロパティ | 用途 | 呼び出し種別 |
|---|---|---|
| `MashiroPlayerFollower.RegisterSelf()` | 自分を候補一覧に登録 | `Button.OnClick` から配線 |
| `MashiroPlayerFollower.TogglePlayerSelection(VRCPlayerApi)` | 追従対象の切替 | ButtonHandler が呼ぶ内部連携用 |
| `MashiroPlayerFollowerButtonHandler.OnButtonClick()` | 一覧ボタンの押下処理 | prefab 内で配線済み |
| `MashiroPlayerFollowerButtonHandler.PlayerId` | ボタンが担当するプレイヤーの playerId（未初期化時は `-1`） | 内部連携用（読み取り専用・配線不要） |
| `Initialize` / `SetSelected` | ボタンの初期化・表示更新 | 内部連携用（手配線不要） |

## 2. MashiroPlayerNameFollower — 名前指定で向ける

DisplayName が完全一致するプレイヤーの方向へ、オブジェクト（スポットライト等）を回転させます。各クライアントが同じ計算をローカル実行するため見え方は概ね一致します（厳密同期なし）。

| フィールド | 既定値 | 内容 |
|---|---|---|
| `Target Object` | – | 向かせたいオブジェクト |
| `Target Player Name` | – | 対象プレイヤーの DisplayName（完全一致） |
| `Target Position Ratio` | `0.02` | 狙う高さの比率。**0 = 頭 / 1 = 足元**（既定値はほぼ頭の位置） |

### API リファレンス

| メソッド | 用途 | 呼び出し種別 |
|---|---|---|
| `_SetTargetPlayerName(string)` | 対象プレイヤー名を変更 | 他コンポーネントから呼ぶ内部連携用 |
| `_ResetRotation()` | 回転を初期状態へ戻す | 同上 |

## 3. MashiroPlayerNameLookTarget — 名前指定で位置追従

DisplayName 指定のプレイヤー位置（頭〜足元の比率指定＋オフセット）へ、自身を滑らかに移動させます。Cinemachine の LookAt にこのオブジェクトを割り当てて使います。

| フィールド | 既定値 | 内容 |
|---|---|---|
| `Target Player Name` | `PlayerName` | 対象プレイヤーの DisplayName（完全一致）。既定値はダミー文字列なので、必ず実際の DisplayName に書き換えます |
| `Target Position Ratio` | `0.35` | 追従する高さの比率。**0 = 頭 / 1 = 足元**（0.3〜0.6 程度が頭の揺れを抑えやすい） |
| `World Offset` | `(0, 0.1, 0)` | 追加のワールドオフセット |
| `Smooth Alpha` | `0.25` | 追従の滑らかさ |
| `Max Step Per Frame` | `0`（無制限） | 1 フレームの最大移動距離 |
| `Fallback Point` | – | 対象不在時に寄せる位置（未指定なら現位置維持） |

### API リファレンス

| メソッド | 用途 | 呼び出し種別 |
|---|---|---|
| `_SetTargetPlayerName(string)` | 対象プレイヤー名を変更 | 他コンポーネントから呼ぶ内部連携用 |

## ライセンス

このフォルダの内容は MIT License で提供します（リポジトリルートの `LICENSE.md` を参照）。

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
