"""
app.py — Life as Lore · Personal Mythology Engine
Narrate your life. Read it as epic fantasy. Dual light/dark theme. Responsive.
"""

import streamlit as st
import streamlit.components.v1 as components
from supabase import create_client, Client
from streamlit_option_menu import option_menu
import database as db
import agents

# ─── Page Setup ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Life as Lore",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "theme" not in st.session_state:
    st.session_state.theme = "light"

IS_DARK = st.session_state.theme == "dark"


def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"


# ─── Theme Palette ────────────────────────────────────────────────────────────

THEMES = {
    "light": dict(
        bg0="#f7f5f0", bg1="#ffffff", bg2="#f0ede6", bg3="#e6e2d9", sidebar="#f1eee7",
        brd1="rgba(90,75,50,0.09)", brd2="rgba(90,75,50,0.16)", brd3="rgba(90,75,50,0.28)",
        tx0="#1c1a16", tx1="#5a5449", tx2="#8e877e",
        accent="#9b6b2f", accentHov="#7d5520", accentLt="#c49052",
        accentBg="rgba(155,107,47,0.06)", accentTx="#ffffff",
        heading="#3e3225", headingSrf="#6b5738",
        green="#1a7f4a", greenBg="rgba(26,127,74,0.08)",
        blue="#2563eb", blueBg="rgba(37,99,235,0.08)",
        red="#dc2626", redBg="rgba(220,38,38,0.08)",
        shCard="0 1px 3px rgba(0,0,0,0.03),0 6px 24px rgba(0,0,0,0.05)",
        shHover="0 8px 30px rgba(0,0,0,0.07)",
        shDeep="0 12px 40px rgba(0,0,0,0.09)",
        bookBg="linear-gradient(160deg,#faf7f1,#f4f0e8)",
        bookSpine="rgba(100,85,60,0.12)",
        inputBg="#faf8f4",
        gBtnBg="#ffffff", gBtnBrd="#dadce0", gBtnTx="#3c4043", gBtnHov="#f7f8f8",
        pCol="130,105,55", pAlpha="0.1",
        propBg="linear-gradient(180deg,#f8f5ef,#f2efe7)",
        authMesh1="rgba(200,160,80,0.12)", authMesh2="rgba(150,130,90,0.08)",
        scrollTrack="#eeebe4", scrollThumb="#d4cfc5",
        tabActive="#9b6b2f",
    ),
    "dark": dict(
        bg0="#0e0f17", bg1="#181a26", bg2="#1f2233", bg3="#282c42", sidebar="#12131c",
        brd1="rgba(180,160,110,0.09)", brd2="rgba(180,160,110,0.16)", brd3="rgba(180,160,110,0.28)",
        tx0="#e5e2db", tx1="#9b968d", tx2="#5e5950",
        accent="#d4a84b", accentHov="#c49935", accentLt="#e8c76e",
        accentBg="rgba(212,168,75,0.07)", accentTx="#1a1815",
        heading="#d4a84b", headingSrf="#c9a04a",
        green="#4ade80", greenBg="rgba(74,222,128,0.1)",
        blue="#60a5fa", blueBg="rgba(96,165,250,0.1)",
        red="#f87171", redBg="rgba(248,113,113,0.1)",
        shCard="0 2px 8px rgba(0,0,0,0.22),0 8px 32px rgba(0,0,0,0.14)",
        shHover="0 8px 24px rgba(0,0,0,0.32)",
        shDeep="0 12px 40px rgba(0,0,0,0.38)",
        bookBg="linear-gradient(160deg,#1f2233,#181a26)",
        bookSpine="rgba(180,160,110,0.12)",
        inputBg="#12131c",
        gBtnBg="#181a26", gBtnBrd="rgba(180,160,110,0.18)", gBtnTx="#e5e2db", gBtnHov="#1f2233",
        pCol="200,168,76", pAlpha="0.16",
        propBg="linear-gradient(180deg,#1f2233,#0e0f17)",
        authMesh1="rgba(212,168,75,0.06)", authMesh2="rgba(100,80,160,0.05)",
        scrollTrack="#181a26", scrollThumb="#2a2d40",
        tabActive="#d4a84b",
    ),
}

T = THEMES[st.session_state.theme]

# ─── SVG Icons ────────────────────────────────────────────────────────────────

ICONS = {
    "quill": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/></svg>',
    "book": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/></svg>',
    "users": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "sword": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 17.5 3 6V3h3l11.5 11.5"/><path d="M13 19l6-6"/><path d="M16 16l4 4"/><path d="M19 21l2-2"/></svg>',
    "crystal": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3h12l4 6-10 13L2 9Z"/><path d="M2 9h20"/><path d="M12 22 6 9"/><path d="M12 22l6-13"/></svg>',
    "sparkle": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 0l2.5 9.5L24 12l-9.5 2.5L12 24l-2.5-9.5L0 12l9.5-2.5z"/></svg>',
    "scroll": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M8 21h12a2 2 0 0 0 2-2v-2H10v2a2 2 0 1 1-4 0V5a2 2 0 1 0-4 0v3h4"/><path d="M19 3H8a2 2 0 0 0-2 2v12"/></svg>',
    "compass": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></svg>',
    "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "crown": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M2 4l3 12h14l3-12-6 7-4-7-4 7-6-7z"/><path d="M5 16h14v4H5z"/></svg>',
    "flame": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/></svg>',
    "eye": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>',
    "sun": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>',
    "moon": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>',
    "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
    "x_mark": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
    "google": '<svg viewBox="0 0 24 24"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>',
}


def icon(name: str, color: str = "", size: int = 20) -> str:
    """Wrap an SVG icon in a sized, colored span."""
    c = color or T["accent"]
    svg = ICONS.get(name, "")
    return f'<span style="color:{c};display:inline-flex;align-items:center;width:{size}px;height:{size}px;">{svg}</span>'


# ─── Styles & Ambient Effects ─────────────────────────────────────────────────

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,400..900;1,400..900&family=Crimson+Pro:ital,wght@0,300..900;1,300..900&family=Cinzel+Decorative:wght@400;700&display=swap');

