"""
agents.py — All LLM API calls for Life as Lore (now using Google Gemini).

Four agents, each with a clear job:
  1. chapter_writer   — turns raw life narration → fantasy prose chapter
  2. character_agent  — extracts people → fantasy archetypes
  3. quest_agent      — extracts / updates goals as epic quests
  4. prophecy_agent   — reads full arc → generates a prophecy
"""

import json
import streamlit as st
from google import genai
from google.genai import types

MODEL = "gemini-2.5-flash"


@st.cache_resource
def get_client():
    # Using the API key from secrets or environment
    import os
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # python-dotenv not installed (e.g. Streamlit Cloud); secrets come from st.secrets
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    return genai.Client(api_key=api_key)


def _call(system: str, user: str) -> str:
    """Simple single-turn call. Returns the text content."""
    client = get_client()
    response = client.models.generate_content(
        model=MODEL,
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=system,
            temperature=0.7,
        ),
    )
    return response.text


# ── 1. Chapter Writer ─────────────────────────────────────────────────────────

CHAPTER_SYSTEM = """You are the narrator of an epic fantasy novel. The protagonist is a real person living a real life — but you render their experiences as richly written fantasy fiction.

Rules:
- Write 3–5 paragraphs of beautiful, atmospheric fantasy prose. Do NOT include markdown horizontal rules (---) or dividers between paragraphs.
- The hero's real problems become quests. Their real friends become named fantasy characters (use the character list provided). Their real feelings become the emotional weather of the world.
- Do NOT be cheesy or generic. Avoid clichés like "little did they know". Write like a literary fantasy novelist — think Ursula Le Guin, not Eragon.
- Keep it grounded in the actual emotions and events described. Fantasy is the lens, not an escape.
- End each chapter with a single sentence that feels like a turning point or a threshold being crossed.
- Return JSON only: {"title": "...", "body": "...", "season": "..."}
  - title: a poetic chapter title (max 8 words)
  - body: the full prose chapter
  - season: the current narrative season (e.g. "The Season of Unraveling", "The Age of Small Fires"). Invent one that fits the mood. Keep it if an existing one still fits."""



def write_chapter(
    raw_entry: str,
    hero_name: str,
    world_name: str,
    current_era: str,
    characters: list[dict],
    active_quests: list[dict],
    recent_chapters: list[dict],
) -> dict:
    """
    Returns {"title": str, "body": str, "season": str}
    """
    char_context = "\n".join(
        f"- {c['real_name']} → {c['lore_name']} ({c['archetype']})"
        for c in characters
    ) or "No established characters yet."

    quest_context = "\n".join(
        f"- {q['title']} → currently: {q['lore_title']} [{q['status']}]"
        for q in active_quests
    ) or "No active quests yet."

    recent_context = "\n\n".join(
        f"Chapter {c['chapter_num']}: {c['title']}\n{c['body'][:300]}..."
        for c in recent_chapters[-2:]
    ) or "This is the very first chapter."

    user_prompt = f"""The hero's name in this world: {hero_name}
The world's name: {world_name}
Current era: {current_era or 'unknown'}

Known characters:
{char_context}

Active quests:
{quest_context}

Most recent chapters (for continuity):
{recent_context}

---
The hero narrates their life today:
\"\"\"{raw_entry}\"\"\"

Write the next chapter. Return only valid JSON."""

    raw = _call(CHAPTER_SYSTEM, user_prompt)
    # Strip markdown fences if present
    raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    return json.loads(raw)


# ── 2. Character Agent ────────────────────────────────────────────────────────

CHARACTER_SYSTEM = """You extract people mentioned in a life narration and map them to fantasy archetypes for an ongoing fantasy novel about the narrator's life.

For each person found:
- Invent a fantasy name that feels fitting (not silly — dignified and evocative)
- Assign an archetype: The Loyal Companion, The Mentor, The Trickster, The Rival, The Oracle, The Lost Soul, The Gatekeeper, The Shadow, The Muse, etc.
- Write a one-sentence description of their role in the hero's story so far.

Return JSON only — an array:
[{"real_name": "...", "lore_name": "...", "archetype": "...", "description": "..."}]

If no people are mentioned, return [].
Only include people who seem significant, not random passersby."""


