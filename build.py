"""Renders content/*.md into a static site in _site/.

    python build.py            # build
    python build.py --serve    # build and serve on port 8000
    python build.py --check    # build and fail on internal links that lead nowhere
    python build.py --preview spinlab --check   # a preview for a subfolder of another site, in _preview/

A preview shows the site before the server is ready. It carries a notice and stays out of search
engines, and it leaves the documents out: their links open the copies on the current site.

Every markdown file becomes a directory with an index.html, so urls stay clean. The people, the
recent publications and the redirects come from data/. Nothing runs on the server: what ends up in
_site/ is plain html, css and a few files.
"""
import argparse
import glob
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from urllib.parse import unquote

import markdown
import yaml

SITE_URL = "https://spinlab.vu.nl"
SITE_NAME = "SPINlab"
CONTENT_DIR = "content"
ASSETS_DIR = "assets"
STATIC_DIR = "static"  # copied to the site root unchanged; the documents live in static/files
DATA_DIR = "data"
OUT_DIR = "_site"
BASE = ""  # the subfolder of a preview, for example /spinlab; empty for the real site
CURRENT_SITE_UPLOADS = "https://spinlab.vu.nl/wp-content/uploads/"
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg")
PREVIEW_NOTE = ('<div class="preview-note">Preview of the new SPINlab website. The current site is still at '
                '<a href="https://spinlab.vu.nl/">spinlab.vu.nl</a>, and documents open from there.</div>')

HOME_NEWS = 4
HOME_PUBLICATIONS = 5
LIST_PUBLICATIONS = 15
HOME_THESES = 4

# Order and grouping of the main navigation. A page that is not listed is still built and is
# reachable through its parent page.
NAV = [
    ("Research", "/research/", [
        ("Spatial analysis and modelling", "/research/spatial-analysis-modelling/"),
        ("Accessibility", "/research/accessibility/"),
        ("Geodesign", "/research/geodesign/"),
        ("Research archive", "/research/researcharchive/"),
    ]),
    ("Tools", "/support/tools/", [
        ("Land Use Scanner", "/research/spatial-analysis-modelling/land-use-scanner-model/"),
        ("Land Use Scanner, student edition", "/support/tools/landusescanner/"),
        ("BAG geocoder", "/support/tools/geodms-bag-geocoder/"),
        ("Definite", "/support/tools/definite-bosda/"),
    ]),
    ("Education", "/education/", [
        ("UNIGIS distance learning", "/unigis/"),
    ]),
    ("Theses", "/supervised-theses/", []),
    ("Publications", "/publications/", [
        ("PhD dissertations", "/publications/phd-dissertations/"),
        ("Land Use Scanner publications", "/publications/land-use-scanner-publications/"),
    ]),
    ("News", "/news/", []),
    ("People", "/people/", []),
    ("About", "/about/", [
        ("About SPINlab", "/about/"),
        ("Partners", "/partners/"),
        ("Support for researchers", "/support/"),
        ("Contact", "/contact/"),
    ]),
]

# The research themes, as tiles on the home page. Kept here rather than parsed out of the
# markdown, because their order is structure, not prose.
THEMES = [
    ("Land use modelling", "/research/spatial-analysis-modelling/land-use-modelling/",
     "Analysing and simulating land-use change, with the Land Use Scanner as the main instrument.", "land-use-modelling"),
    ("Spatial planning", "/research/spatial-analysis-modelling/spatial-planning/",
     "What planning policy does to cities and the countryside, and what it could do.", "spatial-planning"),
    ("Climate adaptation", "/research/spatial-analysis-modelling/climate-adaptation/",
     "How land use and climate change influence each other, and what that means for adaptation.", "climate-adaptation"),
    ("Location value", "/research/spatial-analysis-modelling/location-value/",
     "What location adds to the value of property, from open space to aircraft noise.", "location-value"),
    ("Accessibility", "/research/accessibility/",
     "Accessibility analysis on highly detailed spatial data, alongside transport economics.", "accessibility"),
    ("Geodesign", "/research/geodesign/",
     "Tools that combine models, maps and multi-criteria analysis in collaborative planning.", "geodesign"),
]

# Labels for the themes a news item can carry in its front matter.
THEME_LABELS = {
    "accessibility": "Accessibility", "climate-adaptation": "Climate adaptation", "digital-humanities": "Digital humanities",
    "education": "Education", "geodesign": "Geodesign", "land-use-modelling": "Land use modelling", "phd": "PhD research",
    "rijkswaterstaat": "Rijkswaterstaat", "risk-management": "Risk management", "spatial-analysis": "Spatial analysis",
    "spatial-planning": "Spatial planning", "support": "Support",
}

