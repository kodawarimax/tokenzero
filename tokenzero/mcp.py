# -*- coding: utf-8 -*-
"""
TokenZero MCP (Model Context Protocol) Server
Stdio JSON-RPC 2.0 server for Cursor, Windsurf, Claude Desktop, Cline, and Roo Code.
"""

import sys
import json
from tokenzero.kernel import process_task, get_stats
from tokenzero.ontology import validate_action, OntologyViolation

def make_response(req_id, result=None, error=None):
    resp = {"jsonrpc": "2.0", "id": req_id}
    if error is not None:
        resp["error"] = error
    else:
        resp["result"] = result
    return resp

def run_mcp_server():
    """標準入出力を通じた MCP サーバー実行ループ"""
    tools_def = [
        {
            "name": "tokenzero_run",
            "description": "Evaluate formulas, discounts, taxes, date differences, and regex extractions deterministically (0ms, 0% error, 0 token waste).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Math expression, discount formula, date shift, or text for regex extraction (e.g., '15000円の15%引き', '2026-10-04から2026-12-31までの日数')"
                    }
                },
                "required": ["task"]
            }
        },
        {
            "name": "tokenzero_ontology",
            "description": "Validate and govern business actions against immutable physical/ontology constraints (e.g. max discount rate 30%, state transition rules).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "entity": {
                        "type": "string",
                        "description": "Entity name (e.g. 'Invoice', 'TaskState')"
                    },
                    "action": {
                        "type": "string",
                        "description": "Action name (e.g. 'apply_discount', 'transition_state')"
                    },
                    "params": {
                        "type": "object",
                        "description": "Action parameters JSON object"
                    }
                },
                "required": ["entity", "action", "params"]
            }
        },
        {
            "name": "tokenzero_stats",
            "description": "Retrieve cumulative token savings and ROI metrics.",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        }
    ]

    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            continue

        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        if method == "initialize":
            resp = make_response(req_id, {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "tokenzero-mcp",
                    "version": "0.2.0"
                },
                "capabilities": {
                    "tools": {}
                }
            })
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "notifications/initialized":
            # 通知なのでレスポンス不要
            continue

        elif method == "tools/list":
            resp = make_response(req_id, {"tools": tools_def})
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "tools/call":
            tool_name = params.get("name")
            args = params.get("arguments", {})

            try:
                if tool_name == "tokenzero_run":
                    task = args.get("task", "")
                    res = process_task(task)
                    text_out = json.dumps(res, ensure_ascii=False, indent=2)
                elif tool_name == "tokenzero_ontology":
                    entity = args.get("entity", "")
                    action = args.get("action", "")
                    act_params = args.get("params", {})
                    res = validate_action(entity, action, act_params)
                    text_out = json.dumps(res, ensure_ascii=False, indent=2)
                elif tool_name == "tokenzero_stats":
                    res = get_stats()
                    text_out = json.dumps(res, ensure_ascii=False, indent=2)
                else:
                    text_out = f"Unknown tool: {tool_name}"

                resp = make_response(req_id, {
                    "content": [
                        {
                            "type": "text",
                            "text": text_out
                        }
                    ]
                })
            except OntologyViolation as ov:
                resp = make_response(req_id, {
                    "isError": True,
                    "content": [
                        {
                            "type": "text",
                            "text": f"[ONTOLOGY VIOLATION] {ov}"
                        }
                    ]
                })
            except Exception as e:
                resp = make_response(req_id, {
                    "isError": True,
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error: {e}"
                        }
                    ]
                })

            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "ping":
            resp = make_response(req_id, {})
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        else:
            if req_id is not None:
                resp = make_response(req_id, error={"code": -32601, "message": f"Method not found: {method}"})
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()

if __name__ == "__main__":
    run_mcp_server()
