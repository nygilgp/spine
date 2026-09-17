# spine/research.py — real coordinator with scoped, parallel-capable subagents
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition

def build_options():
    return ClaudeAgentOptions(
        allowed_tools=["Agent"],                     # exam calls this "Task" — REQUIRED to delegate
        agents={
            "web-searcher": AgentDefinition(
                description="Finds web sources for a topic. Use for gathering articles/data.",
                prompt="Search the web. Return each finding as: claim | source URL.",
                tools=["WebSearch"],                 # scoped — search only
            ),
            "doc-analyst": AgentDefinition(
                description="Extracts claims from documents. Use for analyzing papers.",
                prompt="Analyze provided documents. Return: claim | page citation.",
                tools=["Read", "Grep"],              # scoped — read only
            ),
        },
    )

async def main():
    async for msg in query(
        prompt="Research renewable energy adoption broadly (solar, wind, hydro, and others). "
               "Use the web-searcher and doc-analyst agents.",   # names them → forces delegation
        options=build_options(),
    ):
        if hasattr(msg, "result"):
            print(msg.result)

if __name__ == "__main__":
    asyncio.run(main())