# Mashiro Small Theater — VPM Listing

VRChat ワールド用ギミックの配布リポジトリです。VCC (VRChat Creator Companion) から
インストールできます。

## VCC への追加

VCC の **Settings → Packages → Add Repository** に次の URL を追加してください。

```
https://meadowsage.github.io/mashirotheater-vpm/index.json
```

案内ページ: https://meadowsage.github.io/mashirotheater-vpm/
マニュアル: https://meadowsage.github.io/mashirotheater-vpm/docs/

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
置き場**で、中身はすべてソースリポジトリの CI が書き込みます。**直接編集しないでください**
（次の反映で上書きされます）。

| 場所 | 中身 |
| --- | --- |
| Release | 各バージョンの zip / unitypackage / VPM 用 json |
| `gh-pages` ブランチ | GitHub Pages として公開するサイト（`index.json`・`docs/`・案内ページ） |
| `main` ブランチ | この README とライセンス |

このリポジトリにワークフローはありません。`gh-pages` への push で GitHub Pages が更新されます。

### 必要な設定

- **Settings → Pages → Source: Deploy from a branch**（`gh-pages` / `/ (root)`）
- ソースリポジトリ側の Secrets に `DIST_REPO_TOKEN`（このリポジトリへの
  Contents: Read and write 権限を持つ fine-grained PAT）

リリース・マニュアル更新などの手順は、ソースリポジトリの `.packaging/README.md` を参照してください。
