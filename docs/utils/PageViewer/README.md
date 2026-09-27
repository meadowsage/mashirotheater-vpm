# Mashiro Page Viewer

Sprite 配列をページ送りで表示する画像ビューアです。台本・パンフレット・スライド資料などの複数ページ画像を、フェード付きでめくって閲覧できます。ページ位置を全員で同期するモードと、各自がローカルでめくるモードを選べます。

## 主な機能

- Sprite 配列のページ送り（前へ / 次へ、末尾と先頭はループ）
- ページ切り替え時のフェード（時間は調整可）
- ページ番号表示（"3 / 12" 形式）
- **グローバル同期モード**（任意）: ページ位置を全プレイヤーで共有。めくった人がオーナーになり、Late Joiner にも現在ページが反映される
- 拡大・縮小（対象 Transform のスケール操作、上限・下限あり）
- 水平化（傾きのリセット）
- 同じページを複数の `Image` に同時表示（メイン + 追加ディスプレイ）

## 同梱ファイル

配布パッケージに含まれるもの。

| ファイル | 用途 |
|---|---|
| `MashiroPageViewer.prefab` | 基本構成（表示 Image + ページ送り UI） |
| `MashiroImageGalleryWithUIHandle.prefab` | UI ハンドル付きのギャラリー構成例（`MashiroPageViewer.prefab` を内包） |
| `Images/arrow_left.png` `Images/arrow_right.png` | ページ送りボタン用の矢印画像 |

以下はリポジトリ上にのみ存在するサンプルで、**配布パッケージには含まれません**。

| ファイル | 内容 |
|---|---|
| `台本Local_横.prefab` / `台本Local_縦.prefab` | 台本用のローカル閲覧構成サンプル（横書き / 縦書き） |
| `BREAK_FAST/` | 動作確認用のサンプルページ画像 9 枚 |

## セットアップ

1. プレハブをシーンに配置するか、Canvas 配下に `Image` とページ送りボタンを用意して `MashiroPageViewer` を追加します
2. `Images` にページ画像の Sprite 配列を設定します（**1 枚以上必須**。空だと動作しません）
3. ボタンの `OnClick` を API リファレンスの通り配線します

## Inspector フィールド

| フィールド | 既定値 | 内容 |
|---|---|---|
| `Display Image` | – | ページを表示するメインの `Image` |
| `Additional Display Images` | – | 同じページを同時表示する追加の `Image` 配列（不要なら空） |
| `Page Text` | – | ページ番号表示用 `TextMeshProUGUI`（不要なら None） |
| `Images` | – | ページ画像の Sprite 配列（必須） |
| `Fade Duration` | `1` 秒 | ページ切り替え時のフェード時間 |
| `Use Global Sync` | `false` | ON でページ位置を全プレイヤー同期。OFF なら各自ローカル |
| `Reverse Direction` | `false` | ページ送りの方向を反転（右綴じの縦書き台本など） |
| `Scale Target` | – | 拡大・縮小の対象 Transform（未設定なら拡縮機能オフ） |
| `Scale Step` | `0.1` | 1 回あたりの拡縮量 |
| `Min / Max Scale Multiplier` | `0.5` / `2` | 拡縮の下限・上限（初期スケール比） |
| `Horizontal Reset Target` | – | 水平化（傾きのリセット）の対象 Transform。**未設定ならこのコンポーネントが付いた GameObject 自身が対象** |

## API リファレンス

### MashiroPageViewer

すべて **UI の `Button.OnClick` から配線**して使います。

| メソッド | 用途 |
|---|---|
| `OnNextButtonPressed` | 「→」ボタン用。`Reverse Direction` が OFF なら次のページへ、ON なら前のページへ（末尾と先頭はループ） |
| `OnPrevButtonPressed` | 「←」ボタン用。`Reverse Direction` が OFF なら前のページへ、ON なら次のページへ |
| `OnPageAdvanceButtonPressed` | `Reverse Direction` の設定に関係なく、常に次のページへ |
| `OnZoomInButtonPressed` / `OnZoomOutButtonPressed` | 拡大 / 縮小 |
| `OnHorizontalResetButtonPressed` | 対象 Transform を水平化する（X/Z 回転を 0 にし、Y 軸の向きと位置は維持） |

`OnNextButtonPressed` / `OnPrevButtonPressed` は **画面上の矢印の向き**に対応するメソッドです。右綴じの台本などで `Reverse Direction` を ON にすると、矢印ボタンの配線を変えずにページ送りの向きだけを反転できます。

画像パネル全体をボタン化して「クリックで読み進める」ようにする場合など、押した位置と向きが対応しない配線先には `OnPageAdvanceButtonPressed` を使ってください。`Reverse Direction` の設定に左右されず、常にページ番号が増える方向へ進みます。

`OnDeserialization` は同期用の内部処理です（配線不要）。

## 同期の仕様

- 同期方式は **Manual** に固定されています（スクリプト側で指定済みのため、Inspector での変更は不要です）
- `Use Global Sync` が ON のとき、ページをめくったプレイヤーがオブジェクトのオーナーになり、ページ番号が全員に配信されます
- OFF のときは完全ローカルで、各自が好きなページを閲覧できます（台本の個人閲覧向け）
- フェード演出は各クライアントのローカル処理です

## ライセンス

このフォルダの内容は MIT License で提供します（リポジトリルートの `LICENSE.md` を参照）。

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
