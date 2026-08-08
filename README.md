# Mashiro Small Theater — VPM Listing

VRChat ワールド用ギミックの配布リポジトリです。VCC (VRChat Creator Companion) から
インストールできます。

## VCC への追加

VCC の **Settings → Packages → Add Repository** に次の URL を追加してください。

```
https://meadowsage.github.io/mashirotheater-vpm/index.json
```

案内ページ: https://meadowsage.github.io/mashirotheater-vpm/

## 収録パッケージ

| パッケージ | 内容 | 依存 |
| --- | --- | --- |
| `com.mashirotheater.common` | 共有シェーダ・マテリアル・フォント・アイコン | VRChat SDK |
| `com.mashirotheater.utils` | AutoDoor などの小規模ギミック詰め合わせ | 上記 + Common |

依存は VCC が自動で解決します。unitypackage 版も Release に添付しています。

## すでに unitypackage 版を使っている場合

VCC でインストールすると `Assets/MashiroSmallTheater/` 配下の同じフォルダは自動的に
削除されます（`legacyFolders`）。ファイルの GUID は変わらないため、シーンやプレハブからの
参照は維持されます。念のためインストール前にバックアップを取ってください。

## ライセンス

MIT License。同梱しているフォント（SIL OFL 1.1）とアイコン（Apache License 2.0）は
それぞれのライセンスに従います。詳細は [`LICENSE.md`](LICENSE.md) を参照してください。

---

## このリポジトリの仕組み（メンテナ向け）

ギミックのソースは別の非公開リポジトリで管理しています。このリポジトリは**配布物の
公開先**です。

1. ソースリポジトリでタグを push すると、CI が unitypackage と VPM パッケージをビルドする
2. CI が PAT を使って**このリポジトリに Release を作成**し、成果物を添付する
3. その Release イベントで `listing.yml` が動き、全 Release から `index.json` を
   組み立てて GitHub Pages へ公開する

Release を PAT で作るのが要点です。`GITHUB_TOKEN` による操作は他のワークフローを
起動しないため、リスティング更新が連鎖しません。

`index.json` はコミットしません。毎回すべての Release から組み立て直すため、
過去バージョンも常に載ります。

### このリポジトリのファイル

| ファイル | 用途 |
| --- | --- |
| `listing.json` | リスティングの名前・ID・URL |
| `scripts/make_listing.py` | Release から `index.json` を生成する |
| `.github/workflows/listing.yml` | Release を受けて Pages へ公開する |
| `index.html` | 案内ページ |

これらの元ファイルはソースリポジトリの `.packaging/dist-repo/` にあります。変更する
場合はそちらを直してから反映してください。

### 必要な設定

- **Settings → Pages → Source: GitHub Actions**
- ソースリポジトリ側の Secrets に `DIST_REPO_TOKEN`（このリポジトリへの
  Contents: Read and write 権限を持つ fine-grained PAT）