MONTHS = ("January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December")


def read_page(path):
    raw = open(path, encoding="utf-8").read()
    meta = {}
    if raw.startswith("---\n"):
        end = raw.index("\n---\n", 4)
        meta = yaml.safe_load(raw[4:end]) or {}
        raw = raw[end + 5:]
    return meta, raw


def url_for(rel_path):
    # content/index.md -> /, content/about.md -> /about/, content/research/index.md -> /research/.
    # A news file starts with its date so the folder sorts by time; the date stays out of the url.
    rel_path = rel_path.replace("\\", "/")
    if rel_path == "404.md":
        return "/404.html"   # apache serves this by path, so it is not a directory
    parts = rel_path[:-3].split("/")
    if parts[0] == "news" and len(parts) == 2:
        parts[1] = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", parts[1])
    if parts[-1] == "index":
        parts = parts[:-1]
    return "/" + "/".join(parts) + "/" if parts else "/"


def collect_pages():
    pages = {}
    for dir_path, _, file_names in os.walk(CONTENT_DIR):
        for name in sorted(file_names):
            if not name.endswith(".md"):
                continue
            full = os.path.join(dir_path, name)
            rel = os.path.relpath(full, CONTENT_DIR).replace("\\", "/")
            meta, body = read_page(full)
            pages[rel] = {"meta": meta, "body": body, "url": url_for(rel), "source": full}
    return pages


def format_date(value):
    # front matter dates come back from yaml as a date object, or as a string if quoted
    try:
        stamp = datetime.strptime(str(value)[:10], "%Y-%m-%d")
    except ValueError:
        return str(value)
    return f"{stamp.day} {MONTHS[stamp.month - 1]} {stamp.year}"


def nav_html(current_url):
    out = ['<nav class="nav" aria-label="Main">']
    for label, href, children in NAV:
        active = current_url == href or current_url.startswith(href) or any(current_url.startswith(c[1]) for c in children)
        cls = ' class="on"' if active and href != "/" else ""
        if children:
            out.append('<div class="nav-group">')
            out.append(f'<a href="{href}"{cls}>{html.escape(label)}</a>')
            out.append('<div class="nav-drop">')
            for child_label, child_href in children:
                out.append(f'<a href="{child_href}">{html.escape(child_label)}</a>')
            out.append("</div></div>")
        else:
            out.append(f'<a href="{href}"{cls}>{html.escape(label)}</a>')
    out.append('<a class="nav-search" href="/search/" aria-label="Search this site">Search</a>')
    out.append("</nav>")
    return "\n".join(out)


def by_url(pages):
    return {page["url"]: page for page in pages.values()}


def breadcrumb_html(page, index):
    parts = page["url"].strip("/").split("/")
    crumbs = ['<a href="/">Home</a>']
    path = "/"
    for part in parts[:-1]:
        path += part + "/"
        parent = index.get(path)
        if parent:
            crumbs.append(f'<a href="{path}">{html.escape(str(parent["meta"].get("title", part)))}</a>')
    return '<div class="crumbs">' + "<span>/</span>".join(crumbs) + "</div>"


def children_of(url, index):
    found = []
    for other_url, page in index.items():
        if other_url.startswith(url) and other_url != url and other_url.count("/") == url.count("/") + 1:
            found.append((str(page["meta"].get("title", other_url)), other_url))
    return sorted(found)


def sidebar_html(page, index):
    # the pages next to and below this one; WordPress kept this in a menu somebody had to maintain
    url = page["url"]
    if url.startswith("/news/") or url.count("/") < 2:
        return ""
    own = children_of(url, index)
    parent_url = url.rsplit("/", 2)[0] + "/"
    siblings = children_of(parent_url, index) if parent_url != "/" else []
    if not own and not siblings:
        return ""
    out = ['<aside class="side" aria-label="In this section">']
    if parent_url in index and parent_url != "/":
        out.append(f'<a class="side-up" href="{parent_url}">{html.escape(str(index[parent_url]["meta"].get("title", "")))}</a>')
    for title, link in siblings or [(page["meta"].get("title", ""), url)]:
        on = ' class="on"' if link == url else ""
        out.append(f'<a{on} href="{link}">{html.escape(str(title))}</a>')
        if link == url:
            for child_title, child_link in own:
                out.append(f'<a class="side-sub" href="{child_link}">{html.escape(str(child_title))}</a>')
    out.append("</aside>")
    return "".join(out)


