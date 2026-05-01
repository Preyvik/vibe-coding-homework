---
name: new-llm-example
description: Scaffold a new leaf example folder under `1_LLM/<provider>/<topic>/` for the Vibe Coding course, matching the existing repo conventions (uv project, dotenv-loaded API key, idiomatic main.py for that provider). Use when the user says "add a new example", "scaffold a new provider/topic", or asks to start a new leaf in this curriculum. Do NOT use for anything outside the `1_LLM/` curriculum tree.
---

# new-llm-example

Scaffolds one leaf folder in the course's curriculum tree, following the conventions documented in the project's `CLAUDE.md`.

## When to invoke

Trigger on intents like:

- "Scaffold a Gemini chat-history example"
- "Add `1_LLM/3_ollama/4_tools/`"
- "Start a new basics folder for Grok"

Skip if the user is working outside `1_LLM/`, or if the target folder already exists with content (ask first before overwriting).

## What to ask the user

Before scaffolding, confirm:

1. **Provider** — one of the existing folders (`1_openai`, `2_anthropic`, `3_ollama`, `4_huggingface`, `5_gemini`, `6_grok`, `7_runpod.io`, `8_litellm`) or a new one.
2. **Topic** — numbered subfolder name (e.g. `1_basics`, `4_tools`). Same number must mean same topic across providers.
3. **Variant** — `main.py` only, or the dual `main.py` + raw-HTTP sibling pattern (typical for `1_basics`).

If any are unclear, ask one clarifying question. Don't guess provider names.

## Steps

1. Check that the target folder doesn't already exist with files. If it does, stop and ask.
2. Create `1_LLM/<provider>/<topic>/` and write:
   - `pyproject.toml` — uv-managed, Python `>=3.12`, deps: provider's official SDK + `python-dotenv`
   - `main.py` — minimal hello-world for the topic, loading the provider's env var (see table below) via `python-dotenv`
   - `.env.example` — single line with the provider's env var name, empty value
   - `README.md` — 5–10 lines: what this example shows, how to run (`uv run main.py`), required env var
3. If the user asked for the dual SDK/HTTP pattern, also write a sibling file using `requests` against the provider's REST endpoint.
4. Run `uv sync` inside the new folder to materialize the lockfile.
5. Report the created files and the run command (`cd 1_LLM/<provider>/<topic> && uv run main.py`).

## Provider env vars

| Provider     | Env var                                        |
| ------------ | ---------------------------------------------- |
| OpenAI       | `OPENAI_API_KEY`                               |
| Azure OpenAI | `AZURE_OPENAI_API_KEY` (endpoint hardcoded)    |
| Anthropic    | `ANTHROPIC_API_KEY`                            |
| Hugging Face | `HF_TOKEN`                                     |
| Gemini       | `GEMINI_API_KEY`                               |
| Grok         | `GROK_API_KEY`                                 |
| LiteLLM      | `LITELLM_API_KEY`, `LITELLM_BASE_URL`          |
| Ollama       | none (reads `http://localhost:11434`)          |

## Conventions to preserve

- **Pin model IDs** in source — don't write "latest" or pull dynamically.
- **No tests, no linter config, no build step** — `uv run` is the entire workflow.
- **Tool-use shapes differ per provider.** When scaffolding a `4_tools` folder, copy the canonical shape from that provider's existing `4_tools/main-finished.py`. Don't port from another provider.
- **`10_react_agent` stays framework-free** — explicit `while iteration < max_iterations` loop, no LangChain.

## Don'ts

- Don't add a repo-level `pyproject.toml` or workspace. Each leaf is its own uv project.
- Don't add CI, linting, or testing scaffolds. They aren't used in this repo.
- Don't include real API keys in `.env.example` — only the variable name.
- Don't write multi-paragraph README narratives. 5–10 lines is the target.
