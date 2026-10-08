# -*- coding: utf-8 -*-
"""
core/ontology.py
Backwards compatibility layer for TokenZero Ontology (OAG).
Delegates to tokenzero.ontology.
"""

try:
    from tokenzero.ontology import validate_action, OntologyViolation, ALLOWED_STATE_TRANSITIONS
except ImportError:
    import sys
    from pathlib import Path
    _ROOT = Path(__file__).resolve().parent.parent
    if str(_ROOT) not in sys.path:
        sys.path.insert(0, str(_ROOT))
    from tokenzero.ontology import validate_action, OntologyViolation, ALLOWED_STATE_TRANSITIONS

__all__ = ["validate_action", "OntologyViolation", "ALLOWED_STATE_TRANSITIONS"]
