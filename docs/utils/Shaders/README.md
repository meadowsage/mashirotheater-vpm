# _Common / Shaders

各ツールが共有するシェーダーとマテリアル。`MashiroTheater-Utils` に含まれる。

## 構成

`MashiroTheater-Utils` には、配布対象パッケージのアセットから GUID で参照されるファイルのみを同梱する（`.packaging/packages.json` の `pruneToReferenced`）。参照されていないファイルは配布物に含まれない。

| ファイル | 内容 |
|---|---|
| `CubeInteriorBand.shader` | `MashiroTheater/CubeInteriorBand` |
| `TwoSidedOverlay.shader` | `MashiroTheater/TwoSidedOverlay` |
| `TwoSidedOverlayTexture.shader` | `MashiroTheater/TwoSidedOverlayTexture` |
| `../Materials/BlackOut.mat` | `MashiroTheater/TwoSidedOverlay`。`_Color` = `(0, 0, 0, 1)`、`_Alpha` = `0` |
| `../Materials/暗転中ガイド.mat` | `MashiroTheater/CubeInteriorBand`。`_Color` = `(1, 1, 0, 0.031)`、`_Color2` = `(0.953, 0.953, 0.953, 0)`、`_StripeWidth` = `0.1`、`_StripeAngle` = `45`、`_Height` = `1`、`_Thickness` = `1`、`_ShowOutside` = `0` |
| `README.md` | 本ドキュメント |

## 仕様

- すべて Built-in Render Pipeline 用（`CGPROGRAM` / `UnityCG.cginc`）。

| シェーダー | Queue | Cull | ZWrite | ZTest | Blend | GPU インスタンシング | Fallback |
|---|---|---|---|---|---|---|---|
| `MashiroTheater/CubeInteriorBand` | `Transparent` | パス 1: `Front` / パス 2: `Back` | `Off` | 既定 | `SrcAlpha OneMinusSrcAlpha` | 対応 | `Off` |
| `MashiroTheater/TwoSidedOverlay` | `Transparent` | `Off` | `Off` | `Always` | `SrcAlpha OneMinusSrcAlpha` | – | 指定なし |
| `MashiroTheater/TwoSidedOverlayTexture` | `Transparent` | `Off` | `Off` | `Always` | `SrcAlpha OneMinusSrcAlpha` | – | 指定なし |

### MashiroTheater/CubeInteriorBand

- Unity 標準 Cube（ローカル座標 -0.5〜+0.5）を前提とする。
- 4 側面（ローカル `|y| ≤ max(|x|, |z|)` の領域）にのみ水平な帯を描く。天面・底面には描かない。
- 2 パスで描く。パス 1（`Cull Front`）は Cube の内側の面、パス 2（`Cull Back`）は外側の面を描く。
- パス 2 は `_ShowOutside` が 0.5 未満のとき頂点をクリップ範囲外へ移し、描画しない。既定では Cube の内側からのみ帯が見える。
- 帯の中心高さは Cube 底面からのワールド距離 `_Height`、帯の太さは `_Thickness`（いずれも各軸のワールドスケールから換算したメートル単位）。
- 帯の長さ方向に `_StripeWidth` ごとに `_Color` と `_Color2` を交互に切り替える。`_StripeWidth` は 0.0001 未満を 0.0001 として扱う。
- ストライプの境界は `_StripeAngle` 度傾く。0 で帯の長さ方向に垂直。
- ストライプの位相は面ごとに計算するため、X 方向と Z 方向のワールドスケールが異なる Cube ではコーナーで位相が一致しない。
- 出力アルファは選ばれた色のアルファ値。
- テクスチャ・GrabPass・深度テクスチャを使わない。

### MashiroTheater/TwoSidedOverlay

- 単色を出力する。RGB は `_Color`、アルファは `_Alpha`（`_Color` のアルファは使わない）。
- `ZTest Always` のため、他のジオメトリに隠れない。

### MashiroTheater/TwoSidedOverlayTexture

- 出力 = `_MainTex × _Color`。アルファにさらに `_Alpha` を乗算する。
- `_MainTex` のタイリング・オフセットを適用する。
- `ZTest Always` のため、他のジオメトリに隠れない。

## Inspector

### MashiroTheater/CubeInteriorBand

| プロパティ | 表示名 | 型 | 既定値 | 内容 |
|---|---|---|---|---|
| `_Color` | Color 1 (RGB) / Alpha (A) | Color | `(0.30, 0.69, 0.31, 1)` | ストライプの色 1 |
| `_Color2` | Color 2 (RGB) / Alpha (A) | Color | `(1, 1, 1, 1)` | ストライプの色 2 |
| `_StripeWidth` | Stripe Width (m) | Float | `0.1` | ストライプ 1 本の幅（m） |
| `_StripeAngle` | Stripe Angle (deg) | Range(-89, 89) | `0` | ストライプ境界の傾き（度） |
| `_Height` | Height From Floor (m) | Float | `1.0` | Cube 底面から帯の中心までの高さ（m） |
| `_Thickness` | Thickness (m) | Float | `0.02` | 帯の太さ（m） |
| `_ShowOutside` | Visible From Outside | ToggleUI | `0` | ON で Cube の外側の面にも帯を描く |

### MashiroTheater/TwoSidedOverlay

| プロパティ | 表示名 | 型 | 既定値 | 内容 |
|---|---|---|---|---|
| `_Color` | Color | Color | `(0, 0, 0, 1)` | 出力色（RGB のみ使用） |
| `_Alpha` | Alpha | Range(0, 1) | `1.0` | 出力アルファ |

### MashiroTheater/TwoSidedOverlayTexture

| プロパティ | 表示名 | 型 | 既定値 | 内容 |
|---|---|---|---|---|
| `_MainTex` | Texture | 2D | `white` | テクスチャ |
| `_Color` | Color | Color（HDR） | `(1, 1, 1, 1)` | 乗算色 |
| `_Alpha` | Alpha | Range(0, 1) | `1.0` | アルファへの乗算値 |

## ライセンス

- MIT License（リポジトリルートの `LICENSE.md`）。
