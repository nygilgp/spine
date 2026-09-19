# spine/CLAUDE.md (project-level — shared via git)

## Project

Customer Support Resolution Agent + Multi-Agent Research subsystem (Python 3.12, Agent SDK).

## Conventions

- Tool execution ALWAYS routes through guarded_execute() (gate) then normalize_result().
- Financial ordering (verify → refund) is enforced by a PreToolUse gate, never by prompt.
- Subagents get scoped `tools` only; coordinator holds "Agent"/"Task" to delegate.

## Import package standards

@./.claude/standards/testing.md
