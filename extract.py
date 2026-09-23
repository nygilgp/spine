# spine/extract.py — nullable fields + a semantic cross-check
REFUND_EXTRACT_TOOL = {
    "name": "extract_refund_request",
    "description": "Extract refund request fields from a customer message/receipt.",
    "input_schema": {
        "type": "object",
        "properties": {
            "order_id": {"type": ["string", "null"]},        # nullable — may be absent
            "stated_total": {"type": ["number", "null"]},
            "line_items_sum": {"type": ["number", "null"]},  # for a semantic cross-check
            "reason": {"type": "string", "enum": ["damaged", "wrong_item", "unclear", "other"]},
            "reason_detail": {"type": ["string", "null"]},   # for "other"
            "conflict_detected": {"type": "boolean"},        # flag inconsistent source
        },
        "required": ["reason", "conflict_detected"],          # only the always-derivable ones
    },
}
# tool_choice: {"type":"tool","name":"extract_refund_request"}  ← force THIS extraction

# spine/extract.py — route by calibrated confidence (threshold from a labeled set)
REVIEW_THRESHOLD = 0.85   # derived from calibration, NOT guessed
def route_for_review(extraction):
    conf = extraction.get("field_confidence", {})
    low = [f for f, c in conf.items() if c < REVIEW_THRESHOLD]
    return {"needs_human": bool(low) or extraction.get("conflict_detected"), "low_fields": low}