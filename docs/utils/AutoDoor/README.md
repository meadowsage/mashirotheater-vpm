# Mashiro Auto Door

プレイヤーの接近で開閉する自動ドアです。Timeline の前半を「開き」、後半を「閉じ」とみなして再生位置を制御するため、開閉途中でも自然に反転します。

## 主な機能・仕様

- 誰かが判定エリアに入ると即座に開き始める（閉じ途中でも逆算して開き直す）
- **最後の入室**から `Close Delay` 秒ごとにエリア内をチェックし、誰もいなければ閉じ始める（開き途中でも逆算して閉じ直す）
  - まだ人がいればタイマーをリセットし、さらに `Close Delay` 秒後に再チェックします
  - そのため、最後の 1 人が出てから実際に閉じ始めるまで最大 `Close Delay` 秒かかります
- 判定にはプレイヤーの**足元位置**を使用（リモートプレイヤーの Head ボーンは視界外で位置が凍結することがあり、誤動作の原因になるため）
- 全クライアントが同じ条件で同じ判定をローカル実行するため、見え方は一致します（ネットワーク同期なし）

## 同梱ファイル

- `MashiroAutoDoor.cs` — ドア制御本体
- `AutoDoorTrigger.cs` — 判定コライダー側に付けるトリガー中継
- `自動ドア.prefab` — 構成例プレハブ
- `AutoDoor.playable` / `AutoDoorSample.playable` — 開閉アニメの Timeline サンプル

## セットアップ

1. ドアの開閉アニメを 1 本の Timeline にまとめます（**前半 = 開き、後半 = 閉じ**）
2. `MashiroAutoDoor` の `Timeline` に PlayableDirector、`Trigger Zone` に判定用 BoxCollider を割り当てます
3. 判定コライダー（IsTrigger）のオブジェクトに `AutoDoorTrigger` を付け、`Auto Door` フィールドに本体を割り当てます

| フィールド | 既定値 | 内容 |
|---|---|---|
| `Timeline` | – | 開閉アニメの PlayableDirector |
| `Trigger Zone` | – | ドア周囲の判定 BoxCollider |
| `Close Delay` | `3` 秒 | 最後の入室から在室チェックを行うまでの待機時間 |

> **`Trigger Zone` は回転させないでください**
> 在室チェックは Collider のワールド AABB（軸に沿った境界ボックス）で行うため、回転させた BoxCollider では実際の形状より広い範囲が「エリア内」と判定されます。判定範囲はワールド軸に沿った位置・サイズで調整してください。

## API リファレンス

### MashiroAutoDoor

| メソッド | 呼び出し種別 |
|---|---|
| `OnPlayerEntered(VRCPlayerApi)` / `OnPlayerExited(VRCPlayerApi)` | `AutoDoorTrigger` が呼ぶ内部連携用（手配線不要） |

### AutoDoorTrigger

| メソッド | 呼び出し種別 |
|---|---|
| `OnPlayerTriggerEnter(VRCPlayerApi)` / `OnPlayerTriggerExit(VRCPlayerApi)` | VRChat イベントのオーバーライド（配線不要）。本体へ中継するだけ |

## ライセンス

このフォルダの内容は MIT License で提供します（リポジトリルートの `LICENSE.md` を参照）。

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
