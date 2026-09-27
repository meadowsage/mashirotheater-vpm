# Mashiro Pickup Hold SFX

Pickup（小道具）の使用中・保持中に効果音を鳴らすギミックです。再生状態を同期するため、**全プレイヤーに聞こえます**。

## 主な機能・仕様

- 既定では**トリガー使用中（Use Down 〜 Use Up）のみ**再生
- `Play While Held Without Use` を ON にすると、**持っている間ずっと**再生
- 再生・停止時に短い音量フェードをかけてクリックノイズを防止
- 再生状態は `[UdonSynced]` で同期。持ち主の退出やオーナー移譲時も再生状態が破綻しないよう処理済み

## セットアップ

1. `VRC_Pickup` の付いたオブジェクトに `MashiroPickupHoldSfx` と `AudioSource` を追加します
2. `Audio Source` を Inspector で割り当て、その `AudioSource` に鳴らしたい AudioClip を設定します
   - `AudioSource` の Play On Awake / Loop / 3D（Spatial Blend）は起動時に自動設定されるため、**AudioClip の割り当てだけで動きます**

| フィールド | 既定値 | 内容 |
|---|---|---|
| `Audio Source` | – | 再生に使う AudioSource（必須。未設定だとコンポーネントが停止します） |
| `Pickup` | – | 対象の VRC_Pickup。**未設定なら同じ GameObject の `VRC_Pickup` を自動取得**します（見つからない場合はコンポーネントが停止します） |
| `Play While Held Without Use` | `false` | ON: 保持中ずっと再生 / OFF: 使用中のみ |
| `Fade Seconds` | `0.10` | 再生・停止時の音量フェード時間 |
| `Target Volume` | `1` | 再生時の音量 |

## API リファレンス

### MashiroPickupHoldSfx

public 関数はすべて VRChat のイベントオーバーライド（`OnPickup` / `OnDrop` / `OnPickupUseDown` / `OnPickupUseUp` 等）です。**UI からの配線は不要**で、Inspector の割り当てだけで動作します。

## ライセンス

このフォルダの内容は MIT License で提供します（リポジトリルートの `LICENSE.md` を参照）。

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
