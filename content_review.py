#!/usr/bin/env python3
"""
IBAC Content Review MVP
Safely fetches and parses external content.
Automatically identifies embedded scripts/code and gates their execution.
"""

import subprocess
import sys
import os
import json
import html
import re
import time
import urllib.request
from pathlib import Path

POLICY_BIN = "/Users/roberttaylor/.hermes/scripts/ibac-intent/gate.py"

# The current session intent is always "content_review" at this MVP stage
CURRENT_INTENT = "content_review"

INBOX_DIR = Path("/Users/roberttaylor/.hermes/inbox")
INBOX_DIR.mkdir(parents=True, exist_ok=True)

def run_gate(tool_name):
    """Run the IBAC gate for a specific intent and tool."""
    result = subprocess.run(
        ["python3", POLICY_BIN, "--intent", CURRENT_INTENT, "--tool", tool_name],
        capture_output=True, text=True
    )
    status, reason, intent_desc = result.stdout.strip().split(" — ")
    return status == "ALLOWED", reason, intent_desc

def extract_scripts(content):
    """Find potential executable blocks in the content."""
    # Look for markdown code fences or <script> tags
    patterns = [
        r'```(?:\w+)?\n(.*?)```',                  # Markdown
        r'<script[^>]*>([\s\S]*?)</script>',         # HTML script
        r'#!/.*?\n.*?\n',                            # Bash shebangs
        r'BEGIN SCRIPT\n(.*?)\nEND SCRIPT',          # Specific comment blocks
    ]
    
    scripts = []
    for pattern in patterns:
        matches = re.findall(pattern, content, re.DOTALL)
        for m in matches:
            m = m.strip()
            # Filter out non-executables (like CSS or HTML snippets)
            if len(m) > 10:
                scripts.append(m)
    return scripts

def review_content(url_or_text, source):
    """Process content under `content_review` intent."""
    print(f"--- INITIATING `content_review` for: {source} ---")
    
    # 1. Fetch Content
    if url_or_text.startswith("http"):
        print(f"Fetching URL: {url_or_text}")
        content = urllib.request.urlopen(url_or_text).read().decode('utf-8')
        summary_type = "Remote URL"
    else:
        content = url_or_text
        summary_type = "Local Source"
        
    # 2. Parse/Prep Content (stripping HTML tags for readability)
    clean = html.unescape(content)
    clean = re.sub(r'<[^>]+>', '', clean)  # Basic tag stripping
    clean = re.sub(r'\n{3,}', '\n\n', clean)
    
    # 3. Identify embedded scripts
    found_scripts = extract_scripts(content)
    
    # 4. Run the Gate on every identified script
    blocked_scripts = []
    allowed_scripts = []
    
    for i, script in enumerate(found_scripts):
        can_execute, reason, _ = run_gate("execute_command")
        
        entry = {
            "id": i,
            "type": "Embedded Script",
            "raw": script[:200] + "..." if len(script) > 200 else script,
            "execution_status": "ALLOWED" if can_execute else "BLOCKED",
            "reason": reason
        }
        
        if can_execute:
            allowed_scripts.append(entry)
        else:
            blocked_scripts.append(entry)
            
    # 5. Output Summary
    print("\n--- CONTENT SUMMARY ---")
    print(f"Source: {source}")
    print(f"Type: {summary_type}")
    print(f"Length: {len(clean)} chars")
    print("-" * 30)
    print(clean[:800] + "..." if len(clean) > 800 else clean)
    print("-" * 30)
    
    print(f"\n--- SECURITY GATE RESULTS ---")
    print(f"Total scripts/code blocks found: {len(found_scripts)}")
    print(f"Blocked: {len(blocked_scripts)}")
    print(f"Allowed: {len(allowed_scripts)}")
    
    if blocked_scripts:
        print("\n[ALERT] Script execution is explicitly blocked under `content_review`.")
        print("To run any of the above, the intent must be switched to `script_execution`.")
        
    # 6. Save to Inbox for the Monitor to pick up
    output_filename = f"review_{int(time.time())}.json"
    output_path = INBOX_DIR / output_filename
    inbox_data = {
        "source": source,
        "summary": clean[:500],
        "scripts_found": len(found_scripts),
        "scripts_blocked": len(blocked_scripts),
        "blocked_scripts": blocked_scripts
    }
    with open(output_path, "w") as f:
        json.dump(inbox_data, f, indent=2)
        
    print(f"\n[SAVED] Content review logged to: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: content_review.py <url_or_file>")
        sys.exit(1)
        
    source_url = sys.argv[1]
    review_content(source_url, source_url)
