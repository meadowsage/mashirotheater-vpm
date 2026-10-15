# Mashiro Theater Utils

`MashiroTheater-Utils` パッケージ（VPM: `com.mashirotheater.utils`）に収録するツールの一覧。`_Utils/` 配下のフォルダはすべてこのパッケージに入る。各ツールの仕様は各フォルダの `README.md` に記載する。

| ツール | 内容 |
|---|---|
| [AutoDoor](AutoDoor/) | 接近で開閉する自動ドア（Timeline 駆動・途中反転対応） |
| [ButtonLockSystem](ButtonLockSystem/) | UI ボタン群の一括ロック（誤操作防止） |
| [LightGroup](LightGroup/) | 照明の灯体をグループ化し、向き・サイズの調整と点灯テストをエディタで行う |
| [LocalAreaActivator](LocalAreaActivator/) | エリア内にいる間だけオブジェクトを有効化（ローカル） |
| [OnOffSwitches](OnOffSwitches/) | GameObject の ON/OFF スイッチ群（UI ボタン・長押し・持ち運び対応） |
| [PageViewer](PageViewer/) | ページ送り式画像ビューア（同期/ローカル切替・ズーム） |
| [PickupHoldSfx](PickupHoldSfx/) | Pickup の使用中・保持中に効果音を再生（全員同期） |
| [PickupHorizontalReset](PickupHorizontalReset/) | Pickup をドロップした瞬間に水平化 |
| [PickupResetButton](PickupResetButton/) | Pickup 群をボタン 1 つで初期位置へ一括リセット |
| [PickupSpaceFixer](PickupSpaceFixer/) | 小道具を持ったままダブルトリガーで空間固定 |
| [PlayerFollower](PlayerFollower/) | オブジェクトを指定プレイヤーの方向へ向ける（UI 選択式・全員同期 / 名前指定）、またはプレイヤー位置へ移動する |
| [SpeedChangeZone](SpeedChangeZone/) | エリア内で移動速度を倍率変更 |
| [SyncedTimelineToggle](SyncedTimelineToggle/) | Timeline 再生のトグル制御（全員同期・排他グループ対応） |

## 依存

- VRChat SDK（Worlds）`>=3.7.0`
- 共有素材（`_Common/` のフォント・アイコン・シェーダ等）は同じパッケージに同梱する。収録されるのは配布対象のツールから参照されているものと `keep` 指定のもの。

## ライセンス

MIT License（パッケージ同梱の `LICENSE.md`）。

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
