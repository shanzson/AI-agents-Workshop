# Guardrail Agent with Tool Calling and Memory using LangGraph

This notebook demonstrates a LangGraph chatbot that screens both user input and model output with NVIDIA NeMo Guardrails, can call tools, and remembers conversation state across interactions using `MemorySaver`.

## Notebook contents

- **Guardrails configuration:** Loads a NeMo Guardrails config from the local `./config` folder using `RailsConfig` and `LLMRails`.
- **State definition:** Stores the conversation messages and a `blocked` flag that records whether a guardrail refused the request.
- **Model setup:** Initializes the chat model (`gemini-flash-lite-latest`, temperature 0).
- **Tool setup:** Adds a custom `multiply` function and binds it to the language model.
- **Input guardrail:** The `input_guard` node checks the latest user message. If the guardrail refuses it, the refusal is added to the conversation and the graph ends.
- **Tool-calling LLM node:** The `tool_calling_llm` node calls the model with the conversation so far and lets it request tools.
- **Output guardrail:** The `output_guard` node checks the model's final reply before it is returned. If the guardrail refuses it, the refusal message is added to the conversation.
- **Routing:** Conditional edges send blocked requests to `END`, tool calls to the `tools` node, and final answers to the output guardrail.
- **Memory setup:** Creates a `MemorySaver` checkpointer to save graph state for each conversation thread.
- **Thread configuration:** Uses a `thread_id` to continue the same conversation and retrieve its saved state.
- **Testing:** Runs a two-turn conversation (introducing a name, then asking the agent to recall it) to demonstrate memory.

## Workflow

```text
                  ┌───────────────────────┐
                  │         START         │
                  └───────────┬───────────┘
                              ↓
                  ┌───────────────────────┐
                  │      input_guard      │
                  └───────────┬───────────┘
                              ↓
                       Blocked by rails?
                         /          \
                       Yes           No
                        ↓             ↓
                  ┌─────────┐   ┌───────────────────────┐
                  │   END   │   │    tool_calling_llm   │◀──────┐
                  └─────────┘   └───────────┬───────────┘       │
                                            ↓                   │
                                   Tool call requested?         │
                                      /          \              │
                                    Yes           No            │
                                     ↓             ↓            │
                              ┌───────────┐  ┌──────────────┐   │
                              │   Tools   │  │ output_guard │   │
                              └─────┬─────┘  └──────┬───────┘   │
                                    │               ↓           │
                                    └──────────▶ ┌─────┐        │
                                     (results)   │ END │        │
                                                 └─────┘        │
                                    └───────────────────────────┘

                  MemorySaver
          ┌───────────────────────────────┐
          │ Saves/restores graph state    │
          │ for the configured thread_id  │
          └───────────────────────────────┘
```

Tool results always return to `tool_calling_llm`, so the model can use them to write its final answer, which then passes through `output_guard`.

## How the guardrails work

Both guard nodes send the message to `rails.generate_async(...)` and look at the response. If the response contains the phrase `can't respond`, the message is treated as refused: the refusal text is added to the conversation and `blocked` is set to `True`. Otherwise `blocked` is set to `False` and the graph continues.

The refusal check is a simple string match. If your NeMo configuration uses a different refusal message, update the check in both `input_guard` and `output_guard`.

## How memory works

`MemorySaver` is connected to the compiled graph as a checkpointer. When the notebook invokes the graph with a `thread_id`, LangGraph saves the conversation state for that thread and can restore it on later calls using the same ID. Use a different `thread_id` to keep another conversation separate.

This is in-memory checkpointing: the saved state is available while the running process retains it, but it is not permanent storage across process restarts.

