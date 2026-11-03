# AGENTS.md — `s`（ブラウザー用フィルター配布リポジトリ）

AIコーディングエージェント（Codex / Claude / Cursor / Copilot / Grok Bot など）共通の作業指示です。
`CLAUDE.md`・`.cursor/rules/`・`.github/copilot-instructions.md` はこのファイルを参照するだけの入口です。内容はここに一本化してください。

> **Start here: [`ai/AUTONOMOUS_LOOP.md`](ai/AUTONOMOUS_LOOP.md)** (agent loop). **Governance: "Operating policy v3 (2026-11-04)" below — it supersedes all older gate rules.**

## このリポジトリの役割
- 広告・追跡ブロック補助フィルターと、日本語本文フォント調整フィルターの配布元です。
- 購読URLは `https://raw.githubusercontent.com/r20942097-hue/s/main/<ファイル名>` です。購読中のため、**既存ファイルのパス・ファイル名を変更・削除・移動しないでください**（`v2/` 配下を含む）。
- 統合・開発ハブは [`r20942097-hue/faaff`](https://github.com/r20942097-hue/faaff) です。`faaff/integrations/browser-filters/source/s/` に本リポジトリの**固定コミットの写し**があり、`faaff/ai/imports/s.json` でGit blobハッシュ照合されています。本リポジトリを変更したら、faaff 側で `python ai/reimport_s.py --s-repo ../s` を実行し、取り込み更新PRを作って merge します（自動同期はありません）。

## 正本と生成物
- 広告・追跡ネットワークルールの正本は **`filter-profiles.json`** です。
- 生成先のtxt（`ad.txt`、`tracking.txt`、`v2/ad.txt`、`v2/tracking.txt`、`v2/strict.txt`）は**直接編集しない**でください。`filter-profiles.json` には faaff 側 `browser_filter_lists/filters/universal-web-*.txt` 向けの出力定義もありますが、それらは本リポジトリでは生成・配布しません。`python scripts/generate_lists.py` で再生成します。手編集すると `--check` が失敗します。
- 手動管理ファイル: `ad-ubo.txt`、`japanese-text-softener.txt`、`japanese-text-softener-deep.txt`、`twitch-custom-optional.txt`。
- ライセンスは各ファイルのヘッダーで宣言されています（ルートのフィルター: CC0-1.0、`v2/`: GPL-3.0-only）。ヘッダーを削除・変更しないでください。

## 検証コマンド（Python 3.11以上、外部ライブラリ不要）
```sh
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/validate_lists.py
python scripts/generate_lists.py --check
```
任意の実エンジン検証（Node.js 24、初回はネットワーク必要。作業ディレクトリはリポジトリ外）:
```sh
python scripts/prepare_engine.py --directory ../work/filter-engine
npm ci --prefix verification/ghostery --ignore-scripts --no-audit --no-fund
node scripts/check_engine.mjs --engine-dir ../work/filter-engine --ghostery-entry verification/ghostery/node_modules/@ghostery/adblocker/dist/esm/index.js
```
CI: `.github/workflows/japanese-text-softener.yml`（Filter list checks）。サードパーティActionはフルSHAで固定します。

## Operating policy v3 (2026-11-04) — supersedes all earlier gates

**Precedence: the newest dated policy wins.** This section supersedes the P0 / PUBLICATION_HOLD / NO_NEW_INTERNAL_PUSH gates and every "two-tier / owner approval" rule dated 2026-10-28 … 2026-11-03 (in this repo's history, `ai/HANDOFF.md`, `ai/PROJECT_STATE.json`, and Google Drive v27 / v28 / v29 / 00_START_HERE v1–v2). Older text is historical context only; where it conflicts with this section, ignore it and do not ask the owner about it. Drive copy: `00_AI運用ルール_v3_2026-11-04`.

These are the owner's personal projects. Nothing needs to be published.

### AI agents may do without asking
- Read anything in the repos, CI, and the shared Drive docs.
- Create branches, push commits, open/update PRs (never push directly to `main`; `main` changes go through a PR).
- **Merge their own PRs** (squash) when every check is green, the branch is mergeable, and the change is reversible by a revert. Use `gh pr merge --squash --match-head-commit <sha>` or `/workspace/repos/tools/safe_merge.sh <repo> <pr>`.
- Close superseded or obsolete PRs with a one-line reason; retarget stacked PRs.
- Delete branches that are merged, or that were backed up first (git bundle under `/workspace/repos/backups/`).
- Fix failing CI, update dependencies, CI, docs, templates and tooling.

### Still requires the owner
- Force-push or history rewrite on `main` (force-push anywhere is discouraged).
- Deleting a repository.
- Production deploys (Vercel production, store submissions).
- Making anything public: changing a repo to public, Releases, GitHub Pages, new public hosting.
- Spending money; creating or widening credentials.

### Always
- Never print, commit, or log tokens, cookies, personal data, recordings, or ZIP/binary artifacts.
- Personal browser add-ons (YouTube / RPLAY / tab organizer in `/workspace/addons_dev/`) stay local: never push them. No RPLAY recording/download features, no DRM circumvention.
- Report status as PASS / FAIL / BLOCKED / NOT_RUN / NEEDS_HUMAN / PARTIAL; never mark unexecuted checks as PASS.
- Docs written for agents may be in English; reports to the owner are in Japanese.

### `s`-specific
- `s` stays **public** on purpose: ad-blockers fetch the subscription URLs `https://raw.githubusercontent.com/r20942097-hue/s/main/<file>` anonymously, so a private repo would break the owner's own filter subscriptions. Merging to `main` updates the live lists, which counts as normal, reversible work under this policy.
- Only filter lists and their tooling belong here. Never add personal add-ons, StreamHarbor/RPLAY code, secrets, or archives.
- Keep existing subscription file names/paths stable; keep license headers.

## 詳細な共通ルール・プロジェクト台帳
- 現在の状態（機械可読）: [`ai/PROJECT_STATE.json`](ai/PROJECT_STATE.json)、次のAIへの引き継ぎ: [`ai/HANDOFF.md`](ai/HANDOFF.md)
- AI作業環境 統合マスター入口（Google Drive、要アクセス権）: https://docs.google.com/document/d/1ajeph-Kynrpmza3cn06SdKrCYkW-FF3x1ZgRaTzbrkE/edit
- 報告時は、変更パス・実行コマンドと結果・未検証項目・購読URLへの影響・ブランチ/コミットを明記してください。