/* ── Design Tokens ───────────────────────────── */
:root {{
    --bg-0:{T['bg0']}; --bg-1:{T['bg1']}; --bg-2:{T['bg2']}; --bg-3:{T['bg3']}; --sidebar:{T['sidebar']};
    --brd-1:{T['brd1']}; --brd-2:{T['brd2']}; --brd-3:{T['brd3']};
    --tx-0:{T['tx0']}; --tx-1:{T['tx1']}; --tx-2:{T['tx2']};
    --accent:{T['accent']}; --accent-hov:{T['accentHov']}; --accent-lt:{T['accentLt']};
    --accent-bg:{T['accentBg']}; --accent-tx:{T['accentTx']};
    --heading:{T['heading']}; --heading-srf:{T['headingSrf']};
    --green:{T['green']}; --green-bg:{T['greenBg']};
    --blue:{T['blue']}; --blue-bg:{T['blueBg']};
    --red:{T['red']}; --red-bg:{T['redBg']};
    --sh-card:{T['shCard']}; --sh-hover:{T['shHover']}; --sh-deep:{T['shDeep']};
    --book-bg:{T['bookBg']}; --book-spine:{T['bookSpine']};
    --input-bg:{T['inputBg']};
    --g-btn-bg:{T['gBtnBg']}; --g-btn-brd:{T['gBtnBrd']}; --g-btn-tx:{T['gBtnTx']}; --g-btn-hov:{T['gBtnHov']};
    --prop-bg:{T['propBg']};
    --tab-active:{T['tabActive']};
    --scroll-track:{T['scrollTrack']}; --scroll-thumb:{T['scrollThumb']};
    --r: 10px; --r-sm: 6px; --r-lg: 14px;
    --ease: cubic-bezier(0.4, 0, 0.2, 1);
    --tx: all 0.25s var(--ease);
}}

/* ── Foundation ──────────────────────────────── */
html, body, [class*="css"] {{
    background-color: var(--bg-0) !important;
    color: var(--tx-0) !important;
    transition: background-color 0.35s var(--ease), color 0.35s var(--ease);
}}
.stApp {{
    background: var(--bg-0) !important;
}}

/* Custom scrollbar */
::-webkit-scrollbar {{ width: 7px; }}
::-webkit-scrollbar-track {{ background: var(--scroll-track); }}
::-webkit-scrollbar-thumb {{ background: var(--scroll-thumb); border-radius: 10px; }}
::-webkit-scrollbar-thumb:hover {{ background: var(--accent); }}

/* Fade-in animation for content */
@keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(12px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
.fade-in {{ animation: fadeUp 0.5s var(--ease) both; }}

/* ── Sidebar ─────────────────────────────────── */
[data-testid="stSidebar"] {{
    background: var(--sidebar) !important;
    border-right: 1px solid var(--brd-1) !important;
    transition: background 0.35s var(--ease);
}}
[data-testid="stSidebar"] > div {{
    background: var(--sidebar) !important;
}}
[data-testid="stSidebar"] * {{
    font-family: 'Inter', -apple-system, sans-serif !important;
}}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stSidebar"] section {{
    background: transparent !important;
}}
/* Force option-menu in sidebar to inherit theme */
[data-testid="stSidebar"] iframe {{
    background: transparent !important;
}}

.sidebar-brand {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0.2rem 0 0.8rem 0;
    margin-bottom: 0.6rem;
    border-bottom: 1px solid var(--brd-1);
}}
.sidebar-brand-icon {{
    width: 34px; height: 34px;
    border-radius: 8px;
    background: var(--accent-bg);
    border: 1px solid var(--brd-1);
    display: flex; align-items: center; justify-content: center;
    color: var(--accent);
    flex-shrink: 0;
}}
.sidebar-brand-text {{
    font-family: 'Cinzel Decorative', serif !important;
    font-size: 0.95rem !important;
    color: var(--heading) !important;
    font-weight: 700;
    line-height: 1.2;
}}
.sidebar-world {{
    padding: 0.5rem 0 0.8rem 0;
    border-bottom: 1px solid var(--brd-1);
    margin-bottom: 0.8rem;
}}
.sidebar-world-name {{
    font-family: 'Playfair Display', serif !important;
    font-size: 1.2rem !important;
    color: var(--heading) !important;
    font-weight: 600;
    line-height: 1.3;
    margin: 0;
}}
.sidebar-hero {{
    font-family: 'Crimson Pro', serif !important;
    font-size: 0.9rem !important;
    color: var(--tx-1) !important;
    font-style: italic;
    margin: 0.1rem 0 0 0;
}}
.sidebar-era {{
    display: inline-flex; align-items: center; gap: 5px;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.65rem !important;
    color: var(--accent) !important;
    background: var(--accent-bg);
    padding: 2px 9px;
    border-radius: 20px;
    margin-top: 0.4rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    font-weight: 600;
}}
.sidebar-stat {{
    display: flex; align-items: center; gap: 7px;
    font-size: 0.78rem !important; color: var(--tx-1) !important;
    margin-top: 0.5rem;
}}
.sidebar-stat b {{ color: var(--tx-0); font-variant-numeric: tabular-nums; }}
.sidebar-email {{
    font-size: 0.72rem !important;
    color: var(--tx-2) !important;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    margin-bottom: 0.4rem;
}}
/* Theme toggle button in sidebar */
.theme-toggle {{
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 0.78rem !important;
    color: var(--tx-1) !important;
    cursor: pointer;
    padding: 4px 0;
}}

/* Theme switch button — styled clickable element */
.theme-switch-btn .stButton > button {{
    background: var(--bg-2) !important;
    border: 1px solid var(--brd-2) !important;
    color: var(--tx-1) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
    padding: 0.4rem 0.9rem !important;
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
    width: 100% !important;
    justify-content: center !important;
    cursor: pointer !important;
}}
.theme-switch-btn .stButton > button:hover {{
    background: var(--accent-bg) !important;
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    transform: none !important;
}}