def news_items(pages, theme=None):
    # every page under content/news/ except the index itself, newest first
    items = [dict(page["meta"], url=page["url"])
             for rel, page in pages.items()
             if rel.startswith("news/") and rel != "news/index.md" and page["meta"].get("date")]
    if theme:
        items = [item for item in items if theme in (item.get("themes") or [])]
    return sorted(items, key=lambda item: str(item.get("date", "")), reverse=True)


def news_row(item):
    # an item without a picture of its own gets a piece of map, always the same one for that item
    fallback = THEMES[sum(map(ord, item["url"])) % len(THEMES)][3]
    picture = f'<img src="{html.escape(item.get("image") or f"/assets/map/{fallback}.png")}" alt="" loading="lazy">'
    return (f'<a class="news-item" href="{item["url"]}"><span class="news-pic">{picture}</span><span class="news-text">'
            f'<span class="news-date">{html.escape(format_date(item.get("date", "")))}</span>'
            f'<span class="news-title">{html.escape(str(item.get("title", "")))}</span>'
            f'<span class="news-blurb">{html.escape(str(item.get("description", "")))}</span></span></a>')


def news_html(pages, theme=None, limit=None, by_year=False):
    items = news_items(pages, theme)
    if limit:
        items = items[:limit]
    if not items:
        return '<p class="muted">No updates on this topic yet.</p>'
    if not by_year:
        return '<div class="news-list">' + "".join(news_row(item) for item in items) + "</div>"
    out, year = [], None
    for item in items:
        if str(item["date"])[:4] != year:
            if year:
                out.append("</div>")
            year = str(item["date"])[:4]
            out.append(f'<h2 class="year">{year}</h2><div class="news-list">')
        out.append(news_row(item))
    out.append("</div>")
    return "".join(out)


def theme_chips(pages, current=None):
    used = sorted({t for item in news_items(pages) for t in (item.get("themes") or [])}, key=lambda t: THEME_LABELS.get(t, t))
    chips = [f'<a class="chip{" on" if not current else ""}" href="/news/">All news</a>']
    for theme in used:
        cls = " on" if theme == current else ""
        chips.append(f'<a class="chip{cls}" href="/news/theme/{theme}/">{html.escape(THEME_LABELS.get(theme, theme))}</a>')
    return '<div class="chips">' + "".join(chips) + "</div>"


def load_people():
    return yaml.safe_load(open(f"{DATA_DIR}/people.yaml", encoding="utf-8"))


def initials(name):
    words = [w for w in re.split(r"[\s-]+", name) if w[:1].isupper()]
    return (words[0][0] + words[-1][0]) if len(words) > 1 else name[:2]


def person_card(person):
    name = html.escape(person["name"])
    photo = (f'<img src="{html.escape(person["photo"])}" alt="" loading="lazy">' if person.get("photo")
             else f'<span class="initials">{html.escape(initials(person["name"]))}</span>')
    links = []
    if person.get("pure"):
        links.append(f'<a href="https://research.vu.nl/en/persons/{html.escape(person["pure"])}">Research portal</a>')
    if person.get("page"):
        links.append(f'<a href="{html.escape(person["page"])}">Research page</a>')
    if person.get("email"):
        links.append(f'<a href="mailto:{html.escape(person["email"])}">Email</a>')
    return (f'<div class="person"><div class="person-pic">{photo}</div><div><div class="person-name">{name}</div>'
            f'<div class="person-role">{html.escape(person.get("role", ""))}</div>'
            f'<div class="person-links">{" ".join(links)}</div></div></div>')


def people_html():
    data = load_people()
    out = []
    if not data.get("verified"):
        out.append('<p class="draft">Draft: this list comes from the 2019 version of the site and has not been checked yet.</p>')
    for key, label in data["groups"].items():
        members = [p for p in data["people"] if p.get("group") == key]
        if members:
            out.append(f'<h2>{html.escape(label)}</h2><div class="people">{"".join(person_card(p) for p in members)}</div>')
    return "".join(out)


def publications_html(limit):
    path = f"{DATA_DIR}/publications_latest.json"
    if not os.path.exists(path):
        return ""
    items = json.load(open(path, encoding="utf-8"))["items"][:limit]
    rows = "".join(
        f'<a class="pub" href="{html.escape(item["url"])}"><span class="pub-year">{html.escape(item["date"][:4])}</span>'
        f'<span class="pub-title">{html.escape(item["title"])}</span>'
        f'<span class="pub-meta">{html.escape(item.get("meta", ""))}</span></a>'
        for item in items)
    return f'<div class="pub-list">{rows}</div>'


def load_theses():
    data = yaml.safe_load(open(f"{DATA_DIR}/theses.yaml", encoding="utf-8"))
    return data["programmes"], data["theses"]


