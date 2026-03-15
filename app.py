"""
app.py — Life as Lore · Personal Mythology Engine
Narrate your life. Read it as epic fantasy. Multi-user via Supabase RLS.
"""

import streamlit as st
import streamlit.components.v1 as components
from supabase import create_client, Client
import database as db
import agents

# ─── Page Config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Life as Lore",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── SVG Icon Library ────────────────────────────────────────────────────────
# Inline SVGs for a polished, consistent icon set across the UI.

ICONS = {
    "quill": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/></svg>',
    "book": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/></svg>',
    "users": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "sword": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 17.5 3 6V3h3l11.5 11.5"/><path d="M13 19l6-6"/><path d="M16 16l4 4"/><path d="M19 21l2-2"/></svg>',
    "crystal": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3h12l4 6-10 13L2 9Z"/><path d="M2 9h20"/><path d="M12 22 6 9"/><path d="M12 22l6-13"/></svg>',
    "sparkle": '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0l2.5 9.5L24 12l-9.5 2.5L12 24l-2.5-9.5L0 12l9.5-2.5z"/></svg>',
    "scroll": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M8 21h12a2 2 0 0 0 2-2v-2H10v2a2 2 0 1 1-4 0V5a2 2 0 1 0-4 0v3h4"/><path d="M19 3H8a2 2 0 0 0-2 2v12"/></svg>',
    "compass": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></svg>',
    "shield": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "crown": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M2 4l3 12h14l3-12-6 7-4-7-4 7-6-7z"/><path d="M5 16h14v4H5z"/></svg>',
    "flame": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/></svg>',
    "eye": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>',
    "logout": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>',
    "google": '<svg width="18" height="18" viewBox="0 0 24 24"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>',
    "check": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
    "x_mark": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
    "globe": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>',
}

def icon(name: str, color: str = "#c9a84c", size: int = 20) -> str:
    """Return an SVG icon string styled with the given color and size."""
    svg = ICONS.get(name, "")
    return f'<span style="color:{color};display:inline-flex;align-items:center;vertical-align:middle;width:{size}px;height:{size}px;">{svg}</span>'


# ─── Global CSS — Notion × Dark Fantasy ──────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400..900;1,400..900&family=Crimson+Pro:ital,wght@0,300..900;1,300..900&family=Cinzel+Decorative:wght@400;700&display=swap');

/* ── Foundation ──────────────────────────────── */
:root {
    --bg-primary:   #0a0a0f;
    --bg-secondary: #111118;
    --bg-elevated:  #16161f;
    --bg-surface:   #1c1c28;
    --border-subtle: rgba(201, 168, 76, 0.12);
    --border-medium: rgba(201, 168, 76, 0.22);
    --border-strong: rgba(201, 168, 76, 0.4);
    --gold:         #c9a84c;
    --gold-light:   #e8d9b8;
    --gold-dim:     #8c764c;
    --gold-faint:   rgba(201, 168, 76, 0.08);
    --text-primary: #e8e4dd;
    --text-secondary:#a8a29e;
    --text-muted:   #6b6560;
    --accent-green: #4ade80;
    --accent-blue:  #60a5fa;
    --accent-red:   #f87171;
    --radius-sm:    6px;
    --radius-md:    10px;
    --radius-lg:    16px;
    --shadow-card:  0 2px 8px rgba(0,0,0,0.3), 0 12px 40px rgba(0,0,0,0.2);
    --shadow-hover: 0 8px 30px rgba(0,0,0,0.4), 0 0 0 1px var(--border-medium);
    --shadow-deep:  0 20px 60px rgba(0,0,0,0.5), 0 0 0 1px var(--border-subtle);
    --transition:   all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
html, body, [class*="css"] {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}
.stApp {
    background: var(--bg-primary) !important;
    background-image:
        radial-gradient(ellipse 80% 60% at 50% 0%, rgba(201, 168, 76, 0.03) 0%, transparent 60%),
        radial-gradient(circle at 20% 80%, rgba(99, 76, 168, 0.02) 0%, transparent 40%) !important;
}

/* Subtle vignette — less aggressive than before */
.stApp::after {
    content: '';
    position: fixed;
    inset: 0;
    background: radial-gradient(ellipse at center, transparent 50%, rgba(0,0,0,0.35) 100%);
    pointer-events: none;
    z-index: 9999;
}

/* ── Sidebar — Notion-style clean panel ──────── */
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border-subtle) !important;
    backdrop-filter: blur(20px);
}
[data-testid="stSidebar"] * {
    font-family: 'Inter', -apple-system, sans-serif !important;
}

