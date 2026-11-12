# ブラウザー用フィルター

広告・追跡ブロック用の補助フィルターと、日本語本文のフォント調整ルールを管理します。広告・追跡一覧は、保守されている一般用途の基本リストと併用する補助リストです。

## リポジトリ名と購読URL

現在の公開リポジトリは [`r20942097-hue/ad`](https://github.com/r20942097-hue/ad) です。過去の `s` および `faaff` という名称は、移行・取り込み履歴や互換情報にのみ現れます。

購読URLは現在も `https://raw.githubusercontent.com/r20942097-hue/s/main/` を基点としています。これは既存の購読者に影響する互換契約として保持しています。リポジトリ名の整理だけを理由にURL、フィルター内の購読メタデータ、生成元、または契約テストを変更しないでください。URL移行が必要な場合は、既存利用者への影響と検証を含む別の移行計画が必要です。

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

## 検証

Python 3.11以上で実行します。必須の外部Pythonライブラリはありません。

```sh
python -m unittest discover -s tests -v
python scripts/validate_lists.py
python scripts/generate_lists.py --check
python scripts/check_subscription_contract.py --json
```

標準検査はメタデータ、重複、include欠損・循環・範囲外参照、日本語表示ルールの回帰、生成一覧の同期を確認します。購読契約の検査は固定パスとヘッダーの互換性のみを検証し、実際のフィルター動作やエンジン互換性を保証しません。

`filter-profiles.json`を編集して`python scripts/generate_lists.py`で生成します。生成先のtxtを直接編集すると同期検査で失敗します。`ad-ubo.txt`と日本語フォント一覧は手動管理です。

任意の実エンジン検証にはNode.js 24と初回のネットワーク接続が必要です。Python 3.12以上を推奨します。

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

Ghosteryの直接・間接依存は`verification/ghostery/package-lock.json`に固定しています。依存更新時は`engine-lock.json`の版・整合性情報も確認してください。

```sh
npm ci --prefix verification/ghostery --ignore-scripts --no-audit --no-fund
node scripts/check_engine.mjs --engine-dir ../work/filter-engine --ghostery-entry verification/ghostery/node_modules/@ghostery/adblocker/dist/esm/index.js
```

npm依存は検証用で、フィルターの購読や標準Python検査には不要です。CIは固定した2エンジンで確認します。