def thesis_sort_key(thesis):
    return (str(thesis.get("date") or thesis.get("year") or ""), str(thesis.get("title", "")))


def thesis_when(thesis):
    return format_date(thesis["date"]) if thesis.get("date") else str(thesis.get("year", ""))


def thesis_url(thesis):
    return f"/supervised-theses/{thesis['slug']}/"


def thesis_row(thesis):
    title = html.escape(str(thesis["title"]))
    parts = [thesis.get("author"), thesis.get("degree"), thesis_when(thesis)]
    meta = " · ".join(html.escape(str(p)) for p in parts if p)
    if thesis.get("file"):
        title = f'<a class="thesis-title" href="{thesis_url(thesis)}">{title}</a>'
    else:
        title = f'<span class="thesis-title">{title}</span>'
        meta += " · no public copy"
    return f'<div class="thesis">{title}<div class="thesis-meta">{meta}</div></div>'


def theses_html():
    # the collection: one section per programme, newest first, with a filter that needs javascript
    # and therefore stays hidden without it
    programmes, theses = load_theses()
    online = sum(1 for t in theses if t.get("file"))
    out = [f'<p class="muted">{len(theses)} theses, of which {online} can be read online.</p>',
           '<input class="search-box" id="thesis-filter" type="search" placeholder="Filter by title, author, programme or year" aria-label="Filter the theses" hidden>',
           '<div class="chips">' + "".join(f'<a class="chip" href="#{key}">{html.escape(label)}</a>' for key, label in programmes.items()) + "</div>"]
    for key, label in programmes.items():
        members = sorted((t for t in theses if t["programme"] == key), key=thesis_sort_key, reverse=True)
        if members:
            out.append(f'<section class="thesis-group" id="{key}"><h2>{html.escape(label)}</h2>{"".join(thesis_row(t) for t in members)}</section>')
    out.append('<p class="muted" id="thesis-none" hidden>No thesis matches this filter.</p><script src="/assets/theses.js" defer></script>')
    return "".join(out)


def home_theses_html():
    _, theses = load_theses()
    online = [t for t in theses if t.get("file")]
    latest = sorted(online, key=thesis_sort_key, reverse=True)[:HOME_THESES]
    return (f'<p>{len(online)} bachelor and master theses supervised at SPINlab, open for anyone to read. '
            'They are handed in at the university but not published anywhere else.</p>'
            '<p class="more"><a href="/supervised-theses/">All theses</a></p>',
            "".join(thesis_row(t) for t in latest))


def thesis_page_head(thesis):
    # Google Scholar reads these tags, which is how a thesis can be found outside this site
    day = str(thesis.get("date") or thesis.get("year") or "").replace("-", "/")
    tags = {"citation_title": thesis["title"], "citation_author": thesis.get("author", ""), "citation_publication_date": day,
            "citation_dissertation_institution": thesis_institution(thesis), "citation_pdf_url": SITE_URL + thesis["file"]}
    return "".join(f'<meta name="{name}" content="{html.escape(str(value))}">\n' for name, value in tags.items() if value)


def thesis_institution(thesis):
    for name in ("University College Utrecht", "Amsterdam University College"):
        if name in str(thesis.get("degree", "")):
            return name
    return "Amsterdam University College" if thesis.get("programme") == "auc" else "Vrije Universiteit Amsterdam"


def thesis_body(thesis, programmes):
    rows = [("Author", thesis.get("author")), ("Degree", thesis.get("degree")), ("Programme", programmes.get(thesis["programme"])),
            ("Graded" if thesis.get("date") else "Year", thesis_when(thesis)), ("Supervisor", thesis.get("supervisor"))]
    facts = "".join(f"<dt>{name}</dt><dd>{html.escape(str(value))}</dd>" for name, value in rows if value)
    size = os.path.getsize(STATIC_DIR + thesis["file"]) / 1e6 if os.path.exists(STATIC_DIR + thesis["file"]) else 0
    institution = thesis_institution(thesis)
    degree = str(thesis.get("degree", ""))
    place = degree if institution in degree else f"{degree}, {institution}"
    year = str(thesis.get("date") or thesis.get("year") or "")[:4]
    note = f'<p class="archived">{html.escape(str(thesis["note"]))}</p>' if thesis.get("note") else ""
    annexes = "".join(f'<p><a href="{html.escape(a["file"])}">{html.escape(str(a["label"]))}</a></p>' for a in thesis.get("attachments", []))
    return (f'<dl class="facts">{facts}</dl>{note}'
            f'<p><a class="btn btn-blue" href="{html.escape(thesis["file"])}">Read the thesis (pdf, {size:.1f} MB)</a></p>{annexes}'
            f'<h2>How to cite</h2><p>{html.escape(str(thesis.get("author", "")))} ({year}). {html.escape(str(thesis["title"]))}. {html.escape(place)}.</p>'
            '<p class="updated">Are you the author, and would you like this page changed or removed? <a href="/contact/">Contact us</a>.</p>')


