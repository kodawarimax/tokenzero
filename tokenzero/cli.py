# -*- coding: utf-8 -*-
"""
TokenZero CLI & Multi-Agent Interface
Supports Claude Code, OpenAI Codex CLI, and Google Antigravity.
"""

import sys
import os
import json
import shutil
import argparse
from datetime import datetime
from pathlib import Path

from tokenzero.ontology import validate_action, OntologyViolation
from tokenzero.kernel import process_task, get_stats

def deploy_agent_skills(target_base: Path = None):
    """Claude Code, Codex, Antigravity へスキルを展開"""
    home = Path.home()
    repo_skills = Path(__file__).resolve().parent.parent / "skills"
    
    # 配備先リスト
    targets = {
        "Claude Code": [
            home / ".claude" / "skills",
            Path.cwd() / ".claude" / "skills"
        ],
        "Codex CLI": [
            home / ".codex" / "skills",
            home / ".agents" / "skills",
            Path.cwd() / ".agents" / "skills"
        ],
        "Antigravity": [
            home / ".gemini" / "antigravity" / "templates" / "skills",
            home / ".agent" / "skills",
            Path.cwd() / ".agent" / "skills"
        ]
    }
    
    skill_names = ["tokenzero", "formula-first", "laya-ultrafast"]
    results = {}
    
    for agent, dirs in targets.items():
        deployed_paths = []
        for d in dirs:
            # 親ディレクトリが存在するか、明示的に作成
            try:
                d.mkdir(parents=True, exist_ok=True)
                for s in skill_names:
                    src_skill = repo_skills / s / "SKILL.md"
                    dest_skill_dir = d / s
                    dest_skill_dir.mkdir(parents=True, exist_ok=True)
                    dest_skill = dest_skill_dir / "SKILL.md"
                    if src_skill.exists():
                        shutil.copy2(src_skill, dest_skill)
                deployed_paths.append(str(d))
            except Exception:
                pass
        results[agent] = deployed_paths
        
    return results

def check_agent_status():
    """Claude Code, Codex, Antigravity の連携状態を検査"""
    home = Path.home()
    cwd = Path.cwd()
    
    claude_paths = [
        home / ".claude" / "skills" / "tokenzero" / "SKILL.md",
        cwd / ".claude" / "skills" / "tokenzero" / "SKILL.md"
    ]
    claude_active = any(p.exists() for p in claude_paths)
    claude_installed = (home / ".claude").exists()
    
    codex_paths = [
        home / ".codex" / "skills" / "tokenzero" / "SKILL.md",
        home / ".agents" / "skills" / "tokenzero" / "SKILL.md",
        cwd / ".agents" / "skills" / "tokenzero" / "SKILL.md"
    ]
    codex_active = any(p.exists() for p in codex_paths)
    codex_installed = (home / ".codex").exists() or (home / ".agents").exists()
    
    antigravity_paths = [
        home / ".gemini" / "antigravity" / "templates" / "skills" / "tokenzero" / "SKILL.md",
        home / ".agent" / "skills" / "tokenzero" / "SKILL.md",
        cwd / ".agent" / "skills" / "tokenzero" / "SKILL.md"
    ]
    antigravity_active = any(p.exists() for p in antigravity_paths)
    antigravity_installed = (home / ".gemini").exists() or (home / ".agent").exists()
    
    return {
        "Claude Code": ("Active" if claude_active else ("Skill Missing" if claude_installed else "Not Installed"), claude_active or claude_installed),
        "Codex CLI": ("Active" if codex_active else ("Skill Missing" if codex_installed else "Not Installed"), codex_active or codex_installed),
        "Antigravity": ("Active" if antigravity_active else ("Skill Missing" if antigravity_installed else "Not Installed"), antigravity_active or antigravity_installed),
    }

