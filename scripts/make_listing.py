#!/usr/bin/env python3
"""このリポジトリの Release から VPM リスティング (index.json) を組み立てる。

各 Release には、VPM パッケージの zip と一緒に同名の .json が添付されている。
その .json は url と zipSHA256 を含む package.json そのものなので、集めるだけで
リスティングになる。過去バージョンの zip をダウンロードして再ハッシュする必要がない。

使い方（GITHUB_TOKEN があるとレート制限に余裕ができる）:
    python3 scripts/make_listing.py --repo owner/name --output _site/index.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

REQUIRED_FIELDS = ("name", "version", "url", "zipSHA256")


def log(message: str) -> None:
    print(message, file=sys.stderr)


def api(url: str, token: str | None, raw: bool = False):
    request = urllib.request.Request(url)
    request.add_header(
        "Accept", "application/octet-stream" if raw else "application/vnd.github+json"
    )
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request) as response:
        data = response.read()
    return data if raw else json.loads(data)


def collect_versions(repo: str, token: str | None) -> dict[str, dict]:
    packages: dict[str, dict] = {}
    page = 1
    while True:
        releases = api(
            f"https://api.github.com/repos/{repo}/releases?per_page=100&page={page}", token
        )
        if not releases:
            break
        for release in releases:
            if release.get("draft"):
                continue
            for asset in release.get("assets", []):
                if not asset["name"].endswith(".json"):
                    continue
                try:
                    manifest = json.loads(api(asset["url"], token, raw=True))
                except (urllib.error.HTTPError, json.JSONDecodeError) as error:
                    log(f"  スキップ: {asset['name']} ({error})")
                    continue
                # VPM パッケージの manifest かどうかは中身で判定する
                if not all(field in manifest for field in REQUIRED_FIELDS):
                    continue
                entry = packages.setdefault(manifest["name"], {"versions": {}})
                entry["versions"][manifest["version"]] = manifest
                log(f"  {manifest['name']} {manifest['version']}")
        page += 1
    return packages


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="owner/name")
    parser.add_argument("--config", default="listing.json")
    parser.add_argument("--output", default="_site/index.json")
    args = parser.parse_args()

    config = json.loads(Path(args.config).read_text(encoding="utf-8"))

    log(f"リリースを走査中: {args.repo}")
    try:
        packages = collect_versions(args.repo, os.environ.get("GITHUB_TOKEN"))
    except urllib.error.HTTPError as error:
        raise SystemExit(f"GitHub API にアクセスできません ({error.code})") from error

    listing = {
        "name": config["name"],
        "id": config["id"],
        "url": config["url"],
        "author": config["author"],
        "packages": packages,
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(listing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    total = sum(len(p["versions"]) for p in packages.values())
    log(f"{args.output}: {len(packages)} パッケージ / {total} バージョン")
    if not packages:
        log("警告: バージョンが 1 つもありません。まだ Release が無い可能性があります。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
