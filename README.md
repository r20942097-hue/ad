# ブラウザー用フィルター

��告・追跡ブロックの補助フィルターと、日本語本文のフォント調整を管理します。広告・追跡一覧は、保守されている一般用途の基本リストと併用することを前提にしています。

## リポジトリ名と互換性の注意

現在の公開リポジトリは `r20942097-hue/ad` です。

過去の `s`、`faaff` といった名前は履歴上の互換ラベルです。現在の作業やガイドでは、その名称を現行のリポジトリ名として扱わず、必要な場合だけ「旧名・互換履歴」として記載します。生成物や購読の契約は現行の運用に沿い、既存の downstream 互換性を崩さないように維持しています。

## プロファイル一覧

| 用途 | ファイル | 対象・位置づけ |
|---|---|---|
| 広告ブロック | [ad.txt](ad.txt) | 基本一覧。uBOではad-ubo.txtも読み込み |
| uBO専用拡張 | [ad-ubo.txt](ad-ubo.txt) | ad.txtの補助。配置を変更しない |
| 追跡ブロック | [tracking.txt](tracking.txt) | 任意追加。サイト機能に影響する場合あり |
| 日本語本文のフォント調整 | [japanese-text-softener.txt](japanese-text-softener.txt) | uBlock Origin向け標準版 |
| より深いフォント調整 | [japanese-text-softener-deep.txt](japanese-text-softener-deep.txt) | 標準版を含む追加プロファイル |
| 外部Twitch拡張 | [twitch-custom-optional.txt](twitch-custom-optional.txt) | 追加リソースが必要。既定では無効 |
| 次世代フィルター | [v2/README.md](v2/README.md) | 候補版。実サイト検証後に評価 |

購読URLは `https://raw.githubusercontent.com/r20942097-hue/s/main/` に各ファイル名を付けたものです。これは既存の公開契約の維持を優先した互換設定です。リポジトリ名が `ad` に変わっていても、既存の購読者の破壊的変更を避けるため、購読URL自体は履歴上の中核契約を維持しています。

## 検証

Python 3.11以上で実行します。必須の外部Pythonライブラリはありません。

```sh
python -m unittest discover -s tests -v
python scripts/validate_lists.py
python scripts/generate_lists.py --check
```

標準検査はメタデータ、重複、include欠損・循環・範囲外参照、日本語表示ルールの回帰、生成一覧の同期を確認します。

`filter-profiles.json`を編集して`python scripts/generate_lists.py`で生成します。生成先のtxtを直接編集すると同期検査で失敗します。`ad-ubo.txt`と日本語フォント一覧は手動管理です。

生成前に、ヘッダー・ラベル・ルールの改行や制御文字、Versionの不一致、不正なホスト名を検査します。出力名・include名の各要素は255文字以下とし、出力名はWindowsでも使える相対パスに限定し、大文字小文字の衝突、予約デバイス名、ファイルとディレクトリの衝突を拒否します。検出した入力不備によって既存の生成物を部分更新しないよう、出力先を先に確認します。

任意の実エンジン検証にはNode.js 24と、初回のネットワーク接続が必要です。Python 3.12以上を推奨します。

```sh
python scripts/prepare_engine.py --directory ../work/filter-engine
node scripts/check_engine.mjs --engine-dir ../work/filter-engine
```

上流監査は固定した資料をハッシュ照合して参照箇所を抽出します。結果だけでルールを自動採用しません。

```sh
python scripts/audit_upstream.py --cache ../work/upstream-audit --fetch --report ../work/upstream-audit.json
```

変更内容は[更新記録](CHANGELOG.md)、検証に使うバージョンは[エンジン固定情報](verification/engine-lock.json)です。公開ページの通信確認や合成画面テストだけで、ログイン・フォーム・動画再生の互換性を保証しません。

## ライセンス

ルートのフィルターはCC0-1.0、v2フィルターはGPL-3.0-onlyと各ファイルに宣言されています。詳細はファイルのヘッダーを確認してください。

## 任意の第2エンジン

Ghosteryの直接・間接依存は`verification/ghostery/package-lock.json`に固定しています。依存更新時は`engine-lock.json`の版・整合性情報も実際に確認して更新してください。

```sh
npm ci --prefix verification/ghostery --ignore-scripts --no-audit --no-fund
node scripts/check_engine.mjs --engine-dir ../work/filter-engine --ghostery-entry verification/ghostery/node_modules/@ghostery/adblocker/dist/esm/index.js
```

npm依存は検証用で、フィルターの購読や標準Python検査には不要です。CIは固定した2エンジンで確認します。