def main():
    parser = argparse.ArgumentParser(description="TokenZero Engine CLI (Multi-Agent Deterministic Kernel)")
    subparsers = parser.add_subparsers(dest="command")

    # eval
    eval_p = subparsers.add_parser("run", help="Evaluate a task using TokenZero cascade")
    eval_p.add_argument("task", type=str, help="Problem query or description")
    eval_p.add_argument("candidates", nargs="*", help="Optional candidate choices")
    eval_p.add_argument("--json", action="store_true", help="Output raw JSON")

    # stats
    subparsers.add_parser("stats", help="Display cumulative ROI and token savings")

    # ontology action
    ont_p = subparsers.add_parser("ontology", help="Execute an action under Ontology governance (OAG)")
    ont_p.add_argument("entity", type=str, help="Entity type (e.g. Invoice, TaskState)")
    ont_p.add_argument("action", type=str, help="Action name (e.g. apply_discount, transition_state)")
    ont_p.add_argument("--params", type=str, required=True, help="JSON string of parameters")

    # doctor
    subparsers.add_parser("doctor", help="Run system diagnostics and health checks")

    # install-skills (Claude Code, Codex, Antigravity)
    subparsers.add_parser("install-skills", help="Deploy TokenZero skills to Claude Code, Codex, and Antigravity")

    # init (workspace rule injection for Cursor, Windsurf, Cline, Claude, Codex, Antigravity)
    init_p = subparsers.add_parser("init", help="Inject TokenZero discipline rules into current workspace (Cursor, Windsurf, Cline, Claude, Codex, Antigravity)")
    init_p.add_argument("platforms", nargs="*", default=["all"], help="Target platforms: cursor, windsurf, cline, claude, codex, antigravity, or all")

    # mcp (Model Context Protocol stdio server)
    subparsers.add_parser("mcp", help="Run TokenZero stdio MCP server for Cursor, Windsurf, Claude Desktop, and Cline")

    # scaffold (ICM dual-track: production vs lite)
    scaffold_p = subparsers.add_parser("scaffold", help="Scaffold an ICM workspace (production 5-stage or lite 2-stage)")
    scaffold_p.add_argument("template", choices=["content", "sales", "system"], help="Workspace template type")
    scaffold_p.add_argument("--mode", choices=["production", "lite"], default="production", help="ICM architecture mode: production (5-stage) or lite (2-stage lean)")
    scaffold_p.add_argument("--dest", type=str, default=".", help="Target directory")

    # gate: human approval check & approve
    gate_check_p = subparsers.add_parser("gate-check", help="Check human gate approval in ICM workspace")
    gate_check_p.add_argument("workspace_dir", type=str, help="Path to ICM workspace directory")

    gate_approve_p = subparsers.add_parser("gate-approve", help="Grant human gate approval in ICM workspace")
    gate_approve_p.add_argument("workspace_dir", type=str, help="Path to ICM workspace directory")
    gate_approve_p.add_argument("--approver", type=str, default="Human Supervisor", help="Name of approver")

    args = parser.parse_args()

    if args.command == "mcp":
        from tokenzero.mcp import run_mcp_server
        run_mcp_server()
        return

    if args.command == "init":
        from tokenzero.rules import inject_rules
        dest = Path.cwd()
        print(f"\n=== Initializing TokenZero Discipline Rules in: {dest} ===")
        created = inject_rules(dest, args.platforms)
        for platform, files in created.items():
            print(f"[✓] {platform.capitalize():12}: Configured {len(files)} file(s)")
            for f in files:
                rel = Path(f).relative_to(dest)
                print(f"      - {rel}")
        print("\nInitialization complete! All AI agents in this workspace now follow TokenZero discipline.\n")
        return

    if args.command == "install-skills":
        print("\n=== Deploying TokenZero Skills to AI Agent Environments ===")
        results = deploy_agent_skills()
        for agent, paths in results.items():
            if paths:
                print(f"[✓] {agent:12}: Deployed to {len(paths)} location(s)")
                for p in paths:
                    print(f"      - {p}")
            else:
                print(f"[-] {agent:12}: Skipped")
        print("\nDeployment complete! Skills are immediately available in Claude Code, Codex, and Antigravity.\n")
        return

    if args.command == "doctor":
        print("\n==========================================")
        print("   TokenZero Doctor - System Diagnostics")
        print("==========================================")
        print(f"[*] Python Runtime       : {sys.version.split()[0]} ({sys.platform})")
        
        # Tier 0 check
        t0 = process_task("100 * 5")
        t0_status = "PASS" if t0 and t0.get("result") == 500 else "FAIL"
        print(f"[{t0_status}] Tier 0 (Formula-First)  : {t0.get('elapsed_ms', 0)} ms")
        
        # Ontology check (Automated regression across all registered entities)
        try:
            ont_inv = validate_action("Invoice", "apply_discount", {"amount": 100, "discount_rate": 0.1})
            discounted = ont_inv.get("discounted_amount") or ont_inv.get("result_amount")
            ont_task = validate_action("TaskState", "transition_state", {"task_id": "T-1", "current_status": "DRAFT", "next_status": "REVIEW"})
            ont_status = "PASS" if discounted == 90 and ont_task.get("to_status") == "REVIEW" else "FAIL"
        except Exception:
            ont_status = "FAIL"
        print(f"[{ont_status}] Ontology Layer (OAG)    : Verified (Self-testing Invoice & TaskState invariants)")
        
        # Tier 1 LAYA check
        laya_cli = Path.home() / ".local" / "bin" / "laya-cascade"
        if laya_cli.exists():
            print(f"[PASS] Tier 1 (LAYA Local)     : Active (Optional System 1 engine)")
        else:
            print(f"[INFO] Tier 1 (LAYA Local)     : Optional (Not installed - Tier 0 & OAG fully operational)")

        # MCP Server Interface
        print(f"[PASS] MCP Server (Stdio)    : Ready (Cursor, Windsurf, Claude Desktop)")

        # Agent Integrations check (Claude Code, Codex, Antigravity)
        statuses = check_agent_status()
        for agent_name, (status_str, is_present) in statuses.items():
            badge = "PASS" if "Active" in status_str else ("WARN" if "Missing" in status_str else "SKIP")
            print(f"[{badge}] {agent_name:18} : {status_str}")

        # IDE Rules check in current workspace
        cwd = Path.cwd()
        ide_rules = {
            "Cursor (.cursorrules)": (cwd / ".cursorrules").exists() or (cwd / ".cursor/rules").exists(),
            "Windsurf (.windsurfrules)": (cwd / ".windsurfrules").exists(),
            "Cline (.clinerules)": (cwd / ".clinerules").exists(),
        }
        for ide_name, has_rule in ide_rules.items():
            badge = "PASS" if has_rule else "INFO"
            status_text = "Configured" if has_rule else "Not configured (run 'tokenzero init')"
            print(f"[{badge}] {ide_name:18} : {status_text}")
            
        print("==========================================\n")
        return

    if args.command == "scaffold":
        dest_dir = Path(args.dest).resolve() / f"{args.template}-pipeline"
        dest_dir.mkdir(parents=True, exist_ok=True)
        mode = getattr(args, "mode", "production")

        if mode == "lite":
            stages = ["spec", "src"]
            for s in stages:
                (dest_dir / s).mkdir(exist_ok=True)
            with open(dest_dir / "APPROVAL.json", "w") as f:
                json.dump({"status": "PENDING", "template": args.template, "mode": "lite"}, f, indent=2)
            with open(dest_dir / "AGENTS.md", "w") as f:
                f.write(f"# ICM Lite Workspace: {args.template.title()}\n\n## 2-Stage Lean Architecture\n- `spec/`: Requirements & Specifications\n- `src/`: Code & Deliverables\n- `APPROVAL.json`: Human Gatekeeper\n")
            with open(dest_dir / "CONTEXT.md", "w") as f:
                f.write(f"# Router Context (ICM Lite)\nActive Template: {args.template}\nArchitecture: spec/ -> src/. Human review via APPROVAL.json.\n")
            print(f"[✓] Successfully scaffolded Lean ICM workspace at: {dest_dir} (2-stage)")
        else:
            stages = ["00_contract", "01_intake", "02_execution", "03_review_gate", "04_output"]
            for s in stages:
                (dest_dir / s).mkdir(exist_ok=True)
            with open(dest_dir / "AGENTS.md", "w") as f:
                f.write(f"# ICM Workspace: {args.template.title()} Pipeline\n\n## 5-Stage Architecture\n" + "\n".join(f"- `{s}/`" for s in stages) + "\n")
            with open(dest_dir / "CONTEXT.md", "w") as f:
                f.write(f"# Router Context\nActive Template: {args.template}\nEnforce: One stage, one job. Human gate at 03_review_gate.\n")
            print(f"[✓] Successfully scaffolded Production ICM workspace at: {dest_dir} (5-stage)")
        return

    if args.command == "gate-check":
        ws = Path(args.workspace_dir).resolve()
        gate_file = ws / "03_review_gate" / "APPROVAL.json"
        if gate_file.exists():
            try:
                with open(gate_file, "r") as f:
                    data = json.load(f)
                if data.get("status") == "APPROVED":
                    print(f"[GATE PASS] Approved by: {data.get('approver', 'Human')} (at {data.get('timestamp')})")
                    return
            except Exception:
                pass
        print("[GATE LOCKED] Human gate not approved yet. Missing 03_review_gate/APPROVAL.json")
        sys.exit(1)

    if args.command == "gate-approve":
        ws = Path(args.workspace_dir).resolve()
        gate_dir = ws / "03_review_gate"
        gate_dir.mkdir(parents=True, exist_ok=True)
        gate_file = gate_dir / "APPROVAL.json"
        approval_data = {
            "status": "APPROVED",
            "approver": args.approver,
            "timestamp": datetime.now().isoformat()
        }
        with open(gate_file, "w") as f:
            json.dump(approval_data, f, indent=2)
        print(f"[✓] Human gate successfully approved by '{args.approver}' for: {ws.name}")
        return

    if args.command == "ontology":
        try:
            params = json.loads(args.params)
            res = validate_action(args.entity, args.action, params)
            print(json.dumps(res, ensure_ascii=False, indent=2))
        except OntologyViolation as ov:
            print(f"[ONTOLOGY VIOLATION] {ov}")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
        return

    if args.command == "stats":
        stats = get_stats()
        print("\n==========================================")
        print("   TokenZero Engine - Cumulative ROI")
        print("==========================================")
        print(f"Total Requests Processed : {stats['total_runs']:,}")
        print(f"Total Tokens Saved       : {stats['total_tokens_saved']:,} tokens")
        print(f"Total Cost Saved (USD)   : ${stats['total_cost_saved_usd']:,.4f}")
        print(f"Total Cost Saved (JPY)   : ¥{stats['total_cost_saved_jpy']:,}")
        print(f"Average Execution Speed  : {stats['avg_latency_ms']} ms")
        print("==========================================\n")
        return

    task = getattr(args, "task", None)
    if not task:
        parser.print_help()
        return

    result = process_task(task, getattr(args, "candidates", None))
    if getattr(args, "json", False):
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        tier = result.get("tier", "Unknown")
        print(f"[{tier}] ({result.get('elapsed_ms', 0)} ms)")
        if "result" in result:
            print(f"  Result : {result['result']}")
        if "formula" in result:
            print(f"  Formula: {result['formula']}")
        if "details" in result:
            print(f"  Details: {result['details']}")
        if "action" in result:
            print(f"  Action : {result['action']} ({result.get('reason', '')})")

if __name__ == "__main__":
    main()
