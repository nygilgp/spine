# spine/CLAUDE.md (project-level — shared via git)

## Project

Customer Support Resolution Agent + Multi-Agent Research subsystem (Python 3.12, Agent SDK).

## Conventions

- Tool execution ALWAYS routes through guarded_execute() (gate) then normalize_result().
- Financial ordering (verify → refund) is enforced by a PreToolUse gate, never by prompt.
- Subagents get scoped `tools` only; coordinator holds "Agent"/"Task" to delegate.

## Import package standards

@./.claude/standards/testing.md

## Working mode (append to spine/CLAUDE.md)

- Architectural spine changes (new subagent layer, restructuring the loop, changing the
  gate/hook pipeline) → PLAN MODE first: explore deps, design, get approval, then execute.
- Well-scoped fixes (a single tool stub, one gate condition, a normalize_result mapping)
  → DIRECT EXECUTION.
- Multi-file discovery (tracing the refund path across modules) → use the Explore subagent
  so discovery output stays out of the main context.