/* Sidebar world header */
.sidebar-world {
    padding: 0.25rem 0 1rem 0;
    border-bottom: 1px solid var(--border-subtle);
    margin-bottom: 1rem;
}
.sidebar-world-name {
    font-family: 'Playfair Display', serif !important;
    font-size: 1.35rem !important;
    color: var(--gold) !important;
    font-weight: 600;
    letter-spacing: 0.01em;
    margin: 0;
    line-height: 1.3;
}
.sidebar-hero {
    font-family: 'Crimson Pro', serif !important;
    font-size: 0.95rem;
    color: var(--text-secondary);
    font-style: italic;
    margin: 0.15rem 0 0 0;
}
.sidebar-era {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.72rem;
    color: var(--gold-dim);
    background: var(--gold-faint);
    padding: 3px 10px;
    border-radius: 20px;
    margin-top: 0.5rem;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    font-weight: 500;
}
.sidebar-stat {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.82rem;
    color: var(--text-secondary);
    margin-top: 0.6rem;
}
.sidebar-stat-num {
    font-weight: 600;
    color: var(--gold-light);
    font-variant-numeric: tabular-nums;
}

/* Sidebar navigation — Notion-style hover items */
.nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 12px;
    border-radius: var(--radius-sm);
    font-size: 0.9rem;
    color: var(--text-secondary);
    cursor: pointer;
    transition: var(--transition);
    margin: 2px 0;
    font-weight: 400;
}
.nav-item:hover {
    background: var(--gold-faint);
    color: var(--text-primary);
}
.nav-item.active {
    background: rgba(201, 168, 76, 0.12);
    color: var(--gold);
    font-weight: 500;
}

/* Sidebar user footer */
.sidebar-footer {
    border-top: 1px solid var(--border-subtle);
    padding-top: 0.75rem;
    margin-top: auto;
}
.sidebar-email {
    font-size: 0.75rem;
    color: var(--text-muted);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    margin-bottom: 0.5rem;
}

/* ── Typography ──────────────────────────────── */
h1, h2 {
    font-family: 'Playfair Display', serif !important;
    color: var(--gold) !important;
    font-weight: 700 !important;
    letter-spacing: -0.01em;
    text-shadow: none !important;
}
h3, h4 {
    font-family: 'Inter', sans-serif !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em;
    text-shadow: none !important;
}
p, li, div {
    font-family: 'Crimson Pro', serif !important;
    font-size: 1.1rem !important;
    line-height: 1.75 !important;
}

/* Page header with icon */
.page-header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin: 0.5rem 0 0.3rem 0;
    padding-bottom: 0.2rem;
}
.page-header-icon {
    width: 40px;
    height: 40px;
    border-radius: var(--radius-md);
    background: var(--gold-faint);
    border: 1px solid var(--border-subtle);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--gold);
    flex-shrink: 0;
}
.page-header h2 {
    margin: 0 !important;
    font-size: 1.8rem !important;
}
.page-subtitle {
    font-family: 'Crimson Pro', serif !important;
    color: var(--text-secondary);
    font-style: italic;
    font-size: 1.05rem !important;
    margin: 0 0 1.5rem 0;
    padding-left: 54px;
}

/* Notion-style divider */
.lore-divider {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin: 2rem 0;
    color: var(--gold-dim);
    opacity: 0.5;
}
.lore-divider::before, .lore-divider::after {
    content: '';
    flex: 1;
    max-width: 80px;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border-medium), transparent);
}

