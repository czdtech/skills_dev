---
name: droid-executor
description: This skill should be used when executing predefined coding tasks after the architecture and plan have been determined by Claude Code. It modifies code, runs tests and commands, and returns structured results following a clear execution contract.
---

# Droid Executor

## When to Use This Skill

Use this skill when:

- The architecture and plan have been determined by Claude Code (optionally with Codex advisor)
- The current subtask has clear objectives, scope, and acceptance criteria
- The task is suitable for implementation by an execution-oriented programmer

For exploratory work or tasks with highly uncertain requirements, complete the discussion and task breakdown first before using this skill.

## Calling Guide for Claude Code

Before calling this skill, prepare a clear execution contract for the current task:

1. **Objective**:
   - What this change should accomplish (1-2 sentences)
   
2. **Context**:
   - Repository root path and list of relevant modules/files
   
3. **Instructions**:
   - Specific steps to follow, for example:
   - "Convert 7 callback functions in src/utils/parser.ts to async/await while maintaining the public interface"
   
4. **Constraints**:
   - Examples: "Do not modify public API signatures" or "Maintain existing log format"
   
5. **Acceptance Criteria**:
   - Examples: "All npm tests pass" or "New functions have unit tests"

## Input Requirements

To ensure the skill works correctly, follow these requirements:

### Required Fields

- **Objective**: Cannot be empty, maximum 50,000 characters
  - ✅ Correct: "Convert callback functions in callbacks.py to async/await"
  - ❌ Incorrect: "" (empty string)
  - ❌ Incorrect: "   " (whitespace only)

### Optional Fields

- **Instructions**: Recommended < 100,000 characters, longer inputs will be rejected
- **Context**: Can be a string or dictionary; recommended to provide `repo_root` and `files_of_interest`
- **Constraints**: Array listing constraints that must not be violated
- **Acceptance Criteria**: Array listing acceptance criteria

### Execution Time Limits

- **Default timeout**: 10 minutes (600 seconds)
- **Recommendation**: Split tasks expected to exceed 10 minutes into smaller subtasks
- **Reason**: Easier to debug and recover from failures

## Best Practices

### 1. Task Splitting Principles

- ✅ **Recommended**: Focus each task on a single objective (e.g., "Fix Bug X" or "Add Feature Y")
- ❌ **Avoid**: Submitting multiple unrelated tasks at once (e.g., "Fix all bugs and refactor the entire module")

### 2. Clear Instructions

- ✅ **Good instruction**: "Add email parameter validation to User.__init__ method using regex"
- ❌ **Vague instruction**: "Improve user class"

### 3. Provide Sufficient Context

```json
{
  "context": {
    "repo_root": "/path/to/project",
    "files_of_interest": ["src/models/user.py", "tests/test_user.py"],
    "summary": "User management module using SQLAlchemy ORM"
  }
}
```

### 4. Set Reasonable Constraints

```json
{
  "constraints": [
    "Do not modify User.login() method signature",
    "Maintain backward compatibility with API v1",
    "Do not introduce new external dependencies"
  ]
}
```

## Execution Modes

Pass the above content to this skill and specify the execution mode:

- **Direct implementation mode** (default): Focus on completing the changes
- **Preview/exploration mode** (future extension):
  - First estimate impact scope and complexity (e.g., "Expected number of files to change, potential conflicts")
  - Then decide whether to proceed

## Droid Behavior Principles

When this skill is triggered, strictly follow these principles:

1. **Follow the execution contract**: Adhere to the contract and constraints provided by Claude Code
2. **Stay within scope**: Modify code only within the task scope; avoid unrelated large-scale refactoring
3. **Return structured results** after execution, including:
   - Modified files with brief descriptions
   - Actual commands executed and exit codes
   - Test result summary
   - Discovered issues or blocking factors (e.g., missing environment dependencies, requirement conflicts)
4. **Return logs even on failure**: Provide logs and intermediate results to help Claude Code diagnose issues

This skill does not handle final decisions or task status updates—those are managed by Claude Code in other workflows.
