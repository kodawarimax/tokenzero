# -*- coding: utf-8 -*-
"""
TokenZero Universal Rule Generator
Generates discipline rules for Cursor, Windsurf, Cline, Claude Code, Codex, and Antigravity.
"""

from pathlib import Path
from typing import List, Dict

TOKENZERO_DISCIPLINE_MARKDOWN = """# TokenZero Engine Universal Agent Discipline

このワークスペースでは **TokenZero 決定論的エージェント規律** が適用されています。
トークン消費の極小化、ハルシネーションの根絶、および安全なファイル編集のため、以下の4大規律を厳守してください。

---

## 1. 長文外部化規律（Context Bloat Prevention）
- 1,000文字を超える調査レポート、詳細仕様書、長文コード、設計書は**チャット本文にベタ書きせず、必ず外部ファイル（`docs/` や `artifacts/`）として保存**すること。
- チャット本文には「要約・重要判断点・保存先リンク」のみを出力し、**次ターン以降の入力コンテキスト再送爆発（雪だるま現象）を物理的に遮断**すること。

## 2. 最小外科手術スライシング規律（Surgical Slice Patch）
- ファイル全体の全置換（フルリライト）を原則禁止する。
- 編集対象箇所の前後 10〜30 行のみをピンポイントで置換（差分パッチ）すること。
- 編集後は直ちに型チェックや構文チェック（`py_compile`, `tsc --noEmit` 等）を実行し、破損がないことを即時検証すること。

## 3. 前置き・思考実況の全廃（Token-Zero EXECUTOR）
- 実装・バグ修正・テスト・コマンド実行時は、「承知しました」「これから〇〇を修正します」といった前置き・思考実況を全廃すること。
- 直ちにツールを呼び出すか、最小の diff / 1行結果のみを出力すること。

## 4. 決定論的計算・オントロジー即決規律（Formula-First & OAG）
- 算術計算、税込/税抜、割引率、日付差分、正規表現抽出、および業務制約検証は、LLMで推論（ハルシネーション）せず、`tokenzero` コマンドで0ms即決すること：
  ```bash
  # 計算・日付・正規表現 (Tier 0 即決)
  tokenzero run "15000円の15%引き"
  tokenzero run "2026-10-04から2026-12-31までの日数"
  
  # 業務制約・状態遷移検証 (Palantir OAG)
  tokenzero ontology Invoice apply_discount --params '{"amount": 10000, "discount_rate": 0.20}'
  tokenzero ontology TaskState transition_state --params '{"task_id": "T-1", "current_status": "DRAFT", "next_status": "REVIEW"}'
  ```
"""

PLATFORM_TARGETS = {
    "cursor": [
        ".cursorrules",
        ".cursor/rules/tokenzero.mdc"
    ],
    "windsurf": [
        ".windsurfrules"
    ],
    "cline": [
        ".clinerules"
    ],
    "claude": [
        "CLAUDE.md",
        ".claude/skills/tokenzero/SKILL.md"
    ],
    "codex": [
        "AGENTS.md",
        ".agents/skills/tokenzero/SKILL.md"
    ],
    "antigravity": [
        ".agent/skills/tokenzero/SKILL.md"
    ]
}

def inject_rules(target_dir: Path, platforms: List[str] = None) -> Dict[str, List[str]]:
    """指定されたプラットフォーム向けにルールファイルを生成"""
    if not platforms or "all" in platforms:
        selected_platforms = list(PLATFORM_TARGETS.keys())
    else:
        selected_platforms = [p.lower() for p in platforms if p.lower() in PLATFORM_TARGETS]
        
    created_files = {}
    
    # スキル原本のパス
    repo_skills = Path(__file__).resolve().parent.parent / "skills"
    tokenzero_skill_src = repo_skills / "tokenzero" / "SKILL.md"

    for platform in selected_platforms:
        created_files[platform] = []
        files = PLATFORM_TARGETS.get(platform, [])
        for rel_path in files:
            dest_file = target_dir / rel_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            
            # SKILL.md の場合は原本からコピー、それ以外は DISCIPLINE_MARKDOWN を書き込み
            if dest_file.name == "SKILL.md" and tokenzero_skill_src.exists():
                import shutil
                shutil.copy2(tokenzero_skill_src, dest_file)
            else:
                # 既存ファイルが存在する場合の追記配慮
                if dest_file.exists():
                    existing_text = dest_file.read_text(encoding="utf-8")
                    if "TokenZero" not in existing_text:
                        with open(dest_file, "a", encoding="utf-8") as f:
                            f.write("\n\n" + TOKENZERO_DISCIPLINE_MARKDOWN)
                else:
                    dest_file.write_text(TOKENZERO_DISCIPLINE_MARKDOWN, encoding="utf-8")
                    
            created_files[platform].append(str(dest_file))
            
    return created_files
