# spine/research.py — coordinator picks a decomposition strategy
def choose_decomposition(task: str) -> str:
    """Fixed chain for predictable multi-aspect work; adaptive for open-ended investigation."""
    open_ended = any(w in task.lower() for w in
                     ["explore", "investigate", "comprehensive", "legacy", "figure out"])
    return "dynamic_adaptive" if open_ended else "prompt_chaining"

def plan(task: str):
    strategy = choose_decomposition(task)
    if strategy == "prompt_chaining":
        return ["per-file local pass", "cross-file integration pass"]   # fixed, known steps
    return ["map structure", "identify high-impact areas", "prioritize + RE-PLAN as deps surface"]

if __name__ == "__main__":
    print(plan("review these 14 files for bugs"))          # → chaining
    print(plan("add comprehensive tests to legacy code"))  # → adaptive