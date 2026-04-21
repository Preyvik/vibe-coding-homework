# HW01 — Python skript pro LLM API s tool-use

## Zadání
Napsat Python skript, který:
1. Zavolá LLM API
2. Použije nástroj (např. výpočetní funkci)
3. A vrátí odpověď zpět LLM

## Řešení

Soubor [`main.py`](main.py) implementuje kompletní tool-use loop s Anthropic Claude API:

1. **Volá Claude** (`claude-sonnet-4-5`) s definicí nástroje `calculate` — lokální výpočetní funkce, která bezpečně vyhodnotí aritmetický výraz v omezeném namespace (povolené operátory `+ - * / % ( )`, funkce `sqrt`, konstanty `pi`, `e`).
2. **Claude si vyžádá tool call** — na dotaz *"What is 127 * 349 + 2024?"* vrátí `ToolUseBlock(name='calculate', input={'expression': '127 * 349 + 2024'})`.
3. **Skript funkci lokálně spustí** — `calculate("127 * 349 + 2024")` → `{"expression": "127 * 349 + 2024", "result": 46347}`.
4. **Výsledek se pošle zpět Claudovi** jako `tool_result` blok.
5. **Claude vrátí finální textovou odpověď**: *"The result of 127 * 349 + 2024 is **46,347**."*

Tím je splněn kompletní cyklus **user → LLM → tool call → tool result → LLM → final answer**.

## Spuštění

Potřebuješ [uv](https://docs.astral.sh/uv/) a Python 3.12+.

```bash
cp .env.example .env          # doplň ANTHROPIC_API_KEY z console.anthropic.com
uv run main.py
```

## Ověřený výstup

```
First response: Message(... ToolUseBlock(id='toolu_...', input={'expression': '127 * 349 + 2024'}, name='calculate', type='tool_use', ...) ...)
--- Full response: ---
Message(... TextBlock(text='The result of 127 * 349 + 2024 is **46,347**.', type='text') ...)
--- Response text: ---
The result of 127 * 349 + 2024 is **46,347**.
```

## Vyzkoušet vlastní dotaz

V `main.py` dole najdi:
```python
messages = [
    {"role": "user", "content": "What is 127 * 349 + 2024?"},
]
```
a nahraď text čímkoliv — např. `"Calculate 15% of 8400"` nebo `"What is sqrt(2) + pi * 3?"`. Claude si sám odvodí správný výraz pro nástroj.
