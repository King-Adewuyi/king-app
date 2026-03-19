
"""
King David Score Compiler
Always-visible sidebar · Hamburger toggle · Mobile responsive · Light / Dark
"""

import streamlit as st
import pandas as pd
import io, hashlib, time

# ── page config — sidebar EXPANDED always ──────────────────────────────────
st.set_page_config(
    page_title="King David Score Compiler",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── theme tokens ────────────────────────────────────────────────────────────
LIGHT = dict(
    app_bg="#F4F2EE", sb_bg="#1C1F30", sb_text="#D4D0C8", sb_muted="#52566A",
    sb_gold="#C9A84C", card="#FFFFFF", border="#E2DED6", panel="#EDEBE4",
    text1="#14162A", text2="#4E4C64", muted="#8E8AA0",
    gold="#9A6E00", gold_bg="#FEF7E6", gold_bd="#D4B060",
    inp="#FFFFFF", inp_bd="#C8C4D0", div="#E2DED6",
    btn_bg="#1C1F30", btn_fg="#FFFFFF",
)
DARK = dict(
    app_bg="#111220", sb_bg="#0A0B14", sb_text="#C8C4B8", sb_muted="#484C60",
    sb_gold="#C9A84C", card="#181A28", border="#252838", panel="#141526",
    text1="#ECEAF5", text2="#9C98B8", muted="#545670",
    gold="#C9A84C", gold_bg="#1C1600", gold_bd="#6A5010",
    inp="#0A0B14", inp_bd="#252838", div="#1E2030",
    btn_bg="#C9A84C", btn_fg="#0A0B14",
)

def T():
    return DARK if st.session_state.get("theme") == "dark" else LIGHT

# ── helpers ─────────────────────────────────────────────────────────────────
def hp(p):   return hashlib.sha256(p.encode()).hexdigest()
def uid():   return str(int(time.time()*1_000_000) + id(object()))
def ini(n):
    p = n.strip().split()
    return (p[0][0]+p[-1][0]).upper() if len(p)>=2 else n[:2].upper()
def me():        return st.session_state.get("current_user")
def is_root():   return me() and me()["role"]=="root_admin"
def is_admin():  return me() and me()["role"] in ("root_admin","super_admin")

# ── session init ─────────────────────────────────────────────────────────────
def init():
    if "users" not in st.session_state:
        st.session_state.users = {"root":{"id":"root","username":"root",
            "password":hp("root1234"),"display_name":"Root Administrator","role":"root_admin"}}
    for k,v in [("criteria",[
            {"id":1,"name":"Dressing & Appearance","max":5},
            {"id":2,"name":"Aims & Objectives","max":10},
            {"id":3,"name":"Presentation Delivery","max":20},
            {"id":4,"name":"Content & Knowledge","max":20},
            {"id":5,"name":"Response to Questions","max":15},
        ]),("scores",[]),("logged_in",False),("current_user",None),
        ("nav_page",None),("theme","light")]:
        if k not in st.session_state: st.session_state[k]=v
init()

# ── results ──────────────────────────────────────────────────────────────────
def get_results(lf=None):
    sc = st.session_state.scores
    if lf: sc=[s for s in sc if s.get("lecturer_id")==lf]
    if not sc: return pd.DataFrame()
    df=pd.DataFrame(sc)
    cc=[f"crit_{c['id']}" for c in st.session_state.criteria]
    for col in cc:
        if col not in df.columns: df[col]=None
    df[cc]=df[cc].apply(pd.to_numeric,errors="coerce")
    if lf: return df
    g=df.groupby("matric",as_index=False).agg(
        student_name=("student_name",lambda x:next((v for v in x if v),"")),
        lecturer_count=("lecturer_id","nunique"),
        **{col:(col,"mean") for col in cc})
    tm=sum(c["max"] for c in st.session_state.criteria)
    g["total_avg"]=g[cc].sum(axis=1).round(2)
    g["percentage"]=(g["total_avg"]/tm*100).round(1) if tm else 0
    return g.sort_values("total_avg",ascending=False).reset_index(drop=True)

# ── auth ─────────────────────────────────────────────────────────────────────
def do_login(u,p):
    for user in st.session_state.users.values():
        if user["username"].lower()==u.lower() and user["password"]==hp(p):
            st.session_state.logged_in=True
            st.session_state.current_user=user
            st.session_state.nav_page="Dashboard" if user["role"]!="lecturer" else "Enter Scores"
            return True
    return False

def logout():
    st.session_state.update(logged_in=False,current_user=None,nav_page=None)
    st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# CSS — injected fresh every render so theme changes apply immediately
# ════════════════════════════════════════════════════════════════════════════
def css():
    t=T()
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&family=JetBrains+Mono:wght@400;500&display=swap');

*,*::before,*::after{{box-sizing:border-box;}}
html,body,[class*="css"]{{font-family:'Plus Jakarta Sans',sans-serif!important;}}

/* ── Hide Streamlit chrome we don't need ── */
#MainMenu,footer,header,.stDeployButton{{visibility:hidden!important;display:none!important;}}

/* ── App background ── */
.stApp{{background:{t['app_bg']}!important;}}
.main .block-container{{padding:0!important;max-width:100%!important;}}

/* ════ SIDEBAR ════ */
section[data-testid="stSidebar"]{{
    background:{t['sb_bg']}!important;
    min-width:248px!important; max-width:248px!important; width:248px!important;
    border-right:1px solid rgba(255,255,255,0.07)!important;
}}
section[data-testid="stSidebar"] > div:first-child{{
    padding:0!important; background:{t['sb_bg']}!important;
}}

/* ── Hamburger / collapse button — ALWAYS VISIBLE ── */
button[data-testid="collapsedControl"]{{
    display:flex!important; visibility:visible!important; opacity:1!important;
    position:fixed!important; top:14px!important; left:236px!important;
    z-index:99999!important;
    width:32px!important; height:32px!important;
    background:{t['sb_gold']}!important;
    border:none!important; border-radius:50%!important;
    align-items:center!important; justify-content:center!important;
    cursor:pointer!important;
    box-shadow:2px 2px 10px rgba(0,0,0,0.35)!important;
    transition:left 0.3s ease,background 0.15s!important;
    padding:0!important;
}}
button[data-testid="collapsedControl"]:hover{{
    background:#dbb95a!important;
}}
button[data-testid="collapsedControl"] svg{{
    fill:#0A0B14!important; width:14px!important; height:14px!important;
}}
/* When sidebar is collapsed, move the button to the edge */
[data-testid="stSidebar"][aria-expanded="false"] ~ * button[data-testid="collapsedControl"],
.st-emotion-cache-1gwvy71 button[data-testid="collapsedControl"]{{
    left:8px!important;
}}

/* ── Sidebar text colours ── */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div{{color:{t['sb_text']}!important;}}

/* ── Sidebar nav buttons ── */
section[data-testid="stSidebar"] .stButton>button{{
    background:transparent!important; border:none!important;
    border-left:3px solid transparent!important;
    color:{t['sb_muted']}!important;
    font-family:'Plus Jakarta Sans',sans-serif!important;
    font-size:0.84rem!important; font-weight:400!important;
    text-align:left!important; padding:9px 14px!important;
    border-radius:0 8px 8px 0!important;
    width:100%!important; transition:all 0.15s!important;
    margin-bottom:2px!important;
}}
section[data-testid="stSidebar"] .stButton>button:hover{{
    background:rgba(255,255,255,0.07)!important;
    color:{t['sb_text']}!important;
    border-left-color:rgba(201,168,76,0.4)!important;
}}

/* ── Active nav button ── */
.nav-active section[data-testid="stSidebar"] .stButton>button,
section[data-testid="stSidebar"] .nav-is-active .stButton>button{{
    background:rgba(201,168,76,0.13)!important;
    color:#F0EDE4!important; font-weight:600!important;
    border-left-color:#C9A84C!important;
}}

/* Theme buttons in sidebar */
section[data-testid="stSidebar"] button[kind="primary"]{{
    background:{t['sb_gold']}!important; color:#0A0B14!important;
    border:none!important; font-weight:700!important; border-radius:7px!important;
    font-size:0.75rem!important;
}}
section[data-testid="stSidebar"] button[kind="secondary"]{{
    background:transparent!important;
    border:1px solid rgba(255,255,255,0.14)!important;
    color:{t['sb_muted']}!important; border-radius:7px!important;
    font-size:0.75rem!important;
}}

/* Sign out */
section[data-testid="stSidebar"] button[title="Sign Out"]{{
    color:#E07070!important; background:rgba(224,112,112,0.1)!important;
    border:1px solid rgba(224,112,112,0.2)!important; border-radius:8px!important;
    border-left:none!important;
}}

/* ════ MAIN CONTENT ════ */
.kdsc-wrap{{padding:2rem 2.4rem 5rem; max-width:1280px; margin:0 auto;}}
@media(max-width:768px){{.kdsc-wrap{{padding:1.2rem 1rem 4rem;}}}}

/* ── Page header ── */
.ph{{margin-bottom:1.8rem;padding-bottom:1.4rem;border-bottom:1px solid {t['div']};}}
.ph-eye{{font-size:0.62rem;font-weight:700;letter-spacing:0.22em;
    text-transform:uppercase;color:{t['gold']};margin-bottom:4px;}}
.ph-title{{font-family:'Playfair Display',serif;font-size:1.85rem;font-weight:700;
    color:{t['text1']};margin:0;line-height:1.2;}}
.ph-sub{{font-size:0.8rem;color:{t['muted']};margin-top:5px;}}

/* ── Stat cards ── */
.sg{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:2rem;}}
@media(max-width:900px){{.sg{{grid-template-columns:repeat(2,1fr);}}}}
@media(max-width:480px){{.sg{{grid-template-columns:1fr;}}}}
.sc{{background:{t['card']};border:1px solid {t['border']};border-radius:12px;
    padding:1.2rem 1.3rem;position:relative;overflow:hidden;}}
