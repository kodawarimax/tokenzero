# -*- coding: utf-8 -*-
"""
TokenZero Engine: Deterministic Agent Kernel
Multi-Agent (Claude Code, OpenAI Codex CLI, Google Antigravity)
"""

from tokenzero.ontology import validate_action, OntologyViolation, ALLOWED_STATE_TRANSITIONS
from tokenzero.kernel import (
    process_task,
    get_stats,
    record_metrics,
    evaluate_arithmetic,
    evaluate_datetime,
    evaluate_regex
)

from tokenzero.rules import inject_rules, TOKENZERO_DISCIPLINE_MARKDOWN
from tokenzero.mcp import run_mcp_server

__version__ = "0.2.0"

__all__ = [
    "validate_action",
    "OntologyViolation",
    "ALLOWED_STATE_TRANSITIONS",
    "process_task",
    "get_stats",
    "record_metrics",
    "evaluate_arithmetic",
    "evaluate_datetime",
    "evaluate_regex",
    "inject_rules",
    "TOKENZERO_DISCIPLINE_MARKDOWN",
    "run_mcp_server",
    "__version__"
]
