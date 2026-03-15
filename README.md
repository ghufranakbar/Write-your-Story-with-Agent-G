# Life as Lore 📖

> Every life is an epic. Yours begins here.

A personal mythology engine. You narrate your life in plain language. AI agents transform it into an ongoing fantasy novel — with characters, quests, and prophecies that compound in meaning over months and years.

---

## What it does

| Page | What you get |
|---|---|
| 📜 **Narrate** | Write or paste what's happening in your life. Agents write a fantasy chapter from it. |
| 📖 **Chronicle** | Your life, rendered as a growing fantasy novel. |
| 🧙 **Characters** | Every person in your life becomes a named fantasy archetype. |
| ⚔️ **Quests** | Your goals and struggles, tracked as epic quests. |
| 🔮 **Prophecy** | After 3+ entries, the oracle reads your arc and writes a prophecy. |

---

## Stack (100% free)

- **Streamlit Community Cloud** — hosting
- **Supabase** — free Postgres (500MB, plenty for years of entries)
- **Anthropic API** — Claude Sonnet (pay per use, ~$0.01 per narration)

---

## Setup (15 minutes)

### 1. Supabase

1. Create a free project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** and run the contents of `schema.sql`
3. Copy your **Project URL** and **anon/public API key** from Settings → API

### 2. Local development

```bash
git clone <your-repo>
cd life-as-lore
pip install -r requirements.txt

# Create secrets file
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Fill in your keys in secrets.toml

streamlit run app.py
```

### 3. Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app
3. Point it at your repo + `app.py`
4. In **Advanced settings → Secrets**, paste:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key"
```

5. Deploy. That's it.

---

## Why the app sleeping doesn't matter

All state lives in Supabase. When Streamlit wakes from sleep, it reconnects to Supabase and your entire chronicle — every chapter, character, quest, and prophecy — is exactly where you left it.

---

## Cost estimate

A single narration (one entry → one chapter) uses ~1,500 tokens in + ~1,000 tokens out with Claude Sonnet.

At current Sonnet pricing: **roughly $0.01–0.02 per entry**. 

If you write 3 entries a week for a year: ~$3–4 total.

---

## Extending it

**Ideas for v2:**
- Add a `moods` chart showing your emotional arc over time (matplotlib in Streamlit)
- Voice input via `st.audio_input` (Streamlit 1.37+)
- Weekly digest email (Supabase edge functions + resend.com free tier)
- Export your full chronicle as a PDF

---

## File structure

```
life-as-lore/
├── app.py          ← Streamlit UI + routing
├── agents.py       ← All Claude API calls (4 agents)
├── database.py     ← All Supabase operations
├── schema.sql      ← Run this in Supabase SQL editor
├── requirements.txt
└── .streamlit/
    └── secrets.toml.example
```
