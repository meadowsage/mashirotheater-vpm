# AudioZoneController 使い方ガイド

このフォルダには、ワールド内のボイス聞こえ方を
**拡声（Amplify）/ 防音（Soundproof）/ 外音遮断（Outside Sound Block）/ 通常（Neutral）** で制御する
`MashiroAudioZoneController` が含まれています。

> 注意: このコンポーネントは、他の拡声・音声制御ギミックと干渉する可能性があります。

---

## 同梱ファイル

- `MashiroAudioZoneController.cs`
  - メイン制御コンポーネント
- `MashiroAmplifyZone.cs`
  - 拡声エリアごとの `Far / Gain` を持つ補助コンポーネント
- `MashiroSoundproofZone.cs`
  - 防音エリアごとの `BoxCollider` と滞在中インジケータ GameObject を紐付ける補助コンポーネント
- `AudioZoneController.prefab`
  - `MashiroAudioZoneController` と UI（滞在者一覧パネル）、判定用 Collider をまとめた構成例プレハブ
- `MashiroSoundproofShell.mat`
  - 防音エリア滞在中インジケータ用のマテリアル（`MashiroTheater/CubeInteriorBand` シェーダー）

防音エリア滞在中インジケータ用には、汎用シェーダー `_Common/Shaders/CubeInteriorBand.shader` を利用します（Cube 4 側面の指定高さに水平な帯／ボーダー模様を描く方式、Quest 互換）。

---

## 動作ルール（優先順）

**自分（リスナー）から見た他プレイヤーの聞こえ方**として、以下の順番で適用されます。

1. **自分が外音遮断エリア内** かつ **相手が同じ外音遮断エリア外**（エリア外／別の外音遮断エリア内のどちらも該当）
   - `VoiceGain` に `Isolate Outside Gain` を適用（`VoiceDistanceFar` は `Neutral Far` のまま）
2. 相手が **Amplifyゾーン内**
   - そのゾーンの `Override Far / Override Gain` を適用
3. 相手が **Soundproofゾーン内** かつ **自分が同じ防音ゾーン外**
   - `VoiceDistanceFar = 0.01` を適用（固定）
4. それ以外
   - `Neutral Far / Neutral Gain` を適用

自分が外音遮断エリア内にいても、**相手が同じ外音遮断エリア内**にいる場合はルール 1 が適用されず、2 以降（拡声・防音・通常）が通常どおり判定されます。

---

## セットアップ手順

### 共通

1. 任意の GameObject に `MashiroAudioZoneController` をアタッチ
2. 必要に応じて UI テキスト参照を割り当て
   - `playersAmplifyText`
   - `playersSoundproofText`
   - `lastUpdateTimeText`

> **判定 Collider について**
> `MashiroAmplifyZone` / `MashiroSoundproofZone` は、判定に使う `BoxCollider` を `Zone Collider` フィールドで**明示的に指定**します（自動取得・自動添付は行いません）。
> - **1 つの GameObject で完結させたい場合**: 同じ GameObject に `BoxCollider` を置き、それを `Zone Collider` にドラッグして指定します。
> - **当たり判定とインジケータ表示を別 GameObject に分けたい場合**: 別 GameObject に置いた `BoxCollider` を `Zone Collider` に指定できます。コンポーネント側の GameObject には余計な Collider を持たせずに済みます。
> - `Zone Collider` が未設定のエリアは**判定対象から除外**され、Controller 起動時に Console へ警告が出ます。

### 拡声エリアの設置

1. 拡声判定に使う `BoxCollider` を用意する（任意の GameObject）
2. `MashiroAmplifyZone` をアタッチし、`Zone Collider` に手順 1 の `BoxCollider` を指定
3. `MashiroAudioZoneController` の **Amplify** 配列に `MashiroAmplifyZone` を登録

### 防音エリアの設置

1. 防音判定に使う `BoxCollider` を用意する（任意の GameObject）
2. `MashiroSoundproofZone` をアタッチし、`Zone Collider` に手順 1 の `BoxCollider` を指定
3. 必要に応じて滞在中インジケータ GameObject を `MashiroSoundproofZone` の `Inside Indicator` に割り当て（後述）
4. `MashiroAudioZoneController` の **Soundproof** 配列に `MashiroSoundproofZone` を登録

### 外音遮断エリアの設置