/* App title — genesis & auth pages */
.app-title {
    font-family: 'Cinzel Decorative', serif !important;
    font-size: 2.8rem;
    text-align: center;
    color: var(--gold-light);
    letter-spacing: 0.03em;
    margin-top: 2rem;
    background: linear-gradient(180deg, #f0e6d0 0%, #c9a84c 50%, #8c764c 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.app-subtitle {
    text-align: center;
    color: var(--text-secondary);
    font-family: 'Crimson Pro', serif !important;
    font-style: italic;
    font-size: 1.15rem !important;
    margin: 0.3rem 0 2rem 0;
}

/* ── 3D Book Layout (Chapters) ───────────────── */
.book-container {
    display: flex;
    max-width: 920px;
    margin: 2.5rem auto;
    perspective: 1400px;
    filter: drop-shadow(0 16px 40px rgba(0,0,0,0.6));
}
.page-left, .page-right {
    flex: 1;
    background: linear-gradient(160deg, var(--bg-elevated), var(--bg-secondary));
    padding: 2.5rem 2rem;
    border: 1px solid var(--border-subtle);
    position: relative;
}
.page-left {
    transform: rotateY(2.5deg);
    transform-origin: right center;
    border-right: none;
    border-radius: var(--radius-lg) 0 0 var(--radius-lg);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}
.page-left::after {
    content: '';
    position: absolute;
    right: 0;
    top: 10%;
    height: 80%;
    width: 1px;
    background: linear-gradient(180deg, transparent, var(--border-medium), transparent);
}
.page-right {
    transform: rotateY(-2.5deg);
    transform-origin: left center;
    border-left: none;
    border-radius: 0 var(--radius-lg) var(--radius-lg) 0;
}

.chapter-num {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.72rem !important;
    color: var(--gold-dim) !important;
    text-transform: uppercase;
    letter-spacing: 0.25em;
    font-weight: 600;
    margin-bottom: 0.8rem;
}
.chapter-title {
    font-family: 'Playfair Display', serif !important;
    font-size: 1.8rem !important;
    color: var(--gold) !important;
    text-align: center;
    letter-spacing: 0.01em;
    margin-bottom: 0.5rem;
    font-weight: 700;
    line-height: 1.2 !important;
}
.chapter-season {
    font-family: 'Crimson Pro', serif !important;
    font-size: 0.9rem !important;
    color: var(--text-muted) !important;
    text-align: center;
    font-style: italic;
    margin-bottom: 1rem;
}
.chapter-body {
    font-family: 'Crimson Pro', serif !important;
    font-size: 1.15rem !important;
    line-height: 1.85 !important;
    color: var(--text-primary);
}
.chapter-body p {
    margin-bottom: 1rem !important;
    text-align: justify !important;
}
/* Drop cap on first paragraph */
.chapter-body p:first-child::first-letter {
    font-size: 3.5rem;
    font-family: 'Playfair Display', serif;
    float: left;
    line-height: 0.85;
    padding-right: 10px;
    padding-top: 4px;
    color: var(--gold);
    font-weight: 700;
}

/* ── Glassmorphism Cards ─────────────────────── */
.card-3d-wrapper {
    perspective: 1200px;
    margin-bottom: 1rem;
}
.card-3d {
    background: linear-gradient(135deg, var(--bg-elevated), var(--bg-surface));
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 1.5rem;
    backdrop-filter: blur(10px);
    box-shadow: var(--shadow-card);
    transition: var(--transition);
    transform-style: preserve-3d;
    position: relative;
    overflow: hidden;
}
.card-3d::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent);
}
.card-3d:hover {
    box-shadow: var(--shadow-hover);
    border-color: var(--border-medium);
    transform: translateY(-2px);
}
.card-3d-icon {
    width: 36px;
    height: 36px;
    border-radius: var(--radius-sm);
    background: var(--gold-faint);
    border: 1px solid var(--border-subtle);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: var(--gold);
    margin-bottom: 0.8rem;
    font-size: 1.1rem;
}
.card-3d-title {
    font-family: 'Playfair Display', serif !important;
    font-size: 1.15rem !important;
    color: var(--gold-light) !important;
    margin-bottom: 0.2rem;
    font-weight: 600;
}
.card-3d-sub {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.72rem !important;
    color: var(--text-muted) !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.6rem;
    font-weight: 500;
}
.card-3d-desc {
    font-family: 'Crimson Pro', serif !important;
    font-size: 1rem !important;
    color: var(--text-secondary) !important;
    font-style: italic;
    line-height: 1.6 !important;
}

/* ── Quest Status Chips ──────────────────────── */
.quest-chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 12px;
    border-radius: 20px;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.7rem !important;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.quest-active {
    background: rgba(74, 222, 128, 0.1);
    color: var(--accent-green);
    border: 1px solid rgba(74, 222, 128, 0.2);
}
.quest-done {
    background: rgba(96, 165, 250, 0.1);
    color: var(--accent-blue);
    border: 1px solid rgba(96, 165, 250, 0.2);
}
.quest-abandoned {
    background: rgba(248, 113, 113, 0.1);
    color: var(--accent-red);
    border: 1px solid rgba(248, 113, 113, 0.2);
}

/* Quest card — Notion-style block */
.quest-block {
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.75rem;
    transition: var(--transition);
    cursor: default;
}
.quest-block:hover {
    background: var(--bg-surface);
    border-color: var(--border-medium);
}
.quest-block-title {
    font-family: 'Playfair Display', serif !important;
    font-size: 1.05rem !important;
    color: var(--text-primary);
    font-weight: 600;
    margin-bottom: 0.3rem;
}
.quest-block-desc {
    font-family: 'Crimson Pro', serif !important;
    font-size: 0.95rem !important;
    color: var(--text-secondary);
    font-style: italic;
    margin: 0.4rem 0;
}
.quest-block-real {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.75rem !important;
    color: var(--text-muted);
    margin-top: 0.5rem;
}

/* Section label — Notion-style */
.section-label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.75rem !important;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
    margin: 1.5rem 0 0.75rem 0;
}
.section-label-line {
    flex: 1;
    height: 1px;
    background: var(--border-subtle);
}

/* ── Prophecy Box ────────────────────────────── */
.prophecy-box {
    position: relative;
    border: 1px solid var(--border-medium);
    border-radius: var(--radius-lg);
    background: linear-gradient(180deg, var(--bg-elevated), var(--bg-primary));
    padding: 3rem 2.5rem;
    text-align: center;
    max-width: 680px;
    margin: 2rem auto;
    box-shadow: var(--shadow-deep);
    overflow: hidden;
}
.prophecy-box::before {
    content: '';
    position: absolute;
    top: -1px;
    left: 20%;
    right: 20%;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
}
.prophecy-box::after {
    content: '';
    position: absolute;
    bottom: -1px;
    left: 20%;
    right: 20%;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
}
.prophecy-icon {
    width: 48px;
    height: 48px;
    margin: 0 auto 1.5rem auto;
    border-radius: 50%;
    background: var(--gold-faint);
    border: 1px solid var(--border-subtle);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--gold);
}
.prophecy-text {
    font-family: 'Crimson Pro', serif !important;
    font-size: 1.3rem !important;
    font-style: italic;
    color: var(--gold) !important;
    line-height: 2 !important;
    white-space: pre-line;
}

