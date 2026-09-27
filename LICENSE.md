# License

## MIT License

Copyright (c) 2025 Mashiro Small Theater

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## 適用範囲

上記 MIT License は、配布パッケージ `MashiroTheater-Common` / `MashiroTheater-Utils`
（VPM: `com.mashirotheater.common` / `com.mashirotheater.utils`）に含まれるソースコード
(`.cs`)、シェーダ、および Mashiro Small Theater が作成したアセットに適用されます。

次のパッケージは **MIT License の対象外**です。各パッケージに同梱の
「ましろ小劇場 ツール・ギミック汎用利用規約」に従います
（正本: [`licenses/VN3License_ja.pdf`](licenses/VN3License_ja.pdf)、VN3 ライセンス様式）。成果物（ワールド等）への組み込み・改変・商用利用は可能ですが、
素材としての再配布・再販売はできません。

- `MashiroTheater-LightingControlSystem`
- `MashiroTheater-StageTimelineManager`

下記「第三者アセット」に挙げたものは、それぞれの提供元のライセンスに従います。
MIT License の対象外です。

## 第三者アセット

### Zen Kaku Gothic New

`_Common/Fonts/ZenKakuGothicNew-Regular.ttf` および同フォントから生成した
TextMeshPro のフォントアセット。

- Copyright 2022 The Zen Kaku Gothic Project Authors
  (https://github.com/googlefonts/zen-kakugothic)
- SIL Open Font License, Version 1.1
- ライセンス全文: [`licenses/OFL.txt`](licenses/OFL.txt)（パッケージ内では `_Common/Fonts/OFL.txt`）

OFL は、フォントを再配布する際にライセンス全文を同梱することを条件としています。
本リポジトリおよび配布用 unitypackage には `OFL.txt` を同梱しています。

### Material Symbols

`_Common/Icons/` および `_Common/Icons/StageTimeline/` の UI アイコン。

| ファイル | 元アイコン |
| --- | --- |
| `矢印アイコン.png` | `expand_circle_down` |
| `arrow_down.png` | `keyboard_arrow_down` |
| `arrow_up.png` | `keyboard_arrow_up` |
| `icon_cross.png` | `close` |
| `icon_key.png` | `lock` |
| `StageTimeline/icon_play.png` | `play_arrow` |
| `StageTimeline/icon_pause.png` | `pause` |
| `StageTimeline/icon_next.png` | `skip_next` |
| `StageTimeline/icon_back.png` | `skip_previous` |
| `StageTimeline/icon_user.png` | `person` |
| `情報アイコン.png` | `info` |
| `注意マークの線画アイコン.png` | `warning` |
| `無料の音符アイコン素材 その3.png` | `music_note` |
| `CustomStation/ソファーアイコン.png` ※ | `chair` |

- Copyright Google LLC
- Apache License, Version 2.0
- ライセンス全文: [`licenses/Apache-2.0.txt`](licenses/Apache-2.0.txt)（パッケージ内では `_Common/Icons/Apache-2.0.txt`）
- 出典: https://github.com/google/material-design-icons

※ ソファーアイコンのみ `CustomStation/` フォルダにあります。

いずれも Material Symbols の SVG を、元アイコンと同じ寸法の白い PNG として書き出したものです
（`_Common/Icons/` 直下は wght700、`StageTimeline/` は wght400）。
Apache License 2.0 は、再配布時にライセンス全文の同梱を条件としています。
本リポジトリおよび配布用 unitypackage には `Apache-2.0.txt` を同梱しています。