def write_thesis_pages(css_name):
    programmes, theses = load_theses()
    shell = open("theme/page.html", encoding="utf-8").read()
    urls = []
    for thesis in theses:
        if not thesis.get("file"):
            continue
        url = thesis_url(thesis)
        urls.append(url)
        title = html.escape(str(thesis["title"]))
        write_out(url, fill(shell, title=f"{title} · {SITE_NAME}", description=html.escape(f"{thesis.get('degree', '')} by {thesis.get('author', '')}."),
                            canonical=SITE_URL + url, nav=nav_html(url), crumbs='<div class="crumbs"><a href="/">Home</a><span>/</span><a href="/supervised-theses/">Supervised theses</a></div>',
                            pagetitle=title, notice="", side="", layout="no-side", body=thesis_body(thesis, programmes), updated="", css=css_name,
                            year=str(datetime.now(timezone.utc).year), headextra=thesis_page_head(thesis)))
    return urls


def theme_tiles():
    cells = "".join(
        f'<a class="tile" href="{url}"><img class="tile-map" src="/assets/map/{key}.png" alt="" loading="lazy">'
        f'<span class="tile-title">{html.escape(title)}</span><span class="tile-text">{html.escape(blurb)}</span></a>'
        for title, url, blurb, key in THEMES)
    return f'<div class="tiles">{cells}</div>'


def rewrite_links(body):
    # relative links to other markdown files work on github; on the site they become urls
    return re.sub(r"\]\(([^)\s]+\.md)(#[^)]*)?\)", lambda m: "](" + url_for(m.group(1).replace("../", "")) + (m.group(2) or "") + ")", body)


def render_body(page, pages):
    meta = page["meta"]
    body = markdown.markdown(rewrite_links(page["body"]), extensions=["tables", "attr_list", "sane_lists", "md_in_html"])
    # a table has a width of its own, so on a phone it needs a scroller instead of being cut off
    body = body.replace("<table>", '<div class="table-scroll"><table>').replace("</table>", "</table></div>")
    body = body.replace("<img ", '<img loading="lazy" ')

    def token(match):
        name, _, argument = match.group(1).partition(":")
        if name == "news":
            return news_html(pages, argument or None, limit=None if not argument else 6, by_year=not argument)
        if name == "chips":
            return theme_chips(pages)
        if name == "people":
            return people_html()
        if name == "publications":
            return publications_html(LIST_PUBLICATIONS)
        if name == "theses":
            return theses_html()
        if name == "children":
            kids = children_of(page["url"], by_url(pages))
            return '<ul class="children">' + "".join(f'<li><a href="{u}">{html.escape(t)}</a></li>' for t, u in kids) + "</ul>"
        return match.group(0)

    # markdown wraps a token on a line of its own in a paragraph
    body = re.sub(r"<p>\{\{([a-z-]+(?::[a-z-]+)?)\}\}</p>", token, body)
    body = re.sub(r"\{\{([a-z-]+(?::[a-z-]+)?)\}\}", token, body)
    if page["url"].startswith("/news/") and page["url"] != "/news/" and meta.get("date"):
        tags = "".join(f'<a class="chip" href="/news/theme/{t}/">{html.escape(THEME_LABELS.get(t, t))}</a>' for t in (meta.get("themes") or []))
        body = f'<p class="news-stamp">{html.escape(format_date(meta["date"]))}</p>' + body + (f'<div class="chips">{tags}</div>' if tags else "")
    return body


def hashed_name(path, stem, extension):
    # the asset name carries a hash of its contents, so a changed file is a new url and browsers
    # pick it up straight away
    digest = hashlib.sha256(open(path, "rb").read()).hexdigest()[:10]
    return f"{stem}.{digest}.{extension}"


def fill(shell, **values):
    values.setdefault("headextra", "")
    for key, value in values.items():
        shell = shell.replace("{{" + key + "}}", value)
    return shell