/* ── Auth Card ───────────────────────────────── */
.auth-wrapper {
    position: relative;
    max-width: 420px;
    margin: 4rem auto;
}
@keyframes slow-rotate {
    from { transform: translate(-50%, -50%) rotate(0deg); }
    to   { transform: translate(-50%, -50%) rotate(360deg); }
}
.rune-bg {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 500px;
    height: 500px;
    background: conic-gradient(from 0deg, rgba(201,168,76,0.02) 0deg, transparent 30deg, rgba(201,168,76,0.015) 60deg, transparent 90deg);
    border-radius: 50%;
    animation: slow-rotate 90s linear infinite;
    z-index: 0;
    pointer-events: none;
    mask-image: radial-gradient(circle, black 20%, transparent 65%);
    -webkit-mask-image: radial-gradient(circle, black 20%, transparent 65%);
}
.auth-card {
    position: relative;
    z-index: 1;
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 2.5rem 2rem;
    box-shadow: var(--shadow-deep);
}
.auth-card::before {
    content: '';
    position: absolute;
    top: -1px;
    left: 15%;
    right: 15%;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
    border-radius: 1px;
}
.auth-title {
    font-family: 'Cinzel Decorative', serif;
    font-size: 2rem;
    color: var(--gold-light);
    text-align: center;
    margin-bottom: 0.3rem;
}
.auth-sub {
    font-family: 'Crimson Pro', serif;
    text-align: center;
    color: var(--text-muted);
    font-size: 1rem;
    font-style: italic;
    margin-bottom: 1.8rem;
}
.auth-divider {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 1.2rem 0;
    color: var(--text-muted);
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.auth-divider::before, .auth-divider::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border-subtle);
}

/* ── Form Inputs — Notion-style ──────────────── */
.stTextInput input, .stTextArea textarea {
    background: var(--bg-primary) !important;
    border: 1px solid var(--border-subtle) !important;
    color: var(--text-primary) !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'Crimson Pro', serif !important;
    font-size: 1.05rem !important;
    transition: var(--transition) !important;
    padding: 0.6rem 0.8rem !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 3px rgba(201, 168, 76, 0.08) !important;
    outline: none !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {
    color: var(--text-muted) !important;
    font-style: italic !important;
}
label {
    color: var(--text-secondary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em !important;
}

/* ── Buttons — clean press effect ────────────── */
.stButton > button {
    background: linear-gradient(180deg, var(--bg-surface), var(--bg-elevated)) !important;
    border: 1px solid var(--border-medium) !important;
    color: var(--gold) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.55rem 1.5rem !important;
    transition: var(--transition) !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.2) !important;
    letter-spacing: 0.01em;
}
.stButton > button:hover {
    background: linear-gradient(180deg, var(--bg-surface), var(--bg-secondary)) !important;
    border-color: var(--gold) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3), 0 0 0 1px var(--border-medium) !important;
    color: var(--gold-light) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.3), inset 0 1px 3px rgba(0,0,0,0.2) !important;
}

/* Google button style */
.google-btn {
    display: inline-flex !important;
    align-items: center !important;
    gap: 10px !important;
    justify-content: center !important;
    width: 100% !important;
}

/* ── Spinner override ────────────────────────── */
@keyframes ink-flow {
    0%   { opacity: 0.3; transform: scale(0.95); }
    50%  { opacity: 1;   transform: scale(1.05); }
    100% { opacity: 0.3; transform: scale(0.95); }
}
[data-testid="stSpinner"] {
    color: var(--gold) !important;
}

/* ── Tabs — Notion-style ─────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid var(--border-subtle);
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500;
    color: var(--text-muted) !important;
    padding: 0.6rem 1.2rem;
    border-bottom: 2px solid transparent;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    color: var(--gold) !important;
    border-bottom-color: var(--gold) !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    background-color: var(--gold) !important;
}

/* ── Streamlit overrides ─────────────────────── */
.stAlert { background: var(--bg-elevated) !important; border-color: var(--border-subtle) !important; color: var(--text-primary) !important; border-radius: var(--radius-sm) !important; }
[data-testid="stExpander"] { background: var(--bg-elevated) !important; border: 1px solid var(--border-subtle) !important; border-radius: var(--radius-md) !important; }
[data-testid="stExpander"]:hover { border-color: var(--border-medium) !important; }
.stCheckbox label span { color: var(--text-secondary) !important; font-family: 'Inter', sans-serif !important; font-size: 0.85rem !important; }
[data-testid="stStatusWidget"] { background: var(--bg-elevated) !important; border: 1px solid var(--border-subtle) !important; border-radius: var(--radius-md) !important; }
#MainMenu, footer, .stDeployButton { display: none; }

/* ── Empty state ─────────────────────────────── */
.empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: var(--text-muted);
}
.empty-state-icon {
    width: 56px;
    height: 56px;
    margin: 0 auto 1rem auto;
    border-radius: 50%;
    background: var(--gold-faint);
    border: 1px dashed var(--border-subtle);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--gold-dim);
}
.empty-state p {
    color: var(--text-muted) !important;
    font-style: italic;
    max-width: 380px;
    margin: 0 auto;
}

