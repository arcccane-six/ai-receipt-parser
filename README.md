# AI Receipt Parser

Turn free-form receipt text into structured, validated JSON and store it in Postgres — fully automated.

Input: `"kopi susu 2 gelas 10rb, es teh 1 5rb, total 25rb, bayar qris"`
Output: structured items, computed total, arithmetic validity flag, persisted row.

## The problem

Small F&B businesses record sales as free text — WhatsApp messages, handwritten notes, photos of receipts. That data can't be summed, reported on, or audited. Manual entry doesn't scale past a few dozen transactions a day.

## How it works

```
POST /webhook/AI-PARSER  {"teks": "..."}
        |
        v
[Webhook]           receive raw text
        |
        v
[HTTP Request]      Groq LLM -> structured JSON (items, qty, price, payment)
        |
        v
[Code node]         compute total, flag arithmetic mismatch
        |
        v
[Supabase]          persist: raw text + parsed data + validity
        |
        v
[Respond]           return the stored record
```

## Design decisions

**The LLM extracts; code decides.**
- Language understanding (messy text -> structured fields) is the LLM's job.
- Arithmetic is not. Totals and consistency checks live in code — LLMs are unreliable at math.
- The prompt explicitly permits `null` and instructs the model never to guess. Missing data is reported as missing, not invented.
- The raw text is always persisted alongside the parse (`teks_asli`) as an audit trail, so any extraction can be re-verified against the source.

**Provider-agnostic LLM client.** `llm_parse.py` talks to any OpenAI-compatible endpoint; swapping provider is a `.env` change (base URL + model + key), not a code change.

## Stack

- **n8n** (self-hosted on a VPS) — orchestration
- **Groq** — fast, low-cost inference, OpenAI-compatible API
- **Supabase / Postgres** — storage
- **Python + requests** — provider-agnostic client and test harness

## Validation

Arithmetic is verified, not assumed. `valid` is three-state:

- `true` — stated total matches the sum of line items
- `false` — mismatch detected (corrupted or mistranscribed total)
- `null` — no total stated in the source text

## Test matrix

`test_parser.py` runs 4 cases against the live webhook and writes `results.json`:

1. Complete receipt with prices and total — expect full parse, `valid: true`
2. Missing total — expect `valid: null`, no invented numbers
3. Garbage input — expect empty items, no hallucination
4. Multiple line items with a stated total — expect correct arithmetic check

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in your keys
python llm_parse.py    # direct LLM call, no n8n needed
```

To run the full pipeline, import `workflow.json` into your n8n instance and re-attach your own credentials (Groq + Supabase), then set `WEBHOOK_URL` in `.env` to your webhook endpoint and run `python test_parser.py`.

## Repo contents

- `workflow.json` — n8n workflow export (importable)
- `llm_parse.py` — provider-agnostic LLM client, works without n8n
- `test_parser.py` — test harness against the live webhook
- `results.json` — last test run output
- `.env.example` — required configuration

## What I'd add next

- Auth on the webhook (currently open; a signature check or API key)
- n8n error workflow with retry + alerting
- Per-tenant configuration and cost guard on LLM calls
- OCR front-end for photographed receipts