/* ── Typography ──────────────────────────────── */
h1, h2 {{
    font-family: 'Playfair Display', serif !important;
    color: var(--heading) !important;
    font-weight: 700 !important;
    letter-spacing: -0.01em;
}}
h3, h4 {{
    font-family: 'Inter', sans-serif !important;
    color: var(--tx-0) !important;
    font-weight: 600 !important;
}}
p, li, div {{
    font-family: 'Crimson Pro', serif !important;
    font-size: 1.08rem !important;
    line-height: 1.75 !important;
}}

/* Page header — icon badge + title + subtitle */
.page-header {{
    display: flex; align-items: center; gap: 14px;
    margin: 0.5rem 0 0.2rem 0;
    animation: fadeUp 0.4s var(--ease) both;
}}
.page-header-icon {{
    width: 42px; height: 42px;
    border-radius: var(--r);
    background: var(--accent-bg);
    border: 1px solid var(--brd-1);
    display: flex; align-items: center; justify-content: center;
    color: var(--accent);
    flex-shrink: 0;
}}
.page-header h2 {{ margin: 0 !important; font-size: 1.7rem !important; }}
.page-subtitle {{
    font-family: 'Crimson Pro', serif !important;
    color: var(--tx-1) !important;
    font-style: italic;
    font-size: 1rem !important;
    margin: 0 0 1.5rem 56px;
}}

/* App title — gradient shimmer for auth/genesis */
.app-title {{
    font-family: 'Cinzel Decorative', serif !important;
    font-size: 2.6rem;
    text-align: center;
    margin: 0.8rem 0 0.2rem 0;
    background: linear-gradient(135deg, var(--heading) 0%, var(--accent-lt) 50%, var(--heading) 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shimmer 4s linear infinite;
}}
@keyframes shimmer {{
    to {{ background-position: 200% center; }}
}}
.app-subtitle {{
    text-align: center;
    color: var(--tx-1) !important;
    font-family: 'Crimson Pro', serif !important;
    font-style: italic;
    font-size: 1.1rem !important;
    margin: 0 0 1rem 0;
}}

/* Decorative divider */
.lore-divider {{
    display: flex; align-items: center; justify-content: center; gap: 10px;
    margin: 0.8rem 0; color: var(--tx-2); opacity: 0.45;
}}
.lore-divider::before, .lore-divider::after {{
    content: ''; flex: 1; max-width: 60px; height: 1px;
    background: linear-gradient(90deg, transparent, var(--brd-2), transparent);
}}

/* Section label */
.section-label {{
    display: flex; align-items: center; gap: 8px;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.7rem !important; color: var(--tx-2) !important;
    text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600;
    margin: 0.8rem 0 0.5rem 0;
}}
.section-label::after {{
    content: ''; flex: 1; height: 1px; background: var(--brd-1);
}}

/* ── 3D Book Layout ──────────────────────────── */
.book-container {{
    display: flex;
    max-width: 900px;
    margin: 1rem auto;
    perspective: 1400px;
    filter: drop-shadow(var(--sh-deep));
    animation: fadeUp 0.55s var(--ease) both;
}}
.page-left, .page-right {{
    flex: 1;
    background: var(--book-bg);
    padding: 2.2rem 1.8rem;
    border: 1px solid var(--brd-1);
    position: relative;
}}
.page-left {{
    transform: rotateY(2deg);
    transform-origin: right center;
    border-right: none;
    border-radius: var(--r-lg) 0 0 var(--r-lg);
    display: flex; flex-direction: column;
    justify-content: center; align-items: center;
}}
.page-left::after {{
    content: '';
    position: absolute; right: 0; top: 8%; height: 84%; width: 1px;
    background: linear-gradient(180deg, transparent, var(--book-spine), transparent);
}}
.page-right {{
    transform: rotateY(-2deg);
    transform-origin: left center;
    border-left: none;
    border-radius: 0 var(--r-lg) var(--r-lg) 0;
}}
.chapter-num {{
    font-family: 'Inter', sans-serif !important;
    font-size: 0.68rem !important;
    color: var(--tx-2) !important;
    text-transform: uppercase;
    letter-spacing: 0.25em; font-weight: 600;
    margin-bottom: 0.7rem;
    background: var(--accent-bg);
    padding: 3px 14px;
    border-radius: 20px;
    border: 1px solid var(--brd-1);
}}
.chapter-title {{
    font-family: 'Playfair Display', serif !important;
    font-size: 1.6rem !important;
    color: var(--heading) !important;
    text-align: center;
    font-weight: 700;
    line-height: 1.25 !important;
    margin-bottom: 0.4rem;
}}
.chapter-season {{
    font-family: 'Crimson Pro', serif !important;
    font-size: 0.85rem !important;
    color: var(--tx-2) !important;
    text-align: center; font-style: italic;
    margin-bottom: 0.8rem;
}}
.chapter-body {{
    font-family: 'Crimson Pro', serif !important;
    font-size: 1.1rem !important;
    line-height: 1.85 !important;
    color: var(--tx-0);
}}
.chapter-body p {{
    margin-bottom: 0.9rem !important;
    text-align: justify !important;
    text-justify: inter-word;
}}
.chapter-body p:first-child::first-letter {{
    font-size: 3.2rem;
    font-family: 'Playfair Display', serif;
    float: left;
    line-height: 0.85;
    padding: 4px 10px 0 0;
    color: var(--accent);
    font-weight: 700;
}}

/* ── Cards ───────────────────────────────────── */
.card-3d-wrapper {{ perspective: 1200px; margin-bottom: 0.9rem; }}
.card-3d {{
    background: var(--bg-1);
    border: 1px solid var(--brd-1);
    border-radius: var(--r);
    padding: 1.4rem;
    box-shadow: var(--sh-card);
    transition: var(--tx);
    transform-style: preserve-3d;
    position: relative;
    overflow: hidden;
    animation: fadeUp 0.45s var(--ease) both;
}}
.card-3d::before {{
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, {"rgba(255,255,255,0.06)" if IS_DARK else "rgba(255,255,255,0.8)"}, transparent);
}}
.card-3d:hover {{
    box-shadow: var(--sh-hover);
    border-color: var(--brd-2);
    transform: translateY(-3px);
}}
.card-3d-icon {{
    width: 34px; height: 34px;
    border-radius: var(--r-sm);
    background: var(--accent-bg);
    border: 1px solid var(--brd-1);
    display: inline-flex; align-items: center; justify-content: center;
    color: var(--accent);
    margin-bottom: 0.7rem;
}}
.card-3d-title {{
    font-family: 'Playfair Display', serif !important;
    font-size: 1.1rem !important;
    color: var(--heading) !important;
    margin-bottom: 0.15rem;
    font-weight: 600;
}}
.card-3d-sub {{
    font-family: 'Inter', sans-serif !important;
    font-size: 0.68rem !important;
    color: var(--tx-2) !important;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 0.5rem;
    font-weight: 500;
}}
.card-3d-desc {{
    font-family: 'Crimson Pro', serif !important;
    font-size: 0.95rem !important;
    color: var(--tx-1) !important;
    font-style: italic;
    line-height: 1.55 !important;
}}

