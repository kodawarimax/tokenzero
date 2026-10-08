---
name: tokenzero
description: 武藤理論（Formula-First）・Jake Van Clief理論（ICM）・Palantirオントロジー（OAG）を統合したゼロトークン決定論的カーネル。計算・日付・正規表現抽出・型付き制約検証を0ms・コスト0円・誤差0%で即決実行する。Claude Code, Codex, Antigravity完全対応。
---

# TokenZero Skill for Claude Code, OpenAI Codex, & Google Antigravity

## 概要
AIエージェントの過剰推論・ハルシネーション・トークン浪費を根絶する「決定論的エージェントカーネル」。
1. **Tier 0 (Formula-First)**: 算術計算、税込/割引、日付差分、正規表現抽出を 0.1〜1ms で即時解決（誤差0%・コスト0円）。
2. **オントロジー層 (OAG)**: 請求書割引上限（最大30%）やタスク状態遷移（飛び級禁止）のビジネス物理法則を強制。
3. **Tier 1 (System 1)**: ローカル近傍AI（LAYAまたは高速ヒューリスティック）による候補選択（30ms・外部送信0）。
4. **Tier 2 (LLM)**: カオス・高次推論が必要な場合のみ安全にエスカレーション。

## v2.1 最適化規律（効果最大化 ＆ 副作用ゼロ化）
1. **長文外部化 ＆ 3点エグゼクティブ・スニペット**: 1,000文字超はファイル保存。チャットには「①結論」「②核となるdiff/抜粋」「③ファイルリンク」のみ出力（再送爆発遮断 ＋ 認知的即断）。
2. **適応型デュアル・スコープ**: 差分率<30%はピンポイントスライス置換（デグレ根絶）。差分率>=30%や新規作成は1発置換＋即時コンパイル検証（ターン数浪費防止）。
3. **1行インサイト**: おしゃべりは全廃しつつ、ツール直前に `[Why: 〇〇]` の1行で意図を明示（安心感と説明責任）。
4. **ICM Dual-Track**: 日常タスクは `tokenzero scaffold --mode lite` (2ステージ)、基幹リリースは production (5ステージ)。

---

## 1. Claude Code での使用方法
Claude Code は Bash ツール経由で `tokenzero` を直接呼び出します：
```bash
# 決定論的計算・日付・抽出 (Tier 0)
tokenzero run "15000円の15%引き"
tokenzero run "2026-10-04から2026-12-31までの日数"
tokenzero run "((300 + 450) * 12) / 5"

# オントロジー制約検証 (OAG)
tokenzero ontology Invoice apply_discount --params '{"amount": 10000, "discount_rate": 0.20}'

# システム健全性チェック
tokenzero doctor
```

---

## 2. OpenAI Codex CLI での使用方法
Codex セッションまたはスクリプト内から直接実行：
```bash
# 抽出・計算
tokenzero run "お問い合わせ先は support@example.com です。メールを抽出して"

# 状態遷移ガバナンス
tokenzero ontology TaskState transition_state --params '{"task_id": "T-1", "current_status": "DRAFT", "next_status": "REVIEW"}'

# 累積トークン削減集計
tokenzero stats
```

---

## 3. Google Antigravity (Gemini) での使用方法
Antigravity の `run_command` ツールから呼び出し可能：
```bash
tokenzero run "25000円の税込"
tokenzero ontology Invoice apply_discount --params '{"amount": 50000, "discount_rate": 0.15}'
```

---

## 4. Python コード内での直接インポート
```python
import tokenzero

# 1. 決定論的タスク評価
result = tokenzero.process_task("100 * 5 + 20")
print(result["result"])  # 520

# 2. オントロジー制約検証
res = tokenzero.validate_action("Invoice", "apply_discount", {"amount": 10000, "discount_rate": 0.2})
print(res["discounted_amount"])  # 8000.0
```
