# Mashiro Auto Door

プレイヤーの入室で開き、エリア内が無人になると閉じる自動ドア。1 本の Timeline の前半を開きアニメ、後半を閉じアニメとして再生位置を制御し、開閉途中での反転に対応する。

## 構成

| ファイル | 役割 |
| --- | --- |
| `MashiroAutoDoor.cs` | ドア制御本体（Timeline の再生制御・在室チェック） |
| `MashiroAutoDoor.asset` | `MashiroAutoDoor` の UdonSharp ProgramAsset |
| `AutoDoorTrigger.cs` | トリガーコライダーの入退室イベントを `MashiroAutoDoor` へ中継する |
| `AutoDoorTrigger.asset` | `AutoDoorTrigger` の UdonSharp ProgramAsset |
| `自動ドア.prefab` | `MashiroAutoDoor`・`AutoDoorTrigger`・`PlayableDirector` を設定済みのドア一式 |
| `AutoDoor.playable` | 開閉アニメーションの TimelineAsset（全長 6 秒） |
| `AutoDoorSample.playable` | 開閉アニメーションの TimelineAsset（全長 4 秒） |

## 依存

- パッケージ: `MashiroTheater-Utils`（VPM `com.mashirotheater.utils`）
- `MashiroAutoDoor.timeline` に `PlayableDirector`（開閉アニメの TimelineAsset を割り当てたもの）が必要。
- `AutoDoorTrigger` と同じ GameObject に、Is Trigger の Collider が必要（`OnPlayerTriggerEnter` / `OnPlayerTriggerExit` を受けるため）。

## 仕様

### Timeline の区間

- `0` 〜 `duration / 2` を開きアニメ、`duration / 2` 〜 `duration` を閉じアニメとして扱う。
- `duration` は `Start` 時点の `PlayableDirector.duration` を使う。
- `Start` で再生位置を `duration` に設定して `Evaluate` → `Pause` し、全閉状態で開始する。
- 開き再生中に再生位置が `duration / 2` 以上になると、`duration / 2` に固定して `Pause` する（全開）。
- 閉じ再生中に再生位置が `duration` 以上になると、`duration` に固定して `Pause` する（全閉）。

### 開く条件

- `AutoDoorTrigger` の `OnPlayerTriggerEnter` が発火すると `MashiroAutoDoor.OnPlayerEntered` が呼ばれる。対象はローカル・リモートを問わず全プレイヤー。
- 入室のたびに最終入室時刻（`Time.time`）を更新する。
- ドアが全閉または閉じ途中のときのみ開き始める。
  - 全閉から: 再生位置 `0` から再生する。
  - 閉じ途中から: 閉じ区間の進捗 `p` を求め、再生位置 `(duration / 2) × (1 − p)` から開き再生する。
- 退室（`OnPlayerTriggerExit` → `OnPlayerExited`）では何もしない。

### 閉じる条件

- ドアが全開または開き途中の間、`Update` で最終入室時刻からの経過時間を確認する。
- 経過時間が `closeDelay` 秒以上になった時点で在室チェックを行う。
  - 在室者がいる: 最終入室時刻を現在時刻にリセットする（`closeDelay` 秒後に再チェック）。
  - 在室者がいない: 閉じ始める。
- 閉じ始めの再生位置:
  - 全開から: `duration / 2` から再生する。
  - 開き途中から: 開き区間の進捗 `p` を求め、再生位置 `duration / 2 + (duration / 2) × (1 − p)` から閉じ再生する。

### 在室チェック

- `triggerZone.bounds`（ワールド座標の AABB）に、各プレイヤーの `VRCPlayerApi.GetPosition()`（足元位置）が含まれるかで判定する。
- `triggerZone` を回転させても、判定は回転後のコライダーを包むワールド軸平行の箱で行われる。
- `triggerZone` が未設定のときは常に「在室者なし」と判定する。
- 入室の検出（`AutoDoorTrigger` のコライダー）と在室チェック（`triggerZone`）は別々のコライダーを参照する。

### 同期

- 両コンポーネントとも `[UdonSynced]` フィールドを持たず、`[UdonBehaviourSyncMode]` も指定していない。
- 開閉判定・Timeline 制御は各クライアントでローカルに実行する。

### エラー時の挙動

| 条件 | 挙動 |
| --- | --- |
| `timeline` 未設定 | `Start` で Warning `[MashiroAutoDoor] Timeline is not assigned.` を出し、コンポーネントを無効化する |
| `triggerZone` 未設定 | `Start` で Warning `[MashiroAutoDoor] BoxCollider is not assigned.` を出す。動作は継続する |
| `autoDoor` 未設定（`AutoDoorTrigger`） | 入退室イベントを中継しない |

## Inspector

### MashiroAutoDoor

| フィールド | 型 | 既定値 | 必須 | 内容 |
| --- | --- | --- | --- | --- |
| `timeline` | `PlayableDirector` | なし | ○ | 開閉アニメの TimelineAsset を再生する PlayableDirector |
| `triggerZone` | `BoxCollider` | なし | — | 在室チェックに使うコライダー |
| `closeDelay` | `float` | `3` | — | 最終入室から在室チェックを行うまでの秒数 |

### AutoDoorTrigger

| フィールド | 型 | 既定値 | 必須 | 内容 |
| --- | --- | --- | --- | --- |
| `autoDoor` | `MashiroAutoDoor` | なし | ○ | 入退室イベントの中継先 |

## API リファレンス

### MashiroAutoDoor

#### UI へ手配線するもの

なし。

#### 内部連携用（配線不要）

| シグネチャ | 用途 | 呼び出し種別 |
| --- | --- | --- |
| `void OnPlayerEntered(VRCPlayerApi player)` | 最終入室時刻を更新し、閉状態・閉じ途中なら開き始める | `AutoDoorTrigger` が呼ぶ |
| `void OnPlayerExited(VRCPlayerApi player)` | 処理なし | `AutoDoorTrigger` が呼ぶ |

### AutoDoorTrigger

#### UI へ手配線するもの

なし。

#### 内部連携用（配線不要）

| シグネチャ | 用途 | 呼び出し種別 |
| --- | --- | --- |
| `void OnPlayerTriggerEnter(VRCPlayerApi player)` | `autoDoor.OnPlayerEntered` を呼ぶ | VRChat コールバック（内部専用） |
| `void OnPlayerTriggerExit(VRCPlayerApi player)` | `autoDoor.OnPlayerExited` を呼ぶ | VRChat コールバック（内部専用） |

## ライセンス

MIT License（`MashiroTheater-Utils` 同梱の `LICENSE.md` を参照）。

---

本ドキュメントは AI を用いて作成しています。不明点・記載の誤りなどありましたら、下記までお問い合わせください。

- メール: contact@mashirotheater.com
- X: https://x.com/hakushiza
- Discord: https://discord.com/invite/yU2Es38sVX
