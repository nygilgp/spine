# CI step — headless, structured, non-interactive

claude -p "/ci-review 'spine/\*_/_.py'" \
 --output-format json \
 --json-schema '{"type":"object","properties":{"findings":{"type":"array"}}}'

# -p = no hang; json+schema = parseable findings for inline PR comments
