# MashiroLocalAreaActivator

指定したエリア内にローカルプレイヤーが居る間だけ、対象 GameObject を有効化するスイッチです。
**ローカル動作専用**（同期なし）で、プレイヤーごとに独立して内外判定が行われます。

## 特徴

- **OnPlayerTriggerEnter / Exit に依存しない**: ポーリング方式で内外を直接判定するため、テレポート・リスポーン・物理ジャンプ・コライダーレイヤー設定ミスなどによる「入退場イベントの取りこぼし」が原理的に起きません。
- **Collider を再利用**: エリア定義に既存の `Collider` をそのまま流用できます。回転・スケールに追従します。
- **複数ターゲット**: 1 つのエリアで複数 GameObject を同時に ON/OFF できます。
- **軽量**: 状態が変化した瞬間のみ `SetActive` を呼びます（毎フレーム呼び続けない）。判定間隔も調整可。

## 使い方

1. 任意の GameObject に `MashiroLocalAreaActivator` を追加。
2. インスペクタで以下を設定：
   - **Area**: エリア判定に使う `Collider`（Is Trigger 推奨）
   - **Targets**: エリア内で有効化したい GameObject の配列
   - **Invert**: チェックするとエリア「外」で有効になります
   - **Poll Interval**: 判定間隔（秒）。デフォルト `0.1`（10Hz）

## パラメータ詳細

| 項目 | 説明 | 推奨値 |
| --- | --- | --- |
| Area | エリア定義に使う Collider。Box / Sphere / Capsule / Convex MeshCollider に対応 | BoxCollider (Is Trigger) |
| Targets | 有効化対象の GameObject 配列。null 要素は無視 | 任意 |
| Invert | true でエリア外時に有効化 | false |
| Poll Interval | 判定間隔(秒)。0 以下で毎フレーム判定 | 0.1（体感差ほぼ無し） |

## 動作仕様

- **判定基準点**: `Networking.LocalPlayer.GetPosition()`（プレイヤーの足元）
- **内外判定**: `Collider.ClosestPoint(playerPos)` と入力点との距離で判定（距離 0 ≒ 内部）
- **初期状態**: `Start` 時点で即時判定し、エリア内ならスタート時から有効化済みになります
- **位相分散**: 同フレームで複数インスタンスが揃って評価されないよう、初回判定のみランダムにずらします

## 制限・注意事項

- **Non-Convex な MeshCollider は使用不可**: Unity の `Collider.ClosestPoint` 仕様により、`Convex` チェック無しの MeshCollider では正しく判定できません。Box / Sphere / Capsule / Convex Mesh を使ってください。
- **Area が未設定（null）／Collider コンポーネントを無効化（`enabled = false`）したとき**: 「エリア外」として扱い、ターゲットは（Invert オフなら）OFF になります。ただし **Collider が乗っている GameObject 自体を非アクティブにした場合はこの扱いになりません**。エリアを一時的に無効化したいときは Collider コンポーネント側の `enabled` を切ってください。
- **同じ対象を他のスイッチでも制御する場合**: `MashiroGlobalOnOffSwitch` などと同じ GameObject を Targets に入れると、ローカル側で強制的に `SetActive` するため整合性が崩れます。**他のスイッチと対象を共有しない**運用にしてください。
- **エリアコライダーは `Is Trigger` 推奨**: `ClosestPoint` 自体は Trigger でなくても動きますが、物理衝突を発生させないため Trigger を強く推奨します。
- **ローカル限定**: 状態は同期されません。全員に同じ状態を見せたい用途には `MashiroGlobalOnOffSwitch` 等を使ってください。

## パフォーマンス

- デフォルト 10Hz ポーリングで `ClosestPoint` 1 回 + 距離比較のみ。多数並べても軽量です。
- 反応速度を最優先したい場合のみ `Poll Interval = 0` で毎フレーム判定にしてください。
- ステージ全域に大量に並べる場合は、`Poll Interval` を 0.2〜0.5 程度に伸ばすとさらに軽量化できます。

## API リファレンス

### MashiroLocalAreaActivator

public 関数はありません。**配線は不要**で、Inspector の設定だけで動作します。

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
