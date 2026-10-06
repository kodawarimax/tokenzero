---
name: laya-ultrafast
description: Jev Ultrafastの実行規律（Token-Zero・2階層コード参照・最小差分・force_l0）を継承し、武藤理論の「3層カスケード（定義式 Tier 0 ➔ ローカル近傍AI LAYA Tier 1 ➔ 全域LLM Tier 2）」で判定・候補選別を行う進化型高速スキル。Claude Code、Codex、Antigravity全対応。
metadata:
  tags: "laya, ultrafast, token-zero, 3-tier-cascade, local-inference, zero-leak, claude, codex, antigravity"
  priority: "high"
---

# LAYA Ultrafast 実行規律 ＆ 3層カスケード判断スキル仕様書

本スキルは、**Jev Ultrafast 2.0 の完成された運用規律（Token-Zero・2階層スライシング・最小差分・安全ハンドシェイク）**を絶対軸として堅持しながら、判断・選別エンジンに**武藤理論に基づく「3層カスケード（固定式 ➔ ローカル近傍AI ➔ 全域LLM）」**を融合させた、完全オンデバイス・機密漏洩ゼロの超高速実行スキルです。

---

## 1. 3層カスケード判断アーキテクチャ（武藤理論の応用）

「定義式で決まる量は固定式が勝つ」という原則に従い、無駄なAI推論を排除して最速・安全に解決します。

```text
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    LAYA Ultrafast 3層カスケード判定フロー                       │
├───────────────────┬───────────────────────────────────┬─────────────────────────┤
│ レイヤー          │ 判定主体 ＆ 処理内容              │ 速度 ＆ コスト          │
├───────────────────┼───────────────────────────────────┼─────────────────────────┤
│ Tier 0: 固定式    │ 完全一致、正規表現、DB制約、ハッシュ│ 0.0ms / 0円             │
│ (定義式即決)      │ ※ルールで確定するものはAIを呼ばない │ 確信度 1.0 (100%確定)   │
├───────────────────┼───────────────────────────────────┼─────────────────────────┤
│ Tier 1: 局所近傍  │ ローカル LAYA (1.16B Multilingual) │ 30ms〜2s / 0円 (完全オフライン) │
│ (ローカルSystem 1)│ 多言語セマンティック、型付きChoice  │ 確信度 0.95以上で即決   │
├───────────────────┼───────────────────────────────────┼─────────────────────────┤
│ Tier 2: 全域AI    │ メインLLM (Claude / Codex / Gemini)│ 安全フォールバック      │
│ (System 2 推論)   │ 確信度0.95未満時、候補を削らず保持 │ 不可逆な情報欠落を防止 │
└───────────────────┴───────────────────────────────────┴─────────────────────────┘
```

---

## 2. 絶対遵守の4大実行規律（Jev Ultrafast 継承）

1. **意図適応型デュアルモード**:
   - `⚡ EXECUTOR (Token-Zero)`: 実装・修正・コマンド実行時は前置き・実況を全廃。
   - `💡 ADVISOR (Structured Insight)`: 設計・解説時は結論ファースト・構造化解説。
2. **2階層コード参照 (Two-Tier Inspection)**:
   - 全行読み込み禁止。`jev-index --outline` で大域骨格（約150tok）把握後、対象行前後15〜30行のみ外科手術スライス。
3. **最小差分 (Minimal Patch)**:
   - ファイル全置換（write_to_file）を避け、`replace_file_content` で対象関数・行のみ置換。
4. **アクション指向の安全ハンドシェイク**:
   - 破壊的操作・本番変更・外部送信時は即時停止し、10行以内の承認カードを提示。

---

## 3. CLI実行コマンド

全AI環境のPATHに `laya-cascade` が開通しています。

```bash
# 1. 3層カスケード判定（固定式 ➔ LAYA ➔ フォールバック）
laya-cascade "タスク内容" "候補0" "候補1" "候補2"

# 2. 大域アウトライン取得（マクロ把握）
jev-index /path/to/file.py --outline

# 3. 自律トリアージ
jev-index --triage
```

---

## 4. 環境構成とロールバック

* **Python環境**: `/Users/jungosakamoto/.codex/laya-venv/bin/python` (Python 3.12.12)
* **モデル本体**: `convaiinnovations/laya-multilingual` (SHA-256検証済みキャッシュ)
* **元に戻す方法**:
  ```bash
  rm -rf ~/.local/bin/laya-cascade
  rm -rf ~/.claude/skills/laya-ultrafast ~/.codex/skills/laya-ultrafast ~/.agents/skills/laya-ultrafast ~/Claude/.agent/skills/laya-ultrafast
  rm -rf ~/Claude/ai-ops/master_skills/dev/laya-ultrafast
  ```