def render(page, pages, css_name):
    meta = page["meta"]
    title = str(meta.get("title", SITE_NAME))
    is_home = page["url"] == "/"
    index = by_url(pages)
    shell = open("theme/home.html" if is_home else "theme/page.html", encoding="utf-8").read()
    side = sidebar_html(page, index)
    notice = ""
    if meta.get("archived"):
        notice = '<p class="archived">This page describes earlier work and is no longer updated.</p>'
    updated = ""
    if meta.get("updated") and not page["url"].startswith("/news/"):
        updated = f'<p class="updated">Last updated {html.escape(format_date(meta["updated"]))}</p>'
    extra = {}
    if is_home:
        thesis_text, thesis_rows = home_theses_html()
        extra = {
            "thesistext": thesis_text,
            "thesisrows": thesis_rows,
            "tiles": theme_tiles(),
            "homenews": news_html(pages, limit=HOME_NEWS),
            "homepubs": publications_html(HOME_PUBLICATIONS),
            "heading": html.escape(str(meta.get("heading", title))),
            "lead": html.escape(str(meta.get("lead", ""))),
        }
    return fill(shell,
                title=html.escape(title if is_home else f"{title} · {SITE_NAME}"),
                description=html.escape(str(meta.get("description", ""))),
                canonical=SITE_URL + page["url"],
                nav=nav_html(page["url"]),
                crumbs=breadcrumb_html(page, index),
                pagetitle=html.escape(title),
                notice=notice,
                side=side,
                layout="with-side" if side else "no-side",
                body=render_body(page, pages),
                updated=updated,
                css=css_name,
                year=str(datetime.now(timezone.utc).year),
                **extra)


def old_document_addresses():
    # new document path -> its name on the current site, which is where a preview sends people
    files = yaml.safe_load(open(f"{DATA_DIR}/redirects.yaml", encoding="utf-8")).get("files") or {}
    return {new: old.replace("/wp-content/uploads/", "", 1) for old, new in files.items() if new.startswith("/files/")}


OLD_DOCUMENTS = {}


def as_preview(text):
    def document(match):
        path = match.group(1)
        if path.lower().endswith(IMAGE_EXTENSIONS):
            return match.group(0)
        old = OLD_DOCUMENTS.get("/files/" + path, path)
        return f'href="{CURRENT_SITE_UPLOADS}{old}"'

    text = re.sub(r'href="/files/([^"]+)"', document, text)
    text = re.sub(r'\b(href|src)="/(?!/)', lambda m: f'{m.group(1)}="{BASE}/', text)
    text = re.sub(r'<link rel="canonical"[^>]*>\n?', "", text)
    text = text.replace("<head>", '<head>\n<meta name="robots" content="noindex">', 1)
    return re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + PREVIEW_NOTE, text, count=1)


def write_out(url, text):
    path = os.path.join(OUT_DIR, url.lstrip("/")) if url.endswith(".html") else os.path.join(OUT_DIR, url.strip("/"), "index.html")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(as_preview(text) if BASE else text)


def theme_pages(pages, css_name):
    # one list per theme, so a theme page can link to all its news
    shell = open("theme/page.html", encoding="utf-8").read()
    used = {t for item in news_items(pages) for t in (item.get("themes") or [])}
    for theme in sorted(used):
        label = THEME_LABELS.get(theme, theme)
        url = f"/news/theme/{theme}/"
        write_out(url, fill(shell, title=html.escape(f"{label} news · {SITE_NAME}"), description=html.escape(f"News about {label.lower()} from SPINlab."),
                            canonical=SITE_URL + url, nav=nav_html(url), crumbs='<div class="crumbs"><a href="/">Home</a><span>/</span><a href="/news/">News</a></div>',
                            pagetitle=html.escape(label), notice="", side="", layout="no-side",
                            body=theme_chips(pages, theme) + news_html(pages, theme, by_year=True), updated="", css=css_name,
                            year=str(datetime.now(timezone.utc).year)))
    return used


def write_preview_htaccess():
    # Sits in the subfolder of the other site and overrides its security policy, which does not
    # allow the embedded videos. Nothing else of the other site changes.
    lines = [
        f"ErrorDocument 404 {BASE}/404.html",
        "<IfModule mod_headers.c>",
        '  Header always set X-Robots-Tag "noindex"',
        '  Header always set Content-Security-Policy "default-src \'self\'; script-src \'self\'; '
        "style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; "
        "frame-src https://www.youtube-nocookie.com https://player.vimeo.com; "
        "frame-ancestors 'self'; base-uri 'self'; form-action 'self'; object-src 'none'\"",
        "</IfModule>",
    ]
    open(f"{OUT_DIR}/.htaccess", "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")


def copy_static():
    if not os.path.isdir(STATIC_DIR):
        return
    if not BASE:
        shutil.copytree(STATIC_DIR, OUT_DIR, dirs_exist_ok=True)
        return
    # a preview only takes the pictures; documents stay where they are on the current site
    for dir_path, _, file_names in os.walk(STATIC_DIR):
        for name in file_names:
            if name.lower().endswith(IMAGE_EXTENSIONS):
                target = os.path.join(OUT_DIR, os.path.relpath(os.path.join(dir_path, name), STATIC_DIR))
                os.makedirs(os.path.dirname(target), exist_ok=True)
                shutil.copy(os.path.join(dir_path, name), target)


