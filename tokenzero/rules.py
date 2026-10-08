# -*- coding: utf-8 -*-
"""
TokenZero Universal Rule Generator (v2.1 Ultra-Precision)
Generates discipline rules for Cursor, Windsurf, Cline, Claude Code, Codex, and Antigravity.
Optimized to mitigate side effects while maximizing core performance (token savings, 0% error, safety).
"""

from pathlib import Path
from typing import List, Dict

TOKENZERO_DISCIPLINE_MARKDOWN = """# TokenZero Engine Universal Agent Discipline (v2.1 Ultra-Precision)

このワークスペースでは **TokenZero 決定論的エージェント規律** が適用されています。
トークン消費の極小化、ハルシネーションの根絶、および安全・確実なコード開発のため、以下の運用規律を遵守してください。

---

## 1. 長文外部化 ＆ 3点エグゼクティブ・スニペット（再送爆発遮断 ＋ 認知的即断）
- **外部ファイル退避**: 1,000文字を超える詳細設計書、長文コード、調査ログはチャット本文にベタ書きせず、必ず外部ファイル（`docs/` や `artifacts/`）に保存すること。
- **3点インライン抜粋**: チャット本文には以下の3点のみを出力すること：
  1. 【結論】決定事項や修正結果の要点（2〜3行）
  2. 【核となる抜粋】重要な diff、主要メトリクス、またはインターフェース定義
  3. 【保存先リンク】成果物ファイルへの直接ファイルリンク
  これにより、**次ターンの入力トークン再送爆発を物理遮断しながら、人間がチャット画面だけで即断できる認知的快適性を両立**する。

## 2. 適応型デュアル・スコープ編集（デグレ根絶 ＋ ターン数浪費防止）
- **Surgical Slice Mode（局所修正 / 差分率 < 30%）**:
  - 対象行の前後 10〜30 行のみをピンポイント置換し、関係ない箇所のデグレ・誤削除を物理排除。
- **Macro Atomic Mode（大規模刷新 / 差分率 >= 30% または新規作成）**:
  - 構造改革や全面刷新時は、過度な小刻み編集を避け、1発でファイル全体を更新。
  - **必須要件**: 更新直後に必ず静的コンパイル検証（`py_compile`, `tsc --noEmit`, リンター等）を実行し、エラーがあれば即時自動修復すること。これにより、ターン数の無駄な引き伸ばしを防止しながら安全性100%を維持。

## 3. 1行インサイト（無駄な思考おしゃべり全廃 ＋ 説明責任の両立）
- 「承知しました」「これから〇〇を実行します」といったAIの冗長な定型句・思考実況は全廃する。
- 代わりに、ツール実行直前に **`[Why: 〇〇のエラー解消のため型ガードを追加]`** といった1行（わずか15トークン以内）の意図・理由のみを提示すること。
- トークン削減効果を99%維持しながら、人間が意図を一瞬で把握できる透明性を担保する。

## 4. 決定論的計算・オントロジー即決（誤差0%・ハルシネーション根絶）
- 算術計算、税込/割引、日付差分、正規表現抽出、およびビジネス制約検証は、LLM推論を遮断して `tokenzero` コマンドで0ms即決すること：
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