/* ── Genesis card ────────────────────────────── */
.genesis-card {
    max-width: 560px;
    margin: 2rem auto;
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 2.5rem;
    box-shadow: var(--shadow-deep);
}
.genesis-card::before {
    content: '';
    display: block;
    width: 48px;
    height: 48px;
    margin: 0 auto 1.5rem auto;
    border-radius: 50%;
    background: var(--gold-faint);
    border: 1px solid var(--border-subtle);
}

/* ── Responsive polish ───────────────────────── */
@media (max-width: 780px) {
    .book-container { flex-direction: column; margin: 1.5rem auto; }
    .page-left, .page-right { transform: none !important; border-radius: var(--radius-md) !important; }
    .page-left { border-right: 1px solid var(--border-subtle) !important; border-bottom: none; }
    .page-left::after { display: none; }
    .page-header h2 { font-size: 1.4rem !important; }
    .prophecy-box { padding: 2rem 1.5rem; }
}
</style>

<!-- Ambient floating particles — subtle gold motes -->
<canvas id="ember-bg" style="position:fixed;inset:0;width:100vw;height:100vh;pointer-events:none;z-index:-1;"></canvas>
<script>
(function() {
    const c = document.getElementById('ember-bg');
    if (!c) return;
    const ctx = c.getContext('2d');
    let W, H;

    function resize() { W = c.width = innerWidth; H = c.height = innerHeight; }
    addEventListener('resize', resize);
    resize();

    // Fewer, subtler particles for a refined look
    const pts = Array.from({length: 45}, () => ({
        x: Math.random() * W,
        y: Math.random() * H,
        r: Math.random() * 1.5 + 0.4,
        vy: Math.random() * 0.4 + 0.15,
        vx: (Math.random() - 0.5) * 0.25,
        a: Math.random() * 0.25 + 0.05
    }));

    (function draw() {
        ctx.clearRect(0, 0, W, H);
        for (const p of pts) {
            p.y -= p.vy;
            p.x += p.vx;
            if (p.y < -10) { p.y = H + 10; p.x = Math.random() * W; }
            // Soft glow
            ctx.beginPath();
            const g = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r * 3);
            g.addColorStop(0, `rgba(201,168,76,${p.a})`);
            g.addColorStop(1, 'rgba(201,168,76,0)');
            ctx.fillStyle = g;
            ctx.arc(p.x, p.y, p.r * 3, 0, Math.PI * 2);
            ctx.fill();
        }
        requestAnimationFrame(draw);
    })();
})();
</script>
""", unsafe_allow_html=True)

# 3D tilt effect on cards via mousemove
components.html("""
<script>
document.addEventListener("mousemove", e => {
    const cards = window.parent.document.querySelectorAll('.card-3d');
    cards.forEach(card => {
        const r = card.getBoundingClientRect();
        const cx = e.clientX - r.left - r.width/2;
        const cy = e.clientY - r.top - r.height/2;
        card.style.transform = `rotateX(${-cy/25}deg) rotateY(${cx/25}deg) translateY(-3px)`;
    });
});
document.addEventListener("mouseleave", () => {
    const cards = window.parent.document.querySelectorAll('.card-3d');
    cards.forEach(c => { c.style.transform = 'none'; });
});
</script>
""", height=0)


# ─── Supabase Client ─────────────────────────────────────────────────────────

@st.cache_resource
def get_base_client() -> Client:
    """Unauthenticated Supabase client for auth flows only."""
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


def get_authed_client(access_token: str, refresh_token: str) -> Client:
    """Supabase client scoped to the user's session (respects RLS)."""
    client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client.auth.set_session(access_token, refresh_token)
    return client


# ─── Session Helpers ──────────────────────────────────────────────────────────

def is_logged_in() -> bool:
    return st.session_state.get("access_token") is not None


def current_client() -> Client:
    return get_authed_client(st.session_state.access_token, st.session_state.refresh_token)


def current_user_id() -> str:
    return st.session_state.user_id


def store_session(session):
    st.session_state.access_token  = session.access_token
    st.session_state.refresh_token = session.refresh_token
    st.session_state.user_id       = session.user.id
    st.session_state.user_email    = session.user.email


def clear_session():
    for k in ["access_token", "refresh_token", "user_id", "user_email"]:
        st.session_state.pop(k, None)


# ─── OAuth Callback ──────────────────────────────────────────────────────────

def handle_oauth_callback():
    """Exchange ?code= param from Supabase OAuth redirect into a session."""
    code = st.query_params.get("code")
    if code and not is_logged_in():
        try:
            res = get_base_client().auth.exchange_code_for_session({"auth_code": code})
            if res.session:
                store_session(res.session)
                st.query_params.clear()
                st.rerun()
        except Exception as e:
            st.error(f"OAuth error: {e}")


# ─── Auth Pages ───────────────────────────────────────────────────────────────