「エリア内にいる間、エリア外の声を小さくして聞く」ためのエリアです。**専用コンポーネントは不要**で、`BoxCollider` を直接登録します。

1. 遮断判定に使う `BoxCollider` を用意する（任意の GameObject）
2. `MashiroAudioZoneController` の **Outside Sound Block Zones** 配列に、その `BoxCollider` を直接登録
3. `Isolate Outside Gain` で、エリア外の声に適用する `VoiceGain` を調整

---

## Inspector項目

### Amplify

| フィールド | 既定値 | 内容 |
|---|---|---|
| `Amplify Zones` | – | `MashiroAmplifyZone` の配列。各要素の `Override Far / Override Gain` が適用値になる |

`MashiroAmplifyZone` 側のフィールド:

| フィールド | 既定値 | 内容 |
|---|---|---|
| `Zone Collider` | – | 拡声判定に使う `BoxCollider`（別 GameObject でも可） |
| `Override Far` | `70` | このエリアで適用する `VoiceDistanceFar`（0〜1000 にクランプ） |
| `Override Gain` | `15` | このエリアで適用する `VoiceGain`（0〜24 にクランプ） |

### Soundproof

| フィールド | 既定値 | 内容 |
|---|---|---|
| `Soundproof Zones` | – | `MashiroSoundproofZone` の配列 |

`MashiroSoundproofZone` 側のフィールド:

| フィールド | 既定値 | 内容 |
|---|---|---|
| `Zone Collider` | – | 防音判定に使う `BoxCollider`（別 GameObject でも可） |
| `Inside Indicator` | – | 自分が滞在中の間だけ表示する GameObject（任意） |

### Outside Sound Block Zone（外音遮断エリア）

| フィールド | 既定値 | 内容 |
|---|---|---|
| `Outside Sound Block Zones` | – | 外音遮断判定に使う `BoxCollider` の配列。**コンポーネントではなく `BoxCollider` を直接登録** |
| `Isolate Outside Gain` | `1` | エリア内から**エリア外**の声を聞くときに適用する `VoiceGain`（0〜24） |

### Tick

| フィールド | 既定値 | 内容 |
|---|---|---|
| `Update Interval` | `0.2` 秒 | 更新間隔（0.1〜1.0秒）。小さくするほど反映は速くなるが、更新頻度は上がる |

### Voice Targets

| フィールド | 既定値 | 内容 |
|---|---|---|
| `Neutral Far` | `25` | 通常時の `VoiceDistanceFar`（0〜100 にクランプ） |
| `Neutral Gain` | `15` | 通常時の `VoiceGain`（0〜24 にクランプ） |

### Optional UI

| フィールド | 既定値 | 内容 |
|---|---|---|
| `playersAmplifyText` | – | 拡声エリア滞在者の一覧表示 |
| `playersSoundproofText` | – | 防音エリア滞在者の一覧表示 |
| `lastUpdateTimeText` | – | 最終更新時刻の表示 |

---

## 防音エリア滞在中インジケータの作り方

ローカルプレイヤーがその防音エリア内にいる間だけ、対応する GameObject を有効化する仕組みです。判定 Collider は VR の頭抜け対策で広めに取る運用を想定しているため、視覚側は **部屋の実寸に合わせた専用 GameObject** を別途用意するのが推奨です。

1. 部屋の内寸より各方向 2〜5cm 内側に収まるサイズの Cube を作成（Z ファイト防止）
2. Cube の `Box Collider` は削除（判定は controller 側で行うため不要）
3. 新規マテリアルを作成し、Shader を `MashiroTheater/CubeInteriorBand` に設定（汎用シェーダー、`_Common/Shaders/` 配下）
4. マテリアルプロパティを調整
   - `Color 1`: 既定 `#4CAF50`（録音スタジオ慣習の「SAFE = 緑」に合わせています。アルファで透明度も指定可）
   - `Color 2`: 既定 白（ボーダー模様の 2 色目）。`Color 1` と同じ色にすればストライプは消えて単色帯になる。アルファ 0 にすると「色 1 部分だけが見える破線」になる
   - `Stripe Width`: ストライプ 1 本の幅（メートル）。既定 0.1m (10cm)
   - `Stripe Angle`: ストライプの傾き（度、-89〜89）。既定 0（縦縞）。45 でハザードテープ風の斜め縞。帯の厚みが薄いと斜めが目立ちにくいので、明確な斜めには `Thickness` を `Stripe Width` と同程度まで増やすと良い
   - `Height From Floor`: Cube 底面（= 床面）からの帯の中心高さ（メートル）。既定 1.0m
   - `Thickness`: 帯の太さ（メートル）。既定 0.02m (2cm)
