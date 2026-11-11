"""Nada Latrech - data portfolio (Streamlit).

Run locally:  streamlit run app.py
Content comes from data/fr.json and data/en.json (built by build_data.py).
Share the English version with ?lang=en at the end of the URL.
"""
import html
import json
import re
from pathlib import Path

import streamlit as st

HERE = Path(__file__).resolve().parent

st.set_page_config(
    page_title="Nada Latrech · Portfolio data",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

UI = {
    "fr": {
        "tabs": ["Projets", "Expérience", "Formation & compétences", "Certifications", "Contact"],
        "video": "▶ Voir la vidéo",
        "slides": "📑 Voir la présentation",
        "images": "🖼 Voir les captures",
        "details": "Voir le détail",
        "slide": "Diapositive",
        "of": "sur",
        "demo_tab": "Vidéo",
        "pres_tab": "Présentation",
        "shots_tab": "Captures",
        "about_tab": "Le projet",
        "filter": "Filtrer par domaine",
        "count": "{n} projets",
        "verify": "Vérifier le certificat",
        "dd": "Double diplôme",
        "lang": "Langue",
        "media_hint": "Cliquez sur un projet pour voir sa vidéo de démonstration ou sa présentation.",
    },
    "en": {
        "tabs": ["Projects", "Experience", "Education & skills", "Certifications", "Contact"],
        "video": "▶ Watch the video",
        "slides": "📑 View the presentation",
        "images": "🖼 View screenshots",
        "details": "View details",
        "slide": "Slide",
        "of": "of",
        "demo_tab": "Video",
        "pres_tab": "Presentation",
        "shots_tab": "Screenshots",
        "about_tab": "About",
        "filter": "Filter by field",
        "count": "{n} projects",
        "verify": "Verify certificate",
        "dd": "Double degree",
        "lang": "Language",
        "media_hint": "Click a project to watch its demo video or browse its presentation.",
    },
}

CAT_COLORS = {
    "de": ("#0b6e75", "#e3f1f1"),
    "bi": ("#b4650c", "#fbf0e2"),
    "ai": ("#5b3fa8", "#efeafb"),
    "auto": ("#2f7a3b", "#e6f4e8"),
    "sw": ("#3a5a8c", "#e7eef8"),
}


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
  --ink:#142028; --muted:#55646d; --line:#e2e8eb; --paper:#f6f8f9;
  --accent:#0b6e75; --accent-2:#14a0a8; --accent-soft:#e3f1f1;
  --amber:#b4650c; --amber-soft:#fbf0e2;
  --shadow: 0 1px 2px rgba(20,32,40,.04), 0 8px 24px rgba(20,32,40,.06);
  --shadow-hover: 0 2px 4px rgba(20,32,40,.06), 0 16px 40px rgba(11,110,117,.14);
}

