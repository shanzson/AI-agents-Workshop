# Chatbot with Tools using LangGraph

This notebook demonstrates how to build a chatbot that can use tools with LangGraph and a Google Gemini chat model.

## Notebook contents

- **State setup:** Defines a graph state that stores conversation messages.
- **Model initialization:** Configures the `gemini-flash-lite-latest` chat model with a temperature of `0.0`.
- **Tool creation:** Sets up a Tavily Search tool for web searches and a custom `multiply` function for multiplication.
- **Tool binding:** Connects the available tools to the language model so it can request their use when needed.
- **Graph construction:** Creates a `tool_calling_llm` node and a `tools` node, then connects them using conditional routing.
- **Testing:** Runs example questions, including a web-search question and a multiplication question, and displays the conversation messages.

## Workflow

```text
START → tool_calling_llm
             ↓
       Tool requested?
        ↙         ↘
      Tools       END
        ↓
       END
```

The model decides whether a tool is needed. When it requests a tool, LangGraph runs the tool through the `ToolNode`; otherwise, the workflow ends with the model's response.