/* ── Quest Blocks ────────────────────────────── */
.quest-chip {{
    display: inline-flex; align-items: center; gap: 4px;
    padding: 2px 10px;
    border-radius: 20px;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.65rem !important;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}}
.quest-active {{ background: var(--green-bg); color: var(--green); border: 1px solid {"rgba(74,222,128,0.18)" if IS_DARK else "rgba(26,127,74,0.15)"}; }}
.quest-done   {{ background: var(--blue-bg); color: var(--blue); border: 1px solid {"rgba(96,165,250,0.18)" if IS_DARK else "rgba(37,99,235,0.15)"}; }}
.quest-abandoned {{ background: var(--red-bg); color: var(--red); border: 1px solid {"rgba(248,113,113,0.18)" if IS_DARK else "rgba(220,38,38,0.15)"}; }}
.quest-block {{
    background: var(--bg-1);
    border: 1px solid var(--brd-1);
    border-radius: var(--r);
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.65rem;
    transition: var(--tx);
    animation: fadeUp 0.4s var(--ease) both;
}}
.quest-block:hover {{
    background: var(--bg-2);
    border-color: var(--brd-2);
    transform: translateX(4px);
}}
.quest-block-title {{
    font-family: 'Playfair Display', serif !important;
    font-size: 1rem !important;
    color: var(--tx-0) !important;
    font-weight: 600;
    margin-bottom: 0.2rem;
}}
.quest-block-desc {{
    font-family: 'Crimson Pro', serif !important;
    font-size: 0.9rem !important;
    color: var(--tx-1) !important;
    font-style: italic; margin: 0.3rem 0;
}}
.quest-block-real {{
    font-family: 'Inter', sans-serif !important;
    font-size: 0.7rem !important;
    color: var(--tx-2) !important;
    margin-top: 0.4rem;
}}

/* ── Prophecy ────────────────────────────────── */
.prophecy-box {{
    position: relative;
    border: 1px solid var(--brd-2);
    border-radius: var(--r-lg);
    background: var(--prop-bg);
    padding: 2rem 1.8rem;
    text-align: center;
    max-width: 650px;
    margin: 1rem auto;
    box-shadow: var(--sh-deep);
    overflow: hidden;
    animation: fadeUp 0.5s var(--ease) both;
}}
.prophecy-box::before, .prophecy-box::after {{
    content: '';
    position: absolute; left: 18%; right: 18%; height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
}}
.prophecy-box::before {{ top: -1px; }}
.prophecy-box::after  {{ bottom: -1px; }}
.prophecy-icon {{
    width: 44px; height: 44px;
    margin: 0 auto 1.2rem auto;
    border-radius: 50%;
    background: var(--accent-bg);
    border: 1px solid var(--brd-1);
    display: flex; align-items: center; justify-content: center;
    color: var(--accent);
}}
.prophecy-text {{
    font-family: 'Crimson Pro', serif !important;
    font-size: 1.25rem !important;
    font-style: italic;
    color: var(--heading) !important;
    line-height: 2 !important;
    white-space: pre-line;
}}

/* ── Auth Page ────────────────────────────────── */
/* Background orbs — fixed to viewport so they don't create layout space */
.auth-orbs-bg {{
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    pointer-events: none; z-index: 0; overflow: hidden;
}}
@keyframes orb1 {{
    0%,100% {{ transform: translate(0,0) scale(1) rotate(0deg); }}
    33%     {{ transform: translate(30px,-20px) scale(1.1) rotate(5deg); }}
    66%     {{ transform: translate(-15px,15px) scale(0.95) rotate(-3deg); }}
}}
@keyframes orb2 {{
    0%,100% {{ transform: translate(0,0) scale(1) rotate(0deg); }}
    50%     {{ transform: translate(-25px,25px) scale(1.06) rotate(-4deg); }}
}}
.auth-orbs-bg .orb {{
    position: absolute; border-radius: 50%;
    filter: blur(90px); pointer-events: none;
}}
.auth-orbs-bg .orb-1 {{
    width: 380px; height: 380px;
    background: {T['authMesh1']};
    top: 5%; right: 10%;
    animation: orb1 20s ease-in-out infinite;
}}
.auth-orbs-bg .orb-2 {{
    width: 300px; height: 300px;
    background: {T['authMesh2']};
    bottom: 10%; left: 5%;
    animation: orb2 24s ease-in-out infinite;
}}

/* Auth header — title block rendered as self-contained HTML */
.auth-accent-line {{
    width: 40px; height: 3px;
    border-radius: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent-lt));
    margin: 0 auto 1rem auto;
}}
.auth-title {{
    font-family: 'Playfair Display', serif !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    color: var(--heading) !important;
    text-align: center;
    margin-bottom: 0.1rem;
    letter-spacing: -0.01em;
}}
.auth-sub {{
    font-family: 'Crimson Pro', serif !important;
    text-align: center;
    color: var(--tx-2) !important;
    font-size: 0.88rem !important;
    font-style: italic;
    margin-bottom: 0.6rem;
}}
.auth-divider {{
    display: flex; align-items: center; gap: 10px;
    margin: 0.8rem 0;
    color: var(--tx-2);
    font-family: 'Inter', sans-serif !important;
    font-size: 0.68rem !important;
    text-transform: uppercase; letter-spacing: 0.1em;
}}
.auth-divider::before, .auth-divider::after {{
    content: ''; flex: 1; height: 1px; background: var(--brd-1);
}}

