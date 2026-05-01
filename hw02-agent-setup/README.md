# HW02 — Nastavení kódovacího agenta

## Zadání

Nasdílet nastavení kódovacího agenta s využitím **MCP Serverů, Skills a Subagentů**. **NEPOUŽÍVAT plugins ani marketplace.** Kódovací agenti pokryti kurzem: **Codex** (OpenAI) a **Claude Code** (Anthropic).

## Který agent je primární

**Claude Code je můj hlavní pracovní agent — všechny custom Skills, Subagents a MCP servery jsem dělal pro něj.** Codex je v repu doložený pro úplnost (kurz oba zmiňuje), s minimální zrcadlovou konfigurací; aktivně ho nepoužívám. Pokud čtete jen jednu sekci, čtěte tu o Claude Code.

## Co je v této složce

```
hw02-agent-setup/
├── claude/
│   ├── settings.json          ← globální nastavení (~/.claude/settings.json)
│   ├── settings.local.json    ← per-projekt permissions (~/.claude/settings.local.json)
│   ├── mcp-servers.json       ← výřez mcpServers z ~/.claude.json (sanitizováno)
│   ├── agents/
│   │   └── llm-example-finder.md   ← vlastní subagent
│   └── skills/
│       └── new-llm-example/
│           └── SKILL.md            ← vlastní skill
└── codex/
    ├── config.toml            ← ~/.codex/config.toml (model, sandbox, MCP)
    └── AGENTS.md              ← ~/.codex/AGENTS.md (globální system prompt)
```

Žádné soubory z `plugins/` ani z `marketplaces/` — zadání je výslovně zakazuje. Vše je ručně psané.

## 1. Claude Code

### `claude/settings.json`

Globální nastavení v `~/.claude/settings.json`:

- `permissions.defaultMode = "auto"` — Claude pracuje v auto módu, neptá se před každou akcí.
- `effortLevel = "xhigh"` — maximální reasoning effort.
- `voice.enabled = true`, `voice.mode = "hold"` — hlasové ovládání podržením klávesy.
- `agentPushNotifEnabled = true` — push notifikace, když subagent doběhne.
- `skipAutoPermissionPrompt = true` — vypne přepínací prompt mezi módy při startu.
- `remoteControlAtStartup = true` — povolí ovládání z mobilní/web aplikace.

### `claude/settings.local.json`

Lokální allowlist příkazů, které Claude může volat bez doptávání:

```json
{
  "permissions": {
    "allow": [
      "Bash(export PATH=\"/c/Program Files/nodejs:$PATH\")",
      "Bash(npm install:*)",
      "Bash(git:*)"
    ]
  }
}
```

### `claude/mcp-servers.json` — MCP Servery

Výřez ze sekce `mcpServers` v `~/.claude.json`. Aktivní servery:

| Server                  | Typ    | K čemu                                                                  |
| ----------------------- | ------ | ----------------------------------------------------------------------- |
| `everything`            | stdio  | Referenční MCP server od autorů protokolu ([modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers/tree/main/src/everything)). Bundluje ukázkové tools, prompts a resources — slouží jako veřejně reprodukovatelná demo-konfigurace MCP. Bez API klíče, spouští se přes `npx -y @modelcontextprotocol/server-everything`. |
| `claude.ai Google Drive`| HTTP   | Spravovaný Anthropicem (OAuth flow přes claude.ai). Read/write/search vlastního Drive obsahu. |

Žádné API klíče v repu — `everything` je veřejný balíček, Google Drive používá OAuth spravovaný v účtu (token nikdy neopouští `claude.ai`).

### `claude/agents/llm-example-finder.md` — Subagent

Vlastní research subagent, který se hodí k tomuto kurzu. Spouští se buď automaticky (Claude ho vybere podle `description`), nebo ručně přes `Agent({ subagent_type: "llm-example-finder", … })`.

**Use case:** *"Jak Anthropic dělá tool-use oproti OpenAI?"* Subagent prosurfuje strukturu `1_LLM/<provider>/N_topic/`, načte odpovídající `main*.py`, a vrátí stručný diff API shapes (endpoint, request body, content blocks). Read-only — nic needituje. Běží na `sonnet` přes `Glob`, `Grep`, `Read`.

**Proč subagent a ne hlavní vlákno:** odděluje research od implementace. Hlavní vlákno se nezahltí dlouhými výpisy souborů, dostane jen shrnutí.

### `claude/skills/new-llm-example/SKILL.md` — Skill

