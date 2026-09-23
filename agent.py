# spine/agent.py — the spine skeleton (grows every episode)
from dotenv import load_dotenv
import anthropic
# spine/agent.py — PostToolUse-style normalization of tool RESULTS
from datetime import datetime, timezone

STATUS_CODES = {1: "pending", 2: "shipped", 3: "delivered", 4: "refunded"}
TOOLS = [
    {"name": "get_customer", 
     "description": "Verify a customer and return a verified customer_id. INPUT: email. "
                    "USE WHEN: identifying/verifying a person (e.g. 'my email is a@b.com'). "
                    "NOT for order details — use lookup_order for those. Must run before refunds.",
     "input_schema": {"type": "object", "properties": {"email": {"type": "string"}}, "required": ["email"]}
    },
    {"name": "lookup_order", 
     "description": "Retrieve order details (status, amount) for a verified customer_id. "
                    "INPUT: customer_id + order_id. USE WHEN: the user asks about an ORDER "
                    "(e.g. 'check order #12345'). NOT for identifying a person — use get_customer.",
     "input_schema": {"type": "object", "properties": {"customer_id": {"type": "string"}, "order_id": {"type": "string"}}, "required": ["customer_id"]}},
    {"name": "process_refund", 
     "description": "Issue a refund for a verified customer's order.",
     "input_schema": {"type": "object", "properties": {"order_id": {"type": "string"}, "amount": {"type": "number"}}, "required": ["order_id", "amount"]}},
    {"name": "escalate_to_human", 
     "description": "Escalate to a human agent with a structured handoff summary.",
     "input_schema": {"type": "object", "properties": {"reason": {"type": "string"}}, "required": ["reason"]}},
]
# spine/agent.py — add a prerequisite gate around tool execution
STATE = {"verified_customer_id": None}   # module-level case state for now
CASE_FACTS = {}   # transactional facts, never summarized away

def update_case_facts(name, result):
    if name == "get_customer": CASE_FACTS["customer_id"] = result.get("customer_id")
    if name == "lookup_order":
        CASE_FACTS.update({k: result.get(k) for k in ("order_id", "amount", "status")})

RELEVANT = {"lookup_order": {"order_id", "amount", "status", "date", "customer_id"}}
def trim(name, result):
    keep = RELEVANT.get(name)
    return {k: v for k, v in result.items() if k in keep} if keep else result

def case_facts_prompt():
    return "CASE FACTS (persistent): " + "; ".join(f"{k}={v}" for k, v in CASE_FACTS.items())


load_dotenv()                    # reads .env before the client is created
client = anthropic.Anthropic()   # picks up ANTHROPIC_API_KEY automatically

def normalize_result(name, result):
    """PostToolUse pattern: clean heterogeneous formats before the model sees them."""
    r = dict(result)
    if "timestamp" in r and isinstance(r["timestamp"], (int, float)):   # Unix → ISO 8601
        r["timestamp"] = datetime.fromtimestamp(r["timestamp"], tz=timezone.utc).isoformat()
    if "status" in r and isinstance(r["status"], int):                  # numeric code → text
        r["status"] = STATUS_CODES.get(r["status"], f"unknown({r['status']})")
    return r

def fake_execute(name, tool_input):
    # stub tool results — real MCP wiring comes in S4
    return {
            "get_customer": {"customer_id": "C-900"},
            "lookup_order": {"order_id": "12345", "status": 3, "amount": 49.0, "timestamp": 1704067200},
            "process_refund": {"refund_id": "R-1", "status": "issued"},
            "escalate_to_human": {"ticket": "T-1"}}.get(name, {})

def run(user_msg):
    messages = [{"role": "user", "content": user_msg}]
    resp = client.messages.create(model="claude-sonnet-4-5", max_tokens=1024, tools=TOOLS, messages=messages, system=case_facts_prompt())
    while resp.stop_reason == "tool_use":                        # ← THE ONE RULE
        results = []
        for b in resp.content:
            if b.type != "tool_use":
                continue
            raw = guarded_execute(b.name, b.input)
            result = normalize_result(b.name, raw)
            result = trim(b.name, result)
            update_case_facts(b.name, result)
            results.append({"type": "tool_result", "tool_use_id": b.id, "content": str(result)})
        messages.append({"role": "assistant", "content": resp.content})
        messages.append({"role": "user", "content": results})
        resp = client.messages.create(model="claude-sonnet-4-5", max_tokens=1024, tools=TOOLS, messages=messages, system=case_facts_prompt())
    print("FINAL:", "".join(b.text for b in resp.content if b.type == "text"))
    return resp

def gate(name, tool_input):
    if name == "process_refund" and not STATE["verified_customer_id"]:
        return False, {"isError": True, "errorCategory": "business", "isRetryable": False,
                       "message": "Identity not verified; run get_customer first."}
    if name == "process_refund" and tool_input.get("amount", 0) > 500:
        return False, {"isError": True, "errorCategory": "business", "isRetryable": False,
                       "message": "Refund exceeds $500 policy; escalate to human."}
    return True, None

def should_escalate(msg, made_progress, policy_covers, multiple_matches):
    if "speak to a human" in msg.lower(): return "explicit_request"   # honor immediately
    if not policy_covers:                 return "policy_gap"
    if not made_progress:                 return "no_progress"
    if multiple_matches:                  return "need_identifiers"    # ask, don't pick
    return None   # NOTE: no sentiment check, no confidence threshold — those are proxies

def guarded_execute(name, tool_input):
    allowed, msg = gate(name, tool_input)
    if not allowed:
        return {"error": msg}                       # agent sees this, self-corrects
    result = fake_execute(name, tool_input)
    if name == "get_customer":                       # record verification in state
        STATE["verified_customer_id"] = result.get("customer_id")
    return result

if __name__ == "__main__":
    print("=== TEST 1: straight-to-refund — gate should block, agent self-corrects ===")
    STATE["verified_customer_id"] = None
    run("Refund $49 on order 12345.")          # no email → Claude tries process_refund, hits gate

    print("\n=== TEST 2: verify-first — gate never fires ===")
    STATE["verified_customer_id"] = None
    run("My email is a@b.com. Verify my identity first, then refund order 12345 for $49. Also provide the order status and date of purchase.")  # Claude calls get_customer first, then refund