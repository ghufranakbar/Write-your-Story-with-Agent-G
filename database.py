"""
database.py — Supabase operations for Life as Lore (multi-user).

Every function takes a `client` that already has the user's session attached,
so RLS policies on the DB side automatically scope all queries to that user.
The user_id is also passed explicitly for inserts (belt + suspenders).
"""

from supabase import Client


# ── World State ───────────────────────────────────────────────────────────────

def get_world_state(client: Client) -> dict | None:
    res = client.table("world_state").select("*").limit(1).execute()
    return res.data[0] if res.data else None


def create_world_state(client: Client, user_id: str, hero_name: str, world_name: str) -> dict:
    row = {
        "user_id": user_id,
        "hero_name": hero_name,
        "world_name": world_name,
        "current_era": "The Age of Beginning",
        "prophecy": None,
        "total_chapters": 0,
    }
    res = client.table("world_state").insert(row).execute()
    return res.data[0]


def update_world_state(client: Client, updates: dict):
    state = get_world_state(client)
    if state:
        client.table("world_state").update(updates).eq("id", state["id"]).execute()


# ── Entries ───────────────────────────────────────────────────────────────────

def save_entry(client: Client, user_id: str, raw_text: str, mood: str = None, themes: list = None) -> dict:
    row = {"user_id": user_id, "raw_text": raw_text, "mood": mood, "themes": themes or []}
    res = client.table("entries").insert(row).execute()
    return res.data[0]


def get_recent_entries(client: Client, limit: int = 10) -> list[dict]:
    res = (
        client.table("entries")
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return res.data


# ── Chapters ──────────────────────────────────────────────────────────────────

def save_chapter(client: Client, user_id: str, entry_id: str, title: str, body: str, season: str) -> dict:
    state = get_world_state(client)
    next_num = (state["total_chapters"] if state else 0) + 1
    row = {
        "user_id": user_id,
        "entry_id": entry_id,
        "chapter_num": next_num,
        "title": title,
        "body": body,
        "season": season,
    }
    res = client.table("chapters").insert(row).execute()
    update_world_state(client, {"total_chapters": next_num})
    return res.data[0]


def get_all_chapters(client: Client) -> list[dict]:
    res = (
        client.table("chapters")
        .select("*")
        .order("chapter_num", desc=False)
        .execute()
    )
    return res.data


def get_latest_chapters(client: Client, limit: int = 3) -> list[dict]:
    res = (
        client.table("chapters")
        .select("*")
        .order("chapter_num", desc=True)
        .limit(limit)
        .execute()
    )
    return list(reversed(res.data))


# ── Characters ────────────────────────────────────────────────────────────────

def get_all_characters(client: Client) -> list[dict]:
    res = client.table("characters").select("*").order("created_at").execute()
    return res.data


def upsert_character(client: Client, user_id: str, real_name: str, lore_name: str, archetype: str, description: str) -> dict:
    existing = (
        client.table("characters")
        .select("id")
        .eq("real_name", real_name)
        .execute()
    )
    if existing.data:
        res = (
            client.table("characters")
            .update({"description": description, "last_seen": "now()"})
            .eq("id", existing.data[0]["id"])
            .execute()
        )
    else:
        res = client.table("characters").insert({
            "user_id": user_id,
            "real_name": real_name,
            "lore_name": lore_name,
            "archetype": archetype,
            "description": description,
            "last_seen": "now()",
        }).execute()
    return res.data[0]


# ── Quests ────────────────────────────────────────────────────────────────────

def get_active_quests(client: Client) -> list[dict]:
    res = (
        client.table("quests")
        .select("*")
        .eq("status", "active")
        .order("created_at")
        .execute()
    )
    return res.data


def get_all_quests(client: Client) -> list[dict]:
    res = client.table("quests").select("*").order("created_at", desc=True).execute()
    return res.data


def upsert_quest(client: Client, user_id: str, title: str, lore_title: str, description: str, status: str = "active", resolution: str = None) -> dict:
    existing = (
        client.table("quests")
        .select("id")
        .ilike("title", title)
        .execute()
    )
    row = {
        "lore_title": lore_title,
        "description": description,
        "status": status,
        "updated_at": "now()",
    }
    if resolution:
        row["resolution"] = resolution
    if existing.data:
        res = client.table("quests").update(row).eq("id", existing.data[0]["id"]).execute()
    else:
        row["title"] = title
        row["user_id"] = user_id
        res = client.table("quests").insert(row).execute()
    return res.data[0]
