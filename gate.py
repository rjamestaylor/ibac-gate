#!/usr/bin/env python3
"""
IBAC Content Gate - Policy Engine
Simple intent-based access control for content review workflows.

Usage:
    python3 gate.py --intent <intent_name> --tool <tool_name>
    
Examples:
    python3 gate.py --intent content_review --tool fetch_url      # ALLOW
    python3 gate.py --intent content_review --tool execute_command # DENY
"""

import sys
import json
import argparse

POLICY_PATH = "/Users/roberttaylor/.hermes/scripts/ibac-intent/policy.json"

def load_policy():
    """Load the IBAC policy file."""
    with open(POLICY_PATH) as f:
        return json.load(f)

def evaluate_tool_call(intent, tool_name):
    """
    Evaluate if a tool call is allowed for the given intent.
    
    Returns: (allowed: bool, reason: str, intent_desc: str)
    """
    policy = load_policy()
    intents = policy.get("intents", {})
    
    # 1. Check if intent exists
    if intent not in intents:
        return False, f"Unknown intent: {intent}", ""
    
    intent_rules = intents[intent]
    intent_desc = intent_rules.get("description", "")
    allowed_tools = intent_rules.get("allowed", [])
    deny_patterns = intent_rules.get("deny", [])
    
    # 2. Check if tool matches any deny pattern
    for pattern in deny_patterns:
        if pattern in tool_name:
            return False, f"Tool '{tool_name}' blocked by deny pattern '{pattern}' for {intent}", intent_desc
    
    # 3. Check if tool is in allowed list
    if tool_name in allowed_tools:
        return True, f"Tool '{tool_name}' allowed for {intent}", intent_desc
    
    # 4. Tool not in either list - deny by default
    return False, f"Tool '{tool_name}' not in allowed list for {intent}", intent_desc

def main():
    parser = argparse.ArgumentParser(description="IBAC Content Gate Evaluator")
    parser.add_argument("--intent", required=True, help="Current session intent")
    parser.add_argument("--tool", required=True, help="Tool being called")
    args = parser.parse_args()
    
    # Evaluate
    allowed, reason, intent_desc = evaluate_tool_call(args.intent, args.tool)
    
    status = "ALLOWED" if allowed else "DENIED"
    print(f"{status} — {reason}")
    
    sys.exit(0 if allowed else 1)

if __name__ == "__main__":
    main()
