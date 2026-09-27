# MashiroPickupHorizontalReset

`MashiroPickupHorizontalReset` は、Pickup オブジェクトを **ドロップした瞬間に水平化**（傾きを取り除く）する単独コンポーネントです。`MashiroPageViewer` の `OnHorizontalResetButtonPressed` と同じ「水平リセット」機能を、Pickup 1 つに付けるだけで使えるよう切り出したものです。

## 主な機能

- 付与した GameObject 自身の **X/Z 軸の回転を 0** にし、**Y 軸（向き）は維持**する
- VRC_Pickup の `OnDrop` をフックし、オブジェクトを離した瞬間に自動で水平化する
- 既定では **ドロップしたプレイヤーがデスクトップモードのとき** のみ発火する（VR プレイヤーが落としたときは何もしない）
- 外部の Udon や UI ボタンからも `ResetHorizontal` イベントで手動発火できる

## ユースケース

- デスクトップユーザーが台本やパンフレットなどの Pickup を雑に置いても、自動で水平に整う
- VR ユーザーは自分の手の角度どおりに置けるよう、既定ではデスクトップ時のみに限定

## 配置手順

1. 水平化したい **VRC_Pickup が付いた GameObject** に `MashiroPickupHorizontalReset`（UdonSharp）を追加する
   - `OnDrop` を受け取るため、また付与した GameObject 自身を水平化するため、VRC_Pickup と**同じ GameObject** に付ける必要があります
2. VR プレイヤーがドロップしたときも水平化したい場合は `Desktop Mode Only` のチェックを外す

## インスペクタ項目

| パラメータ | 既定値 | 説明 |
|---|---|---|
| Desktop Mode Only | true | true のとき、ドロップしたプレイヤーがデスクトップモードの場合のみ自動発火する |

## API リファレンス

### MashiroPickupHorizontalReset

別の Udon や UI ボタンから手動で水平化したい場合は、以下を `SendCustomEvent` で呼び出せます。

| メソッド | 動作 | 呼び出し種別 |
|---|---|---|
| `OnDrop` | ドロップ時の自動水平化 | VRChat イベント（配線不要） |
| `ResetHorizontal` | この GameObject を即座に水平化する（`Desktop Mode Only` の判定は経由しない） | 他の Udon・UI から `SendCustomEvent` で呼ぶ |

## 同期設計

- 同期変数を持たない（Udon 変数の同期は行わない）
- 水平化は `OnDrop` を受け取ったクライアント（= そのとき Pickup のオーナー）でのみ実行する
- 他プレイヤーから見た回転は VRChat 標準の VRC_Pickup の Transform 同期に任せる

## 制約

- VRC_Pickup と同じ GameObject に付けないと `OnDrop` が呼ばれず自動発火しない
- 水平化対象は付与した GameObject 自身に固定（子オブジェクトや別 Transform は対象にできない）
- ワールド回転の X/Z を 0 にするため、親が傾いている場合でも結果はワールド水平になる

## 同梱ファイル

- `MashiroPickupHorizontalReset.cs` メインスクリプト
- `README.md` 本マニュアル

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
