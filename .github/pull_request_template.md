## 概要
- 目的（1〜2行）:
- 変更パス:
- 置換・関連PR:

## 実行した検証（PASS / FAIL / BLOCKED / NOT_RUN）
- [ ] `python -m unittest discover -s tests -p 'test_*.py'`
- [ ] `python scripts/validate_lists.py`
- [ ] `python scripts/generate_lists.py --check`
- [ ] 実エンジン `check_engine.mjs`（依存・フィルター変更時）
- [ ] CI 結果（`gh pr checks` で確認）
- [ ] 実ブラウザ確認（未実行なら UNVERIFIED と明記）

## 購読URL・公開への影響
- 既存ファイル名・パスの変更: なし / あり（要承認）
- フィルター本文の変更: なし / あり
- faaff 取り込み（`ai/imports/s.json`）の追従: 不要 / 別PRで提案
- ロールバック手順:

## 所有者の承認が必要な事項（なければ「なし」）
- 

merge・close・削除・Release・公開設定変更は所有者の承認後に行います（`ai/AUTONOMOUS_LOOP.md`）。
