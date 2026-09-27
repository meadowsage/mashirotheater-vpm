# _Common / Shaders

ワールド共通で使えるユーティリティシェーダー群です。

---

## UICanvasOpaque

`Shader "MashiroTheater/UICanvasOpaque"` / `UICanvasOpaque.shader`

Canvas (RawImage / Image) のパネル背景が **奥にある別の UI (動画プレイヤー UI 等) を透けさせてしまう問題** を、Canvas 自体に貼るマテリアルだけで解消するためのシェーダーです。

### 背景

Unity 標準の `UI/Default` は `ZWrite Off` で Transparent キュー (3000) に描画されるため、深度バッファに書き込みません。結果として後から描画される別 Transparent (別 Canvas や半透明オブジェクト) を奥側で隠せず、「パネルの奥が透けて見える」状態になります。

本シェーダーは `UI/Default` を踏襲しつつ以下を変更し、不透明ピクセルが深度バッファに書き込まれるようにしています。

- `ZWrite On`
- `_OpaqueAlphaThreshold` 未満のアルファを `clip` で破棄
- 書き込む深度値だけを画面位置を変えずに「ごく僅かに奥」へバイアス (`_DepthBias`) し、同一 Canvas 内の兄弟要素 (テキスト等) と Z-fighting しないようにする

### 解決できるもの / できないもの

- ✅ 通常の Transparent シェーダー (`UI/Default` 等) で描画された奥の UI / オブジェクト
- ✅ 不透明シェーダーで描画されたワールドメッシュ
- ❌ **VRChat のネームプレート** … 常時最前面表示 (overlay レイヤー / `ZTest Always` 相当) で描画されるため、Canvas 側マテリアルでは原理的に隠せません。プレイヤー側の Safety / ネームプレート設定に依存するため、配置で逃がす必要があります。

### 使い方

1. プロジェクト内の任意の場所 (例: `_Common/Materials/`) で `Create > Material` 。
2. Shader に `MashiroTheater/UICanvasOpaque` を選択。
3. パネルに使っている RawImage / Image の **Material** 欄に割り当て。

### Inspector パラメータ

| プロパティ | 説明 | 推奨値 |
| --- | --- | --- |
| `Tint` | 色 (RawImage/Image の `color` と乗算) | 用途に応じて |
| `Opaque Alpha Threshold` | このアルファ未満のピクセルは破棄 (描画されない & 深度も書かない) | 完全不透明パネル: `0.99` / フチを残したい場合: `0.5` 前後 |
| `Depth Bias (push back)` | 書き込む深度値だけを奥側にずらす量。同一 Canvas 内のテキストや子要素と Z-fighting して点滅・欠けが出るときに使用 | 通常: `0.001` / 干渉が残るなら少し増やす |
| `Use Alpha Clip` | UI 標準の `UNITY_UI_ALPHACLIP` 互換 (通常 OFF のままで OK) | OFF |

その他 (Stencil / ColorMask) は `UI/Default` と同じ意味で、Mask コンポーネントとの互換性のために残してあります。

### 注意

- アンチエイリアスのかかったフチや半透明グラデーションは、`Opaque Alpha Threshold` のしきい値で**完全に破棄されます**。柔らかいフチが必要な場合はしきい値を下げるか、フチ部分と背景部分を別 Image に分けてください。
- Canvas が **Screen Space - Overlay** の場合は、そもそも深度バッファを参照しない描画のため本シェーダーの利点はありません。**World Space Canvas** での利用を想定しています。
- ワールド内に複数の本シェーダー製パネルを重ねる場合は、互いの前後関係は Transform 距離で決まります。順序が安定しない場合は Canvas の `Sorting Order` で調整してください。
- 同じ Canvas 内で「最背面の Panel だけにこのシェーダーを適用し、上に文字やボタンを乗せる」使い方を想定しています。Panel と兄弟要素が同じ Z 平面にいるため、`Depth Bias` を `0` にすると Z-fighting で文字や子要素が欠けることがあります。デフォルト値のままで通常問題ないはずです。
