# Important Note

These are not the final python notebooks that we were going to use and any change or any suggestion for change in them will be gladly welcomed.

# Structure

## This repository cotains 5 types of architectures/agents each just building on their previous one

1st: Basic Chatbot
2nd: Chatbot with tool
3rd: ReAct agent architecture
4th: Agent with volatile memory
5th: Agent with Guardrails

## Each folder contains the python notebook as well as a readme on the architecture/agent/bot

## These bots/agents use Google's Gemini API (model `gemini-flash-lite-latest`), which has a free tier.

They were originally written for OpenAI's `gpt-4.1-mini`. To switch a notebook back, replace `ChatGoogleGenerativeAI` with `ChatOpenAI` from `langchain_openai`.


# Quick start

**You need Python 3.10–3.13.** Python 3.14 and newer will not work, because `nemoguardrails` does not support them yet.
Check your version with `python3 --version`. If it is 3.14 or newer, install 3.13 first (macOS: `brew install python@3.13`, Windows: the python.org installer).

macOS / Linux:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
jupyter lab
```

Windows (PowerShell):

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
jupyter lab
```

Before running `jupyter lab`, open `.env` and paste in your two keys. Never commit `.env`.

- `GOOGLE_API_KEY`: free from https://aistudio.google.com (**Get API key**).
- `TAVILY_API_KEY`: free from https://app.tavily.com.

The free Gemini tier has rate limits. If a cell fails with `429` or `RESOURCE_EXHAUSTED`, wait a minute and run it again.
If the model name stops working, change `gemini-flash-lite-latest` in the notebooks and in `5. Agent with Guardrails/config/config.yml` to a current model from https://ai.google.dev/gemini-api/docs/models.

If you already created `.venv` with the wrong Python version, delete it (`rm -rf .venv`) and start again from the first command.

Work through the folders in order, 1 to 5. Each agent adds one idea to the previous one.

`instructor-demos/` holds the instructor's showcase (RAG and MCP) and `preflight.py`, an environment check.
Attendees don't need it.