def auth_page():
    handle_oauth_callback()
    if is_logged_in():
        return

    st.markdown(f'''
    <div class="auth-wrapper">
        <div class="rune-bg"></div>
        <div class="auth-card">
            <div style="text-align:center;margin-bottom:1rem;">{icon("globe", "#c9a84c", 32)}</div>
            <div class="auth-title">Life as Lore</div>
            <div class="auth-sub">Every life is an epic. Yours begins here.</div>
    ''', unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs(["Sign In", "Create Account"])

    with tab_login:
        _login_form()

    with tab_signup:
        _signup_form()

    st.markdown('</div></div>', unsafe_allow_html=True)


def _login_form():
    with st.form("login"):
        email    = st.text_input("Email", placeholder="your@email.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Enter the World")

    if submitted:
        if not email or not password:
            st.error("Fill in both fields.")
            return
        try:
            res = get_base_client().auth.sign_in_with_password({"email": email, "password": password})
            store_session(res.session)
            st.rerun()
        except Exception:
            st.error("Incorrect email or password.")

    st.markdown('<div class="auth-divider">or</div>', unsafe_allow_html=True)
    if st.button("Continue with Google", key="google_login"):
        _start_google_oauth()


def _signup_form():
    with st.form("signup"):
        email    = st.text_input("Email", placeholder="your@email.com", key="su_email")
        password = st.text_input("Password", type="password", placeholder="At least 6 characters", key="su_pw")
        confirm  = st.text_input("Confirm password", type="password", placeholder="••••••••", key="su_pw2")
        submitted = st.form_submit_button("Begin the Chronicle")

    if submitted:
        if not email or not password:
            st.error("Fill in all fields.")
            return
        if password != confirm:
            st.error("Passwords don't match.")
            return
        if len(password) < 6:
            st.error("Password must be at least 6 characters.")
            return
        try:
            res = get_base_client().auth.sign_up({"email": email, "password": password})
            if res.session:
                store_session(res.session)
                st.rerun()
            else:
                st.success("Account created! Check your email to confirm, then sign in.")
        except Exception as e:
            st.error(f"Could not create account: {e}")

    st.markdown('<div class="auth-divider">or</div>', unsafe_allow_html=True)
    if st.button("Sign up with Google", key="google_signup"):
        _start_google_oauth()


def _start_google_oauth():
    """Redirect browser to Google OAuth via Supabase."""
    try:
        app_url = st.secrets.get("APP_URL", "http://localhost:8501")
        res = get_base_client().auth.sign_in_with_oauth({
            "provider": "google",
            "options": {"redirect_to": app_url},
        })
        st.markdown(f'<meta http-equiv="refresh" content="0; url={res.url}">', unsafe_allow_html=True)
        st.stop()
    except Exception as e:
        st.error(f"Could not start Google sign-in: {e}")


# ─── Rendering Helpers ────────────────────────────────────────────────────────

def render_page_header(icon_name: str, title: str, subtitle: str = ""):
    """Notion-style page header with icon badge and subtitle."""
    st.markdown(f'''
    <div class="page-header">
        <div class="page-header-icon">{icon(icon_name, "#c9a84c", 22)}</div>
        <h2>{title}</h2>
    </div>
    {"<p class='page-subtitle'>" + subtitle + "</p>" if subtitle else ""}
    ''', unsafe_allow_html=True)


def render_divider():
    st.markdown(f'<div class="lore-divider">{icon("sparkle", "#8c764c", 10)}</div>', unsafe_allow_html=True)


def render_empty(icon_name: str, text: str):
    """Empty-state placeholder with icon and message."""
    st.markdown(f'''
    <div class="empty-state">
        <div class="empty-state-icon">{icon(icon_name, "#8c764c", 24)}</div>
        <p>{text}</p>
    </div>
    ''', unsafe_allow_html=True)


def render_section_label(label: str):
    st.markdown(f'''
    <div class="section-label">
        {label}
        <span class="section-label-line"></span>
    </div>
    ''', unsafe_allow_html=True)


def render_chapter(chapter: dict):
    """Display a chapter in the 3D open-book layout."""
    season_html = f'<div class="chapter-season">{chapter["season"]}</div>' if chapter.get("season") else ""
    paragraphs = chapter["body"].strip().split("\n\n")
    body_html = "".join(f"<p>{p.strip()}</p>" for p in paragraphs if p.strip())

    st.markdown(f"""
    <div class="book-container">
        <div class="page-left">
            <div class="chapter-num">Chapter {chapter["chapter_num"]}</div>
            <div class="chapter-title">{chapter["title"]}</div>
            {season_html}
            <div class="lore-divider" style="margin:1rem 0">{icon("sparkle", "#8c764c", 8)}</div>
        </div>
        <div class="page-right">
            <div class="chapter-body">{body_html}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def lore_card(title: str, subtitle: str, desc: str, icon_name: str = "shield"):
    """Glassmorphism character card with 3D tilt and icon badge."""
    st.markdown(f"""
    <div class="card-3d-wrapper">
        <div class="card-3d">
            <div class="card-3d-icon">{icon(icon_name, "#c9a84c", 18)}</div>
            <div class="card-3d-title">{title}</div>
            <div class="card-3d-sub">{subtitle}</div>
            <div class="card-3d-desc">{desc}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_quest_block(q: dict, status_class: str, status_label: str, status_icon: str):
    """Notion-style quest block with chip badge."""
    desc = q.get("description") or q.get("resolution") or ""
    st.markdown(f"""
    <div class="quest-block">
        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;">
            <div class="quest-block-title">{q.get("lore_title", q.get("title", ""))}</div>
            <span class="quest-chip {status_class}">{icon(status_icon, "currentColor", 12)} {status_label}</span>
        </div>
        {"<div class='quest-block-desc'>" + desc + "</div>" if desc else ""}
        <div class="quest-block-real">{q.get("title", "")}</div>
    </div>
    """, unsafe_allow_html=True)


# ─── Genesis (First-Time Setup) ──────────────────────────────────────────────

def genesis_page(client: Client, user_id: str):
    st.markdown('<div class="app-title">Life as Lore</div>', unsafe_allow_html=True)
    st.markdown('<p class="app-subtitle">Your world is waiting to be named.</p>', unsafe_allow_html=True)

    with st.form("genesis"):
        real_name = st.text_input("Your name", placeholder="What do people call you?")
        intro = st.text_area(
            "Tell me about yourself",
            placeholder="Where are you in life right now? What are you working on, struggling with, hoping for?",
            height=120,
        )
        submitted = st.form_submit_button("Begin the Chronicle")

    if submitted and real_name and intro:
        with st.spinner("The world is being named..."):
            identity = agents.generate_hero_identity(real_name, intro)
            db.create_world_state(client, user_id, identity["hero_name"], identity["world_name"])
        st.success(f"Welcome, **{identity['hero_name']}**. Your world — *{identity['world_name']}* — awaits.")
        st.rerun()


# ─── Sidebar ──────────────────────────────────────────────────────────────────

def sidebar(world: dict) -> str:
    with st.sidebar:
        # World identity block
        st.markdown(f"""
        <div class="sidebar-world">
            <div class="sidebar-world-name">{world["world_name"]}</div>
            <div class="sidebar-hero">{world["hero_name"]}</div>
            {"<div class='sidebar-era'>" + icon("compass", "#8c764c", 12) + " " + world["current_era"] + "</div>" if world.get("current_era") else ""}
            <div class="sidebar-stat">
                {icon("book", "#a8a29e", 15)}
                <span><span class="sidebar-stat-num">{world["total_chapters"]}</span> chapters written</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        page = st.radio(
            "Navigate",
            ["Narrate", "Chronicle", "Characters", "Quests", "Prophecy"],
            format_func=lambda x: {
                "Narrate":    "✎  Narrate",
                "Chronicle":  "◉  Chronicle",
                "Characters": "⚇  Characters",
                "Quests":     "⚔  Quests",
                "Prophecy":   "◈  Prophecy",
            }.get(x, x),
            label_visibility="collapsed",
        )

        st.divider()

        # User footer
        st.markdown(f'<div class="sidebar-email">{st.session_state.get("user_email", "")}</div>', unsafe_allow_html=True)
        if st.button("Sign Out"):
            try:
                get_base_client().auth.sign_out()
            except Exception:
                pass
            clear_session()
            st.rerun()

        return page


# ─── Page: Narrate ────────────────────────────────────────────────────────────

def page_narrate(client: Client, user_id: str, world: dict):
    render_page_header("quill", "Speak Your Truth",
                       "What has been happening in your life? Speak freely — the mundane and the momentous alike.")

    with st.form("narrate_form"):
        entry_text = st.text_area(
            "Your narration",
            placeholder="I've been feeling stuck on this project for weeks now. My friend keeps cancelling plans and I don't know if something is wrong. There's a new opportunity at work but it scares me...",
            height=200,
            label_visibility="collapsed",
        )
        submit = st.form_submit_button("Weave into the Lore")

    if submit and entry_text.strip():
        with st.status("The scribes are at work...", expanded=True) as status:

            st.write("Saving your narration...")
            entry = db.save_entry(client, user_id, entry_text)

            st.write("Reading the characters...")
            existing_chars = db.get_all_characters(client)
            new_chars = agents.extract_characters(entry_text, existing_chars)
            for c in new_chars:
                db.upsert_character(client, user_id, c["real_name"], c["lore_name"], c["archetype"], c["description"])

            st.write("Updating quests...")
            existing_quests = db.get_active_quests(client)
            new_quests = agents.extract_quests(entry_text, existing_quests)
            for q in new_quests:
                db.upsert_quest(client, user_id, q["title"], q["lore_title"], q["description"],
                                q.get("status", "active"), q.get("resolution"))

            st.write("Writing the chapter...")
            all_chars  = db.get_all_characters(client)
            all_quests = db.get_active_quests(client)
            recent     = db.get_latest_chapters(client, 3)
            chapter_data = agents.write_chapter(
                entry_text, world["hero_name"], world["world_name"],
                world.get("current_era", ""), all_chars, all_quests, recent,
            )
            db.save_chapter(client, user_id, entry["id"],
                            chapter_data["title"], chapter_data["body"], chapter_data["season"])

            if chapter_data.get("season"):
                db.update_world_state(client, {"current_era": chapter_data["season"]})

            status.update(label="The chapter is written.", state="complete")

        render_divider()
        render_chapter({**chapter_data, "chapter_num": world["total_chapters"] + 1})


# ─── Page: Chronicle ─────────────────────────────────────────────────────────

def page_chronicle(client: Client):
    render_page_header("book", "The Chronicle", "Every chapter of your unfolding story, bound in one place.")
    chapters = db.get_all_chapters(client)

    if not chapters:
        render_empty("scroll", "The pages are blank. Narrate your first entry to begin the chronicle.")
        return

    show_all = st.checkbox("Show all chapters", value=False)
    display = chapters if show_all else chapters[-3:]

    for ch in reversed(display):
        render_chapter(ch)


# ─── Page: Characters ────────────────────────────────────────────────────────

ARCHETYPE_ICONS = {
    "the loyal companion": "shield",
    "the mentor": "crown",
    "the trickster": "flame",
    "the rival": "sword",
    "the oracle": "crystal",
    "the muse": "eye",
}

def page_characters(client: Client):
    render_page_header("users", "Characters of the World",
                       "The souls who walk beside you, rendered in the language of myth.")
    chars = db.get_all_characters(client)

    if not chars:
        render_empty("users", "No characters have emerged yet. Narrate your life to let them appear.")
        return

    cols = st.columns(2)
    for i, c in enumerate(chars):
        with cols[i % 2]:
            archetype_lower = c.get("archetype", "").lower()
            card_icon = ARCHETYPE_ICONS.get(archetype_lower, "shield")
            lore_card(
                c["lore_name"],
                f'{c["archetype"]}  ·  known as {c["real_name"]}',
                c.get("description", ""),
                icon_name=card_icon,
            )


# ─── Page: Quests ─────────────────────────────────────────────────────────────

def page_quests(client: Client):
    render_page_header("sword", "The Book of Quests",
                       "Your goals and struggles, elevated to the stature they deserve.")
    quests = db.get_all_quests(client)

    if not quests:
        render_empty("sword", "No quests have been recorded. Mention your goals and struggles when you narrate.")
        return

    active = [q for q in quests if q["status"] == "active"]
    done   = [q for q in quests if q["status"] == "completed"]
    lost   = [q for q in quests if q["status"] == "abandoned"]

    if active:
        render_section_label(f"Active  ·  {len(active)}")
        for q in active:
            render_quest_block(q, "quest-active", "Ongoing", "flame")

    if done:
        render_section_label(f"Completed  ·  {len(done)}")
        for q in done:
            render_quest_block(q, "quest-done", "Completed", "check")

    if lost:
        render_section_label(f"Abandoned  ·  {len(lost)}")
        for q in lost:
            render_quest_block(q, "quest-abandoned", "Abandoned", "x_mark")


# ─── Page: Prophecy ──────────────────────────────────────────────────────────

def page_prophecy(client: Client, world: dict):
    render_page_header("crystal", "The Prophecy",
                       "Let the oracle read the arc of your story and speak of what lies ahead.")

    if world["total_chapters"] < 3:
        render_empty("eye", "The oracle needs more chapters to read. Write at least three entries first.")
        return

    existing_prophecy = world.get("prophecy")
    if existing_prophecy:
        st.markdown(f'''
        <div class="prophecy-box">
            <div class="prophecy-icon">{icon("crystal", "#c9a84c", 24)}</div>
            <div class="prophecy-text">{existing_prophecy}</div>
        </div>
        ''', unsafe_allow_html=True)

    btn_label = "Consult the Oracle" if not existing_prophecy else "Read the Omens Again"
    if st.button(btn_label):
        with st.spinner("The oracle considers your arc..."):
            chapters = db.get_all_chapters(client)
            quests   = db.get_all_quests(client)
            result   = agents.generate_prophecy(chapters, quests, world.get("current_era", ""))

        prophecy = result["prophecy"]
        new_era  = result.get("new_era")
        updates  = {"prophecy": prophecy}
        if new_era and new_era.lower() != "null":
            updates["current_era"] = new_era
        db.update_world_state(client, updates)

        st.markdown(f'''
        <div class="prophecy-box">
            <div class="prophecy-icon">{icon("crystal", "#c9a84c", 24)}</div>
            <div class="prophecy-text">{prophecy}</div>
        </div>
        ''', unsafe_allow_html=True)
        if new_era and new_era.lower() != "null":
            st.caption(f"The era shifts: *{new_era}*")
        st.rerun()


# ─── Main Router ──────────────────────────────────────────────────────────────

def main():
    handle_oauth_callback()

    if not is_logged_in():
        auth_page()
        return

    client  = current_client()
    user_id = current_user_id()
    world   = db.get_world_state(client)

    if not world:
        genesis_page(client, user_id)
        return

    page = sidebar(world)

    if "Narrate" in page:
        page_narrate(client, user_id, world)
    elif "Chronicle" in page:
        page_chronicle(client)
    elif "Characters" in page:
        page_characters(client)
    elif "Quests" in page:
        page_quests(client)
    elif "Prophecy" in page:
        page_prophecy(client, world)


if __name__ == "__main__":
    main()
