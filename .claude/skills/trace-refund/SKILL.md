---
name: trace-refund
description: Trace all dependencies of the refund flow across the codebase
context: fork
allowed-tools: Read, Grep, Glob
argument-hint: <entry-function>
---

Starting from $ARGUMENTS, trace every caller and dependency of the refund path.
Return ONLY a concise dependency summary (not the full exploration log).
