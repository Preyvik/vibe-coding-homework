# Global AGENTS.md

Default instructions Codex applies to every session unless a project-level `AGENTS.md` overrides.

## Working style

- Be concise. Default to minimal explanation; the user reads the diff.
- Prefer editing existing files over creating new ones.
- Don't write speculative abstractions. Three similar lines beats a premature helper.
- Don't add comments that restate what the code does. Only comment non-obvious "why".

## Safety

- Never run destructive git commands (`reset --hard`, `push --force`, branch deletes) without explicit confirmation.
- Never bypass hooks (`--no-verify`) or signing (`--no-gpg-sign`) unless the user asks.
- Don't commit `.env` or anything that smells like a secret. If the user requests it, warn first.

## Stack defaults on this machine

- Python projects use **uv** (`uv run`, `uv sync`). Each leaf folder under `1_LLM/` is its own uv project — there is no repo-level workspace.
- Node is available via `nvm-windows` / global PATH. npm packages installed globally land in `%APPDATA%\npm`.
- Shell is **PowerShell** on Windows; bash via Git Bash is also installed. POSIX-only commands (`grep`, `cat`, `find`) work in bash but not in PowerShell — use the right one for the right shell.

## When the user asks about LLM provider examples

The course repo at `C:/Users/tados/Claude/vibe-coding-course` follows a strict convention: providers are top-level under `1_LLM/<provider>/`, and the **same numbered subfolder means the same topic across providers** (`1_basics`, `2_multimodal`, `3_chat_history`, `4_tools`, `10_react_agent`). When porting behavior between providers, find the matching number rather than guessing. Tool-use message shapes differ per provider — consult the existing `4_tools/main-finished.py` for the canonical shape.
