# spine/research.py — decide how to re-enter a prior investigation
def reentry_strategy(changed_files: list[str], total_analyzed: int) -> dict:
    """Resume if mostly valid; fresh+summary if substantially stale."""
    if not changed_files:
        return {"mode": "resume"}                                   # nothing changed
    stale_ratio = len(changed_files) / max(total_analyzed, 1)
    if stale_ratio <= 0.3:
        return {"mode": "resume", "reanalyze": changed_files}       # targeted re-analysis
    return {"mode": "fresh_with_summary"}                           # too stale → clean start

# Fork pattern (docs shape) — branch a shared baseline, original untouched:
#   ClaudeAgentOptions(resume=analyzed_session_id, fork_session=True)

if __name__ == "__main__":
    print(reentry_strategy([], 20))                 # → resume
    print(reentry_strategy(["a.py","b.py"], 20))    # → resume + reanalyze those 2
    print(reentry_strategy([f"f{i}.py" for i in range(12)], 20))  # → fresh_with_summary