def write_redirects(pages):
    # A moved page gets a small html page at its old address, which works on any webserver.
    # A file cannot do that, so old file addresses are handled in .htaccess.
    redirects = yaml.safe_load(open(f"{DATA_DIR}/redirects.yaml", encoding="utf-8"))
    taken = {page["url"] for page in pages.values()}
    for old, new in (redirects.get("pages") or {}).items():
        if old in taken:
            continue
        target = html.escape(new)
        write_out(old, f'<!doctype html><meta charset="utf-8"><title>Moved</title><meta name="robots" content="noindex">'
                       f'<link rel="canonical" href="{SITE_URL}{target}"><meta http-equiv="refresh" content="0; url={target}">'
                       f'<p>This page has moved to <a href="{target}">{target}</a>.</p>\n')
    lines = [
        "# Generated by build.py - do not edit on the server, edit build.py instead.",
        "",
        "DirectoryIndex index.html",
        "ErrorDocument 404 /404.html",
        "",
        "# the old host name, should it point here as well",
        "RewriteEngine On",
        "RewriteCond %{HTTP_HOST} ^spinlab\\.labs\\.vu\\.nl$ [NC]",
        "RewriteRule ^(.*)$ https://spinlab.vu.nl/$1 [R=301,L]",
        "RewriteRule ^wp-(login|signup|cron|trackback)\\.php$ / [R=301,L]",
        "RewriteRule ^wp-admin(/.*)?$ / [R=301,L]",
        "",
        "# documents that moved or that now live elsewhere, such as at a doi or in the research portal",
    ]
    for old, new in (redirects.get("files") or {}).items():
        lines.append(f'Redirect 301 "{old}" "{new}"')
    lines += [
        "# every other old upload address: the same path under /files/",
        "RedirectMatch 301 ^/wp-content/uploads/(.*)$ /files/$1",
        "",
        "<IfModule mod_headers.c>",
        '  Header always set X-Content-Type-Options "nosniff"',
        '  Header always set X-Frame-Options "SAMEORIGIN"',
        '  Header always set Referrer-Policy "strict-origin-when-cross-origin"',
        '  Header always set Content-Security-Policy "default-src \'self\'; script-src \'self\'; '
        "style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; "
        "frame-src https://www.youtube-nocookie.com https://player.vimeo.com; "
        "frame-ancestors 'self'; base-uri 'self'; form-action 'self'; object-src 'none'\"",
        '  <FilesMatch "\\.(html|txt|xml|json)$">',
        '    Header always set Cache-Control "no-cache"',
        "  </FilesMatch>",
        '  <FilesMatch "\\.(css|js|png|jpg|jpeg|gif|svg|ico|webp|woff2?)$">',
        '    Header always set Cache-Control "public, max-age=3600, must-revalidate"',
        "  </FilesMatch>",
        "</IfModule>",
    ]
    open(f"{OUT_DIR}/.htaccess", "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")


def close_folders():
    # A folder without an index.html can be listed by the webserver, which the VU security team
    # flagged on the old site. This closes them whatever the server is set to.
    for dir_path, _, file_names in os.walk(f"{OUT_DIR}/files"):
        if "index.html" not in file_names:
            open(os.path.join(dir_path, "index.html"), "w", encoding="utf-8").write(
                f'<!doctype html><meta charset="utf-8"><title>Documents</title><meta name="robots" content="noindex"><p><a href="{BASE}/publications/">Publications</a></p>\n')


def write_sitemap(pages, extra_urls):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    urls = sorted([p["url"] for p in pages.values() if not p["url"].endswith(".html")] + extra_urls)
    with open(f"{OUT_DIR}/sitemap.xml", "w", encoding="utf-8") as fn:
        fn.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for url in urls:
            fn.write(f"  <url><loc>{SITE_URL}{url}</loc><lastmod>{today}</lastmod></url>\n")
        fn.write("</urlset>\n")
    open(f"{OUT_DIR}/robots.txt", "w", encoding="utf-8").write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")


