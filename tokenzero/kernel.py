# -*- coding: utf-8 -*-
"""
TokenZero Engine Kernel
Takefuji Formula-First & 3-Tier Deterministic Cascade
"""

import sys
import os
import re
import ast
import json
import math
import time
import sqlite3
from datetime import datetime, date, timedelta
from pathlib import Path

DB_PATH = Path.home() / ".tokenzero" / "metrics.db"

def init_metrics_db():
    """ROI・トークン削減カウンター用 SQLite の初期化"""
    try:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    tier TEXT,
                    task_snippet TEXT,
                    elapsed_ms REAL,
                    tokens_saved INTEGER,
                    cost_saved_usd REAL,
                    status TEXT
                )
            """)
            conn.commit()
    except Exception:
        pass

def record_metrics(tier: str, task: str, elapsed_ms: float, tokens_saved: int, cost_saved_usd: float, status: str = "SUCCESS"):
    """実行結果と削減値をDBに累積記録"""
    try:
        init_metrics_db()
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                INSERT INTO executions (timestamp, tier, task_snippet, elapsed_ms, tokens_saved, cost_saved_usd, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (datetime.now().isoformat(), tier, task[:100], elapsed_ms, tokens_saved, cost_saved_usd, status))
            conn.commit()
    except Exception:
        pass

def get_stats():
    """ROI削減統計の集計"""
    if not DB_PATH.exists():
        return {
            "total_runs": 0,
            "total_tokens_saved": 0,
            "total_cost_saved_usd": 0.0,
            "total_cost_saved_jpy": 0,
            "avg_latency_ms": 0.0
        }
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*), SUM(tokens_saved), SUM(cost_saved_usd), AVG(elapsed_ms) FROM executions")
            row = cursor.fetchone()
            count = row[0] or 0
            tokens = row[1] or 0
            usd = row[2] or 0.0
            avg_ms = row[3] or 0.0
            return {
                "total_runs": count,
                "total_tokens_saved": tokens,
                "total_cost_saved_usd": round(usd, 4),
                "total_cost_saved_jpy": int(usd * 150),
                "avg_latency_ms": round(avg_ms, 2)
            }
    except Exception:
        return {
            "total_runs": 0,
            "total_tokens_saved": 0,
            "total_cost_saved_usd": 0.0,
            "total_cost_saved_jpy": 0,
            "avg_latency_ms": 0.0
        }

# --- Tier 0: 決定論的コード合成・計算エンジン ---

def normalize_text(text: str) -> str:
    """全角英数・記号の標準化および漢字単位（万、億）の数値展開"""
    import unicodedata
    norm = unicodedata.normalize('NFKC', text).strip()
    
    # 億の変換 (例: "1.5億" -> "150000000", "2億" -> "200000000")
    def repl_oku(m):
        val = float(m.group(1))
        return str(int(val * 100000000))
    norm = re.sub(r'(\d+(?:\.\d+)?)\s*億', repl_oku, norm)
    
    # 万の変換 (例: "1000万" -> "10000000", "30万" -> "300000", "1.5万" -> "15000")
    def repl_man(m):
        val = float(m.group(1))
        return str(int(val * 10000))
    norm = re.sub(r'(\d+(?:\.\d+)?)\s*万', repl_man, norm)
    
    return norm

def evaluate_arithmetic(text: str):
    """四則演算・パーセンテージ・税率の固定式評価"""
    norm = normalize_text(text).replace(",", "")
    
    # 日本語特有の表現: 半額 (例: "5000円の半額")
    half_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:円|ドル)?\s*の\s*半額', norm)
    if half_match:
        base = float(half_match.group(1))
        res = base * 0.5
        return {
            "type": "DISCOUNT_FORMULA",
            "formula": f"{base} * 0.5",
            "result": int(res) if res.is_integer() else round(res, 4)
        }

    # 日本語特有の表現: N割引 (例: "5000円の2割引", "3000の3割引き")
    wari_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:円|ドル)?\s*の\s*(\d+(?:\.\d+)?)\s*割(?:引|引き)?', norm)
    if wari_match:
        base, wari = float(wari_match.group(1)), float(wari_match.group(2))
        res = base * (1.0 - wari / 10.0)
        return {
            "type": "DISCOUNT_FORMULA",
            "formula": f"{base} * (1 - {wari} / 10)",
            "result": int(res) if res.is_integer() else round(res, 4)
        }

    # 割引・オフ計算 (例: "5000円の20%引き", "12000の15%オフ")
    disc = re.search(r'(\d+(?:\.\d+)?)\s*(?:円|ドル)?\s*の\s*(\d+(?:\.\d+)?)\s*%\s*(?:引き|オフ|割引)', norm)
    if disc:
        base, pct = float(disc.group(1)), float(disc.group(2))
        res = base * (1.0 - pct / 100.0)
        return {
            "type": "DISCOUNT_FORMULA",
            "formula": f"{base} * (1 - {pct} / 100)",
            "result": int(res) if res.is_integer() else round(res, 4)
        }

    # 消費税・加算 (例: "3000円の税込", "5000の消費税10%")
    tax = re.search(r'(\d+(?:\.\d+)?)\s*(?:円)?\s*の\s*(?:税込|消費税(\d+(?:\.\d+)?)%)', norm)
    if tax:
        base = float(tax.group(1))
        rate = float(tax.group(2)) if tax.group(2) else 10.0
        res = math.floor(base * (1.0 + rate / 100.0))
        return {
            "type": "TAX_FORMULA",
            "formula": f"floor({base} * (1 + {rate} / 100))",
            "result": res
        }

    # 純粋な算術式 (例: "(120 + 45) * 8 / 2")
    expr = norm.replace("^", "**")
    if re.match(r'^[\d\s\+\-\*\/\%\(\)\.]+$', expr):
        try:
            tree = ast.parse(expr, mode='eval')
            # ASTノードの安全検証 (危険な呼び出しを遮断)
            for node in ast.walk(tree):
                if isinstance(node, (ast.Call, ast.Import, ast.ImportFrom, ast.Attribute)):
                    return None
            res = eval(compile(tree, '<string>', 'eval'), {"__builtins__": {}}, {})
            return {
                "type": "EXACT_MATH",
                "formula": expr,
                "result": int(res) if isinstance(res, float) and res.is_integer() else (round(res, 4) if isinstance(res, float) else res)
            }
        except Exception:
            pass

    # --- ビジネスKPI / マーケティング決定論的計算 ---
    # 1. ROAS (広告費用対効果: 売上 ÷ 広告費 * 100)
    roas_m = re.search(r'(?:売上|広告売上|回収)\s*(\d+(?:\.\d+)?)\s*(?:円|万|ドル)?\s*、?\s*(?:広告費|コスト|費用|突っ込んで)\s*(\d+(?:\.\d+)?)\s*(?:円|万|ドル)?\s*(?:の\s*ROAS|の\s*費用対効果|の\s*投資対効果)', norm, re.IGNORECASE)
    if not roas_m:
        roas_m = re.search(r'(?:広告費|コスト|費用|広告に)\s*(\d+(?:\.\d+)?)\s*(?:円|万|ドル)?\s*(?:使って|かけて|突っ込んで)\s*(?:売上|回収)\s*(\d+(?:\.\d+)?)\s*(?:円|万|ドル)?\s*(?:の\s*ROAS|の\s*費用対効果|の\s*効果)', norm, re.IGNORECASE)
    if roas_m:
        rev_or_cost1, rev_or_cost2 = float(roas_m.group(1)), float(roas_m.group(2))
        cost, rev = (rev_or_cost1, rev_or_cost2) if "使って" in norm or "かけて" in norm or "広告に" in norm else (rev_or_cost2, rev_or_cost1)
        if cost > 0:
            roas = (rev / cost) * 100.0
            return {
                "type": "BUSINESS_KPI_ROAS",
                "formula": f"({rev} / {cost}) * 100",
                "result": f"{round(roas, 2)}%",
                "details": f"売上({rev}) ÷ 広告費({cost}) × 100 = {round(roas, 2)}%"
            }

    # 2. CTR (クリック率: クリック数 ÷ インプレッション * 100)
    ctr_m = re.search(r'(?:インプ|表示回数|imp)\s*(\d+)\s*(?:回)?\s*、?\s*(?:クリック|click)\s*(\d+)\s*(?:回)?\s*の\s*CTR', norm, re.IGNORECASE)
    if not ctr_m:
        ctr_m = re.search(r'(\d+)\s*(?:回)?\s*(?:表示|インプ|imp)\s*(?:されて|で)\s*(\d+)\s*(?:回)?\s*(?:クリック|click)\s*(?:された|の)\s*(?:CTR|クリック率)', norm, re.IGNORECASE)
    if ctr_m:
        imp, click = float(ctr_m.group(1)), float(ctr_m.group(2))
        if imp > 0:
            ctr = (click / imp) * 100.0
            return {
                "type": "BUSINESS_KPI_CTR",
                "formula": f"({click} / {imp}) * 100",
                "result": f"{round(ctr, 2)}%",
                "details": f"クリック({click}) ÷ インプレッション({imp}) × 100 = {round(ctr, 2)}%"
            }

    # 3. 利益率 (粗利率: (売上 - 原価) ÷ 売上 * 100)
    margin_m = re.search(r'(?:売価|売上|定価|販売価格)\s*(\d+(?:\.\d+)?)\s*(?:円)?\s*、?\s*(?:原価|仕入|仕入れ)\s*(\d+(?:\.\d+)?)\s*(?:円)?\s*の\s*(?:利益率|粗利率)', norm)
    if not margin_m:
        margin_m = re.search(r'(?:仕入|原価|仕入れ)\s*(\d+(?:\.\d+)?)\s*(?:円)?\s*(?:のものを|で)\s*(\d+(?:\.\d+)?)\s*(?:円)?\s*(?:で売った|で販売した)\s*(?:時の利益率|の粗利率|の利益率)', norm)
        if margin_m:
            cost, price = float(margin_m.group(1)), float(margin_m.group(2))
            if price > 0:
                margin = ((price - cost) / price) * 100.0
                return {
                    "type": "BUSINESS_KPI_MARGIN",
                    "formula": f"(({price} - {cost}) / {price}) * 100",
                    "result": f"{round(margin, 2)}%",
                    "details": f"(売上({price}) - 原価({cost})) ÷ 売上({price}) × 100 = {round(margin, 2)}%"
                }
    if margin_m:
        price, cost = float(margin_m.group(1)), float(margin_m.group(2))
        if price > 0:
            margin = ((price - cost) / price) * 100.0
            return {
                "type": "BUSINESS_KPI_MARGIN",
                "formula": f"(({price} - {cost}) / {price}) * 100",
                "result": f"{round(margin, 2)}%",
                "details": f"(売上({price}) - 原価({cost})) ÷ 売上({price}) × 100 = {round(margin, 2)}%"
            }

    # --- 教育・学習シーン決定論的計算 ---
    # 1. 幾何学: 円の面積 (半径 r)
    circle_area_m = re.search(r'半径\s*(\d+(?:\.\d+)?)\s*(?:cm|m)?\s*の円の(?:面積|広さ)', norm)
    if circle_area_m:
        r = float(circle_area_m.group(1))
        area = math.pi * (r ** 2)
        return {
            "type": "EDUCATION_GEOMETRY_CIRCLE",
            "formula": f"pi * ({r} ** 2)",
            "result": round(area, 4),
            "details": f"円周率(π) × 半径({r})² = {round(area, 4)}"
        }

    # 2. 幾何学: 球の体積 (半径 r)
    sphere_vol_m = re.search(r'半径\s*(\d+(?:\.\d+)?)\s*(?:cm|m)?\s*の球の体積', norm)
    if sphere_vol_m:
        r = float(sphere_vol_m.group(1))
        vol = (4.0 / 3.0) * math.pi * (r ** 3)
        return {
            "type": "EDUCATION_GEOMETRY_SPHERE",
            "formula": f"(4/3) * pi * ({r} ** 3)",
            "result": round(vol, 4),
            "details": f"(4/3) × π × 半径({r})³ = {round(vol, 4)}"
        }

    # 3. 統計・教育: 平均値 (例: "10, 20, 30, 40, 50の平均")
    avg_m = re.search(r'([\d\s\,\.]+)\s*の\s*平均(?:値)?', norm)
    if avg_m:
        nums_str = re.findall(r'\d+(?:\.\d+)?', avg_m.group(1))
        if len(nums_str) >= 2:
            nums = [float(x) for x in nums_str]
            avg_val = sum(nums) / len(nums)
            return {
                "type": "EDUCATION_STATS_AVERAGE",
                "formula": f"sum({nums}) / len({nums})",
                "result": int(avg_val) if avg_val.is_integer() else round(avg_val, 4),
                "details": f"合計({sum(nums)}) ÷ 要素数({len(nums)}) = {avg_val}"
            }

    return None

def evaluate_datetime(text: str):
    """日付差分、N日後/前の決定論的計算"""
    norm = text.strip()
    
    # 2つの日付間の日数差 (例: "2026-10-04から2026-12-31までの日数")
    dates = re.findall(r'(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?)', norm)
    if len(dates) >= 2:
        def parse_d(s):
            s = s.replace("年", "-").replace("月", "-").replace("日", "")
            parts = [int(p) for p in re.split(r'[-/]', s) if p]
            return date(parts[0], parts[1], parts[2])
        try:
            d1, d2 = parse_d(dates[0]), parse_d(dates[1])
            diff = abs((d2 - d1).days)
            return {
                "type": "DATE_DIFF",
                "formula": f"abs(date('{d2}') - date('{d1}')).days",
                "result": diff,
                "unit": "days"
            }
        except Exception:
            pass

    # N日後/前の計算 (例: "2026-10-04の14日後", "2026-10-04の3日前")
    shift = re.search(r'(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?)\s*の\s*(\d+)\s*日(後|前)', norm)
    if shift:
        s_date, n_days, direction = shift.group(1), int(shift.group(2)), shift.group(3)
        s_date = s_date.replace("年", "-").replace("月", "-").replace("日", "")
        parts = [int(p) for p in re.split(r'[-/]', s_date) if p]
        d = date(parts[0], parts[1], parts[2])
        delta = timedelta(days=n_days) if direction == "後" else timedelta(days=-n_days)
        target = d + delta
        return {
            "type": "DATE_SHIFT",
            "formula": f"date('{d}') {'+' if direction == '後' else '-'} timedelta(days={n_days})",
            "result": target.isoformat()
        }

    return None

def evaluate_regex(text: str):
    """Email, URL, IPアドレス等の構造化抽出"""
    emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    if emails and any(k in text for k in ["メール", "email", "Email", "アドレス", "抽出"]):
        return {
            "type": "EXTRACT_EMAIL",
            "formula": r"re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)",
            "result": emails
        }

    urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', text)
    if urls and any(k in text for k in ["URL", "url", "リンク", "抽出"]):
        return {
            "type": "EXTRACT_URL",
            "formula": r"re.findall(r'https?://[^\s<>\"]+|www\.[^\s<>\"]+', text)",
            "result": urls
        }

    return None

def evaluate_tier1_laya(task: str, candidates: list):
    """Tier 1: ローカル近傍AI (LAYA) または軽量ヒューリスティックによる型付き選択"""
    laya_cli = Path.home() / ".local" / "bin" / "laya-cascade"
    if laya_cli.exists():
        try:
            import subprocess
            payload = {"task": task, "candidates": candidates}
            res = subprocess.run(
                [str(laya_cli), "--json-input"],
                input=json.dumps(payload, ensure_ascii=False),
                capture_output=True,
                text=True,
                timeout=25,
                check=True
            )
            return json.loads(res.stdout)
        except Exception:
            pass

    # 軽量ヒューリスティック System 1（PyTorch / LAYA未導入環境向けのゼロ依存フォールバック）
    import difflib
    cand_texts = [c if isinstance(c, str) else c.get("text", "") for c in candidates]
    matches = difflib.get_close_matches(task, cand_texts, n=1, cutoff=0.5)
    if matches:
        best_idx = cand_texts.index(matches[0])
        ratio = difflib.SequenceMatcher(None, task, matches[0]).ratio()
        return {
            "tier": "Tier 1 (Heuristic System 1)",
            "choice": str(best_idx),
            "chosen_text": matches[0],
            "confidence": round(ratio, 4),
            "safe_high_confidence": ratio >= 0.75,
            "engine": "Standard Library Heuristic"
        }
    return None

def process_task(task: str, candidates: list = None):
    """
    TokenZero メイン処理ループ
    武藤カスケード 3段階判定 + トークン削減メトリクス記録
    """
    start_time = time.monotonic()
    
    # 1. 算術・計算
    res = evaluate_arithmetic(task)
    if res:
        elapsed = round((time.monotonic() - start_time) * 1000, 2)
        res["tier"] = "Tier 0 (Formula-First)"
        res["elapsed_ms"] = elapsed
        res["tokens_saved"] = 650
        res["cost_saved_usd"] = 0.00975
        record_metrics("Tier 0", task, elapsed, 650, 0.00975)
        return res

    # 2. 日付・時刻
    res = evaluate_datetime(task)
    if res:
        elapsed = round((time.monotonic() - start_time) * 1000, 2)
        res["tier"] = "Tier 0 (Formula-First)"
        res["elapsed_ms"] = elapsed
        res["tokens_saved"] = 550
        res["cost_saved_usd"] = 0.00825
        record_metrics("Tier 0", task, elapsed, 550, 0.00825)
        return res

    # 3. 構造抽出
    res = evaluate_regex(task)
    if res:
        elapsed = round((time.monotonic() - start_time) * 1000, 2)
        res["tier"] = "Tier 0 (Formula-First)"
        res["elapsed_ms"] = elapsed
        res["tokens_saved"] = 800
        res["cost_saved_usd"] = 0.01200
        record_metrics("Tier 0", task, elapsed, 800, 0.01200)
        return res

    # 4. 候補選択タスク (LAYA)
    if candidates:
        t1 = evaluate_tier1_laya(task, candidates)
        if t1 and t1.get("safe_high_confidence"):
            elapsed = round((time.monotonic() - start_time) * 1000, 2)
            t1["tokens_saved"] = 1200
            t1["cost_saved_usd"] = 0.01800
            record_metrics("Tier 1", task, elapsed, 1200, 0.01800)
            return t1
        elif t1:
            return t1

    # 5. フォールバック
    elapsed = round((time.monotonic() - start_time) * 1000, 2)
    record_metrics("Tier 2", task, elapsed, 0, 0.0, "ESCALATED")
    return {
        "tier": "Tier 2 (System 2 LLM Required)",
        "action": "ESCALATE_TO_LLM",
        "reason": "Task involves high-order semantics, chaos dynamics, or unstructured reasoning.",
        "elapsed_ms": elapsed
    }
