# HW03 — Supervisor multi-agent PR review (Claude Agent SDK)

## Zadání

Třetí domácí úkol z kurzu **Vibe Coding 1**: vytvořit projekt s praktickým použitím **SDK pro kódovacího agenta**, který demonstruje libovolnou orchestraci (workflow nebo multi-agent) a má praktické použití. Deadline 14. 5. 2026, max 100 bodů, odevzdání jako odkaz na GitHub.

**Co tento projekt naplňuje z položek zadání:**
- **Kódovací agent:** Claude Code (přes oficiální `claude-agent-sdk` pro Python).
- **Orchestrace:** Multi-agent → **Supervisor** (jeden hlavní agent deleguje na 3 specializované sub-agenty a agreguje jejich výstupy).
- **Praktické použití:** **PR Review Committee** — automatizovaný code review git diffu třemi paralelními specialisty (security / performance / style).

## Řešení

Skript dostane git diff a pošle ho na **review výboru** tří specializovaných sub-agentů, kteří běží **paralelně** pod jedním supervisorem. Supervisor pak jejich nálezy agreguje do jednoho přehledného Markdown reviewu.

```
           ┌──────────────────────────────┐
           │  Supervisor (Opus 4.7)       │
           │  • čte diff                  │
           │  • dispatches 3 sub-agenty   │
           │  • agreguje findings         │
           └──────────────┬───────────────┘
                          │ Agent / Task tool (parallel)
           ┌──────────────┼──────────────┐
           ▼              ▼              ▼
     ┌──────────┐   ┌──────────┐   ┌──────────┐
     │ Security │   │   Perf   │   │  Style   │
     │ Auditor  │   │ Reviewer │   │ Checker  │
     │ (Sonnet  │   │ (Sonnet  │   │ (Sonnet  │
     │   4.6)   │   │   4.6)   │   │   4.6)   │
     └──────────┘   └──────────┘   └──────────┘
       Read/Grep      Read/Grep      Read/Grep
       (read-only)    (read-only)    (read-only)
                          │
                          ▼
                  review-output.md
                     + stdout
```

**Jak to funguje.** `main.py` načte diff (`sample.diff`, libovolný soubor, nebo `git diff --staged`), zabalí ho do user message a předá supervisorovi přes jedno volání `query()` z `claude-agent-sdk`. Supervisor má v `ClaudeAgentOptions` programmatic registraci tří `AgentDefinition` instancí — žádné externí `.claude/agents/*.md` soubory. Paralelizaci si supervisor řídí sám: instrukce v system promptu mu říká, ať všechny tři sub-agenty dispatchne v jednom batchi a počká na všechny.

**Specializace sub-agentů.** Každý má vlastní system prompt zaměřený na jeden druh problémů (bezpečnost / výkon / styl), aby supervisor dostal nezávislé pohledy. Všichni vrací zprávy ve **stejném Markdown formátu** (`severity` → `file` → `line` → `issue` → `suggestion`), takže supervisor je jen poslepuje pod sekce a doplní summary + top priorities. Žádný JSON parsing.

**Sandbox.** Supervisor má `allowed_tools=["Agent", "Task", "Read", "Grep", "Glob"]` (žádné `Edit`/`Write`/`Bash`). Sub-agenti dostávají jen `["Read", "Grep", "Glob"]`. Review je z principu read-only — agenti diff jen analyzují, neopravují.

## Spuštění

```bash
cp .env.example .env          # doplň ANTHROPIC_API_KEY
uv sync                       # nainstaluje claude-agent-sdk + python-dotenv
uv run main.py                # default: sample.diff v této složce
uv run main.py path/to.diff   # vlastní diff soubor
uv run main.py --staged       # `git diff --staged` z aktuálního repa
```

## Ověření

```text
$ uv run main.py
Spouštím PR Review Committee (3 sub-agenti paralelně)...

# PR Review

## Summary
- Total findings: 5 (Critical: 2, High: 2, Medium: 1)
- Verdict: REQUEST CHANGES — two critical security issues block merge.

## Security (security-auditor)
### [CRITICAL] SQL injection in get_user
- **File:** `app/users.py`
- **Line:** 7
- **Issue:** Query is built via string concatenation with user_id.
- **Suggestion:** Restore parameterized form `("SELECT ... WHERE id = ?", (user_id,))`.

### [CRITICAL] Hardcoded API key
- **File:** `app/users.py`
- **Line:** 5
- **Issue:** Production API key committed in source.
- **Suggestion:** Load from environment variable; rotate the leaked key.

## Performance (performance-reviewer)
### [HIGH] Blocking time.sleep in async function
...

## Style (style-checker)
### [MEDIUM] PascalCase function name and dead code in ProcessData
...

## Top Priorities
- [CRITICAL] SQL injection in get_user
- [CRITICAL] Hardcoded API key
- [HIGH] Blocking time.sleep in async function

---
Výstup uložen do: review-output.md
```

Reálný výstup z posledního běhu je v souboru [`review-output.md`](review-output.md) — vyučující ho vidí přímo v repu, není nutné spouštět.

## Klíčová API z Claude Agent SDK

- `query(prompt, options)` — async generator, jednorázová supervisor session.
- `ClaudeAgentOptions(system_prompt, model, agents, allowed_tools, permission_mode)` — kompletní config.
- `AgentDefinition(description, prompt, tools, model)` — programmatic sub-agent: vlastní system prompt + tool sandbox + per-agent model.
- `agents={"name": AgentDefinition(...)}` — registrace v paměti, žádné `.md` soubory.
- `allowed_tools=["Agent", ...]` — supervisor smí delegovat přes `Agent` (resp. `Task`) tool.

## Vyzkoušet vlastní diff

V libovolném git repu si naprepuj pár změn (`git add -p`) a zavolej:

```bash
cd C:\Users\XXX\Claude\vibe-coding-homework\hw03-pr-review-committee
uv run main.py --staged
```

Skript načte `git diff --staged` z **aktuálního** pracovního adresáře (nikoli z této hw03 složky), takže nejdřív se přepni do toho repa, ze kterého chceš review:

```bash
cd /path/to/your/repo
uv run --project C:\Users\XXX\Claude\vibe-coding-homework\hw03-pr-review-committee main.py --staged
```