Vlastní skill `/new-llm-example`, který škáloví novou listovou složku v kurikulu `1_LLM/<provider>/<topic>/` podle konvencí z hlavního `CLAUDE.md` kurzu (uv projekt, `.env.example`, idiomatický `main.py` pro daného providera, mini-README).

**Vyvolání:** `/new-llm-example` nebo přirozeným jazykem (*"přidej nový základní příklad pro Grok"*) — Claude skill rozpozná podle `description`.

**Co dělá:**
1. Doptá se na **provider** + **topic** + variantu (jen `main.py`, nebo dual SDK + raw-HTTP).
2. Vytvoří `pyproject.toml`, `main.py`, `.env.example`, `README.md` v cílové složce.
3. Spustí `uv sync`.
4. Reportne run command.

**Proč skill a ne ad-hoc:** kurz má pevné konvence (čísla = topicy napříč providery, pinované model ID, dual SDK/HTTP varianta v `1_basics`). Skill je drží v kódu, takže se nemusí pokaždé připomínat.

## 2. Codex CLI

Codex se instaluje globálně přes npm:

```bash
npm install -g @openai/codex
codex --version          # → codex-cli 0.128.0
codex login              # přihlášení přes prohlížeč (ChatGPT účet)
```

### `codex/config.toml`

`~/.codex/config.toml`. Klíčové volby:

- `model = "gpt-5-codex"` — výchozí model.
- `approval_policy = "on-failure"` — Codex se ptá až když příkaz selže (kompromis mezi `untrusted` a `never`).
- `sandbox_mode = "workspace-write"` — může editovat workspace, ale bez síťových volání.
- `[shell_environment_policy] inherit = "all"` — dědí PATH a env z rodičovského shellu (nutné pro uv, node, atd.).
- `[mcp_servers.everything]` — **stejný** demo MCP server jako v Claude Code, takže oba agenti sdílejí jednu MCP konfiguraci. Spouští se přes `npx`, žádný klíč.

### `codex/AGENTS.md`

`~/.codex/AGENTS.md` je globální system prompt — analogie `CLAUDE.md`, ale pro Codex. Pokrývá:

- Working style (stručnost, žádné spekulativní abstrakce, žádné komentáře typu "co kód dělá").
- Safety pravidla (nikdy `git reset --hard` / `--force` bez potvrzení, nikdy neskákat hooks).
- Stack defaults pro tento stroj (uv pro Python, PowerShell + Git Bash, npm globals v `%APPDATA%\npm`).
- Pravidla specifická pro `1_LLM/` kurikulum (čísla = topicy, tool-use shapes se neportují mechanicky).

## Jak to nainstalovat na čistém stroji

```powershell
# Claude Code
copy hw02-agent-setup\claude\settings.json        $env:USERPROFILE\.claude\settings.json
copy hw02-agent-setup\claude\settings.local.json  $env:USERPROFILE\.claude\settings.local.json

mkdir $env:USERPROFILE\.claude\agents -Force
copy hw02-agent-setup\claude\agents\*.md          $env:USERPROFILE\.claude\agents\

mkdir $env:USERPROFILE\.claude\skills\new-llm-example -Force
copy hw02-agent-setup\claude\skills\new-llm-example\SKILL.md `
     $env:USERPROFILE\.claude\skills\new-llm-example\SKILL.md

# MCP servery: zkopíruj sekci `mcpServers` z mcp-servers.json do ~/.claude.json
# (claude.ai Google Drive se přidá z UI, ne ze souboru)

# Codex
npm install -g @openai/codex
mkdir $env:USERPROFILE\.codex -Force
copy hw02-agent-setup\codex\config.toml  $env:USERPROFILE\.codex\config.toml
copy hw02-agent-setup\codex\AGENTS.md    $env:USERPROFILE\.codex\AGENTS.md

# Auth (Claude i Codex používají vlastní OAuth flow, ne raw API klíč)
codex login    # otevře prohlížeč, přihlaš se přes ChatGPT účet
claude         # Claude Code si OAuth pamatuje; pokud ne, `claude /login`
```

## Ověření

```bash
# Claude vidí subagent (uvnitř Claude session)
/agents
# → měl by vypsat llm-example-finder

# Claude vidí skill
/
# → seznam slash commandů by měl obsahovat /new-llm-example

# Claude vidí MCP server (z terminálu)
claude mcp list
# → everything: ✓ Connected
# → claude.ai Google Drive: ✓ Connected

# Codex vidí MCP server
codex mcp list
# → everything    enabled

# Codex základní run
codex "list the providers in 1_LLM/"
```
