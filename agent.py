# spine/agent.py — the spine skeleton (grows every episode)
from dotenv import load_dotenv
load_dotenv()                    # reads .env before the client is created
import anthropic
client = anthropic.Anthropic()   # picks up ANTHROPIC_API_KEY automatically

TOOLS = [
    {"name": "get_customer", "description": "Verify a customer and return a verified customer_id. Must run before order or refund operations.",
     "input_schema": {"type": "object", "properties": {"email": {"type": "string"}}, "required": ["email"]}},
    {"name": "lookup_order", "description": "Retrieve order details for a verified customer_id.",
     "input_schema": {"type": "object", "properties": {"customer_id": {"type": "string"}, "order_id": {"type": "string"}}, "required": ["customer_id"]}},
    {"name": "process_refund", "description": "Issue a refund for a verified customer's order.",
     "input_schema": {"type": "object", "properties": {"order_id": {"type": "string"}, "amount": {"type": "number"}}, "required": ["order_id", "amount"]}},
    {"name": "escalate_to_human", "description": "Escalate to a human agent with a structured handoff summary.",
     "input_schema": {"type": "object", "properties": {"reason": {"type": "string"}}, "required": ["reason"]}},
]

def fake_execute(name, tool_input):
    # stub tool results — real MCP wiring comes in S4
    return {"get_customer": {"customer_id": "C-900"},
            "lookup_order": {"order_id": "12345", "status": "delivered", "amount": 49.0},
            "process_refund": {"refund_id": "R-1", "status": "issued"},
            "escalate_to_human": {"ticket": "T-1"}}.get(name, {})

def run(user_msg):
    messages = [{"role": "user", "content": user_msg}]
    resp = client.messages.create(model="claude-sonnet-4-5", max_tokens=1024, tools=TOOLS, messages=messages)
    while resp.stop_reason == "tool_use":                        # ← THE ONE RULE
        results = [{"type": "tool_result", "tool_use_id": b.id,
                    "content": str(fake_execute(b.name, b.input))}
                   for b in resp.content if b.type == "tool_use"]
        messages.append({"role": "assistant", "content": resp.content})
        messages.append({"role": "user", "content": results})
        resp = client.messages.create(model="claude-sonnet-4-5", max_tokens=1024, tools=TOOLS, messages=messages)
    print("FINAL:", "".join(b.text for b in resp.content if b.type == "text"))
    return resp

# spine/agent.py — add a prerequisite gate around tool execution
STATE = {"verified_customer_id": None}   # module-level case state for now

def gate(name, tool_input):
    """Block refunds until identity is verified. Returns (allowed, message)."""
    if name == "process_refund" and not STATE["verified_customer_id"]:
        return False, "BLOCKED: call get_customer to verify identity before any refund."
    return True, None

def guarded_execute(name, tool_input):
    allowed, msg = gate(name, tool_input)
    if not allowed:
        return {"error": msg}                       # agent sees this, self-corrects
    result = fake_execute(name, tool_input)
    if name == "get_customer":                       # record verification in state
        STATE["verified_customer_id"] = result.get("customer_id")
    return result

if __name__ == "__main__":
    run("I want a refund for order 12345, my email is a@b.com")