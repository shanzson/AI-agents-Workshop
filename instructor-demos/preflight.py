"""Workshop preflight check. Run this the day before AND 15 minutes before the session.

    python preflight.py          # offline checks only (Python, packages, keys present, files)
    python preflight.py --live   # also makes ONE tiny OpenAI call and ONE Tavily call

Security: this script never prints your keys. It only reports whether each key is set
and shows the first 3 characters so you can tell a project key from a personal one.
"""
import argparse
import importlib
import os
import sys
from pathlib import Path

OK, BAD, WARN = "[ OK ]", "[FAIL]", "[WARN]"
failures = 0


def report(ok, msg, warn=False):
    global failures
    tag = OK if ok else (WARN if warn else BAD)
    if not ok and not warn:
        failures += 1
    print(f"{tag} {msg}")


def mask(value: str) -> str:
    return f"{value[:7]}… ({len(value)} chars)" if value else "missing"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="make one real OpenAI + Tavily call")
    args = ap.parse_args()

    v = sys.version_info
    report((3, 10) <= (v.major, v.minor) <= (3, 13), f"Python {v.major}.{v.minor} (3.10–3.13 tested)")
    report(sys.prefix != sys.base_prefix, "running inside a virtual environment", warn=True)

    for mod in ["langchain", "langchain_core", "langchain_openai", "langchain_tavily", "langgraph",
                "dotenv", "nemoguardrails", "langchain_mcp_adapters", "mcp"]:
        try:
            m = importlib.import_module(mod)
            report(True, f"import {mod} {getattr(m, '__version__', '')}".rstrip())
        except Exception as e:  # noqa: BLE001 - we want every failure listed
            report(False, f"import {mod}: {type(e).__name__}: {e}")

    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    for key in ["OPENAI_API_KEY", "TAVILY_API_KEY"]:
        val = os.environ.get(key, "")
        report(bool(val), f"{key}: {mask(val)}")

    env_file = Path(".env")
    if env_file.exists() and Path(".gitignore").exists():
        report(".env" in Path(".gitignore").read_text(encoding="utf-8", errors="ignore"),
               ".env is listed in .gitignore")

    cfg = Path("..") / "5. Agent with Guardrails" / "config" / "prompts.yml"
    if cfg.exists():
        report(cfg.stat().st_size > 0, f"{cfg} is not empty (NeMo will not load otherwise)")

    if args.live and failures == 0:
        try:
            from langchain_openai import ChatOpenAI
            r = ChatOpenAI(model="gpt-4.1-mini", temperature=0, max_tokens=5).invoke("Reply with: ok")
            report(True, f"OpenAI live call answered: {r.content!r}")
        except Exception as e:  # noqa: BLE001
            report(False, f"OpenAI live call: {type(e).__name__}: {str(e)[:120]}")
        try:
            from langchain_tavily import TavilySearch
            r = TavilySearch(max_results=1).invoke("LangGraph")
            report(bool(r.get("results")), "Tavily live call returned a result")
        except Exception as e:  # noqa: BLE001
            report(False, f"Tavily live call: {type(e).__name__}: {str(e)[:120]}")

    print("\nAll good." if failures == 0 else f"\n{failures} problem(s) to fix before the session.")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
