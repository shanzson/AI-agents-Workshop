# Basic Chatbot with LangGraph

This notebook demonstrates a simple chatbot workflow built with
LangGraph and a Google Gemini chat model.

## Notebook contents

-   **Imports and setup:** Loads the libraries and environment variables
    used by the notebook.
-   **Model initialization:** Creates a chat model that generates
    responses to user messages.
-   **State definition:** Defines a graph state that stores the
    conversation messages.
-   **Chatbot function:** Passes the messages to the language model and
    returns its response.
-   **Graph construction:** Connects the chatbot node between the start
    and end of the LangGraph workflow.
-   **Testing:** Runs example prompts through the graph and displays the
    chatbot's responses.

## Workflow

``` text
START → Chatbot → END
```

The notebook illustrates the basic structure of a LangGraph chatbot. It
uses a single chatbot node and does not add tool calling, guardrails, or
persistent memory.
