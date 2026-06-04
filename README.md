# IBAC Gate

Intent-based access control (IBAC) system that gates tool execution based on the current task intent.

## Overview

IBAC Gate provides a policy engine for content review workflows that automatically identifies embedded scripts/code and gates their execution. The system evaluates tool calls against intent-specific allow/deny rules, ensuring safe and controlled access to system resources.

## Components

- **`gate.py`** - Policy engine that evaluates tool calls against intent rules
- **`content_review.py`** - Content review MVP that fetches, parses, and gates external content
- **`policy.json`** - Intent configuration defining allowed/denied tools per intent

## Getting Started

### Prerequisites

- Python 3.7+

### Setup

```bash
git clone https://github.com/rjamestaylor/ibac-gate.git
cd ibac-gate
```

### Usage

Run the gate evaluator:

```bash
python3 gate.py --intent <intent_name> --tool <tool_name>
```

Examples:

```bash
# Allow fetching URL during content review
python3 gate.py --intent content_review --tool fetch_url

# Deny executing commands during content review
python3 gate.py --intent content_review --tool execute_command
```

Run content review:

```bash
python3 content_review.py <url_or_file>
```

## Configuration

Policies are defined in `policy.json`. Each intent specifies a description, an `allowed` list of tools, and a `deny` list of blocked tools:

```json
{
  "intents": {
    "content_review": {
      "description": "Evaluate, summarize, and categorize external content.",
      "allowed": ["fetch_url", "parse_html", "extract_text"],
      "deny": ["execute_command", "write_file", "ssh", "git"]
    }
  }
}
```

## License

MIT License. See [LICENSE](LICENSE) for details.