/* Google OAuth button — Streamlit button with G logo via ::before */
  .g-btn-wrap .g-auth-link {{
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      text-decoration: none !important;
      background: {T['gBtnBg']} !important;
      border: 1px solid {T['gBtnBrd']} !important;
      color: {T['gBtnTx']} !important;
      font-family: 'Inter', sans-serif !important;
      font-size: 0.88rem !important;
      font-weight: 500 !important;
      border-radius: 8px !important;
      padding: 10px 16px !important;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
      transition: all 0.2s var(--ease) !important;
      width: 100% !important;
  }}
  .g-btn-wrap .g-auth-link::before {{
      content: '';
      display: inline-block;
      width: 18px; height: 18px;
      margin-right: 10px;
      flex-shrink: 0;
      vertical-align: middle;
      background: url("data:image/svg+xml,%3Csvg viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z' fill='%234285F4'/%3E%3Cpath d='M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z' fill='%2334A853'/%3E%3Cpath d='M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z' fill='%23FBBC05'/%3E%3Cpath d='M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z' fill='%23EA4335'/%3E%3C/svg%3E") no-repeat center/contain;
  }}
  .g-btn-wrap .g-auth-link:hover {{
    box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
    border-color: {'#c0c0c0' if not IS_DARK else 'rgba(180,160,110,0.28)'} !important;
    transform: none !important;
}}

/* Auth footer — theme toggle row */
.auth-footer {{
    margin-top: 0.8rem; padding-top: 0.8rem;
    border-top: 1px solid var(--brd-1);
}}
.auth-footer .stButton > button {{
      background: transparent !important;
      border: 1px solid rgba(130, 110, 70, 0.4) !important;
      color: #d8c8a8 !important;
      font-family: 'Inter', sans-serif !important;
      font-size: 0.88rem !important;
      font-weight: 500 !important;
      border-radius: 8px !important;
      padding: 10px 16px !important;
      height: 40px !important;
      width: 100% !important;
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      gap: 6px !important;
      cursor: pointer !important;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
      transition: all 0.2s;
  }}
  .auth-footer .stButton > button:hover {{
      background: rgba(60, 60, 65, 0.2) !important;
      border-color: rgba(180, 160, 110, 0.6) !important;
      color: #d8c8a8 !important;
    border: 1px solid var(--brd-1) !important;
    color: var(--tx-0) !important;
    border-radius: var(--r-sm) !important;
    font-family: 'Crimson Pro', serif !important;
    font-size: 1.02rem !important;
    transition: var(--tx) !important;
    padding: 0.55rem 0.75rem !important;
}}
.stTextInput input:focus, .stTextArea textarea:focus {{
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-bg) !important;
    outline: none !important;
}}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {{
    color: var(--tx-2) !important;
    font-style: italic !important;
}}
label {{
    color: var(--tx-1) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.015em !important;
}}

/* ── Buttons ─────────────────────────────────── */
.stButton > button {{
    background: var(--bg-1) !important;
    border: 1px solid var(--brd-2) !important;
    color: var(--accent) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    border-radius: var(--r-sm) !important;
    padding: 0.5rem 1.4rem !important;
    transition: var(--tx) !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
}}
.stButton > button:hover {{
    background: var(--accent-bg) !important;
    border-color: var(--accent) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06) !important;
    color: var(--accent-hov) !important;
    transform: translateY(-1px) !important;
}}
.stButton > button:active {{
    transform: translateY(0) !important;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.08) !important;
}}
/* Primary action buttons (form submits) */
[data-testid="stFormSubmitButton"] > button {{
    background: var(--accent) !important;
    border: 1px solid var(--accent) !important;
    color: var(--accent-tx) !important;
    font-weight: 600 !important;
}}
[data-testid="stFormSubmitButton"] > button:hover {{
    background: var(--accent-hov) !important;
    border-color: var(--accent-hov) !important;
    color: var(--accent-tx) !important;
}}

/* ── Tabs ─────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    gap: 0;
    border-bottom: 1px solid var(--brd-1);
}}
.stTabs [data-baseweb="tab"] {{
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500;
    color: var(--tx-2) !important;
    padding: 0.55rem 1.1rem;
    border-bottom: 2px solid transparent;
    background: transparent !important;
    transition: color 0.2s var(--ease);
}}
.stTabs [aria-selected="true"] {{
    color: var(--tab-active) !important;
    border-bottom-color: var(--tab-active) !important;
}}
.stTabs [data-baseweb="tab-highlight"] {{
    background-color: var(--tab-active) !important;
}}

/* ── Spinner ──────────────────────────────────── */
[data-testid="stSpinner"] {{ color: var(--accent) !important; }}

/* ── Empty state ──────────────────────────────── */
.empty-state {{
    text-align: center;
    padding: 2rem 1rem;
    animation: fadeUp 0.5s var(--ease) both;
}}
.empty-state-icon {{
    width: 52px; height: 52px;
    margin: 0 auto 1rem auto;
    border-radius: 50%;
    background: var(--accent-bg);
    border: 1px dashed var(--brd-2);
    display: flex; align-items: center; justify-content: center;
    color: var(--tx-2);
}}
.empty-state p {{
    color: var(--tx-2) !important;
    font-style: italic;
    max-width: 360px; margin: 0 auto;
}}

/* ── Streamlit Overrides ──────────────────────── */
.stAlert {{ background: var(--bg-2) !important; border-color: var(--brd-1) !important; color: var(--tx-0) !important; border-radius: var(--r-sm) !important; }}
[data-testid="stExpander"] {{ background: var(--bg-1) !important; border: 1px solid var(--brd-1) !important; border-radius: var(--r) !important; }}
[data-testid="stExpander"]:hover {{ border-color: var(--brd-2) !important; }}
.stCheckbox label span {{ color: var(--tx-1) !important; font-family: 'Inter', sans-serif !important; font-size: 0.82rem !important; }}
[data-testid="stStatusWidget"] {{ background: var(--bg-1) !important; border: 1px solid var(--brd-1) !important; border-radius: var(--r) !important; }}
#MainMenu, footer, .stDeployButton {{ display: none; }}
[data-testid="stSidebarNav"] {{ display: none; }}