def write_feed(pages):
    items = news_items(pages)[:20]
    rows = "".join(
        f"<item><title>{html.escape(str(i.get('title', '')))}</title><link>{SITE_URL}{i['url']}</link>"
        f"<guid>{SITE_URL}{i['url']}</guid><pubDate>{datetime.strptime(str(i['date'])[:10], '%Y-%m-%d').strftime('%a, %d %b %Y 00:00:00 +0000')}</pubDate>"
        f"<description>{html.escape(str(i.get('description', '')))}</description></item>"
        for i in items)
    open(f"{OUT_DIR}/feed.xml", "w", encoding="utf-8").write(
        f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>SPINlab news</title><link>{SITE_URL}/news/</link>'
        f"<description>News from the Spatial Information Laboratory, Vrije Universiteit Amsterdam</description>{rows}</channel></rss>\n")


def write_search_index(pages):
    records = []
    for page in pages.values():
        if page["url"].endswith(".html") or page["url"] == "/search/":
            continue
        text = re.sub(r"!\[[^\]]*\]\([^)]*\)|\{\{[^}]*\}\}|\{:[^}]*\}", " ", page["body"])
        text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
        text = re.sub(r"[#*_>`|]", " ", text)
        records.append({"t": str(page["meta"].get("title", "")), "u": page["url"], "d": str(page["meta"].get("description", ""))[:160],
                        "x": re.sub(r"\s+", " ", text).strip()[:3000]})
    # every thesis is a record of its own, otherwise only the first few on the list could be found
    programmes, theses = load_theses()
    for thesis in theses:
        records.append({"t": str(thesis["title"]), "u": thesis_url(thesis) if thesis.get("file") else "/supervised-theses/",
                        "d": " · ".join(str(p) for p in (thesis.get("author"), thesis.get("degree"), thesis_when(thesis)) if p),
                        "x": f"{thesis.get('author', '')} {programmes.get(thesis['programme'], '')} {thesis.get('degree', '')} {thesis.get('year', '')}"})
    for record in records:
        record["u"] = BASE + record["u"]
    json.dump(records, open(f"{OUT_DIR}/search.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))


REF_RE = re.compile(r'\b(?:href|src)="(/[^"#?]*)')


def check_links():
    # The failure this generator has: a link to a page or file that does not exist.
    broken = {}
    for path in glob.glob(f"{OUT_DIR}/**/*.html", recursive=True):
        text = open(path, encoding="utf-8").read()
        for ref in set(REF_RE.findall(text)):
            local = ref[len(BASE):] if BASE and ref.startswith(BASE + "/") else ref
            target = os.path.join(OUT_DIR, unquote(local).lstrip("/").replace("/", os.sep))
            if not (os.path.isfile(target) or os.path.isfile(os.path.join(target, "index.html"))):
                broken.setdefault(ref, []).append(os.path.relpath(path, OUT_DIR))
    for ref, sources in sorted(broken.items()):
        print(f"BROKEN {ref}  (on {sources[0]}{' and more' if len(sources) > 1 else ''})")
    print(f"{len(broken)} broken internal links")
    return not broken


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serve", action="store_true", help="serve the result on port 8000")
    parser.add_argument("--check", action="store_true", help="fail on internal links that lead nowhere")
    parser.add_argument("--preview", metavar="FOLDER", help="build a preview for this subfolder, in _preview/")
    args = parser.parse_args()

    global BASE, OUT_DIR, OLD_DOCUMENTS
    if args.preview:
        BASE = "/" + args.preview.strip("/")
        OUT_DIR = "_preview" + BASE
        OLD_DOCUMENTS = old_document_addresses()

    if os.path.isdir(OUT_DIR):
        shutil.rmtree(OUT_DIR)
    os.makedirs(OUT_DIR)

    css_name = hashed_name("theme/site.css", "site", "css")
    pages = collect_pages()
    for page in pages.values():
        write_out(page["url"], render(page, pages, css_name))
    used = theme_pages(pages, css_name)
    thesis_urls = write_thesis_pages(css_name)
    print(f"{len(pages)} pages, {len(thesis_urls)} thesis pages, {len(used)} news themes")

    shutil.copytree(ASSETS_DIR, f"{OUT_DIR}/assets", dirs_exist_ok=True)
    shutil.copy("theme/site.css", f"{OUT_DIR}/assets/{css_name}")
    copy_static()

    if BASE:
        write_preview_htaccess()
    else:
        write_redirects(pages)
        write_sitemap(pages, thesis_urls)
    close_folders()
    write_feed(pages)
    write_search_index(pages)
    if not load_people().get("verified"):
        print("WARNING: data/people.yaml is not verified yet; the People page shows a draft notice")
    print(f"site written to {OUT_DIR}/")

    if args.check and not check_links():
        sys.exit(1)
    if args.serve:
        subprocess.run([sys.executable, "-m", "http.server", "8000"], cwd=OUT_DIR)


if __name__ == "__main__":
    main()
