---
name: tokenzero
description: 武藤理論（Formula-First）・Jake Van Clief理論（ICM）・Palantirオントロジー（OAG）を統合したゼロトークン決定論的カーネル。計算・日付・正規表現抽出・型付き制約検証を0ms・コスト0円・誤差0%で即決実行する。
---

# TokenZero Skill for Codex & Claude & Antigravity

## 概要
AIの過剰推論・ハルシネーション・トークン浪費を根絶する「決定論的エージェントカーネル」。
1. **Tier 0 (Formula-First)**: 算術計算、税込/割引、日付差分、正規表現抽出を 0.1〜1ms で即時解決（誤差0%・コスト0円）。
2. **オントロジー層 (OAG)**: 請求書割引上限やタスク状態遷移（飛び級禁止）のビジネス物理法則を強制。
3. **Tier 1 (LAYA)**: ローカル近傍AIによる型付き候補選択（30ms）。
4. **Tier 2 (LLM)**: カオス・意味理解が必要な場合のみ安全にエスカレーション。

## Codexでの使用方法
```bash
# 1. 決定論的計算・日付・抽出 (Tier 0)
tokenzero run "15000円の15%引き"
tokenzero run "2026-10-04の45日後"
tokenzero run "((300 + 450) * 12) / 5"

# 2. オントロジー・ガバナンス実行 (OAG)
# 正常系 (20%引き)
tokenzero ontology Invoice apply_discount --params '{"amount": 10000, "discount_rate": 0.20, "client_name": "Acme"}'
# 異常系 (上限30%を超える50%引きは遮断される)
tokenzero ontology Invoice apply_discount --params '{"amount": 10000, "discount_rate": 0.50, "client_name": "Acme"}'

# 3. 状態遷移の飛び級遮断
tokenzero ontology TaskState transition_state --params '{"task_id": "T-1", "current_status": "DRAFT", "next_status": "REVIEW"}'

# 4. 削減ROIカウンターの確認
tokenzero stats
```