/* ── Kill empty space ────────────────────────── */
/* Reduce Streamlit's default block gap (the main source of whitespace) */
[data-testid="stVerticalBlock"] > div:has( > [data-testid="stMarkdownContainer"]:empty),
.element-container:has(> iframe[height="0"]) {{
    display: none !important;
}}
[data-testid="stVerticalBlock"] > div {{
    margin-bottom: 0 !important;
    padding-bottom: 0 !important;
}}
.block-container {{
    padding-top: 1.5rem !important;
    padding-bottom: 1rem !important;
}}
header[data-testid="stHeader"] {{
    background: var(--bg-0) !important;
}}

/* Toggle switch */
[data-testid="stToggle"] label {{
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important;
    color: var(--tx-1) !important;
}}
[data-testid="stToggle"] label span {{
    color: var(--tx-1) !important;
}}

/* Option menu overrides — force theme colors on all states */
.nav-link {{
    transition: all 0.2s var(--ease) !important;
    background-color: transparent !important;
}}
.nav-link:hover {{
    background-color: var(--bg-2) !important;
    color: var(--accent) !important;
}}
.nav-link-selected {{
    background-color: var(--accent-bg) !important;
    color: var(--accent) !important;
}}

/* Streamlit divider \u2014 less space */
[data-testid="stSidebar"] hr {{
    margin: 0.4rem 0 !important;
    border-color: var(--brd-1) !important;
}}
hr {{
    border-color: var(--brd-1) !important;
}}

/* ── Responsive ──────────────────────────────── */
@media (max-width: 768px) {{
    .book-container {{ flex-direction: column; margin: 1rem auto; }}
    .page-left, .page-right {{ transform: none !important; border-radius: var(--r) !important; }}
    .page-left {{ border-right: 1px solid var(--brd-1) !important; border-bottom: none; }}
    .page-left::after {{ display: none; }}
    .page-header h2 {{ font-size: 1.3rem !important; }}
    .page-subtitle {{ margin-left: 0; padding-left: 0; }}
    .prophecy-box {{ padding: 1.8rem 1.2rem; }}
    .auth-card {{ padding: 2rem 1.4rem; }}
    .app-title {{ font-size: 2rem; }}
    .chapter-title {{ font-size: 1.3rem !important; }}
    .card-3d {{ padding: 1.1rem; }}
}}
@media (max-width: 480px) {{
    .page-header {{ gap: 10px; }}
    .page-header-icon {{ width: 34px; height: 34px; }}
    .app-title {{ font-size: 1.6rem; }}
    .auth-card {{ padding: 1.5rem 1rem; }}
    .auth-blob1, .auth-blob2 {{ display: none; }}
}}
</style>

<!-- Ambient floating motes — theme-aware -->
<canvas id="mote-canvas" style="position:fixed;inset:0;width:100vw;height:100vh;pointer-events:none;z-index:-1;opacity:0.6;"></canvas>
<script>
(function() {{
    const c = document.getElementById('mote-canvas');
    if (!c) return;
    const ctx = c.getContext('2d');
    let W, H;
    function resize() {{ W = c.width = innerWidth; H = c.height = innerHeight; }}
    addEventListener('resize', resize); resize();

    const N = {'30' if IS_DARK else '18'};
    const pts = Array.from({{length: N}}, () => ({{
        x: Math.random()*W, y: Math.random()*H,
        r: Math.random()*1.2+0.3,
        vy: Math.random()*0.3+0.08,
        vx: (Math.random()-0.5)*0.15,
        a: Math.random()*{T['pAlpha']}+0.03
    }}));

    (function draw() {{
        ctx.clearRect(0,0,W,H);
        for (const p of pts) {{
            p.y -= p.vy; p.x += p.vx;
            if (p.y < -10) {{ p.y = H+10; p.x = Math.random()*W; }}
            ctx.beginPath();
            const g = ctx.createRadialGradient(p.x,p.y,0,p.x,p.y,p.r*3);
            g.addColorStop(0, 'rgba({T["pCol"]},'+p.a+')');
            g.addColorStop(1, 'rgba({T["pCol"]},0)');
            ctx.fillStyle = g;
            ctx.arc(p.x,p.y,p.r*3,0,Math.PI*2);
            ctx.fill();
        }}
        requestAnimationFrame(draw);
    }})();
}})();
</script>
""", unsafe_allow_html=True)

# 3D card tilt on mouse
components.html("""
<script>
document.addEventListener("mousemove", e => {
    const cards = window.parent.document.querySelectorAll('.card-3d');
    cards.forEach(card => {
        const r = card.getBoundingClientRect();
        const cx = e.clientX - r.left - r.width/2;
        const cy = e.clientY - r.top - r.height/2;
        card.style.transform = `rotateX(${-cy/30}deg) rotateY(${cx/30}deg) translateY(-3px)`;
    });
});
document.addEventListener("mouseleave", () => {
    window.parent.document.querySelectorAll('.card-3d').forEach(c => {
        c.style.transform = 'none';
    });
});
</script>
""", height=0)


# ─── Supabase ─────────────────────────────────────────────────────────────────

@st.cache_resource
def get_base_client() -> Client:
    """Unauthenticated Supabase client for auth flows only."""
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


def get_authed_client(access_token: str, refresh_token: str) -> Client:
    """Supabase client scoped to the user's session (respects RLS)."""
    client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client.auth.set_session(access_token, refresh_token)
    return client


# ─── Session ──────────────────────────────────────────────────────────────────

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


# ─── OAuth ────────────────────────────────────────────────────────────────────

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


def _get_google_oauth_url() -> str:
    """Get the Google OAuth URL via Supabase."""
    try:
        app_url = st.secrets.get("APP_URL", "http://localhost:8501")
        res = get_base_client().auth.sign_in_with_oauth({
            "provider": "google",
            "options": {"redirect_to": app_url},
        })
        return res.url
    except Exception as e:
        st.error(f"Could not prepare Google sign-in: {e}")
        return "#"


