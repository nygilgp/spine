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

def run(user_msg):
    messages = [{"role": "user", "content": user_msg}]
    resp = client.messages.create(model="claude-sonnet-4-5", max_tokens=1024, tools=TOOLS, messages=messages)
    print("stop_reason:", resp.stop_reason)   # E1.1 turns this into the real loop
    return resp

if __name__ == "__main__":
    run("I want a refund for order 12345, my email is a@b.com")