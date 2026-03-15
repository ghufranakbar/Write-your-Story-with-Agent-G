"""
app.py — Life as Lore (multi-user)
A personal mythology engine. Narrate your life. Read it as epic fantasy.
Each user gets their own completely private, isolated chronicle.
"""

import streamlit as st
from supabase import create_client, Client
import database as db
import agents

# ── Page Config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Life as Lore",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS & Scripts — 3D Dark Fantasy Aesthetic ─────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700&family=Crimson+Pro:ital,wght@0,300..900;1,300..900&family=Uncial+Antiqua&display=swap');

/* Base & Vignette Overlay */
html, body, [class*="css"] { 
    background-color: #080608 !important; 
    color: #e2d8c3 !important; 
}
.stApp { 
    background: radial-gradient(circle at 50% 50%, rgba(20, 10, 25, 0.3) 0%, #080608 100%) !important; 
}
.stApp::after {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: radial-gradient(circle at center, transparent 30%, rgba(0,0,0,0.6) 100%);
    pointer-events: none;
    z-index: 9999;
}

/* Sidebar - Dark Leather */
[data-testid="stSidebar"] { 
    background: repeating-linear-gradient(45deg, #0f0a0c 0%, #171113 4%, #0f0a0c 8%) !important;
    border-right: 4px ridge #c9a84c; 
    box-shadow: inset -5px 0 15px rgba(0,0,0,0.8);
}
[data-testid="stSidebar"] * { color: #d1b882 !important; font-family: 'Crimson Pro', serif !important; }
[data-testid="stSidebar"] h3 { font-family: 'Uncial Antiqua', serif !important; text-shadow: 0 0 5px rgba(201,168,76,0.3); }
[data-testid="stSidebarHr"] {
    border-top: 2px dashed #c9a84c;
    background: none;
    opacity: 0.5;
}

/* Typography */
h1, h2, h3 { 
    font-family: 'Uncial Antiqua', serif !important; 
    color: #c9a84c !important; 
    letter-spacing: 0.05em; 
    text-shadow: 1px 2px 4px rgba(0,0,0,0.8);
}
.app-title { font-family: 'Cinzel Decorative', serif !important; font-size: 3rem; text-align: center; color: #e8d9b8; text-shadow: 0 0 15px rgba(201, 168, 76, 0.5); margin-top:2rem; }
p, li, div { font-family: 'Crimson Pro', serif !important; font-size: 1.15rem !important; line-height: 1.8 !important; }

/* 3D Open Book (Chapters) */
.book-container {
    display: flex;
    flex-direction: row;
    max-width: 900px;
    margin: 3rem auto;
    perspective: 1200px;
    filter: drop-shadow(0 20px 30px rgba(0,0,0,0.9));
}
.page-left, .page-right {
    flex: 1;
    background: linear-gradient(135deg, #1a1617, #0e0b0c);
    padding: 3rem 2rem;
    box-shadow: 
        inset 0 1px 3px rgba(255,255,255,0.05),
        inset 0 -5px 15px rgba(201,168,76,0.1),
        0 10px 20px rgba(0,0,0,0.5);
    border: 1px solid #2a2218;
}
.page-left {
    transform: rotateY(3deg);
    transform-origin: right center;
    border-right: 3px double #0a0708;
    display: flex;
    flex-direction: column;
    justify-content: center;
    border-radius: 8px 0 0 8px;
}
.page-right {
    transform: rotateY(-3deg);
    transform-origin: left center;
    border-left: 1px solid #33291f;
    border-radius: 0 8px 8px 0;
}

.chapter-title { font-family: 'Uncial Antiqua', serif !important; font-size: 2rem !important; color: #c9a84c !important; text-align: center; letter-spacing: 0.05em; margin-bottom: 0.5rem; text-shadow: 0 2px 4px rgba(0,0,0,0.8); }
.chapter-num { font-family: 'Cinzel Decorative', serif !important; font-size: 1rem !important; color: #8c764c !important; text-align: center; letter-spacing: 0.2em; text-transform: uppercase; margin-bottom: 1rem; }
.chapter-season { font-family: 'Crimson Pro', serif !important; font-size: 1rem !important; color: #7a6a4a !important; text-align: center; font-style: italic; margin-bottom: 2rem; }
.chapter-body { font-family: 'Crimson Pro', serif !important; font-size: 1.25rem !important; line-height: 1.9 !important; color: #e2d8c3; }
.chapter-body p:first-child::first-letter { 
    font-size: 4rem; 
    font-family: 'Uncial Antiqua', serif; 
    float: left; 
    line-height: 0.8; 
    padding-right: 12px; 
    color: #c9a84c; 
    text-shadow: 2px 2px 0px rgba(0,0,0,0.6), 0 0 8px rgba(201,168,76,0.5); 
}

/* Pulsing Ornaments */
@keyframes pulse-golds {
    0% { color: #4a3f28; text-shadow: 0 0 2px transparent; }
    50% { color: #c9a84c; text-shadow: 0 0 8px #c9a84c; }
    100% { color: #4a3f28; text-shadow: 0 0 2px transparent; }
}
.ornament { text-align: center; font-size: 1.5rem; margin: 2rem 0; letter-spacing: 0.5rem; animation: pulse-golds 3s infinite; }

/* 3D Cards */
.card-3d-wrapper {
    perspective: 1000px;
    margin-bottom: 1rem;
}
.card-3d {
    background: linear-gradient(to bottom right, #1a1617, #110e0c);
    border: 1px solid #3a2e22;
    border-radius: 6px;
    padding: 1.5rem;
    box-shadow: 
        0 10px 20px rgba(0,0,0,0.6), 
        inset 0 1px 1px rgba(255, 255, 255, 0.05),
        inset 0 -15px 15px -15px rgba(201, 168, 76, 0.3);
    transition: transform 0.1s;
    transform-style: preserve-3d;
}
.card-3d-title { font-family: 'Uncial Antiqua', serif; font-size: 1.2rem; color: #c9a84c; margin-bottom: 0.3rem; }
.card-3d-sub { font-family: 'Cinzel Decorative', serif; font-size: 0.8rem; color: #8c764c; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.8rem; }
.card-3d-desc { font-family: 'Crimson Pro', serif; font-size: 1.05rem; color: #b8a98a; font-style: italic; }

.char-glow { text-shadow: 0 0 8px rgba(201, 168, 76, 0.4); font-weight: bold; color:#e8d9b8; }

/* Quest Badges */
.badge-active, .badge-done, .badge-abandoned {
    display: inline-block;
    padding: 0.2rem 0.8rem;
    border-radius: 20px;
    font-family: 'Cinzel Decorative', serif;
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    box-shadow: 
        inset 0 2px 3px rgba(255,255,255,0.1),
        inset 0 -2px 3px rgba(0,0,0,0.5),
        0 4px 6px rgba(0,0,0,0.6);
    text-transform: uppercase;
}
.badge-active   { background: #2a3a1f; color: #9bcd7a; border: 1px solid #4a6a2f; }
.badge-done     { background: #1c2c3a; color: #7ab3d6; border: 1px solid #2f4f6a; }
.badge-abandoned{ background: #3a221f; color: #cd7a7a; border: 1px solid #6a322f; }

/* Prophecy Box */
.prophecy-box { 
    border: 2px solid #5a4a2a; 
    border-radius: 8px; 
    background: linear-gradient(180deg, #141012, #080608); 
    padding: 3rem; 
    text-align: center; 
    max-width: 700px; 
    margin: 2rem auto;
    box-shadow: 0 15px 35px rgba(0,0,0,0.8), inset 0 0 20px rgba(201,168,76,0.1);
    transform: perspective(1000px) rotateX(2deg);
}
.prophecy-text { font-family: 'Crimson Pro', serif !important; font-size: 1.4rem !important; font-style: italic; color: #c9a84c !important; line-height: 2 !important; white-space: pre-line; text-shadow: 0 0 8px rgba(201,168,76,0.3); }

/* Auth Form & Rune Background */
.auth-wrapper {
    position: relative;
    max-width: 450px;
    margin: 5rem auto;
    perspective: 1200px;
}
@keyframes rotate-runes {
    0% { transform: translate(-50%, -50%) rotate(0deg); }
    100% { transform: translate(-50%, -50%) rotate(360deg); }
}
.rune-bg {
    position: absolute;
    top: 50%; left: 50%;
    width: 600px; height: 600px;
    background: repeating-conic-gradient(
        from 0deg,
        rgba(201, 168, 76, 0.02) 0deg 10deg,
        transparent 10deg 20deg
    );
    border-radius: 50%;
    animation: rotate-runes 60s linear infinite;
    z-index: 0;
    pointer-events: none;
    mask-image: radial-gradient(circle, black 30%, transparent 70%);
    -webkit-mask-image: radial-gradient(circle, black 30%, transparent 70%);
}
.auth-card { 
    position: relative;
    z-index: 1;
    background: linear-gradient(135deg, #161214, #0b0809); 
    border: 1px solid #3a2e22; 
    border-radius: 8px; 
    padding: 3rem 2rem;
    box-shadow: 0 30px 50px rgba(0,0,0,0.9), inset 0 2px 2px rgba(255,255,255,0.05);
    transform: rotateX(5deg) translateY(-20px);
}
.auth-title { font-family: 'Cinzel Decorative', serif; font-size: 2.5rem; color: #e8d9b8; text-align: center; margin-bottom: 0.5rem; text-shadow: 0 0 10px rgba(201,168,76,0.4); }
.auth-sub { font-family: 'Crimson Pro', serif; text-align: center; color: #8c764c; font-size: 1.1rem; font-style: italic; margin-bottom: 2rem; }
.auth-divider { display: flex; align-items: center; gap: 10px; margin: 1.5rem 0; color: #5a4a2a; font-family: 'Cinzel Decorative', serif; font-size: 0.8rem; }
.auth-divider::before, .auth-divider::after { content: ''; flex: 1; height: 1px; background: #3a2e22; }

/* Streamlit Inputs */
.stTextInput input { background: #0f0b0d !important; border: 1px solid #3a2e22 !important; color: #e2d8c3 !important; border-radius: 4px !important; font-family: 'Crimson Pro', serif !important; font-size: 1.1rem !important; }
.stTextInput input:focus { border-color: #c9a84c !important; box-shadow: 0 0 8px rgba(201, 168, 76, 0.2) !important; }
.stTextArea textarea { background: #0f0b0d !important; border: 1px solid #3a2e22 !important; color: #e2d8c3 !important; font-family: 'Crimson Pro', serif !important; font-size: 1.1rem !important; border-radius: 4px !important; }
label { color: #b8a98a !important; font-family: 'Cinzel Decorative', serif !important; font-size: 0.85rem !important; letter-spacing: 0.05em !important; }

/* 3D Press Buttons */
.stButton > button { 
    background: linear-gradient(180deg, #2a2015, #140f0a) !important; 
    border: 1px solid #5a4a2a !important; 
    color: #c9a84c !important; 
    font-family: 'Uncial Antiqua', serif !important; 
    font-size: 1.1rem !important; 
    border-radius: 4px !important; 
    padding: 0.6rem 2rem !important; 
    transition: all 0.15s ease !important; 
    box-shadow: 0 6px 15px rgba(0,0,0,0.6), inset 0 1px 1px rgba(255,255,255,0.1) !important;
    transform: translateY(0);
}
.stButton > button:hover { 
    background: linear-gradient(180deg, #35291b, #1a140d) !important; 
    border-color: #c9a84c !important; 
    box-shadow: 0 8px 20px rgba(0,0,0,0.8), inset 0 1px 1px rgba(255,255,255,0.2) !important;
    color: #f4e8cb !important;
}
.stButton > button:active {
    transform: translateY(2px) !important;
    box-shadow: 0 2px 5px rgba(0,0,0,0.8), inset 0 2px 5px rgba(0,0,0,0.5) !important;
}

/* Quill Spinner */
@keyframes quill-write {
    0% { transform: translate(0, 0) rotate(0deg); }
    25% { transform: translate(10px, -5px) rotate(10deg); }
    50% { transform: translate(20px, 0) rotate(-5deg); }
    75% { transform: translate(30px, -5px) rotate(15deg); }
    100% { transform: translate(40px, 0) rotate(0deg); opacity: 0; }
}
[data-testid="stSpinner"] > div { display: none !important; }
[data-testid="stSpinner"]::before {
    content: '';
    display: inline-block;
    width: 24px; height: 24px;
    background-image: url('data:image/svg+xml;utf8,<svg fill="%23c9a84c" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M20.7,3.3c-0.4-0.4-1.1-0.4-1.5,0c-0.5,0.5-2.2,2.4-3.5,4.9c-2.3,4.4-1.9,8.5-1.9,8.6c0,0.2,0.1,0.4,0.3,0.5c0.1,0.1,0.3,0.1,0.4,0.1c0.1,0,0.2,0,0.3-0.1c0.1-0.1,4.2-2.1,6.5-7C23.1,6.9,21.5,3.9,20.7,3.3z M15,18.8c0.1-0.9,0.3-1.9,0.7-2.9L8.4,23.3l-2.7-0.7L5,19.9l7.3-7.3c-1.1,0.5-2.2,1.2-3.1,2.1L8.5,14L7,12.5l0.7-0.7c1-1,2.2-1.7,3.4-2.1L3.8,2.4L4.5,1L7.2,1.7l7.4,7.4c0-0.1,0.1-0.2,0.1-0.3l1.8,1.8C16.8,11.8,17,13.2,15,18.8z"/></svg>');
    background-size: contain;
    background-repeat: no-repeat;
    animation: quill-write 1.5s infinite;
    margin-right: 15px;
}
.stAlert { background: #161214 !important; border-color: #3a2e22 !important; color: #e2d8c3 !important; }
#MainMenu, footer, .stDeployButton { display: none; }
</style>

<!-- Canvas for Embers -->
<canvas id="ember-bg" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: -1;"></canvas>
<script>
(function() {
    const canvas = document.getElementById('ember-bg');
    if(!canvas) return;
    const ctx = canvas.getContext('2d');
    let width, height;
    function resize() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resize);
    resize();
    const embers = [];
    for(let i=0; i<80; i++) {
        embers.push({
            x: Math.random() * width,
            y: Math.random() * height,
            size: Math.random() * 2 + 0.5,
            speedY: Math.random() * 1 + 0.5,
            speedX: (Math.random() - 0.5) * 0.5,
            opacity: Math.random() * 0.5 + 0.1
        });
    }
    function draw() {
        ctx.clearRect(0, 0, width, height);
        embers.forEach(e => {
            e.y -= e.speedY;
            e.x += e.speedX;
            if(e.y < -10) { e.y = height + 10; e.x = Math.random() * width; }
            ctx.fillStyle = `rgba(201, 168, 76, ${e.opacity})`;
            ctx.beginPath();
            ctx.arc(e.x, e.y, e.size, 0, Math.PI * 2);
            ctx.fill();
        });
        requestAnimationFrame(draw);
    }
    draw();
})();
</script>
""", unsafe_allow_html=True)

# Inject 3D Mousemove script via st.components.v1
import streamlit.components.v1 as components
components.html("""
<script>
document.addEventListener("mousemove", (e) => {
    const cards = window.parent.document.querySelectorAll('.card-3d');
    cards.forEach(card => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width/2;
        const y = e.clientY - rect.top - rect.height/2;
        const rotateX = -y / 20;
        const rotateY = x / 20;
        card.style.transform = `rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
    });
});
document.addEventListener("mouseout", () => {
    const cards = window.parent.document.querySelectorAll('.card-3d');
    cards.forEach(card => { card.style.transform = 'rotateX(0) rotateY(0) translateY(0)'; });
});
</script>
""", height=0)



# ── Supabase client factory ───────────────────────────────────────────────────

@st.cache_resource
def get_base_client() -> Client:
    """Unauthenticated client — used only for auth operations (sign in / sign up)."""
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


def get_authed_client(access_token: str, refresh_token: str) -> Client:
    """
    Returns a Supabase client with the user's session attached.
    All DB calls through this client will respect RLS and scope to this user.
    """
    client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client.auth.set_session(access_token, refresh_token)
    return client


# ── Session helpers ───────────────────────────────────────────────────────────

def is_logged_in() -> bool:
    return "access_token" in st.session_state and st.session_state.access_token is not None


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
    for key in ["access_token", "refresh_token", "user_id", "user_email"]:
        st.session_state.pop(key, None)


# ── OAuth callback handler ────────────────────────────────────────────────────

def handle_oauth_callback():
    """
    After Google OAuth, Supabase redirects to your app with ?code=...
    We detect it here and exchange it for a session.
    """
    params = st.query_params
    code = params.get("code")
    if code and not is_logged_in():
        try:
            client = get_base_client()
            res = client.auth.exchange_code_for_session({"auth_code": code})
            if res.session:
                store_session(res.session)
                st.query_params.clear()
                st.rerun()
        except Exception as e:
            st.error(f"OAuth error: {e}")


# ── Auth Pages ────────────────────────────────────────────────────────────────

def auth_page():
    handle_oauth_callback()
    if is_logged_in():
        return

    st.markdown('''
    <div class="auth-wrapper">
        <div class="rune-bg"></div>
        <div class="auth-card">
            <div class="auth-title">Life as Lore</div>
            <div class="auth-sub">Every life is an epic. Yours begins here.</div>
            <div class="ornament">✦ ✦ ✦</div>
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
            client = get_base_client()
            res = client.auth.sign_in_with_password({"email": email, "password": password})
            store_session(res.session)
            st.rerun()
        except Exception as e:
            st.error("Incorrect email or password.")

    # Google OAuth
    st.markdown('<div class="auth-divider">or</div>', unsafe_allow_html=True)
    if st.button("Continue with Google"):
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
            client = get_base_client()
            res = client.auth.sign_up({"email": email, "password": password})
            if res.session:
                # Email confirmation disabled in Supabase → immediate session
                store_session(res.session)
                st.rerun()
            else:
                # Email confirmation enabled → tell user to check inbox
                st.success("Account created! Check your email to confirm, then sign in.")
        except Exception as e:
            st.error(f"Could not create account: {e}")

    st.markdown('<div class="auth-divider">or</div>', unsafe_allow_html=True)
    if st.button("Sign up with Google", key="google_signup"):
        _start_google_oauth()


def _start_google_oauth():
    """
    Kicks off the Google OAuth flow.
    The redirect_to URL must be whitelisted in:
    Supabase dashboard → Authentication → URL Configuration → Redirect URLs
    """
    try:
        client = get_base_client()
        # On Streamlit Cloud your URL is https://<your-app>.streamlit.app
        # Change this if you use a custom domain
        app_url = st.secrets.get("APP_URL", "http://localhost:8501")
        res = client.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {"redirect_to": app_url},
        })
        # Redirect the browser to Google
        st.markdown(f'<meta http-equiv="refresh" content="0; url={res.url}">', unsafe_allow_html=True)
        st.stop()
    except Exception as e:
        st.error(f"Could not start Google sign-in: {e}")


# ── Helpers ───────────────────────────────────────────────────────────────────

def render_chapter(chapter: dict):
    season_html = f'<div class="chapter-season">{chapter["season"]}</div>' if chapter.get("season") else ""
    paragraphs = chapter["body"].strip().split("\n\n")
    body_html = "".join(f"<p>{p.strip()}</p>" for p in paragraphs if p.strip())
    
    st.markdown(f"""
    <div class="book-container">
        <div class="page-left">
            <div class="chapter-num">Chapter {chapter["chapter_num"]}</div>
            <div class="chapter-title">{chapter["title"]}</div>
            {season_html}
            <div class="ornament">✦ ✦ ✦</div>
        </div>
        <div class="page-right">
            <div class="chapter-body">
                {body_html}
            </div>
            <div class="ornament" style="font-size: 1rem; margin-top:3rem;">— ✦ —</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def lore_card(title: str, subtitle: str, desc: str):
    st.markdown(f"""
    <div class="card-3d-wrapper">
        <div class="card-3d">
            <div class="card-3d-title char-glow">{title}</div>
            <div class="card-3d-sub">{subtitle}</div>
            <div class="card-3d-desc">{desc}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Genesis (first-time setup per user) ──────────────────────────────────────

def genesis_page(client: Client, user_id: str):
    st.markdown('<div class="app-title">Life as Lore</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;color:#b8a98a;font-style:italic;font-family:\'Crimson Pro\',serif;font-size:1.2rem;">Your world is waiting to be named.</p>', unsafe_allow_html=True)
    st.markdown('<div class="ornament">✦ ✦ ✦</div>', unsafe_allow_html=True)

    with st.form("genesis"):
        real_name = st.text_input("Your name", placeholder="What do people call you?")
        intro = st.text_area(
            "Tell me about yourself",
            placeholder="Where are you in life right now? What are you working on, struggling with, hoping for? A few sentences is enough.",
            height=120,
        )
        submitted = st.form_submit_button("Begin the Chronicle")

    if submitted and real_name and intro:
        with st.spinner("The world is being named..."):
            identity = agents.generate_hero_identity(real_name, intro)
            db.create_world_state(client, user_id, identity["hero_name"], identity["world_name"])
        st.success(f"Welcome, **{identity['hero_name']}**. Your world — *{identity['world_name']}* — awaits.")
        st.rerun()


# ── Sidebar ───────────────────────────────────────────────────────────────────

def sidebar(world: dict) -> str:
    with st.sidebar:
        st.markdown(f"### {world['world_name']}")
        st.markdown(f"*{world['hero_name']}*")
        if world.get("current_era"):
            st.markdown(f"**{world['current_era']}**")
        st.markdown(f"📖 {world['total_chapters']} chapters written")
        st.divider()

        page = st.radio(
            "Navigate",
            ["📜 Narrate", "📖 Chronicle", "🧙 Characters", "⚔️ Quests", "🔮 Prophecy"],
            label_visibility="collapsed",
        )

        st.divider()
        st.caption(st.session_state.get("user_email", ""))
        if st.button("Sign Out"):
            try:
                get_base_client().auth.sign_out()
            except Exception:
                pass
            clear_session()
            st.rerun()

        return page


# ── Page: Narrate ─────────────────────────────────────────────────────────────

def page_narrate(client: Client, user_id: str, world: dict):
    st.markdown("## Speak Your Truth")
    st.markdown("*What has been happening in your life? Speak freely — the mundane and the momentous alike.*")

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

            st.write("Updating the quests...")
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
            db.save_chapter(client, user_id, entry["id"], chapter_data["title"], chapter_data["body"], chapter_data["season"])

            if chapter_data.get("season"):
                db.update_world_state(client, {"current_era": chapter_data["season"]})

            status.update(label="The chapter is written.", state="complete")

        st.markdown('<div class="ornament">✦ ✦ ✦</div>', unsafe_allow_html=True)
        render_chapter({**chapter_data, "chapter_num": world["total_chapters"] + 1})


# ── Page: Chronicle ───────────────────────────────────────────────────────────

def page_chronicle(client: Client):
    st.markdown("## The Chronicle")
    chapters = db.get_all_chapters(client)

    if not chapters:
        st.markdown("*The pages are blank. Narrate your first entry to begin the chronicle.*")
        return

    show_all = st.checkbox("Show all chapters", value=False)
    display  = chapters if show_all else chapters[-3:]

    for ch in reversed(display):
        render_chapter(ch)


# ── Page: Characters ──────────────────────────────────────────────────────────

def page_characters(client: Client):
    st.markdown("## Characters of the World")
    chars = db.get_all_characters(client)

    if not chars:
        st.markdown("*No characters have emerged yet. Narrate your life to let them appear.*")
        return

    cols = st.columns(2)
    for i, c in enumerate(chars):
        with cols[i % 2]:
            lore_card(
                c["lore_name"],
                f"{c['archetype']}  ·  known as {c['real_name']}",
                c.get("description", ""),
            )


# ── Page: Quests ──────────────────────────────────────────────────────────────

def page_quests(client: Client):
    st.markdown("## The Book of Quests")
    quests = db.get_all_quests(client)

    if not quests:
        st.markdown("*No quests have been recorded. Mention your goals and struggles when you narrate.*")
        return

    active = [q for q in quests if q["status"] == "active"]
    done   = [q for q in quests if q["status"] == "completed"]
    lost   = [q for q in quests if q["status"] == "abandoned"]

    if active:
        st.markdown("#### Active Quests")
        for q in active:
            with st.expander(q["lore_title"]):
                st.markdown('<span class="badge-active">⚔ ONGOING</span>', unsafe_allow_html=True)
                st.markdown(f"*{q.get('description', '')}*")
                st.caption(f"Real goal: {q['title']}")

    if done:
        st.markdown("#### Completed")
        for q in done:
            with st.expander(q["lore_title"]):
                st.markdown('<span class="badge-done">✦ COMPLETED</span>', unsafe_allow_html=True)
                if q.get("resolution"):
                    st.markdown(f"*{q['resolution']}*")

    if lost:
        st.markdown("#### Abandoned")
        for q in lost:
            with st.expander(q["lore_title"]):
                st.markdown('<span class="badge-abandoned">— ABANDONED</span>', unsafe_allow_html=True)


# ── Page: Prophecy ────────────────────────────────────────────────────────────

def page_prophecy(client: Client, world: dict):
    st.markdown("## The Prophecy")
    st.markdown("*Read the arc of your story so far. Let the oracle speak.*")

    if world["total_chapters"] < 3:
        st.markdown("*The oracle needs more chapters to read. Write at least three entries first.*")
        return

    existing_prophecy = world.get("prophecy")
    if existing_prophecy:
        st.markdown('<div class="prophecy-box">', unsafe_allow_html=True)
        st.markdown(f'<div class="prophecy-text">{existing_prophecy}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("")

    if st.button("Consult the Oracle" if not existing_prophecy else "Read the Omens Again"):
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

        st.markdown('<div class="prophecy-box">', unsafe_allow_html=True)
        st.markdown(f'<div class="prophecy-text">{prophecy}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        if new_era and new_era.lower() != "null":
            st.caption(f"The era shifts: *{new_era}*")
        st.rerun()


# ── Main Router ───────────────────────────────────────────────────────────────

def main():
    # Handle Google OAuth callback before anything else
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