/* page */
.stApp {
  background:
    radial-gradient(1100px 520px at 0% -8%, #dcf0f0 0%, rgba(220,240,240,0) 62%),
    radial-gradient(900px 480px at 100% 0%, #fdf0e1 0%, rgba(253,240,225,0) 58%),
    var(--paper);
}
html, body, .stApp, .stMarkdown, p, li, span, label, button { font-family: 'IBM Plex Sans', system-ui, sans-serif; }
h1, h2, h3, .hero-name, .sec h2, .ptitle { font-family: 'Bricolage Grotesque', 'IBM Plex Sans', sans-serif !important; }
.block-container { padding-top: 1.6rem; padding-bottom: 4rem; max-width: 1180px; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { display: none; }

/* hero */
.hero {
  position: relative; overflow: hidden;
  background: linear-gradient(135deg, rgba(255,255,255,.92), rgba(255,255,255,.72));
  border: 1px solid rgba(11,110,117,.12); border-radius: 28px;
  padding: 2.6rem 2.8rem 2.2rem; box-shadow: var(--shadow); margin-bottom: 1.6rem;
}
.hero::after {
  content: ""; position: absolute; right: -120px; top: -120px; width: 380px; height: 380px;
  background: radial-gradient(circle, rgba(20,160,168,.18) 0%, rgba(20,160,168,0) 70%); pointer-events: none;
}
.eyebrow { text-transform: uppercase; letter-spacing: .14em; font-size: .74rem; color: var(--accent); font-weight: 600; }
.hero-name {
  font-size: clamp(2.6rem, 6vw, 4.4rem); font-weight: 800; line-height: 1.02; letter-spacing: -.02em;
  margin: .5rem 0 1rem; color: var(--ink);
}
.hero-name span {
  background: linear-gradient(90deg, var(--accent) 0%, var(--accent-2) 60%, #d08a2c 100%);
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
.roles { margin-bottom: 1.1rem; }
.role {
  display:inline-block; padding:.32rem .9rem; margin:0 .4rem .45rem 0; border-radius:999px;
  background: #fff; border: 1px solid rgba(11,110,117,.25); color: var(--accent); font-weight:600; font-size:.88rem;
}
.lede { font-size: 1.12rem; line-height: 1.65; color: #2a3a43; max-width: 760px; margin-bottom: 1.6rem; }
.facts { display: grid; grid-template-columns: repeat(4, 1fr); gap: .8rem; margin-bottom: 1.6rem; }
.fact {
  background: #fff; border: 1px solid var(--line); border-radius: 16px; padding: 1rem 1.1rem;
  display: flex; gap: .75rem; align-items: flex-start;
}
.fact .ico { font-size: 1.35rem; line-height: 1; padding: .45rem; border-radius: 12px; background: var(--accent-soft); }
.fact.amber .ico { background: var(--amber-soft); }
.fact b { display:block; font-family:'Bricolage Grotesque',sans-serif; font-size:1.08rem; color: var(--ink); }
.fact small { color: var(--muted); font-size:.84rem; line-height:1.35; display:block; margin-top:.15rem; }
.cta a {
  display:inline-block; text-decoration:none !important; font-weight:600; font-size:.95rem;
  padding:.65rem 1.3rem; border-radius:999px; margin-right:.5rem; transition: all .2s ease;
}
.cta a.primary { background: linear-gradient(135deg, var(--accent), var(--accent-2)); color:#fff !important; box-shadow: 0 6px 18px rgba(11,110,117,.25); }
.cta a.ghost { background:#fff; color: var(--ink) !important; border:1px solid var(--line); }
.cta a:hover { transform: translateY(-2px); }

/* section headings */
.sec { margin: .6rem 0 1.2rem; }
.sec h2 { font-size: 2rem; font-weight: 700; color: var(--ink); margin: .2rem 0 .3rem; padding: 0; letter-spacing: -.01em; }
.sec p { color: var(--muted); font-size: 1rem; max-width: 760px; margin: 0; }

/* main tabs */
.stTabs [data-baseweb="tab-list"] {
  gap: .35rem; background: rgba(255,255,255,.75); padding: .35rem; border-radius: 999px;
  border: 1px solid var(--line); width: fit-content; max-width: 100%; overflow-x: auto; box-shadow: var(--shadow);
}
.stTabs [data-baseweb="tab"] {
  height: auto; padding: .5rem 1.1rem; border-radius: 999px; font-weight: 600; color: var(--muted); background: transparent;
}
.stTabs [data-baseweb="tab"] p { font-size: .95rem; }
.stTabs [aria-selected="true"] { background: var(--accent) !important; color: #fff !important; }
.stTabs [aria-selected="true"] p { color: #fff !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.4rem; }

/* cards (every keyed box_ container) */
[class*="st-key-box_"] {
  background: #fff; border: 1px solid var(--line) !important; border-radius: 20px !important;
  padding: 1.1rem 1.15rem 1.2rem; box-shadow: var(--shadow); transition: transform .2s ease, box-shadow .2s ease;
}
[class*="st-key-box_"]:hover { transform: translateY(-3px); box-shadow: var(--shadow-hover); }
[class*="st-key-box_card_de"] { border-top: 4px solid #0b6e75 !important; }
[class*="st-key-box_card_bi"] { border-top: 4px solid #d08a2c !important; }
[class*="st-key-box_card_ai"] { border-top: 4px solid #7b61c9 !important; }
[class*="st-key-box_card_auto"] { border-top: 4px solid #3f9a4d !important; }
[class*="st-key-box_card_sw"] { border-top: 4px solid #4f78b8 !important; }
[class*="st-key-box_"] img { border-radius: 14px; aspect-ratio: 16/9; object-fit: cover; }
[class*="st-key-box_cert"] img { aspect-ratio: auto; object-fit: contain; background: var(--paper); }

.gen {
  aspect-ratio: 16/9; border-radius:14px; display:flex; align-items:center; justify-content:center;
  font-family:'IBM Plex Mono',monospace; font-weight:500; text-align:center; padding:1rem; font-size:1rem;
}
.cardhead { display:flex; justify-content:space-between; align-items:center; margin-top:.2rem; }
.cat { display:inline-block; padding:.2rem .65rem; border-radius:999px; font-size:.74rem; font-weight:600; }
.when { color: var(--muted); font-size:.8rem; font-weight:500; }
.kicker { color: var(--muted); font-size:.74rem; text-transform:uppercase; letter-spacing:.08em; margin-top:.75rem; font-weight:500; }
.ptitle { font-weight:700; font-size:1.25rem; line-height:1.25; margin:.2rem 0 .25rem; color: var(--ink); }
.psub { color: var(--accent); font-size:.95rem; font-weight:500; margin-bottom:.6rem; }
.pdesc { color:#2a3a43; font-size:.95rem; line-height:1.6; margin-bottom:.5rem; }
.flow {
  font-family:'IBM Plex Mono',monospace; font-size:.8rem; color: var(--accent);
  background: var(--accent-soft); padding:.55rem .75rem; border-radius:10px; margin:.5rem 0 .7rem; line-height:1.5;
}
ul.pts { list-style:none; padding:0; margin:.2rem 0 .8rem; }
ul.pts li { position:relative; padding-left:1.25rem; margin:.35rem 0; font-size:.9rem; line-height:1.55; color:#33434c; }
ul.pts li::before {
  content:""; position:absolute; left:.2rem; top:.62em; width:.45rem; height:.45rem; border-radius:50%;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
}
code { font-family:'IBM Plex Mono',monospace; font-size:.85em; background: var(--accent-soft); color: var(--accent); padding:.05rem .3rem; border-radius:5px; }
.tags { margin-top:.3rem; }
.tag {
  display:inline-block; padding:.18rem .6rem; margin:0 .3rem .35rem 0; border-radius:999px;
  background: #f1f5f6; font-size:.76rem; color: #3d4d56; font-weight:500;
}

/* buttons */
.stButton button[kind="primary"] {
  background: linear-gradient(135deg, var(--accent), var(--accent-2)); border: none; border-radius: 999px;
  font-weight: 600; padding: .6rem 1rem; box-shadow: 0 6px 16px rgba(11,110,117,.22); transition: all .2s ease;
}
.stButton button[kind="primary"]:hover { transform: translateY(-1px); box-shadow: 0 10px 24px rgba(11,110,117,.3); }
[data-testid="stLinkButton"] a { border-radius: 999px; font-weight: 600; }

/* filter pills */
[data-testid="stButtonGroup"] button { border-radius: 999px !important; font-weight: 500; }

/* dialog */
div[role="dialog"] { border-radius: 24px !important; }
div[role="dialog"] .ptitle { font-size: 1.7rem; }

/* experience timeline */
.tl { position: relative; padding-left: 1.6rem; }
.tl::before { content:""; position:absolute; left:.45rem; top:.4rem; bottom:.4rem; width:2px; background: linear-gradient(var(--accent), rgba(11,110,117,.1)); }
.job {
  position: relative; background:#fff; border:1px solid var(--line); border-radius:18px; padding:1.1rem 1.3rem;
  margin-bottom:1rem; box-shadow: var(--shadow);
}
.job::before {
  content:""; position:absolute; left:-1.52rem; top:1.35rem; width:.9rem; height:.9rem; border-radius:50%;
  background:#fff; border:3px solid var(--accent);
}
.job-top { display:flex; justify-content:space-between; gap:1rem; flex-wrap:wrap; align-items:baseline; }
.job h3 { font-size:1.15rem; margin:0; padding:0; color: var(--ink); }
.job .when { background: var(--accent-soft); color: var(--accent); padding:.15rem .6rem; border-radius:999px; font-weight:600; }

/* education / skills / contact */
.grid2 { display:grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.panel { background:#fff; border:1px solid var(--line); border-radius:20px; padding:1.3rem 1.4rem; box-shadow: var(--shadow); }
.panel h3 { font-size:1.15rem; margin:0 0 .8rem; padding:0; color: var(--ink); }
.degree { padding:.75rem 0; border-bottom:1px dashed var(--line); }
.degree:last-child { border-bottom:none; }
.degree b { display:block; color: var(--ink); }
.degree span { color: var(--muted); font-size:.9rem; }
.dd-badge { display:inline-block; font-size:.7rem; font-weight:600; color: var(--amber); background: var(--amber-soft); padding:.1rem .55rem; border-radius:999px; margin-bottom:.3rem; }
.lang { margin:.55rem 0 .9rem; }
.lang-top { display:flex; justify-content:space-between; font-size:.95rem; }
.lang-top span { color: var(--muted); }
.cefr { display:flex; gap:.3rem; margin-top:.35rem; }
.cefr i { flex:1; height:.45rem; border-radius:999px; background:#e7eef0; }
.cefr i.on { background: linear-gradient(90deg, var(--accent), var(--accent-2)); }
.skills { display:grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-top: .6rem; }
.contact-band {
  background: linear-gradient(135deg, #e3f1f1, #fdf0e1); border-radius: 26px; padding: 2.2rem 2.4rem;
  border: 1px solid rgba(11,110,117,.12);
}
.contact-band h2 { font-size: 2rem; margin: .2rem 0 .5rem; padding:0; color: var(--ink); }
.contact-band p { color:#2a3a43; max-width: 720px; }
.contacts { display:grid; grid-template-columns: repeat(4, 1fr); gap:.8rem; margin-top:1.2rem; }
.contact { background:#fff; border-radius:16px; padding:.9rem 1rem; border:1px solid var(--line); }
.contact small { display:block; color: var(--muted); font-size:.75rem; text-transform:uppercase; letter-spacing:.08em; }
.contact a, .contact span { color: var(--ink) !important; font-weight:600; word-break: break-all; text-decoration:none; }
.foot { text-align:center; color: var(--muted); font-size:.85rem; margin-top:2.5rem; }

@media (max-width: 900px) {
  .facts, .contacts { grid-template-columns: 1fr 1fr; }
  .grid2, .skills { grid-template-columns: 1fr; }
  .hero { padding: 1.8rem 1.4rem; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


@st.cache_data
def load(lang):
    return json.loads((HERE / "data" / f"{lang}.json").read_text(encoding="utf-8"))


def media(rel):
    return str(HERE / rel)


def esc(s):
    return html.escape(s or "")


def md(s):
    """Escape, then turn the **bold** and `code` markers from the data into HTML."""
    out = esc(s)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    return re.sub(r"`(.+?)`", r"<code>\1</code>", out)


def tag_html(tags):
    return '<div class="tags">' + "".join(f'<span class="tag">{esc(t)}</span>' for t in tags) + "</div>"


def sec(eyebrow, title, sub=""):
    st.markdown(
        f'<div class="sec"><div class="eyebrow">{esc(eyebrow)}</div><h2>{esc(title)}</h2>'
        + (f"<p>{esc(sub)}</p>" if sub else "") + "</div>",
        unsafe_allow_html=True,
    )


CEFR = {"C2": 6, "C1": 5, "B2": 4, "B1": 3, "A2": 2, "A1": 1}


def cefr_level(level):
    for k, v in CEFR.items():
        if k in level:
            return v
    return 6  # native / langue maternelle


# ---------- language ----------
qp = st.query_params.get("lang", "fr")
lang = qp if qp in UI else "fr"
_, top_r = st.columns([7, 1])
with top_r:
    choice = st.segmented_control(
        "lang", ["FR", "EN"], default=lang.upper(), label_visibility="collapsed", key="lang_sw"
    )
    if choice and choice.lower() != lang:
        st.query_params["lang"] = choice.lower()
        st.rerun()
t = UI[lang]
D = load(lang)

# ---------- hero ----------
ICONS = ["🎓", "🌍", "⚡", "✅"]
facts = "".join(
    f'<div class="fact{" amber" if i in (1, 3) else ""}"><div class="ico">{ICONS[i % 4]}</div>'
    f'<div><b>{esc(f["b"])}</b><small>{esc(f["span"])}</small></div></div>'
    for i, f in enumerate(D["facts"])
)
st.markdown(
    f"""<div class="hero">
<div class="eyebrow">{esc(D["eyebrow"])}</div>
<div class="hero-name">Nada <span>Latrech</span></div>
<div class="roles">{"".join(f'<span class="role">{esc(r)}</span>' for r in D["roles"])}</div>
<div class="lede">{md(D["lede"])}</div>
<div class="facts">{facts}</div>
<div class="cta">
<a class="primary" href="https://www.linkedin.com/in/nada-l-7b268a412" target="_blank" rel="noopener">LinkedIn</a>
<a class="ghost" href="https://github.com/nadapianist" target="_blank" rel="noopener">GitHub</a>
</div></div>""",
    unsafe_allow_html=True,
)


# ---------- projects ----------
def cat_style(c):
    fg, bg = CAT_COLORS.get(c, ("#0b6e75", "#e3f1f1"))
    return f"color:{fg};background:{bg}"


def explain_html(p):
    h = ""
    if p["desc"]:
        h += f'<div class="pdesc">{md(p["desc"])}</div>'
    if p["flow"]:
        h += f'<div class="flow">{esc(p["flow"])}</div>'
    if p["bullets"]:
        h += '<ul class="pts">' + "".join(f"<li>{md(b)}</li>" for b in p["bullets"]) + "</ul>"
    return h + tag_html(p["tags"])


def head_html(p):
    return (
        f'<div class="cardhead"><span class="cat" style="{cat_style(p["cat"])}">'
        f'{esc(D["categories"].get(p["cat"], ""))}</span><span class="when">{esc(p["when"])}</span></div>'
        f'<div class="kicker">{esc(p["kicker"])}</div>'
        f'<div class="ptitle">{esc(p["title"])}</div>'
        + (f'<div class="psub">{esc(p["subtitle"])}</div>' if p["subtitle"] else "")
    )


@st.dialog(" ", width="large")
def show_project(p):
    # The explanation comes first, then the demo / presentation below it.
    st.markdown(head_html(p) + explain_html(p), unsafe_allow_html=True)
    names, kinds = [], []
    if p["video"]:
        names.append(t["demo_tab"]); kinds.append("video")
    if p["slides"]:
        names.append(t["pres_tab"]); kinds.append("slides")
    if p["images"]:
        names.append(t["shots_tab"]); kinds.append("images")
    if not kinds:
        return
    for tab, kind in zip(st.tabs(names), kinds):
        with tab:
            if kind == "video":
                st.video(media(p["video"]), start_time=p["start"] or 0, end_time=p["end"])
            elif kind == "slides":
                n = len(p["slides"])
                i = 1
                if n > 1:
                    i = st.slider(t["slide"], 1, n, 1, key=f"sl_{p['title']}")
                st.image(media(p["slides"][i - 1]), width="stretch")
                st.caption(f'{t["slide"]} {i} {t["of"]} {n}')
            else:
                for im in p["images"]:
                    st.image(media(im), width="stretch")


def card(p, idx):
    fg, bg = CAT_COLORS.get(p["cat"], ("#0b6e75", "#e3f1f1"))
    with st.container(key=f"box_card_{p['cat']}_{idx}"):
        if p["thumb"]:
            st.image(media(p["thumb"]), width="stretch")
        else:
            st.markdown(
                f'<div class="gen" style="background:linear-gradient(135deg,{bg},#ffffff);color:{fg}">'
                f'{esc(p["thumb_text"] or p["kicker"])}</div>',
                unsafe_allow_html=True,
            )
        st.markdown(head_html(p) + explain_html(p), unsafe_allow_html=True)
        if p["video"]:
            label = t["video"]
        elif p["slides"]:
            label = t["slides"]
        elif p["images"]:
            label = t["images"]
        else:
            return
        if st.button(label, key=f"open_{idx}", width="stretch", type="primary"):
            show_project(p)


# ---------- tabs ----------
tab_p, tab_x, tab_e, tab_c, tab_k = st.tabs(t["tabs"])

with tab_p:
    sec(D["nav"].get("projects", ""), D["projects_title"], f'{D["projects_intro"]} {t["media_hint"]}')
    cats = list(D["categories"].keys())
    counts = {c: (len(D["projects"]) if c == "all" else sum(p["cat"] == c for p in D["projects"])) for c in cats}
    sel = st.pills(
        t["filter"], cats, default="all", key=f"filter_{lang}",
        format_func=lambda c: f'{D["categories"][c]} · {counts[c]}',
        label_visibility="collapsed",
    ) or "all"
    st.write("")
    shown = [(i, p) for i, p in enumerate(D["projects"]) if sel == "all" or p["cat"] == sel]
    grid = st.columns(2, gap="medium")
    for k, (i, p) in enumerate(shown):
        with grid[k % 2]:
            card(p, i)

with tab_x:
    sec(D["nav"].get("experience", ""), D["experience_title"])
    jobs = "".join(
        f'<div class="job"><div class="job-top"><h3>{esc(j["title"])}</h3><span class="when">{esc(j["when"])}</span></div>'
        f'<ul class="pts">{"".join(f"<li>{md(li)}</li>" for li in j["bullets"])}</ul>{tag_html(j["tags"])}</div>'
        for j in D["experience"]
    )
    st.markdown(f'<div class="tl">{jobs}</div>', unsafe_allow_html=True)

with tab_e:
    sec(D["nav"].get("education", ""), D["education_title"])
    dd_badge = f'<span class="dd-badge">{esc(t["dd"])}</span>'
    degrees = "".join(
        f'<div class="degree">{dd_badge if d["dd"] else ""}'
        f'<b>{esc(d["title"])}</b><span>{esc(d["where"])}</span></div>'
        for d in D["degrees"]
    )
    langs = "".join(
        f'<div class="lang"><div class="lang-top"><b>{esc(l["name"])}</b><span>{esc(l["level"])}</span></div>'
        f'<div class="cefr">{"".join("<i class=on></i>" if k < cefr_level(l["level"]) else "<i></i>" for k in range(6))}</div></div>'
        for l in D["languages"]
    )
    h0 = D["edu_headings"][0] if D["edu_headings"] else ""
    h1 = D["edu_headings"][1] if len(D["edu_headings"]) > 1 else t["lang"]
    st.markdown(
        f'<div class="grid2"><div class="panel"><h3>{esc(h0)}</h3>{degrees}</div>'
        f'<div class="panel"><h3>{esc(h1)}</h3>{langs}</div></div>',
        unsafe_allow_html=True,
    )
    st.write("")
    sec(D["nav"].get("skills", ""), D["skills_title"])
    skills = "".join(f'<div class="panel"><h3>{esc(g["group"])}</h3>{tag_html(g["tags"])}</div>' for g in D["skills"])
    st.markdown(f'<div class="skills">{skills}</div>', unsafe_allow_html=True)

with tab_c:
    sec("Certifications", D["certs_title"])
    cc = st.columns(3, gap="medium")
    for i, c in enumerate(D["certs"]):
        with cc[i % 3]:
            with st.container(key=f"box_cert_{i}"):
                if c["img"] and (HERE / c["img"]).exists():
                    st.image(media(c["img"]), width="stretch")
                st.markdown(
                    f'<div class="kicker">{esc(c["issuer"])}</div><div class="ptitle" style="font-size:1.05rem">{esc(c["title"])}</div>'
                    + (f'<div class="pdesc">{esc(c["desc"])}</div>' if c["desc"] else "")
                    + ('<ul class="pts">' + "".join(f"<li>{esc(s)}</li>" for s in c["skills"]) + "</ul>" if c["skills"] else ""),
                    unsafe_allow_html=True,
                )
                if c["verify"]:
                    st.link_button(t["verify"], c["verify"], width="stretch")

with tab_k:
    k = D["contact"]
    items = "".join(
        f'<div class="contact"><small>{esc(it["label"])}</small>'
        + (f'<a href="{esc(it["href"])}" target="_blank" rel="noopener">{esc(it["value"])}</a>' if it["href"] else f'<span>{esc(it["value"])}</span>')
        + "</div>"
        for it in k["items"]
    )
    st.markdown(
        f'<div class="contact-band"><div class="eyebrow">{esc(D["nav"].get("contact", "Contact"))}</div>'
        f'<h2>{esc(k["title"])}</h2><p>{esc(k["text"])}</p><div class="contacts">{items}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown('<div class="foot">© 2026 Nada Latrech · Île-de-France</div>', unsafe_allow_html=True)
