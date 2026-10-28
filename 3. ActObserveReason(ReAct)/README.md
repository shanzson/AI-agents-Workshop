# ReAct Agent using LangGraph

This notebook demonstrates a simple ReAct-style agent built with LangGraph and a Google Gemini chat model. The agent can respond directly or call tools when they are useful.

## Notebook contents

- **State definition:** Creates a graph state that stores conversation messages.
- **Model setup:** Initializes the `gemini-flash-lite-latest` chat model with a temperature of `0.0`.
- **Tool setup:** Adds a Tavily Search tool for web searches and a custom `multiply` function for multiplication.
- **Tool binding:** Binds the tools to the language model so it can request tool calls.
- **Graph construction:** Creates a `tool_calling_llm` node and a `tools` node, with conditional routing to run tools when requested.
- **Testing:** Sends a question involving multiplication and a recent FIFA match, then prints the messages returned by the graph.

## Workflow

```text
START → tool_calling_llm
             ↓
       Tool requested?
        ↙         ↘
      Tools       END
        ↓
 tool_calling_llm
```

The model can use a tool, observe its result, and continue generating a response. If no tool is requested, the graph ends with the model's response.