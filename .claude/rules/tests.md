---
paths: ['**/*_test.py', '**/test_*.py']
---

# Test conventions (loads ONLY when a test file is touched)

- Use pytest; name tests test*<behavior>*<condition>.
- Every gate/hook change needs a test proving the blocked path (e.g. refund-without-verify).
- Arrange-Act-Assert; one behavior per test.
