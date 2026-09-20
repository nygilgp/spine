---
description: Headless security+gate review with explicit criteria
argument-hint: [changed-files-glob]
allowed-tools: Read, Grep
---

Review $ARGUMENTS. REPORT only:

- BUGS: refund path bypasses guarded_execute(); tool result skips normalize_result().
- SECURITY: unverified customer_id reaching process_refund; secrets in code.
  SKIP: style, naming, local formatting.
  Severity — CRITICAL: money/security can leak (example: refund without verify).
  MINOR: defensive nit that can't cause incorrect refunds.
  Report ONLY new or still-unaddressed issues.