def _render_google_button(key: str = "google_login"):
    """Google sign-in: rendered using Streamlit components so Javascript execution can forcibly redirect the top window."""
    auth_url = _get_google_oauth_url()

    # Streamlit components render inside their own iframes. 
    # Use target="_blank" so we explicitly exit Streamlit entirely to do the Google auth. 
    # Background transparent per user request!
    components.html(f'''
    <style>
        body {{ margin: 0; padding: 0; display: flex; justify-content: center; background: transparent !important; }}
        .btn {{
            display: flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
            background: transparent;
            border: 1px solid rgba(130, 110, 70, 0.4);
            color: #d8c8a8;
            font-family: 'Inter', sans-serif;
            font-size: 0.88rem;
            font-weight: 500;
            border-radius: 8px;
            padding: 10px 16px;
            width: 100%;
            height: 40px;
            box-sizing: border-box;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .btn:hover {{
            background: rgba(60, 60, 65, 0.2);
            border-color: rgba(180, 160, 110, 0.6);
        }}
        .logo {{
            width: 18px; height: 18px;
            margin-right: 10px;
            flex-shrink: 0;
            background: url("data:image/svg+xml,%3Csvg viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z' fill='%234285F4'/%3E%3Cpath d='M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z' fill='%2334A853'/%3E%3Cpath d='M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z' fill='%23FBBC05'/%3E%3Cpath d='M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z' fill='%23EA4335'/%3E%3C/svg%3E") no-repeat center/contain;
        }}
    </style>
    <a class="btn" href="{auth_url}" target="_blank">
        <div class="logo"></div>
        <span>Continue with Google</span>
    </a>
    ''', height=45)

# ─── Auth Page ────────────────────────────────────────────────────────────────

def auth_page():
    handle_oauth_callback()
    if is_logged_in():
        return

    # Decorative background orbs (fixed, no layout impact)
    st.markdown('''<div class="auth-orbs-bg">
        <div class="orb orb-1"></div>
        <div class="orb orb-2"></div>
    </div>''', unsafe_allow_html=True)

    # Center auth content in a narrow column
    spacer_l, center, spacer_r = st.columns([1.3, 1, 1.3])

    with center:
        # Title block
        st.markdown(f'''
            <div class="auth-accent-line"></div>
            <div class="auth-title">Life as Lore</div>
            <div class="auth-sub">Transform your life into an epic fantasy chronicle</div>
        ''', unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["Sign In", "Create Account"])

        with tab_login:
            _login_form()

        with tab_signup:
            _signup_form()

        # Theme button — real clickable button
        st.markdown('<div class="auth-footer">', unsafe_allow_html=True)
        theme_label = "Switch to Dark Mode" if not IS_DARK else "Switch to Light Mode"
        if st.button(f"{'🌙' if not IS_DARK else '☀️'}  {theme_label}", key="auth_theme_btn", use_container_width=True):
            st.session_state.theme = "dark" if not IS_DARK else "light"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


