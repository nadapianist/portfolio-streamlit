"""Build the Streamlit portfolio's data from the HTML portfolio.

Reads ../index-fr.html and ../index.html, writes data/fr.json and data/en.json,
copies the media the app needs into ./media, and renders each PDF
presentation into slide images (media/slides/<name>/NN.jpg) so the app can
show presentations in any browser without a PDF viewer.

Run from anywhere:  python build_data.py
"""
import json
import re
import shutil
from pathlib import Path

import pymupdf
from bs4 import BeautifulSoup

HERE = Path(__file__).resolve().parent
SRC = HERE.parent
OUT_MEDIA = HERE / "media"
OUT_DATA = HERE / "data"


def txt(el):
    return " ".join(el.get_text(" ", strip=True).split()) if el else ""


def inner_html(el):
    """Keep <strong>/<code> as markdown, drop other tags."""
    if el is None:
        return ""
    for b in el.find_all(["strong", "b"]):
        b.replace_with(f"**{b.get_text(strip=True)}**")
    for c in el.find_all("code"):
        c.replace_with(f"`{c.get_text(strip=True)}`")
    out = " ".join(el.get_text(" ", strip=True).split())
    return re.sub(r" ([.,)])", lambda m: m.group(1), out).replace("( ", "(")


def tags(el):
    return [t.get_text(strip=True) for t in el.select(".tag")] if el else []


def parse(path):
    s = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    hero = s.select_one("header.hero")
    data = {
        "eyebrow": txt(hero.select_one(".eyebrow")),
        "roles": [txt(r) for r in hero.select(".role")],
        "lede": inner_html(hero.select_one(".lede")),
        "facts": [{"b": txt(f.b), "span": txt(f.span)} for f in hero.select(".fact")],
        "nav": {a["href"].lstrip("#"): txt(a) for a in s.select("nav ul a")},
    }

    exp = s.find("section", id="experience")
    data["experience_title"] = txt(exp.select_one(".sec-head h2"))
    data["experience"] = [
        {
            "title": txt(j.select_one("h3")),
            "when": txt(j.select_one(".when")),
            "bullets": [inner_html(li) for li in j.select("ul li")],
            "tags": tags(j),
        }
        for j in exp.select("article.job")
    ]

    proj = s.find("section", id="projects")
    head = proj.select_one(".sec-head")
    data["projects_title"] = txt(head.h2)
    data["projects_intro"] = txt(head.p)
    data["categories"] = {
        b["data-f"]: txt(b).strip() for b in proj.select(".filters button")
    }
    cards = []
    for c in proj.select("article.card"):
        img = c.select_one(".thumb img")
        gen = c.select_one(".thumb.gen span")
        body = c.select_one(".card-body")
        desc = [p for p in body.find_all("p", recursive=False) if not p.get("class")]
        cards.append(
            {
                "cat": c.get("data-c"),
                "video": c.get("data-video"),
                "pdf": c.get("data-pdf"),
                "images": c.get("data-images", "").split("|") if c.get("data-images") else [],
                "start": int(c["data-start"]) if c.get("data-start") else 0,
                "end": int(c["data-end"]) if c.get("data-end") else None,
                "thumb": img["src"] if img else None,
                "thumb_text": txt(gen),
                "when": txt(c.select_one(".card-meta .when")),
                "kicker": txt(body.select_one(".eyebrow-c")),
                "title": txt(body.h3),
                "subtitle": txt(body.select_one(".subtitle")),
                "desc": " ".join(inner_html(p) for p in desc),
                "flow": txt(body.select_one(".flow")),
                "bullets": [inner_html(li) for li in body.select("ul li")],
                "tags": tags(body),
            }
        )
    data["projects"] = cards

    edu = s.find("section", id="education")
    data["education_title"] = txt(edu.select_one(".sec-head h2"))
    data["degrees"] = [
        {"title": txt(d.b), "where": txt(d.find("span", class_=False)), "dd": "dd" in d.get("class", [])}
        for d in edu.select(".degree")
    ]
    data["languages"] = [
        {"name": txt(l.select_one(".lang-top b")), "level": txt(l.select_one(".lang-top span"))}
        for l in edu.select(".lang")
    ]
    panels = edu.select(".panel h3")
    data["edu_headings"] = [txt(h.contents[0]) if h.contents else txt(h) for h in panels]

    sk = s.find("section", id="skills")
    data["skills_title"] = txt(sk.select_one(".sec-head h2"))
    data["skills"] = [{"group": txt(g.h3), "tags": tags(g)} for g in sk.select(".skill-group")]

    ce = s.find("section", id="certifications")
    data["certs_title"] = txt(ce.select_one(".sec-head h2"))
    data["certs"] = [
        {
            "img": c.get("data-img"),
            "verify": c.get("data-verify"),
            "issuer": txt(c.small),
            "title": txt(c.b),
            "desc": txt(c.find("span")),
            "skills": [txt(li) for li in c.select(".cert-skills li")],
        }
        for c in ce.select(".cert")
    ]

    ft = s.find("footer", id="contact")
    data["contact"] = {
        "title": txt(ft.h2),
        "text": txt(ft.p),
        "items": [
            {
                "label": txt(c.small),
                "value": txt(c.select_one(".val")),
                "href": c.select_one("a.val")["href"] if c.select_one("a.val") else None,
            }
            for c in ft.select(".contact")
        ],
    }
    return data


def copy_media(paths):
    for rel in paths:
        if not rel:
            continue
        src, dst = SRC / rel, HERE / rel
        if src.exists() and (not dst.exists() or dst.stat().st_size != src.stat().st_size):
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def render_pdf(rel):
    """Render a PDF to slide JPEGs; return the list of relative slide paths."""
    name = Path(rel).stem
    out = OUT_MEDIA / "slides" / name
    if out.exists() and any(out.iterdir()):
        return [f"media/slides/{name}/{p.name}" for p in sorted(out.glob("*.jpg"))]
    out.mkdir(parents=True, exist_ok=True)
    slides = []
    with pymupdf.open(SRC / rel) as doc:
        for i, page in enumerate(doc, 1):
            # ~1400 px wide whatever the page size
            zoom = 1400 / page.rect.width
            pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
            p = out / f"{i:02d}.jpg"
            pix.save(p, jpg_quality=72)
            slides.append(f"media/slides/{name}/{p.name}")
    return slides


def main():
    OUT_DATA.mkdir(exist_ok=True)
    slide_cache = {}
    for lang, fname in (("fr", "index-fr.html"), ("en", "index.html")):
        data = parse(SRC / fname)
        media = []
        for p in data["projects"]:
            media += [p["video"], p["thumb"], *p["images"]]
            if p["pdf"]:
                if p["pdf"] not in slide_cache:
                    slide_cache[p["pdf"]] = render_pdf(p["pdf"])
                p["slides"] = slide_cache[p["pdf"]]
            else:
                p["slides"] = []
        media += [c["img"] for c in data["certs"]]
        copy_media(media)
        (OUT_DATA / f"{lang}.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        print(lang, len(data["projects"]), "projects,", len(data["certs"]), "certs")


if __name__ == "__main__":
    main()
