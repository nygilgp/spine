# spine/research.py — coordinator sketch (concept, not yet SDK-wired)
def search_subagent(brief):        # a "spoke" — only sees its brief
    return [{"claim": "Solar grew 34% in 2024", "source": "iea.org/2025"},
            {"claim": "Offshore wind up 12%", "source": "bnef.com/wind"}]

def synthesis_subagent(prompt):    # a "spoke" — ONLY knows what's in `prompt`
    return f"[synthesis based only on what was passed]\n{prompt}"

def coordinator(topic):
    findings = search_subagent(f"Search: {topic}")          # hub calls spoke 1
    # ❌ WRONG: synthesis_subagent("Synthesize the findings")  ← isolated context, sees nothing
    # ✅ RIGHT: pass the complete findings EXPLICITLY into the prompt
    passed = "\n".join(f"[{i+1}] {f['source']} — {f['claim']}"
                       for i, f in enumerate(findings))
    return synthesis_subagent(f"Synthesize these findings, preserve sources:\n{passed}")

if __name__ == "__main__":
    print(coordinator("renewable energy adoption"))