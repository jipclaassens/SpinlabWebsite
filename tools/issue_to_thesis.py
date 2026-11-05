"""Adds a thesis from the text of a "Thesis" issue. Run by .github/workflows/thesis-from-issue.yml.

Reads ISSUE_TITLE and ISSUE_BODY from the environment. The pdf dragged into the issue lives on GitHub;
it is downloaded to static/files/theses/ so the thesis does not depend on the issue. The block goes
into data/theses.yaml as text, so the instructions at the top of that file stay where they are.
"""
import os
import re
import unicodedata
import urllib.request

import yaml

THESES = "data/theses.yaml"
PDF_RE = re.compile(r"https://github\.com/[^\s)\]]+|https://[a-z-]*user-[a-z]*\.?githubusercontent\.com/[^\s)\]]+")


def sections(body):
    # an issue form arrives as "### Label" followed by the answer
    parts = re.split(r"^### (.+)$", body.replace("\r\n", "\n"), flags=re.M)
    return {parts[i].strip(): parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}


def slug_of(author, title):
    text = unicodedata.normalize("NFKD", f"{author} {title}").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:70].rstrip("-")


def download(url, path, token):
    headers = {"User-Agent": "spinlab-site"}
    if token and url.startswith("https://github.com/"):
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=180) as answer:
        data = answer.read()
    if not data.startswith(b"%PDF"):
        raise SystemExit(f"This is not a pdf: {url}")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "wb").write(data)


def main():
    title = os.environ["ISSUE_TITLE"].strip()
    answers = sections(os.environ["ISSUE_BODY"])
    if not re.search(r"^- \[[xX]\]", answers.get("Permission", ""), flags=re.M):
        raise SystemExit("The box that the student gave permission is not ticked")

    data = yaml.safe_load(open(THESES, encoding="utf-8"))
    programme = next((key for key, label in data["programmes"].items() if label == answers.get("Programme", "").strip()), None)
    author = answers.get("Student", "").strip()
    date = answers.get("Date graded", "").strip()
    links = PDF_RE.findall(answers.get("The thesis as a pdf", ""))
    if not programme or not author or not links:
        raise SystemExit("The form is missing a programme, a student or the pdf")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        raise SystemExit(f"The date should look like 2026-08-20, not {date}")

    slug = slug_of(author, title)
    taken = {t.get("slug") for t in data["theses"]}
    base, number = slug, 1
    while slug in taken:
        number += 1
        slug = f"{base}-{number}"

    download(links[0], f"static/files/theses/{slug}.pdf", os.environ.get("GH_TOKEN"))

    entry = {"author": author, "title": title, "degree": answers.get("Degree", "").strip(), "programme": programme, "date": date, "year": int(date[:4])}
    supervisor = answers.get("Supervisor", "").strip()
    if supervisor and supervisor != "_No response_":
        entry["supervisor"] = supervisor
    entry["file"] = f"/files/theses/{slug}.pdf"
    entry["slug"] = slug

    block = yaml.safe_dump([entry], allow_unicode=True, sort_keys=False, width=1000)
    text = open(THESES, encoding="utf-8").read()
    assert "\ntheses:\n" in text
    with open(THESES, "w", encoding="utf-8", newline="\n") as fn:
        fn.write(text.replace("\ntheses:\n", "\ntheses:\n" + block, 1))
    yaml.safe_load(open(THESES, encoding="utf-8"))  # stop here rather than commit a broken file

    print("added", slug)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as fn:
            fn.write(f"url=https://spinlab.vu.nl/supervised-theses/{slug}/\n")


if __name__ == "__main__":
    main()
