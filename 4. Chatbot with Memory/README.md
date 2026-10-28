# Chatbot/Agent with Memory using LangGraph

This notebook demonstrates a LangGraph chatbot that can call tools and remember conversation state across interactions using `MemorySaver`.

## Notebook contents

- **State definition:** Stores the conversation messages.
- **Model setup:** Initializes the chat model.
- **Tool setup:** Adds Tavily Search for web searches and a custom `multiply` function.
- **Tool binding:** Makes the tools available to the language model.
- **Memory setup:** Creates a `MemorySaver` checkpointer to save graph state for each conversation thread.
- **Graph construction:** Connects the `tool_calling_llm` and `tools` nodes so tool results return to the model.
- **Thread configuration:** Uses a `thread_id` to continue the same conversation and retrieve its saved state.
- **Testing:** Runs example interactions to demonstrate tool use and recall of earlier conversation details.

## Workflow

```text
                  ┌───────────────────────┐
                  │         START         │
                  └───────────┬───────────┘
                              ↓
                  ┌───────────────────────┐
          ┌──────▶│    tool_calling_llm   │◀─────────┐
          │       └───────────┬───────────┘          │
          │                   ↓                      │
          │          Tool call requested?            │
          │              /          \                │
          │            Yes           No               │
          │             ↓             ↓               │
          │       ┌───────────┐   ┌─────────┐         │
          └───────│   Tools   │   │   END   │         │
                  └───────────┘   └─────────┘         │
                                                      │
                  MemorySaver                         │
          ┌───────────────────────────────┐           │
          │ Saves/restores graph state    │───────────┘
          │ for the configured thread_id  │
          └───────────────────────────────┘
```

`MemorySaver` is connected to the compiled graph as a checkpointer. When the notebook invokes the graph with a `thread_id`, LangGraph saves the conversation state for that thread and can restore it on later calls using the same ID. Use a different `thread_id` to keep another conversation separate.

This is in-memory checkpointing: the saved state is available while the running process retains it, but it is not permanent storage across process restarts.
