## 概要
- 目的（1〜2行）:
- 変更パス:
- 置換・関連PR:

## 実行した検証（対象に適用する項目のみ。未実行は NOT_RUN）
- [ ] `python -m unittest discover -s tests -p 'test_*.py'`
- [ ] `python scripts/validate_lists.py`
- [ ] `python scripts/generate_lists.py --check`
- [ ] 実エンジン `check_engine.mjs`（依存・フィルター変更時）
- [ ] CI 結果（`gh pr checks` で確認）
- [ ] 実ブラウザ確認（未実行なら UNVERIFIED と明記）

## 購読URL・公開への影響
- 既存ファイル名・パスの変更: なし / あり（現在の利用者への影響・互換性・必要な移行策を記載。変更可否は当該依頼と検証結果に基づき判断）
- フィルター本文の変更: なし / あり
- faaff 取り込み（`ai/imports/s.json`）の追従: 不要 / 別PRで提案
- ロールバック手順:

## Owner-only items (force-push/history rewrite, repo deletion, prod deploy, making public, spending) — usually「なし」
- 

マージ可否は当該依頼の権限範囲、現在のブランチ保護・必要なCI・レビュー条件で判断します。CI 全緑や revert 可能というだけで自動マージを包括許可しません（`ai/AUTONOMOUS_LOOP.md`）。