def extract_characters(raw_entry: str, existing_chars: list[dict]) -> list[dict]:
    existing = ", ".join(c["real_name"] for c in existing_chars) or "none yet"
    user_prompt = f"""Already established characters: {existing}

Life narration:
\"\"\"{raw_entry}\"\"\"

Extract any new or updated significant people. Return JSON array only."""

    raw = _call(CHARACTER_SYSTEM, user_prompt)
    raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    result = json.loads(raw)
    return result if isinstance(result, list) else []


# ── 3. Quest Agent ────────────────────────────────────────────────────────────

QUEST_SYSTEM = """You track goals, problems, and struggles from a person's life narration as epic fantasy quests.

For each goal/problem/struggle found:
- Give it a plain title (what it actually is)
- Give it a lore title (what it would be called in an epic fantasy novel)
- Write a short description (1–2 sentences)
- Assign status: "active", "completed", or "abandoned"
- If completed or abandoned, write a one-sentence resolution in fantasy style

Return JSON only:
[{"title": "...", "lore_title": "...", "description": "...", "status": "active|completed|abandoned", "resolution": null}]

If no quests are mentioned, return [].
Update existing quests if the narration describes progress or resolution."""


def extract_quests(raw_entry: str, existing_quests: list[dict]) -> list[dict]:
    existing = "\n".join(
        f"- {q['title']} (currently {q['status']})"
        for q in existing_quests
    ) or "none yet"

    user_prompt = f"""Active/existing quests: 
{existing}

Life narration:
\"\"\"{raw_entry}\"\"\"

Extract or update quests. Return JSON array only."""

    raw = _call(QUEST_SYSTEM, user_prompt)
    raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    result = json.loads(raw)
    return result if isinstance(result, list) else []


# ── 4. Prophecy Agent ────────────────────────────────────────────────────────

PROPHECY_SYSTEM = """You are an ancient oracle reading the arc of a hero's life. Given their story so far, write a prophecy — a poetic, ambiguous 3–5 line verse that hints at where their story is heading.

The prophecy should:
- Feel genuinely earned by the themes in their story
- Be poetic but not purple — spare and resonant
- Be ambiguous enough to feel true over time
- Not be generic ("great things await") — it must feel specific to THIS person's arc

Also suggest a new era name if the current one no longer fits. Return JSON:
{"prophecy": "...", "new_era": "...or null if current era still fits"}"""


def generate_prophecy(
    chapters: list[dict],
    quests: list[dict],
    current_era: str,
) -> dict:
    chapter_summaries = "\n".join(
        f"Ch.{c['chapter_num']} — {c['title']}: {c['body'][:200]}..."
        for c in chapters[-8:]
    )
    quest_summary = "\n".join(
        f"- {q['title']} [{q['status']}]" for q in quests
    )

    user_prompt = f"""Current era: {current_era or 'unnamed'}

Recent chapters:
{chapter_summaries}

All quests:
{quest_summary}

Generate the prophecy. Return JSON only."""

    raw = _call(PROPHECY_SYSTEM, user_prompt)
    raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    return json.loads(raw)


# ── 5. World Genesis Agent ────────────────────────────────────────────────────

GENESIS_SYSTEM = """A new user is starting their personal fantasy chronicle. Based on their name and a brief intro, generate:
- A fantasy hero name for them (dignified, not silly)
- A world name (evocative, unique — not "Middle Earth" style clichés)

Return JSON only: {"hero_name": "...", "world_name": "..."}"""


def generate_hero_identity(real_name: str, intro: str) -> dict:
    raw = _call(
        GENESIS_SYSTEM,
        f"Real name: {real_name}\nIntro: {intro}\n\nReturn JSON only.",
    )
    raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    return json.loads(raw)
