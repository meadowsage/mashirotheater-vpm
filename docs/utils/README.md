# Mashiro Theater Utils

ましろ小劇場のワールド用小規模ギミック集です。このフォルダのツールは `MashiroTheater-Utils` パッケージとして配布されます。各ツールの詳細は、それぞれのフォルダの `README.md` を参照してください。

| ツール | 内容 |
|---|---|
| [AudioZoneController](AudioZoneController/) | エリア単位でボイスの聞こえ方を制御（防音・拡声ゾーン） |
| [AutoDoor](AutoDoor/) | 接近で開閉する自動ドア（Timeline 駆動・途中反転対応） |
| [ButtonLockSystem](ButtonLockSystem/) | UI ボタン群の一括ロック（誤操作防止） |
| [ChairHeightAdjuster](ChairHeightAdjuster/) | VRCStation の椅子高さを段階調整 |
| [CustomStation](CustomStation/) | 観客席向けカスタムステーション（メニュー・字幕連携・降車ゲージ） |
| [LocalAreaActivator](LocalAreaActivator/) | エリア内にいる間だけオブジェクトを有効化（ローカル） |
| [OnOffSwitches](OnOffSwitches/) | GameObject の ON/OFF スイッチ群 |
| [PageViewer](PageViewer/) | ページ送り式画像ビューア（同期/ローカル切替・ズーム） |
| [PickupHoldSfx](PickupHoldSfx/) | Pickup の使用中・保持中に効果音を再生（全員同期） |
| [PickupHorizontalReset](PickupHorizontalReset/) | Pickup をドロップした瞬間に水平化 |
| [PickupResetButton](PickupResetButton/) | Pickup 群をボタン 1 つで初期位置へ一括リセット |
| [PickupSpaceFixer](PickupSpaceFixer/) | 小道具を持ったままダブルトリガーで空間固定 |
| [PlayerFollower](PlayerFollower/) | オブジェクトをプレイヤーに追従（UI 選択式 / 名前指定） |
| [SpeedChangeZone](SpeedChangeZone/) | エリア内で移動速度を倍率変更 |
| [StationAutoSeatByDisplayName](StationAutoSeatByDisplayName/) | DisplayName 一致のプレイヤーを自動着席 |
| [StationAutoSeatOnActive](StationAutoSeatOnActive/) | 起動時にエリア内のプレイヤーを自動着席 |
| [SyncedTimelineToggle](SyncedTimelineToggle/) | Timeline 再生のトグル制御（全員同期・排他グループ対応） |
| [VoiceMuteZone](VoiceMuteZone/) | ゾーン内プレイヤーの声をミュート |

## 依存

各ツールは共有素材パッケージ `MashiroTheater-Common`（フォント・アイコン等）を参照します。VCC 経由なら自動で解決されます。unitypackage の場合は Common → Utils の順にインポートしてください。

## ライセンス

MIT License（リポジトリルートの `LICENSE.md` を参照）。

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
