---
name: codex-advisor
description: Expert technical consultation for critical design decisions. Use when facing architectural choices, tradeoff analysis, or need assumption checking before implementation. Provides structured analysis through Codex CLI.
license: Complete terms in LICENSE.txt
---

# Codex Advisor

## When to Use

Use this skill for:
- Architectural decisions affecting multiple modules
- High-risk areas (performance, security, data consistency)
- Tradeoff analysis between design alternatives
- Assumption validation before implementation

For simple tasks (single-file changes, straightforward bugfixes), implement directly without this skill.

## How to Use

Call the advisor by running:

```bash
python scripts/wrapper_codex.py "Your problem description" \
  --context "Background and constraints" \
  --focus-areas "performance,security"
```

The bridge service starts automatically when needed.

## Input Format

Provide:
- **problem**: Core technical question (required, ≤100k chars)
- **context**: Background, tech stack, constraints (≤200k chars)
- **candidate_plans**: Your proposed solutions with assumptions
- **focus_areas**: Dimensions to prioritize (e.g., "performance", "maintainability")

## Output Format

Returns structured analysis:
- **clarifying_questions**: Questions to refine the problem
- **assumption_check**: Validation of your assumptions (plausible/risky/invalid)
- **alternatives**: Additional approaches to consider
- **tradeoffs**: Multi-dimensional analysis
- **recommendation**: Preferred solution with confidence level
- **followup_suggestions**: Next steps

## Example

```bash
python scripts/wrapper_codex.py \
  "Choose state management for React app with 50+ components" \
  --context "Real-time data updates, 100k users, current stack: Node.js + PostgreSQL" \
  --focus-areas "performance,maintainability"
```

## Notes

- Default timeout: 30 minutes (complex analysis takes time)
- For very complex problems, break into focused questions
- Service auto-starts and auto-stops as needed