5. Cube を、対応する防音エリアの `MashiroSoundproofZone` の `Inside Indicator` フィールドにドラッグ
6. Cube は初期状態で **非アクティブ** にしておく（controller が必要時に有効化）

### 表示 ON の安全遅延

インジケータは「**自分が防音エリアに入ってから一定時間経過後**」に表示が ON になります。これは、**「視覚的には防音中なのに、他クライアントから見ると同期遅延でまだ防音されていない」というニセ安全状態を避ける** ためです。

- **ON 遅延**: `Update Interval × 2 + 0.2 秒`（既定 Interval 0.2s なら 0.6 秒）
  - 内訳: 自分の Tick 揺らぎ ＋ ネットワーク同期遅延 ＋ 他クライアントの Tick 揺らぎ を保守的に吸収
- **OFF（退出時）は即時反映**
  - 退出後しばらく他者からは防音状態が続くが、これは「他者には聞こえないだけ」で安全側
- エリア境界を短時間に出入りした場合、表示は ON 確定しないまま終わる（ちらつかない）

ラグを短くしたい場合は `Update Interval` を小さく（例: 0.1 秒）すれば、ON 遅延も自動で短く（0.4 秒）なります。

### シェーダーの仕様

- Built-in パイプライン、Quest 互換（テクスチャ・GrabPass・深度参照なし）
- Cube の **4 側面のみ** に水平な帯を描画（天面・床面には描かれない）
- 高さ・ストライプ幅は Cube の各軸ワールドスケールから算出するため、Cube を非正方形に拡縮しても帯の位置とストライプ幅はメートル単位で安定
- 隣接する側面のストライプは、部屋が正方形でないとコーナーでつなぎ目がずれることがあります（仕様上の制約）
- Unity 標準 Cube（ローカル境界 -0.5 〜 +0.5）を前提とした実装
- `Cull Front`: 中から見たときだけ見える設定。外からも見せたい場合はシェーダーの `Cull Front` を `Cull Off` に書き換えてください
- `Blend SrcAlpha OneMinusSrcAlpha`: 通常のアルファブレンド。色の透明度を `Color 1 / Color 2` のアルファチャンネルでそのまま制御できます

---

## UI表示フォーマット

### Amplify表示

```text
[エリア名 | Far : xx | Gain : yy]
name1, name2, name3
```

### Soundproof表示

```text
[エリア名]
name1, name2, name3
```

---

## 固定仕様（調整不可）

- Mute時 `VoiceDistanceFar` は **0.01固定**
- 書き込み差分閾値（epsilon）は **0.01固定**

---

## 運用上の注意

- `OnDisable` / `OnDestroy` で、対象プレイヤーの `Far/Gain` を Neutral 値に戻します。
- そのため、別の音声制御ギミックを同時使用している場合は、値の取り合いが起きる可能性があります。

---

## API リファレンス

**UI へ手配線するものはありません。** 3 コンポーネントとも Inspector の設定だけで動作します。

### MashiroAudioZoneController

public 関数はありません。

### MashiroAmplifyZone（Controller が読み取る内部連携用・配線不要）

| プロパティ | 用途 |
|---|---|
| `BoxCollider Collider { get; }` | 拡声判定に使う Collider（未設定なら `null`。Controller 側でスキップ） |
| `float OverrideFar { get; }` | 適用する `VoiceDistanceFar`（0〜1000 にクランプした値） |
| `float OverrideGain { get; }` | 適用する `VoiceGain`（0〜24 にクランプした値） |

### MashiroSoundproofZone（Controller が読み取る内部連携用・配線不要）

| プロパティ | 用途 |
|---|---|
| `BoxCollider Collider { get; }` | 防音判定に使う Collider（未設定なら `null`。Controller 側でスキップ） |
| `GameObject InsideIndicator { get; }` | 自分が滞在中の間だけ表示する GameObject（未指定可） |

## ライセンス

- `AudioZoneController/LICENSE` は MIT ライセンスです。
- ライセンス適用範囲は、このフォルダ内のスクリプト（`.cs`）です。

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
