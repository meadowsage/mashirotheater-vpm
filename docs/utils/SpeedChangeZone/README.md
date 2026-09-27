# Mashiro Speed Change Zone

指定エリア内にいる間、プレイヤーの移動速度を倍率変更するギミックです。舞台裏の高速移動や、演出上の減速エリアなどに使います。

## 主な機能・仕様

- Start 時に実測した通常速度を基準（Neutral）とし、毎チェックで「エリア内なら Neutral × 倍率 / 外なら Neutral」を維持します（ステートレス方式）
- 判定はローカルプレイヤーの**足元位置**で行い、回転した BoxCollider にも対応
- 完全ローカル処理（同期なし）
- コンポーネントが無効化・破棄されたとき（`OnDisable` / `OnDestroy`）は、速度を Neutral へ戻します
- **他の移動速度系ギミックとの併用は非対応**です。本コンポーネントが速度の最終決定者として毎回上書きします

## セットアップ

同梱の `SpeedChangeZone.prefab` は、エリア形状用の Trigger 付き BoxCollider（描画は無効）と `MashiroSpeedChangeZone` を持つプレハブです。

1. `SpeedChangeZone.prefab` をシーンに配置し、Transform の位置・スケールで速度を変えたいエリアの形を作ります。
2. `Speed Zones` に、そのエリアの BoxCollider（プレハブ自身のものでも可）を割り当てます。プレハブでは未設定のため、割り当てないと何も起こりません。
3. `Speed Ratio` で倍率を調整します。

プレハブを使わない場合は、`MashiroSpeedChangeZone` を任意の GameObject に付け、同じく `Speed Zones` と倍率を設定します。

| フィールド | 既定値 | 内容 |
|---|---|---|
| `Speed Zones` | – | 速度倍率を適用するエリアの BoxCollider 群 |
| `Update Interval` | `1.0` 秒 | チェック間隔 |
| `Speed Ratio` | `0.44` | エリア内での速度倍率（0.05〜10） |
| `Apply Epsilon` | `0.01` | この差を超えたときだけ速度を再設定（微小な上書きの抑制） |

## API リファレンス

### MashiroSpeedChangeZone

public 関数はありません。**配線は不要**で、Inspector の設定だけで動作します。

## ライセンス

このフォルダの内容は MIT License で提供します（リポジトリルートの `LICENSE.md` を参照）。

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