.sc::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px;
    background:linear-gradient(90deg,{t['gold']},transparent);}}
.sc-l{{font-size:0.62rem;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;
    color:{t['muted']};margin-bottom:8px;}}
.sc-v{{font-family:'Playfair Display',serif;font-size:1.9rem;font-weight:700;
    color:{t['text1']};line-height:1;margin-bottom:4px;}}
.sc-s{{font-size:0.7rem;color:{t['muted']};}}

/* ── Section title ── */
.stitle{{font-size:0.7rem;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;
    color:{t['text2']};margin:0 0 1rem;display:flex;align-items:center;gap:10px;}}
.stitle::after{{content:'';flex:1;height:1px;background:{t['div']};}}

/* ── Badges ── */
.badge{{display:inline-flex;align-items:center;padding:3px 10px;border-radius:4px;
    font-size:0.67rem;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;}}
.b-root{{background:{t['gold_bg']};color:{t['gold']};border:1px solid {t['gold_bd']};}}
.b-super{{background:#EEF2FF;color:#3B5998;border:1px solid #B0C0E8;}}
.b-lect{{background:#EDFAF3;color:#1A7A4A;border:1px solid rgba(26,122,74,0.3);}}

/* ── Avatar ── */
.av{{width:36px;height:36px;border-radius:50%;background:{t['gold_bg']};
    border:1.5px solid {t['gold_bd']};display:inline-flex;align-items:center;
    justify-content:center;font-size:0.8rem;font-weight:700;color:{t['gold']};flex-shrink:0;}}

/* ── Crit tag ── */
.ctag{{font-family:'JetBrains Mono',monospace;font-size:0.72rem;color:{t['gold']};
    background:{t['gold_bg']};border:1px solid {t['gold_bd']};
    padding:3px 10px;border-radius:20px;font-weight:500;}}

/* ── Empty state ── */
.empty{{text-align:center;padding:3rem 2rem;background:{t['panel']};
    border:1.5px dashed {t['border']};border-radius:12px;}}
.empty-t{{font-family:'Playfair Display',serif;font-size:1.15rem;font-weight:600;
    color:{t['muted']};margin-bottom:5px;}}
.empty-s{{font-size:0.78rem;color:{t['muted']};}}

/* ════ FORM FIELDS ════ */
.stTextInput>div>div>input,
.stNumberInput>div>div>input,
.stTextArea>div>textarea{{
    background:{t['inp']}!important; border:1px solid {t['inp_bd']}!important;
    border-radius:8px!important; color:{t['text1']}!important;
    font-family:'Plus Jakarta Sans',sans-serif!important;
    font-size:0.88rem!important; padding:10px 12px!important;
}}
.stTextInput>div>div>input:focus,
.stNumberInput>div>div>input:focus{{
    border-color:{t['gold']}!important;
    box-shadow:0 0 0 3px {t['gold_bg']}!important;
}}
.stSelectbox>div>div,div[data-baseweb="select"]>div{{
    background:{t['inp']}!important; border:1px solid {t['inp_bd']}!important;
    border-radius:8px!important;
}}
div[data-baseweb="select"] span,div[data-baseweb="select"] div{{
    color:{t['text1']}!important; font-family:'Plus Jakarta Sans',sans-serif!important;
}}
.stTextInput label,.stNumberInput label,.stSelectbox label,.stTextArea label{{
    font-size:0.68rem!important; font-weight:700!important;
    letter-spacing:0.1em!important; text-transform:uppercase!important;
    color:{t['text2']}!important;
}}

/* ── Primary btn ── */
div[data-testid="stFormSubmitButton"]>button,
.stButton>button[kind="primary"]{{
    background:{t['btn_bg']}!important; border:none!important;
    color:{t['btn_fg']}!important; font-family:'Plus Jakarta Sans',sans-serif!important;
    font-size:0.78rem!important; font-weight:700!important;
    letter-spacing:0.08em!important; text-transform:uppercase!important;
    border-radius:8px!important; padding:10px 22px!important; transition:all 0.15s!important;
}}
div[data-testid="stFormSubmitButton"]>button:hover,
.stButton>button[kind="primary"]:hover{{opacity:0.85!important;transform:translateY(-1px)!important;}}

/* ── Secondary btn ── */
.stButton>button[kind="secondary"]{{
    background:transparent!important; border:1px solid {t['inp_bd']}!important;
    color:{t['text2']}!important; font-family:'Plus Jakarta Sans',sans-serif!important;
    font-size:0.78rem!important; border-radius:8px!important; transition:all 0.15s!important;
}}
.stButton>button[kind="secondary"]:hover{{
    border-color:{t['gold_bd']}!important; color:{t['gold']}!important;
    background:{t['gold_bg']}!important;
}}

/* ── Default btn ── */
.stButton>button:not([kind]){{
    background:transparent!important; border:1px solid {t['div']}!important;
    color:{t['text2']}!important; font-family:'Plus Jakarta Sans',sans-serif!important;
    font-size:0.78rem!important; border-radius:7px!important; transition:all 0.15s!important;
}}
.stButton>button:not([kind]):hover{{
    background:{t['panel']}!important; color:{t['text1']}!important;
    border-color:{t['gold_bd']}!important;
}}

/* ── Download btn ── */
.stDownloadButton>button{{
    background:{t['btn_bg']}!important; border:none!important;
    color:{t['btn_fg']}!important; font-family:'Plus Jakarta Sans',sans-serif!important;
    font-size:0.78rem!important; font-weight:700!important;
    border-radius:8px!important; padding:10px 18px!important;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"]{{background:transparent!important;border-bottom:2px solid {t['div']}!important;}}
.stTabs [data-baseweb="tab"]{{
    background:transparent!important; border:none!important; color:{t['muted']}!important;
    font-family:'Plus Jakarta Sans',sans-serif!important; font-size:0.78rem!important;
    font-weight:500!important; padding:9px 18px!important;
    border-bottom:2px solid transparent!important; margin-bottom:-2px!important;
}}
.stTabs [aria-selected="true"]{{color:{t['text1']}!important; font-weight:700!important;
    border-bottom:2px solid {t['gold']}!important;}}

/* ── Dataframe ── */
.stDataFrame{{border:1px solid {t['border']}!important;border-radius:10px!important;overflow:hidden!important;}}

/* ── Expander ── */
details>summary{{background:{t['panel']}!important; border:1px solid {t['border']}!important;
    border-radius:8px!important; color:{t['text1']}!important;
    font-size:0.87rem!important; font-weight:500!important; padding:11px 16px!important;}}

/* ── File uploader ── */
[data-testid="stFileUploader"] section{{background:{t['panel']}!important;
    border:1.5px dashed {t['border']}!important; border-radius:10px!important;}}

/* ── Alerts ── */
[data-testid="stAlert"]{{border-radius:8px!important; font-size:0.84rem!important;}}

/* ── HR ── */
hr{{border:none!important; border-top:1px solid {t['div']}!important; margin:1.5rem 0!important;}}
.stCaption{{color:{t['muted']}!important; font-size:0.73rem!important;}}

/* ── Number input ── */
.stNumberInput button{{background:{t['panel']}!important; border-color:{t['inp_bd']}!important;
    color:{t['text2']}!important;}}

/* ── Scrollbar ── */
::-webkit-scrollbar{{width:5px;height:5px;}}
::-webkit-scrollbar-track{{background:{t['app_bg']};}}
::-webkit-scrollbar-thumb{{background:{t['div']};border-radius:10px;}}

/* ── Login card ── */
.login-card{{background:{t['card']};border:1px solid {t['border']};border-radius:20px;
    padding:2.8rem 2.6rem;box-shadow:0 4px 40px rgba(0,0,0,0.07);}}
.login-ring{{width:52px;height:52px;border-radius:50%;background:{t['gold_bg']};
    border:2px solid {t['gold_bd']};display:flex;align-items:center;justify-content:center;
    margin:0 auto 1rem;font-size:1.2rem;color:{t['gold']};font-weight:700;}}
.login-eye{{font-size:0.62rem;letter-spacing:0.24em;text-transform:uppercase;
    color:{t['gold']};text-align:center;margin-bottom:6px;font-weight:700;}}
.login-title{{font-family:'Playfair Display',serif;font-size:1.65rem;font-weight:700;
    color:{t['text1']};text-align:center;line-height:1.25;margin-bottom:5px;}}
.login-sub{{font-size:0.78rem;color:{t['muted']};text-align:center;margin-bottom:2rem;}}
.login-rule{{height:1px;background:{t['div']};margin:1.4rem 0;}}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
def sidebar():
    t = T()
    u = me()
    role_labels = {"root_admin":"Root Administrator","super_admin":"Super Admin","lecturer":"Lecturer"}

    with st.sidebar:
        # ── Brand ──
        st.markdown(f"""
        <div style="padding:1.6rem 1.2rem 1rem;border-bottom:1px solid rgba(255,255,255,0.07);">
          <div style="font-size:0.58rem;letter-spacing:0.28em;text-transform:uppercase;
               color:{t['sb_gold']};font-weight:700;margin-bottom:4px;">Academic Scoring</div>
          <div style="font-family:'Playfair Display',serif;font-size:1.18rem;font-weight:700;
               color:#F0EDE4;line-height:1.3;">King David<br>Score Compiler</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Theme toggle ──
        st.markdown("<div style='padding:0.6rem 0.5rem 0;'>", unsafe_allow_html=True)
        tc1, tc2 = st.columns(2)
        with tc1:
            if st.button("Light", key="t_light",
                         type="primary" if st.session_state.theme=="light" else "secondary",
                         use_container_width=True):
                st.session_state.theme = "light"; st.rerun()
        with tc2:
            if st.button("Dark", key="t_dark",
                         type="primary" if st.session_state.theme=="dark" else "secondary",
                         use_container_width=True):
                st.session_state.theme = "dark"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"<hr style='border-color:rgba(255,255,255,0.07);margin:0.8rem 0;'>",
                    unsafe_allow_html=True)

        # ── Nav ──
        def section(lbl):
            st.markdown(f"""
            <div style="font-size:0.58rem;font-weight:700;letter-spacing:0.2em;
                 text-transform:uppercase;color:{t['sb_muted']};
                 padding:0.7rem 0.5rem 0.25rem;">
              {lbl}
            </div>""", unsafe_allow_html=True)

        def nav(lbl):
            active = st.session_state.nav_page == lbl
            if active:
                # inject style for the NEXT button rendered
                st.markdown(f"""
                <style>
                section[data-testid="stSidebar"] .stButton:has(+*) > button,
                section[data-testid="stSidebar"] div[data-testid="element-container"]:last-child .stButton > button
                {{ }}
                </style>
                """, unsafe_allow_html=True)
                # active state via a wrapper
                st.markdown(f"""
                <style>
                section[data-testid="stSidebar"] button[title="{lbl}"] {{
                    background:rgba(201,168,76,0.14)!important;
                    color:#F0EDE4!important; font-weight:600!important;
                    border-left:3px solid #C9A84C!important;
                }}
                </style>""", unsafe_allow_html=True)
            if st.button(lbl, key=f"nav_{lbl}", use_container_width=True):
                st.session_state.nav_page = lbl; st.rerun()

        if is_admin():
            section("Overview");       nav("Dashboard")
            section("Administration"); nav("Scoring Criteria"); nav("Manage Lecturers")
            if is_root():              nav("Admin Accounts")
        section("Scoring");            nav("Enter Scores"); nav("My Submissions")
        if is_admin():
            section("Reports");        nav("Export Results")

        # ── User block ──
        st.markdown(f"<hr style='border-color:rgba(255,255,255,0.07);margin:0.8rem 0 0;'>",
                    unsafe_allow_html=True)
        st.markdown(f"""
        <div style="padding:0.75rem 0.5rem;">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
            <div class="av" style="background:{t['gold_bg']};border-color:{t['gold_bd']};
                 color:{t['gold']};">{ini(u['display_name'])}</div>
            <div>
              <div style="font-size:0.85rem;font-weight:600;color:#F0EDE4;">
                {u['display_name']}</div>
              <div style="font-size:0.7rem;color:{t['sb_muted']};">
                {role_labels.get(u['role'],u['role'])}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Sign Out", key="sb_signout", use_container_width=True):
            logout()

# ════════════════════════════════════════════════════════════════════════════
# UI HELPERS
# ════════════════════════════════════════════════════════════════════════════
def ph(eye, title, sub=""):
    s = f'<div class="ph-sub">{sub}</div>' if sub else ""
    st.markdown(f'<div class="ph"><div class="ph-eye">{eye}</div>'
                f'<h1 class="ph-title">{title}</h1>{s}</div>', unsafe_allow_html=True)

def sec(title):
    st.markdown(f'<div class="stitle">{title}</div>', unsafe_allow_html=True)

def stat_cards(items):
    h = '<div class="sg">'
    for l,v,s in items:
        h += f'<div class="sc"><div class="sc-l">{l}</div><div class="sc-v">{v}</div><div class="sc-s">{s}</div></div>'
    st.markdown(h+'</div>', unsafe_allow_html=True)

def badge(role):
    cls={"root_admin":"b-root","super_admin":"b-super","lecturer":"b-lect"}
    lbl={"root_admin":"Root Admin","super_admin":"Super Admin","lecturer":"Lecturer"}
    return f'<span class="badge {cls.get(role,"")}">{lbl.get(role,role)}</span>'

# ════════════════════════════════════════════════════════════════════════════
# LOGIN
# ════════════════════════════════════════════════════════════════════════════
def login_page():
    t=T()
    st.markdown('<div class="kdsc-wrap">', unsafe_allow_html=True)
    _, col, _ = st.columns([1,1.1,1])
    with col:
        st.markdown(f"""
        <div style="margin-top:6vh;">
          <div class="login-card">
            <div class="login-ring">◆</div>
            <div class="login-eye">Academic Assessment Platform</div>
            <div class="login-title">King David Score Compiler</div>
            <div class="login-sub">Sign in to access your workspace</div>
            <div class="login-rule"></div>
          </div>
        </div>""", unsafe_allow_html=True)
        with st.form("lf"):
            uname = st.text_input("Username", placeholder="Enter your username")
            pwd   = st.text_input("Password", type="password", placeholder="Enter your password")
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            if st.form_submit_button("Sign In", use_container_width=True, type="primary"):
                if do_login(uname, pwd): st.rerun()
                else: st.error("Incorrect username or password.")
        st.markdown(f"""
        <p style="text-align:center;font-size:0.72rem;color:{t['muted']};margin-top:1rem;">
          Default &mdash; username:
          <code style="background:{t['panel']};color:{t['text2']};padding:2px 6px;border-radius:4px;">root</code>
          &nbsp;/&nbsp; password:
          <code style="background:{t['panel']};color:{t['text2']};padding:2px 6px;border-radius:4px;">root1234</code>
        </p>""", unsafe_allow_html=True)

    # theme toggle on login
    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
    _, tc, _ = st.columns([2,1,2])
    with tc:
        lbl = "Switch to Dark" if st.session_state.theme=="light" else "Switch to Light"
        if st.button(lbl, use_container_width=True):
            st.session_state.theme = "dark" if st.session_state.theme=="light" else "light"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# PAGES
# ════════════════════════════════════════════════════════════════════════════
def page_dashboard():
    ph("Overview","Dashboard","Aggregated results across all lecturers and students")
    results=get_results()
    tmax=sum(c["max"] for c in st.session_state.criteria)
    nl=len([u for u in st.session_state.users.values() if u["role"]=="lecturer"])
    stat_cards([
        ("Students Scored",len(results),"unique matric numbers"),
        ("Score Entries",len(st.session_state.scores),"submitted by lecturers"),
        ("Active Lecturers",nl,"registered"),
        ("Class Average",f"{results['total_avg'].mean():.1f}" if not results.empty else "—",
         f"out of {tmax} marks"),
    ])
    if results.empty:
        st.markdown('<div class="empty"><div class="empty-t">No scores recorded yet</div>'
                    '<div class="empty-s">Entries appear once lecturers begin submitting.</div></div>',
                    unsafe_allow_html=True)
        return
    sec("Averaged Results")
    d=results[["matric","student_name","lecturer_count"]].copy()
    d.columns=["Matric","Student Name","Lecturers"]
    for c in st.session_state.criteria:
        col=f"crit_{c['id']}"
        if col in results.columns: d[f"{c['name']} (/{c['max']})"]=results[col].round(2)
    d[f"Total (/{tmax})"]=results["total_avg"]
    d["Percentage"]=results["percentage"].astype(str)+"%"
    st.dataframe(d,use_container_width=True,hide_index=True)
    st.markdown("<div style='height:1.5rem'></div>",unsafe_allow_html=True)
    c1,c2=st.columns([1,2])
    with c1:
        sec("Grade Distribution")
        def gr(p):
            if p>=70: return "A — Distinction"
            if p>=60: return "B — Credit"
            if p>=50: return "C — Pass"
            if p>=45: return "D — Marginal"
            return "F — Fail"
        gc=results["percentage"].apply(gr).value_counts().reset_index()
        gc.columns=["Grade","Count"]
        st.dataframe(gc,use_container_width=True,hide_index=True)
    with c2:
        sec("Score Distribution")
        st.bar_chart(results.set_index("matric")["total_avg"],height=210)


def page_criteria():
    ph("Administration","Scoring Criteria","Define what is assessed and the maximum marks for each dimension")
    tmax=sum(c["max"] for c in st.session_state.criteria)
    sec(f"Active Criteria — {tmax} total marks")
    t=T()
    if st.session_state.criteria:
        for c in st.session_state.criteria:
            c1,c2,c3=st.columns([5,1,1])
            c1.markdown(f'<div style="padding:10px 0;font-size:0.9rem;font-weight:500;'
                        f'color:{t["text1"]};">{c["name"]}</div>',unsafe_allow_html=True)
            c2.markdown(f'<div style="padding:10px 0;"><span class="ctag">{c["max"]} pts</span></div>',
                        unsafe_allow_html=True)
            if c3.button("Remove",key=f"dc_{c['id']}",type="secondary"):
                st.session_state.criteria=[x for x in st.session_state.criteria if x["id"]!=c["id"]]
                st.rerun()
    else:
        st.markdown('<div class="empty"><div class="empty-t">No criteria defined</div></div>',
                    unsafe_allow_html=True)
    st.markdown("<hr>",unsafe_allow_html=True)
    sec("Add New Criterion")
    with st.form("acf",clear_on_submit=True):
        f1,f2=st.columns([4,1])
        nn=f1.text_input("Criterion Name",placeholder="e.g. Research Methodology")
        nm=f2.number_input("Max Marks",min_value=1,max_value=100,value=10)
        if st.form_submit_button("Add Criterion",type="primary"):
            if nn.strip():
                nid=max((c["id"] for c in st.session_state.criteria),default=0)+1
                st.session_state.criteria.append({"id":nid,"name":nn.strip(),"max":int(nm)})
                st.rerun()
            else: st.error("Criterion name required.")


def _user_panel(role):
    t=T()
    rl={"lecturer":"Lecturer","super_admin":"Super Admin"}[role]
    users=[u for u in st.session_state.users.values() if u["role"]==role]
    sec(f"{rl}s — {len(users)} registered")
    if users:
        for u in users:
            c1,c2,c3,c4=st.columns([0.55,3,2,1])
            c1.markdown(f'<div style="padding-top:4px;"><div class="av">{ini(u["display_name"])}</div></div>',
                        unsafe_allow_html=True)
            c2.markdown(f'<div style="padding:3px 0"><div style="font-size:0.88rem;font-weight:600;'
                        f'color:{t["text1"]};">{u["display_name"]}</div>'
                        f'<div style="font-size:0.72rem;color:{t["muted"]};'
                        f'font-family:\'JetBrains Mono\',monospace;">{u["username"]}</div></div>',
                        unsafe_allow_html=True)
            c3.markdown(f'<div style="padding:7px 0">{badge(u["role"])}</div>',unsafe_allow_html=True)
            if c4.button("Remove",key=f"du_{u['id']}",type="secondary"):
                del st.session_state.users[u["id"]]; st.rerun()
    else:
        st.markdown(f'<div class="empty"><div class="empty-t">No {rl}s yet</div>'
                    f'<div class="empty-s">Create the first one below.</div></div>',
                    unsafe_allow_html=True)
    st.markdown("<hr>",unsafe_allow_html=True)
    sec(f"Create {rl}")
    with st.form(f"cf_{role}",clear_on_submit=True):
        r1,r2=st.columns(2)
        dn=r1.text_input("Full Name",placeholder="e.g. Dr. Adeyemi Kolawole")
        un=r2.text_input("Username",placeholder="e.g. adeyemi")
        r3,r4=st.columns(2)
        pw=r3.text_input("Password",type="password")
        pw2=r4.text_input("Confirm Password",type="password")
        if st.form_submit_button(f"Create {rl}",type="primary"):
            errs=[]
            if not dn.strip(): errs.append("Full name required.")
            if not un.strip(): errs.append("Username required.")
            if not pw:         errs.append("Password required.")
            if pw!=pw2:        errs.append("Passwords do not match.")
            if any(u["username"].lower()==un.strip().lower() for u in st.session_state.users.values()):
                errs.append("Username already taken.")
            if errs:
                for e in errs: st.error(e)
            else:
                nid=uid()
                st.session_state.users[nid]={"id":nid,"username":un.strip(),
                    "password":hp(pw),"display_name":dn.strip(),"role":role}
                st.success(f"Account created for {dn.strip()}.")
                st.rerun()


def page_manage_lecturers():
    ph("Administration","Manage Lecturers","Create and remove lecturer accounts")
    _user_panel("lecturer")

def page_admin_accounts():
    ph("Administration","Admin Accounts","Manage super administrator accounts")
    if not is_root(): st.error("Restricted to Root Administrator."); return
    _user_panel("super_admin")


def page_enter_scores():
    t=T()
    ph("Scoring","Enter Scores","Submit assessment scores for a student presentation")
    if not st.session_state.criteria:
        st.warning("No scoring criteria configured. An administrator must set them up first.")
        return
    sec("Score Entry Form")
    with st.form("sef",clear_on_submit=True):
        if is_admin():
            lects=[u for u in st.session_state.users.values() if u["role"]=="lecturer"]
            if lects:
                opts={u["display_name"]:u for u in lects}
                sel=st.selectbox("Scoring Lecturer",list(opts.keys()))
                lu=opts[sel]
            else:
                st.warning("No lecturer accounts yet. Go to Manage Lecturers first.")
                lu=me()
        else:
            st.markdown(f'<div style="margin-bottom:1rem;">'
                        f'<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.1em;'
                        f'text-transform:uppercase;color:{t["muted"]};margin-bottom:5px;">Scoring Lecturer</div>'
                        f'<div style="font-size:0.9rem;font-weight:600;color:{t["text1"]};'
                        f'background:{t["panel"]};border:1px solid {t["border"]};'
                        f'border-radius:8px;padding:10px 14px;">{me()["display_name"]}</div></div>',
                        unsafe_allow_html=True)
            lu=me()
        f1,f2=st.columns(2)
        mat=f1.text_input("Matrix Number",placeholder="e.g. CS/2021/001")
        snm=f2.text_input("Student Name",placeholder="e.g. Amaka Obi  (optional)")
        st.markdown("<div style='height:6px'></div>",unsafe_allow_html=True)
        sec("Marks per Criterion")
        sv={}
        cols=st.columns(min(len(st.session_state.criteria),3))
        for idx,crit in enumerate(st.session_state.criteria):
            sv[crit["id"]]=cols[idx%3].number_input(
                crit["name"],min_value=0.0,max_value=float(crit["max"]),
                value=0.0,step=0.5,help=f"Max: {crit['max']} marks",key=f"se_{crit['id']}")
        st.markdown("<div style='height:4px'></div>",unsafe_allow_html=True)
        if st.form_submit_button("Save Score Entry",type="primary",use_container_width=True):
            if not mat.strip(): st.error("Matrix number is required.")
            else:
                row={"id":uid(),"matric":mat.strip().upper(),"student_name":snm.strip(),
                     "lecturer_id":lu["id"],"lecturer_name":lu["display_name"]}
                for crit in st.session_state.criteria: row[f"crit_{crit['id']}"]=sv[crit["id"]]
                st.session_state.scores.append(row)
                st.success(f"Entry saved — {mat.strip().upper()} scored by {lu['display_name']}")
                st.rerun()

    if is_admin():
        st.markdown("<div style='height:1rem'></div>",unsafe_allow_html=True)
        with st.expander("Bulk CSV Upload"):
            ch=", ".join(c["name"].lower().replace(" ","_").replace("&","and")
                         for c in st.session_state.criteria)
            st.caption(f"Columns: matric, lecturer_username, student_name, then: {ch}")
            tc=["matric","student_name","lecturer_username"]+[
                c["name"].lower().replace(" ","_").replace("&","and")
                for c in st.session_state.criteria]
            st.download_button("Download CSV Template",
                               pd.DataFrame(columns=tc).to_csv(index=False),
                               "kdsc_template.csv","text/csv")
            uf=st.file_uploader("Upload completed CSV",type=["csv"])
            if uf:
                try:
                    udf=pd.read_csv(uf); udf.columns=udf.columns.str.strip().str.lower()
                    um={u["username"].lower():u for u in st.session_state.users.values()}
                    nr,errs=[],[]
                    for i,row in udf.iterrows():
                        lu2=um.get(str(row.get("lecturer_username","")).strip().lower())
                        if not lu2: errs.append(f"Row {i+2}: unknown lecturer"); continue
                        r={"id":uid(),"matric":str(row.get("matric","")).strip().upper(),
                           "student_name":str(row.get("student_name","")).strip(),
                           "lecturer_id":lu2["id"],"lecturer_name":lu2["display_name"]}
                        for crit in st.session_state.criteria:
                            k=crit["name"].lower().replace(" ","_").replace("&","and")
                            raw=pd.to_numeric(row.get(k,0),errors="coerce") or 0
                            if raw>crit["max"]: errs.append(f"Row {i+2}: {crit['name']} exceeds max")
                            r[f"crit_{crit['id']}"]=min(raw,crit["max"])
                        nr.append(r)
                    for e in errs: st.warning(e)
                    if nr: st.session_state.scores.extend(nr); st.success(f"Imported {len(nr)} rows."); st.rerun()
                except Exception as ex: st.error(f"Error: {ex}")


def page_my_submissions():
    ph("Scoring","My Submissions","Score entries submitted under your account")
    my=[s for s in st.session_state.scores if s.get("lecturer_id")==me()["id"]]
    tmax=sum(c["max"] for c in st.session_state.criteria)
    mats=list({s["matric"] for s in my})
    stat_cards([("My Entries",len(my),"total rows"),("Students",len(mats),"unique matrics"),
                ("Criteria",len(st.session_state.criteria),"dimensions"),("Max Possible",tmax,"per student")])
    if not my:
        st.markdown('<div class="empty"><div class="empty-t">No submissions yet</div>'
                    '<div class="empty-s">Your entries appear here after submission.</div></div>',
                    unsafe_allow_html=True); return
    sec("All Score Entries")
    df=pd.DataFrame(my)
    rn={"matric":"Matric","student_name":"Student"}
    for c in st.session_state.criteria: rn[f"crit_{c['id']}"]=f"{c['name']} (/{c['max']})"
    sh=["matric","student_name"]+[f"crit_{c['id']}" for c in st.session_state.criteria]
    st.dataframe(df[[c for c in sh if c in df.columns]].rename(columns=rn),
                 use_container_width=True,hide_index=True)
    sec("Summary by Student")
    rows=[]
    for m in mats:
        ms=[s for s in my if s["matric"]==m]
        sn=next((s["student_name"] for s in ms if s.get("student_name")),"")
        tots=[sum(s.get(f"crit_{c['id']}",0) or 0 for c in st.session_state.criteria) for s in ms]
        rows.append({"Matric":m,"Student":sn,"Entries":len(ms),"Avg Total":round(sum(tots)/len(tots),2)})
    st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)


def page_export():
    ph("Reports","Export Results","Download compiled and averaged scores for all students")
    if not is_admin(): st.error("Access restricted to administrators."); return
    results=get_results(); tmax=sum(c["max"] for c in st.session_state.criteria)
    if results.empty:
        st.markdown('<div class="empty"><div class="empty-t">No data to export</div></div>',
                    unsafe_allow_html=True); return
    stat_cards([("Students",len(results),"in export"),
                ("Highest",f"{results['total_avg'].max():.1f}",f"out of {tmax}"),
                ("Lowest",f"{results['total_avg'].min():.1f}",f"out of {tmax}"),
                ("Class Average",f"{results['total_avg'].mean():.1f}",f"out of {tmax}")])
    sec("Full Results Table")
    d=results[["matric","student_name","lecturer_count"]].copy()
    d.columns=["Matric","Student Name","Lecturers Scored"]
    for c in st.session_state.criteria:
        col=f"crit_{c['id']}"
        if col in results.columns: d[f"{c['name']} (/{c['max']})"]=results[col].round(2)
    d[f"Total Avg (/{tmax})"]=results["total_avg"]
    d["Percentage"]=results["percentage"].astype(str)+"%"
    st.dataframe(d,use_container_width=True,hide_index=True)
    buf=io.StringIO(); d.to_csv(buf,index=False)
    st.markdown("<div style='height:0.5rem'></div>",unsafe_allow_html=True)
    st.download_button("Download Full Results as CSV",data=buf.getvalue(),
                       file_name="kdsc_results.csv",mime="text/csv",type="primary")
    lects={u["id"]:u["display_name"] for u in st.session_state.users.values()
           if u["role"] in ("lecturer","super_admin","root_admin")}
    if lects:
        st.markdown("<div style='height:1.5rem'></div>",unsafe_allow_html=True)
        sec("Per-Lecturer Breakdown")
        sn=st.selectbox("Select Lecturer",list(lects.values()))
        sid=next(k for k,v in lects.items() if v==sn)
        ldf=get_results(lf=sid)
        if not ldf.empty:
            lc={"matric":"Matric","student_name":"Student"}
            for c in st.session_state.criteria: lc[f"crit_{c['id']}"]=f"{c['name']} (/{c['max']})"
            sh=["matric","student_name"]+[f"crit_{c['id']}" for c in st.session_state.criteria]
            st.dataframe(ldf[[c for c in sh if c in ldf.columns]].rename(columns=lc),
                         use_container_width=True,hide_index=True)
        else: st.info("No entries from this lecturer yet.")

# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════
css()   # inject styles every render

if not st.session_state.logged_in:
    login_page()
else:
    sidebar()   # render Streamlit native sidebar (always expanded)

    if st.session_state.nav_page is None:
        st.session_state.nav_page = "Dashboard" if is_admin() else "Enter Scores"

    st.markdown('<div class="kdsc-wrap">', unsafe_allow_html=True)

    routes = {
        "Dashboard":        page_dashboard,
        "Scoring Criteria": page_criteria,
        "Manage Lecturers": page_manage_lecturers,
        "Admin Accounts":   page_admin_accounts,
        "Enter Scores":     page_enter_scores,
        "My Submissions":   page_my_submissions,
        "Export Results":   page_export,
    }
    fn = routes.get(st.session_state.nav_page)
    if fn: fn()
    else:  st.error(f"Page not found: {st.session_state.nav_page}")

    st.markdown('</div>', unsafe_allow_html=True)