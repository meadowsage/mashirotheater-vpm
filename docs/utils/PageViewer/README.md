# Mashiro Page Viewer

Sprite 配列を 1 枚ずつ `Image` に表示し、フェード付きでページ送りする UdonSharp コンポーネント（`MashiroPageViewer`）。ページ位置はローカル管理と全プレイヤー同期を切り替えられる。対象 Transform の拡大・縮小と水平化も行う。

## 構成

| ファイル | 内容 |
|---|---|
| `MashiroPageViewer.cs` | 本体スクリプト（`MashiroPageViewer`） |
| `MashiroPageViewer.asset` | `MashiroPageViewer` の UdonSharp ProgramAsset |
| `MashiroPageViewer.prefab` | Canvas 配下に表示 `Image`・`Prev` / `Next` ボタン・ページ番号用 `TextMeshProUGUI`・`MashiroPageViewer` を配置したプレハブ |
| `MashiroImageGalleryWithUIHandle.prefab` | `MashiroPageViewer.prefab` をネストし、ルートに `BoxCollider`・`Rigidbody`・`VRC_Pickup` を持つプレハブ |
| `台本Local_横.prefab` | 台本用のローカル閲覧構成（横）（配布対象外） |
| `台本Local_縦.prefab` | 台本用のローカル閲覧構成（縦）（配布対象外） |
| `BREAK_FAST/` | サンプルページ画像 9 枚（配布対象外） |

## 依存

- パッケージ: `MashiroTheater-Utils`（VPM `com.mashirotheater.utils`）
- TextMeshPro（`pageText` が `TextMeshProUGUI` 型）
- `MashiroPageViewer.prefab` は `_Common/Icons/arrow_left.png` / `_Common/Icons/arrow_right.png` を参照する。

## 仕様

### ページ送り

- `images` が null または空のとき、`Start` で `Debug.LogError("No images assigned to MashiroPageViewer")` を出して初期化を中断する。
- ページ番号は `images` の添字（0 始まり）で管理し、末尾の次は先頭、先頭の前は末尾へループする。
- フェード中（フェードアウト・フェードイン）のページ送り操作は無視する。
- ページ切り替えは、フェードアウト（`fadeDuration` 秒）→ Sprite 差し替え → フェードイン（`fadeDuration` 秒）の順に行う。切り替え全体の所要時間は `fadeDuration` の 2 倍。
- フェードは各 `Image` の `color` のアルファを、`Start` 時点の色のアルファに 0〜1 を乗じた値で変化させる。
- Sprite は `displayImage` と `additionalDisplayImages` の全要素（null を除く）に同じものを設定する。
- `pageText` には `"{現在ページ + 1} / {images.Length}"` を表示する。更新は Sprite 差し替えのタイミングで行う。
- `reverseDirection` が `true` のとき、`OnNextButtonPressed` と `OnPrevButtonPressed` の進む向きが入れ替わる。`OnPageAdvanceButtonPressed` は常に +1 ページ進む。

### 同期

- 同期モード: `BehaviourSyncMode.Manual`
- 同期変数: `syncedIndex`（`int`、`[UdonSynced(UdonSyncMode.None)]`）
- `useGlobalSync` が `true` のとき:
  - ページ送り操作を行ったプレイヤーが `Networking.SetOwner` でオーナーになり、`syncedIndex` を更新して `RequestSerialization` する。
  - 次ページの計算元は `syncedIndex`。
  - `OnDeserialization` で `syncedIndex` が表示中のページと異なればフェードアウトを開始する。この処理はフェード中でも実行され、進行中のフェードを最初からやり直す。
  - `Start` 時点の `syncedIndex` を初期ページにする。
- `useGlobalSync` が `false` のとき、ページ位置はローカルのみで管理し、`OnDeserialization` は何もしない。
- フェード、拡大・縮小、水平化は同期しない（実行したクライアントのみ）。

### 拡大・縮小

- `scaleTarget` 未設定のときは倍率のみ変化し、Transform は変更しない。
- `Start` 時点の `scaleTarget.localScale` を基準スケールとし、`基準スケール × 倍率` を適用する。
- 倍率の初期値は `Mathf.Clamp(1, minScaleMultiplier, maxScaleMultiplier)`。
- 1 回の操作で倍率を `scaleStep` 増減し、`minScaleMultiplier`〜`maxScaleMultiplier` に制限する。
- `scaleStep` が 0 以下のとき、拡大・縮小操作は何もしない。

### 水平化

- 対象は `horizontalResetTarget`。未設定ならこのコンポーネントが付いた GameObject の Transform。
- 対象のワールド回転（`eulerAngles`）を `(0, 現在の Y, 0)` に設定する。位置は変更しない。

## Inspector

### MashiroPageViewer

| フィールド | 型 | 既定値 | 必須 | 内容 |
|---|---|---|---|---|
| `displayImage` | `Image` | なし | – | ページを表示する `Image` |
| `additionalDisplayImages` | `Image[]` | 空 | – | 同じページを同時に表示する追加の `Image` |
| `pageText` | `TextMeshProUGUI` | なし | – | ページ番号の表示先。未設定なら表示しない |
| `images` | `Sprite[]` | 空 | ○ | ページ画像。1 要素以上 |
| `fadeDuration` | `float` | `1` | – | フェードアウト・フェードインそれぞれの秒数 |
| `useGlobalSync` | `bool` | `false` | – | `true` でページ位置を全プレイヤー同期する |
| `reverseDirection` | `bool` | `false` | – | `true` で `OnNextButtonPressed` / `OnPrevButtonPressed` の向きを反転する |
| `scaleTarget` | `Transform` | なし | – | 拡大・縮小の対象 |
| `scaleStep` | `float` | `0.1` | – | 1 回の拡大・縮小で増減する倍率 |
| `minScaleMultiplier` | `float` | `0.5` | – | 倍率の下限 |
| `maxScaleMultiplier` | `float` | `2` | – | 倍率の上限 |
| `horizontalResetTarget` | `Transform` | なし | – | 水平化の対象。未設定ならこの GameObject 自身 |

## API リファレンス

### MashiroPageViewer

#### UI へ手配線するもの

| シグネチャ | 用途 | 呼び出し種別 |
|---|---|---|
| `void OnNextButtonPressed()` | `reverseDirection` が `false` なら +1、`true` なら −1 ページ送る | `Button.OnClick` から配線 |
| `void OnPrevButtonPressed()` | `reverseDirection` が `false` なら −1、`true` なら +1 ページ送る | `Button.OnClick` から配線 |
| `void OnPageAdvanceButtonPressed()` | `reverseDirection` に関係なく +1 ページ送る | `Button.OnClick` から配線 |
| `void OnZoomInButtonPressed()` | 倍率を `scaleStep` 上げる | `Button.OnClick` から配線 |
| `void OnZoomOutButtonPressed()` | 倍率を `scaleStep` 下げる | `Button.OnClick` から配線 |
| `void OnHorizontalResetButtonPressed()` | 対象 Transform を水平化する | `Button.OnClick` から配線 |

#### 内部連携用（配線不要）

| シグネチャ | 用途 | 呼び出し種別 |
|---|---|---|
| `override void OnDeserialization()` | 同期されたページ位置を反映する | VRChat コールバック（内部専用） |

## ライセンス

MIT License（リポジトリルートの `LICENSE.md`）。

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