def _login_form():
    with st.form("login"):
        email    = st.text_input("Email", placeholder="your@email.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submitted = st.form_submit_button("Sign In", use_container_width=True)

    if submitted:
        if not email or not password:
            st.error("Please fill in both fields.")
            return
        try:
            res = get_base_client().auth.sign_in_with_password({"email": email, "password": password})
            store_session(res.session)
            st.rerun()
        except Exception:
            st.error("Incorrect email or password.")

    st.markdown('<div class="auth-divider">or</div>', unsafe_allow_html=True)
    _render_google_button("google_login")


def _signup_form():
    with st.form("signup"):
        email    = st.text_input("Email", placeholder="your@email.com", key="su_email")
        password = st.text_input("Password", type="password", placeholder="At least 6 characters", key="su_pw")
        confirm  = st.text_input("Confirm password", type="password", placeholder="Re-enter password", key="su_pw2")
        submitted = st.form_submit_button("Create Account", use_container_width=True)

    if submitted:
        if not email or not password:
            st.error("Please fill in all fields.")
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
    _render_google_button("google_signup")


# ─── Rendering Helpers ────────────────────────────────────────────────────────

def render_page_header(icon_name: str, title: str, subtitle: str = ""):
    """Page header with icon badge and optional subtitle."""
    st.markdown(f'''
    <div class="page-header">
        <div class="page-header-icon">{icon(icon_name, T["accent"], 22)}</div>
        <h2>{title}</h2>
    </div>
    {"<p class='page-subtitle'>" + subtitle + "</p>" if subtitle else ""}
    ''', unsafe_allow_html=True)


def render_divider():
    st.markdown(f'<div class="lore-divider">{icon("sparkle", T["tx2"], 8)}</div>', unsafe_allow_html=True)


def render_empty(icon_name: str, text: str):
    st.markdown(f'''
    <div class="empty-state">
        <div class="empty-state-icon">{icon(icon_name, T["tx2"], 22)}</div>
        <p>{text}</p>
    </div>
    ''', unsafe_allow_html=True)


def render_section_label(label: str):
    st.markdown(f'<div class="section-label">{label}</div>', unsafe_allow_html=True)


def render_chapter(chapter: dict):
    """Display a chapter in the 3D open-book layout."""
    season = f'<div class="chapter-season">{chapter["season"]}</div>' if chapter.get("season") else ""
    paras = chapter["body"].strip().split("\n\n")
    body = "".join(f"<p>{p.strip()}</p>" for p in paras if p.strip())

    st.markdown(f"""
    <div class="book-container">
        <div class="page-left">
            <div class="chapter-num">Chapter {chapter["chapter_num"]}</div>
            <div class="chapter-title">{chapter["title"]}</div>
            {season}
        </div>
        <div class="page-right">
            <div class="chapter-body">{body}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def lore_card(title: str, subtitle: str, desc: str, icon_name: str = "shield"):
    """Character card with icon badge and 3D tilt."""
    st.markdown(f"""
    <div class="card-3d-wrapper">
        <div class="card-3d">
            <div class="card-3d-icon">{icon(icon_name, T["accent"], 17)}</div>
            <div class="card-3d-title">{title}</div>
            <div class="card-3d-sub">{subtitle}</div>
            <div class="card-3d-desc">{desc}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_quest_block(q: dict, css_class: str, label: str, ico: str):
    """Notion-style quest block with status chip."""
    desc = q.get("description") or q.get("resolution") or ""
    st.markdown(f"""
    <div class="quest-block">
        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:6px;">
            <div class="quest-block-title">{q.get("lore_title", q.get("title", ""))}</div>
            <span class="quest-chip {css_class}">{icon(ico, "currentColor", 11)} {label}</span>
        </div>
        {"<div class='quest-block-desc'>" + desc + "</div>" if desc else ""}
        <div class="quest-block-real">{q.get("title", "")}</div>
    </div>
    """, unsafe_allow_html=True)


# ─── Genesis ──────────────────────────────────────────────────────────────────

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
        submitted = st.form_submit_button("Begin the Chronicle", use_container_width=True)

    if submitted and real_name and intro:
        with st.spinner("The world is being named..."):
            identity = agents.generate_hero_identity(real_name, intro)
            db.create_world_state(client, user_id, identity["hero_name"], identity["world_name"])
        st.success(f"Welcome, **{identity['hero_name']}**. Your world — *{identity['world_name']}* — awaits.")
        st.rerun()


# ─── Sidebar ──────────────────────────────────────────────────────────────────

def sidebar(world: dict) -> str:
    with st.sidebar:
        # Brand mark
        st.markdown(f"""
        <div class="sidebar-brand">
            <div class="sidebar-brand-icon">{icon("book", T["accent"], 16)}</div>
            <div class="sidebar-brand-text">Life as Lore</div>
        </div>
        """, unsafe_allow_html=True)

        # World info
        st.markdown(f"""
        <div class="sidebar-world">
            <div class="sidebar-world-name">{world["world_name"]}</div>
            <div class="sidebar-hero">{world["hero_name"]}</div>
            {"<div class='sidebar-era'>" + icon("compass", T['accent'], 10) + " " + world["current_era"] + "</div>" if world.get("current_era") else ""}
            <div class="sidebar-stat">
                {icon("scroll", T["tx1"], 14)}
                <span><b>{world["total_chapters"]}</b> chapters written</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation — proper vector icons via Bootstrap Icons
        page = option_menu(
            menu_title=None,
            options=["Narrate", "Chronicle", "Characters", "Quests", "Prophecy"],
            icons=["vector-pen", "journal-richtext", "people", "lightning-charge", "gem"],
            default_index=0,
            key="nav_menu",
            styles={
                "container": {"padding": "0 !important", "background-color": "transparent"},
                "icon": {"color": T["accent"], "font-size": "15px"},
                "nav-link": {
                    "font-family": "'Inter', sans-serif",
                    "font-size": "0.88rem",
                    "text-align": "left",
                    "padding": "0.5rem 0.75rem",
                    "margin": "2px 0",
                    "border-radius": "6px",
                    "color": T["tx1"],
                    "--hover-color": T["bg2"],
                },
                "nav-link-selected": {
                    "background-color": T["accentBg"],
                    "color": T["accent"],
                    "font-weight": "500",
                },
            },
        )

        st.divider()

        # Theme button — visible, clickable
        theme_label = "Dark Mode" if not IS_DARK else "Light Mode"
        st.markdown('<div class="theme-switch-btn">', unsafe_allow_html=True)
        if st.button(f"{'🌙' if not IS_DARK else '☀️'}  {theme_label}", key="sidebar_theme_btn", use_container_width=True):
            st.session_state.theme = "dark" if not IS_DARK else "light"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="sidebar-email">{st.session_state.get("user_email", "")}</div>', unsafe_allow_html=True)

        if st.button("Sign Out", use_container_width=True):
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
                       "What has been happening in your life? The mundane and the momentous alike.")

    with st.form("narrate_form"):
        entry_text = st.text_area(
            "Your narration",
            placeholder="I've been feeling stuck on this project for weeks. My friend keeps cancelling plans and I don't know if something is wrong. There's a new opportunity at work but it scares me...",
            height=200,
            label_visibility="collapsed",
        )
        submit = st.form_submit_button("Weave into the Lore", use_container_width=True)

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

    # Chapter count
    st.markdown(f'<div class="section-label">{len(chapters)} chapter{"s" if len(chapters) != 1 else ""} total</div>', unsafe_allow_html=True)

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
    "the lost soul": "compass",
    "the gatekeeper": "scroll",
    "the shadow": "moon",
}


def page_characters(client: Client):
    render_page_header("users", "Characters of the World",
                       "The souls who walk beside you, rendered in the language of myth.")
    chars = db.get_all_characters(client)

    if not chars:
        render_empty("users", "No characters have emerged yet. Narrate your life to let them appear.")
        return

    render_section_label(f"{len(chars)} character{'s' if len(chars) != 1 else ''}")

    cols = st.columns(2)
    for i, c in enumerate(chars):
        with cols[i % 2]:
            archetype_key = c.get("archetype", "").lower()
            card_icon = ARCHETYPE_ICONS.get(archetype_key, "shield")
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
        render_empty("eye", "The oracle needs more of your story. Write at least three entries first.")
        return

    existing_prophecy = world.get("prophecy")
    if existing_prophecy:
        st.markdown(f'''
        <div class="prophecy-box">
            <div class="prophecy-icon">{icon("crystal", T["accent"], 22)}</div>
            <div class="prophecy-text">{existing_prophecy}</div>
        </div>
        ''', unsafe_allow_html=True)

    btn_label = "Consult the Oracle" if not existing_prophecy else "Read the Omens Again"
    if st.button(btn_label, use_container_width=False):
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
            <div class="prophecy-icon">{icon("crystal", T["accent"], 22)}</div>
            <div class="prophecy-text">{prophecy}</div>
        </div>
        ''', unsafe_allow_html=True)
        if new_era and new_era.lower() != "null":
            st.caption(f"The era shifts: *{new_era}*")
        st.rerun()


# ─── Router ───────────────────────────────────────────────────────────────────

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
