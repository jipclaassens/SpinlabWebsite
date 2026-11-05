"""Writes a news page from the text of a "News item" issue. Run by .github/workflows/news-from-issue.yml.

Reads ISSUE_TITLE and ISSUE_BODY from the environment. Pictures dragged into the issue live on
GitHub; they are downloaded to static/files/news/ so the page does not depend on the issue. The
text is treated as data: it only ever ends up in a markdown file.
"""
import datetime
import os
import re
import unicodedata
import urllib.request

import yaml

THEMES = {"Accessibility": "accessibility", "Climate adaptation": "climate-adaptation", "Education": "education",
          "Geodesign": "geodesign", "Land use modelling": "land-use-modelling", "PhD research": "phd",
          "Spatial analysis": "spatial-analysis", "Spatial planning": "spatial-planning"}
EMPTY = "_No response_"
PICTURE_RE = re.compile(r'!\[([^\]]*)\]\((https://[^)\s]+)\)|<img[^>]*?src="(https://[^"]+)"[^>]*>')
ALLOWED_PICTURE_HOSTS = ("https://github.com/", "https://user-images.githubusercontent.com/", "https://private-user-images.githubusercontent.com/")
TYPES = {"image/jpeg": "jpg", "image/png": "png", "image/gif": "gif", "image/webp": "webp"}


def sections(body):
    # an issue form arrives as "### Label" followed by the answer
    parts = re.split(r"^### (.+)$", body.replace("\r\n", "\n"), flags=re.M)
    return {parts[i].strip(): parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}


def slug_of(title):
    text = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:60].rstrip("-") or "news"


def download(url, stem, token):
    headers = {"User-Agent": "spinlab-site"}
    if token and url.startswith("https://github.com/"):
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as answer:
        extension = TYPES.get(answer.headers.get_content_type())
        if not extension:
            raise ValueError(f"not a picture: {url}")
        data = answer.read()
    path = f"static/files/news/{stem}.{extension}"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "wb").write(data)
    return "/" + path.removeprefix("static/")


def summary_of(text):
    plain = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    plain = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", plain)
    plain = re.sub(r"\s+", " ", re.sub(r"[#*_>`]", " ", plain)).strip()
    return plain if len(plain) <= 180 else plain[:180].rsplit(" ", 1)[0] + "..."


def main():
    title = os.environ["ISSUE_TITLE"].strip()
    answers = sections(os.environ["ISSUE_BODY"])
    text = answers.get("Text", "").strip()
    if not text or text == EMPTY:
        raise SystemExit("The issue has no text")

    date = answers.get("Date", "").strip()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        date = datetime.date.today().isoformat()
    slug = slug_of(title)
    themes = [THEMES[m] for m in re.findall(r"^- \[[xX]\] (.+)$", answers.get("Themes", ""), flags=re.M) if m in THEMES]

    first_picture = None
    counter = 0

    def replace(match):
        nonlocal first_picture, counter
        url = match.group(2) or match.group(3)
        if not url.startswith(ALLOWED_PICTURE_HOSTS):
            return match.group(0)
        counter += 1
        local = download(url, f"{date}-{slug}-{counter}", os.environ.get("GH_TOKEN"))
        first_picture = first_picture or local
        return f"![{match.group(1) or ''}]({local})"

    text = PICTURE_RE.sub(replace, text)
    meta = {"title": title, "date": date, "description": summary_of(text)}
    if themes:
        meta["themes"] = themes
    if first_picture:
        meta["image"] = first_picture

    path = f"content/news/{date}-{slug}.md"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    front = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False, width=1000).strip()
    with open(path, "w", encoding="utf-8", newline="\n") as fn:
        fn.write(f"---\n{front}\n---\n\n{text}\n")

    url = f"https://spinlab.vu.nl/news/{slug}/"
    print("written", path)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as fn:
            fn.write(f"file={path}\nurl={url}\n")


if __name__ == "__main__":
    main()
