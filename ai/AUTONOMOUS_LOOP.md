# 自律開発ループ（AIエージェント向け・1枚で完結）

目的: 所有者の介入を「承認が必要な操作」だけに絞り、AI が調査→実装→検証→PR→自己確認まで自走すること。
権限の正本は [`../AGENTS.md`](../AGENTS.md)（`s` は購読URLの配布元。ファイル名・パスを変更しない）。本書はその実行手順で、権限を広げるものではありません。

## 0. 起動（毎回 1〜2 分）
1. `git fetch --all --prune` し、`origin/main` の SHA を確認（Drive・台帳・`projects.json` の SHA は観測値。Git が正）。
2. `python ../faaff/ai/repo_health.py`（faaff の読み取り専用スクリプト。両リポジトリを一覧化） でオープンPR・CI失敗・NO_GO・PRなしブランチを把握（読み取り専用）。
3. `ai/PROJECT_STATE.json` と `ai/HANDOFF.md` で前回の続きと blocker を確認。
4. ボックス環境なら `/workspace/repos/bootstrap.sh` を 1 回実行（冪等。clone/fetch・ツール確認・全テスト）。

## 1. タスク選択（優先順）
1. 所有者の最新指示
2. CI 失敗中のPR（自分で直せるもの: 新ブランチで修正PR）
3. 既存PR同士の重複・置換関係の整理（クローズは提案のみ）
4. `ai/PROJECT_STATE.json` の `open_items`
5. 小さな品質改善（テスト追加・ドキュメントの陳腐化修正）

同じ目的の PR が既にあれば新規に作らず、その PR の改善コミット（別ブランチ）か置換PRにします。PR数は増やしすぎない。

## 2. 実装
- ブランチ名: `proposal/<短い説明>-<YYYYMMDD>`（`main` 直 push は禁止）。
- 変更は最小・目的単位。関連する小変更は 1 PR に束ねる。
- 公開購読URL・生成物・ライセンスヘッダー・原本ファイルは変更しない（`AGENTS.md` 参照）。

## 3. 検証（PR 前に必ずローカルで）
```sh
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/validate_lists.py
python scripts/generate_lists.py --check
# 実エンジン（依存・エンジン・フィルター変更時。Node 24 推奨、20 でも動作確認済み）
python scripts/prepare_engine.py --directory ../work/filter-engine
npm ci --prefix verification/ghostery --ignore-scripts --no-audit --no-fund
node scripts/check_engine.mjs --engine-dir ../work/filter-engine --ghostery-entry verification/ghostery/node_modules/@ghostery/adblocker/dist/esm/index.js
```
- 依存更新時は `verification/ghostery/package*.json` と `verification/engine-lock.json` の `secondary_engine` を必ず同時に更新（片方だけだと `engine` ジョブが FAIL）。
- 本リポジトリを変更・merge したら、faaff の `ai/imports/s.json` と `ai/projects.json` の追従を別PRで提案。
結果は PASS / FAIL / BLOCKED / NOT_RUN / NEEDS_HUMAN / PARTIAL で記録。実行していない検査を PASS と書かない。

## 4. PR と自己確認
- PR 本文は `.github/pull_request_template.md` に従う（実行コマンドと結果、影響、ロールバック、要承認事項）。
- push 後 `gh pr checks <番号> --watch` で CI を確認。失敗したら原因を読み、同じブランチに修正コミット（force-push しない）。
- 同じ失敗を 2 回以上繰り返したら止めて、原因・試したこと・代替案を PR に記録し、次のタスクへ。

## 5. 引き継ぎ
- 完了時に `ai/HANDOFF.md` / `PROJECT_STATE.json` を更新（別PRでも可）。秘密情報は書かない。
- 所有者への報告は日本語・簡潔に。承認が必要な事項は「1行1件・推奨案つき」の決定リストにまとめる。

## AI が承認なしで行ってよいこと
読み取り全般／作業ブランチ作成と push／Draft・通常PRの作成と本文更新／自分のPRへの修正コミット／CI 再実行／ローカル検証／ドキュメント・テスト・CI チェックの提案。

## 所有者の明示承認が必要なこと（AI は提案のみ）
| 操作 | 理由 |
|---|---|
| PR の merge（`main` への反映） | 本番の正本が変わる |
| PR のクローズ、ブランチ削除 | 作業の喪失 |
| force-push・履歴書き換え | 復元困難 |
| 公開範囲（visibility）・Ruleset・リポジトリ設定の変更 | 安全境界 |
| Release 作成・購読URL変更・公開物の変更（PUBLICATION_HOLD）、`main` の購読ファイル内容の変更の merge | 利用者に影響 |
| 本番デプロイ、Vercel プロジェクト削除 | 公開影響 |
| ZIP・バイナリの追加、認証情報の利用・保存 | 漏えい・汚染 |
| Google Drive 既存ファイルの上書き・移動・削除 | 原本保全（新規作成のみ可） |
