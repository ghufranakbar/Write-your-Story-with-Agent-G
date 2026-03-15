# Life as Lore

**A personal mythology engine.** You narrate your life in plain language. AI agents transform it into an ongoing fantasy novel -- with characters, quests, and prophecies that compound in meaning over months and years.

> Every life is an epic. Yours begins here.

---

## What It Does

Life as Lore is a multi-user Streamlit web application that turns your everyday journal entries into a continuously evolving fantasy chronicle. You write about what happened today; five specialized AI agents render it as richly written epic fiction.

### Pages

| Page | Description |
|---|---|
| **Narrate** | Write or paste what's happening in your life. The chapter-writer agent produces a fantasy prose chapter from your entry, while the character and quest agents extract people and goals in the background. |
| **Chronicle** | Your life rendered as a growing fantasy novel, displayed in a 3D open-book layout with drop caps, chapter titles, and seasonal markers. |
| **Characters** | Every person in your life becomes a named fantasy archetype (The Loyal Companion, The Mentor, The Trickster, etc.), tracked across entries. |
| **Quests** | Your real goals and struggles, tracked as epic quests with statuses (active, completed, abandoned) and lore-style titles. |
| **Prophecy** | After 3+ entries, an oracle agent reads your entire arc and writes a poetic, ambiguous prophecy hinting at where your story is heading. |

---

## Architecture

The project is split into three clean modules:

```
life-as-lore/
├── app.py              # Streamlit UI, routing, auth, theming (light/dark)
├── agents.py           # All LLM calls -- 5 agents powered by Google Gemini
├── database.py         # All Supabase/Postgres operations (RLS-scoped)
├── requirements.txt
└── LICENSE             # MIT
```

### `agents.py` -- Five AI Agents

All agents use **Google Gemini 2.5 Flash** via the `google-genai` SDK. Each agent has a focused system prompt and returns structured JSON.

1. **Chapter Writer** -- Turns a raw life narration into 3-5 paragraphs of literary fantasy prose (think Ursula Le Guin, not Eragon). Returns a chapter title, body, and narrative season name.
2. **Character Agent** -- Extracts people mentioned in an entry and maps them to fantasy archetypes with invented names and descriptions.
3. **Quest Agent** -- Identifies goals, problems, and struggles as epic quests. Tracks status across entries (active/completed/abandoned).
4. **Prophecy Agent** -- Reads the full arc of chapters and quests, then generates a poetic 3-5 line prophecy specific to the user's story.
5. **World Genesis Agent** -- On first sign-up, generates a fantasy hero name and world name based on the user's real name and a brief intro.

### `database.py` -- Supabase with Row-Level Security

All database operations go through a Supabase client that has the user's session attached. RLS policies on the Postgres side automatically scope every query to the authenticated user. Tables:

- `world_state` -- Hero name, world name, current era, prophecy, chapter count
- `entries` -- Raw journal entries with optional mood and themes
- `chapters` -- Generated fantasy chapters linked to entries
- `characters` -- Fantasy character mappings (real name to lore name, archetype)
- `quests` -- Tracked quests with lore titles, descriptions, statuses, resolutions

### `app.py` -- UI and Auth

- **Google OAuth** via Supabase Auth -- users sign in with Google, sessions are managed through Supabase tokens.
- **Dual theme** -- Full light and dark mode with a comprehensive design token system (backgrounds, borders, text, accents, shadows, etc.).
- **Custom typography** -- Playfair Display for headings, Crimson Pro for prose, Inter for UI labels, Cinzel Decorative for branding.
- **Visual effects** -- Ambient floating particle canvas, 3D card tilt on mouse hover, fade-in animations, 3D open-book layout for the chronicle.
- **Responsive** -- Breakpoints at 768px and 480px for mobile.

---

## Tech Stack

| Component | Service |
|---|---|
| Frontend + hosting | Streamlit (free on Streamlit Community Cloud) |
| Database | Supabase (free tier -- 500MB Postgres, plenty for years of entries) |
| AI model | Google Gemini 2.5 Flash via `google-genai` SDK |
| Auth | Supabase Auth with Google OAuth |

---

## License

MIT -- see [LICENSE](LICENSE) for details.
