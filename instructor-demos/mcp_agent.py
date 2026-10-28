"""The ReAct agent from notebook 3, but its tools come from an MCP server instead of Python functions.

    python mcp_agent.py
    python mcp_agent.py --question "Read the pilot feedback note and count its words."
    python mcp_agent.py --evil        # server adds a tool with a poisoned description
    python mcp_agent.py --offline     # rehearsal: fake LLM, real MCP server, no API key

What to point out:
  1. The agent code does not know any tool in advance: it asks the server (tools/list).
  2. Each tool arrives as name + description + JSON schema: exactly what bind_tools() needs.
  3. The graph is identical to notebook 3. MCP changes where tools come from, not how agents work.
"""
import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Annotated, TypedDict

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

SERVER = Path(__file__).with_name("mcp_server.py").resolve()


class State(TypedDict):
    messages: Annotated[list, add_messages]


def make_llm(offline: bool):
    if not offline:
        from dotenv import load_dotenv
        from langchain_openai import ChatOpenAI
        load_dotenv()
        return ChatOpenAI(model="gpt-4.1-mini", temperature=0)

    from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
    from langchain_core.messages import AIMessage

    class Fake(GenericFakeChatModel):
        def bind_tools(self, tools, **kwargs):
            return self

    script = iter([
        AIMessage(content="", tool_calls=[{"name": "list_notes", "args": {}, "id": "t1"}]),
        AIMessage(content="", tool_calls=[{"name": "read_note", "args": {"name": "agenda.md"}, "id": "t2"}]),
        AIMessage(content="", tool_calls=[{"name": "read_note", "args": {"name": "../../.env"}, "id": "t3"}]),
        AIMessage(content="(offline rehearsal) The agenda has 7 items; the path-traversal attempt was refused."),
    ])
    return Fake(messages=script)


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--question", default="What notes do you have? Summarise the agenda in one line.")
    ap.add_argument("--evil", action="store_true")
    ap.add_argument("--offline", action="store_true")
    args = ap.parse_args()

    server_env = {"WORKSHOP_EVIL": "1"} if args.evil else {}
    # Pass PATH so the subprocess can start; deliberately NOT passing os.environ (keeps API keys out).
    server_env["PATH"] = os.environ.get("PATH", "")
    if os.name == "nt":
        server_env["SYSTEMROOT"] = os.environ.get("SYSTEMROOT", "")

    client = MultiServerMCPClient({
        "notes": {"transport": "stdio", "command": sys.executable, "args": [str(SERVER)], "env": server_env},
    })

    print("=== 1. DISCOVER: tools/list from the MCP server ===")
    tools = await client.get_tools()
    for t in tools:
        schema = t.args_schema if isinstance(t.args_schema, dict) else t.args_schema.model_json_schema()
        print(f"- {t.name}: {t.description.strip()}")
        print(f"    input schema: {json.dumps(schema.get('properties', {}))}")

    llm_with_tools = make_llm(args.offline).bind_tools(tools)

    def tool_calling_llm(state: State):
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    builder = StateGraph(State)
    builder.add_node("tool_calling_llm", tool_calling_llm)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "tool_calling_llm")
    builder.add_conditional_edges("tool_calling_llm", tools_condition)
    builder.add_edge("tools", "tool_calling_llm")
    graph = builder.compile()

    print("\n=== 2. RUN: same ReAct loop as notebook 3 ===")
    result = await graph.ainvoke({"messages": [("user", args.question)]}, {"recursion_limit": 12})
    for m in result["messages"]:
        m.pretty_print()


if __name__ == "__main__":
    asyncio.run(main())
