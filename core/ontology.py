# -*- coding: utf-8 -*-
"""
TokenZero Ontology Layer (OAG: Ontology Action Governance)
Based on Palantir Ontology & System Physics Constraints.
"""

from typing import Dict, Any

class OntologyViolation(Exception):
    """オントロジー制約・物理法則違反時に送出される例外"""
    pass

# 許可されたタスク状態遷移テーブル（飛び級禁止）
ALLOWED_STATE_TRANSITIONS = {
    "DRAFT": ["REVIEW", "CANCELLED"],
    "REVIEW": ["APPROVED", "REJECTED", "DRAFT"],
    "APPROVED": ["IN_PROGRESS", "CANCELLED"],
    "IN_PROGRESS": ["COMPLETED", "FAILED", "REVIEW"],
    "COMPLETED": [],
    "FAILED": ["RETRY", "CANCELLED"],
    "CANCELLED": []
}

def validate_action(entity: str, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    エンティティのアクションをオントロジー制約に従って検証・実行する。
    """
    if entity == "Invoice":
        if action == "apply_discount":
            discount_rate = float(params.get("discount_rate", 0.0))
            amount = float(params.get("amount", 0.0))
            
            # 制約: 割引率は最大30% (0.30) まで
            if discount_rate > 0.30:
                raise OntologyViolation(
                    f"割引率 {discount_rate*100:.1f}% は上限 30.0% を超過しています (OAG: Invoice Discount Limit)"
                )
            if discount_rate < 0.0:
                raise OntologyViolation("割引率は 0% 以上である必要があります")
                
            discounted_amount = amount * (1.0 - discount_rate)
            return {
                "status": "APPROVED",
                "entity": "Invoice",
                "action": "apply_discount",
                "original_amount": amount,
                "discount_rate": discount_rate,
                "discounted_amount": discounted_amount,
                "client_name": params.get("client_name", "Unknown")
            }
            
    elif entity == "TaskState":
        if action == "transition_state":
            current_status = params.get("current_status")
            next_status = params.get("next_status")
            task_id = params.get("task_id", "Unknown")
            
            allowed = ALLOWED_STATE_TRANSITIONS.get(current_status, [])
            if next_status not in allowed:
                raise OntologyViolation(
                    f"不正な状態遷移: '{current_status}' -> '{next_status}' は禁止されています。"
                    f"許可されている遷移: {allowed} (飛び級禁止ルール)"
                )
                
            return {
                "status": "APPROVED",
                "entity": "TaskState",
                "action": "transition_state",
                "task_id": task_id,
                "from_status": current_status,
                "to_status": next_status
            }
            
    raise OntologyViolation(f"未定義または不正なエンティティ/アクションです: {entity}.{action}")
