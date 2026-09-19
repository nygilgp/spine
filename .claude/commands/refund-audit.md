---
description: Audit the refund path for gate/hook coverage
argument-hint: [order-id]
allowed-tools: Read, Grep
---

Audit the refund flow for order #$1.
Verify guarded_execute() blocks process_refund without a verified customer_id,
and that normalize_result() runs on the result. Report any gaps.
