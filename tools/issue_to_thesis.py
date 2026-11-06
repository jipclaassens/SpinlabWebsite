"""Adds a thesis from the text of a "Thesis" issue. Run by .github/workflows/thesis-from-issue.yml.

Reads ISSUE_TITLE and ISSUE_BODY from the environment. The pdf dragged into the issue lives on GitHub;
it is downloaded to static/files/theses/ and put on data/documents.yaml, and the workflow then uploads
it to the web server, so the thesis does not depend on the issue. git ignores the pdf itself. The block
goes into data/theses.yaml as text, so the instructions at the top of that file stay where they are.
"""
import os
import re
import unicodedata
import urllib.request

import yaml

from documents import add_to_list

THESES = "data/theses.yaml"
PARTICLES = {"van", "de", "der", "den", "het", "'t", "t", "ter", "te", "ten", "el", "von", "la", "le", "di", "da", "du", "dos", "del"}
LOOSE_WORDS = {"a", "an", "the", "of", "in", "on", "and", "for", "to", "with", "at", "by", "from", "de", "het", "een", "van", "en", "op", "voor", "met", "naar", "der", "te", "bij", "aan", "als", "om", "or", "as", "under", "using", "s", "t"}
TITLE_LENGTH = 55
PDF_RE = re.compile(r"https://github\.com/[^\s)\]]+|https://[a-z-]*user-[a-z]*\.?githubusercontent\.com/[^\s)\]]+")


def sections(body):
    # an issue form arrives as "### Label" followed by the answer
    parts = re.split(r"^### (.+)$", body.replace("\r\n", "\n"), flags=re.M)
    return {parts[i].strip(): parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}


def plain(text):
    text = re.sub("['’‘]", "", text.replace("ø", "o").replace("Ø", "O").replace("ß", "ss"))
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def surname_of(author):
    author = re.sub("[’‘]", "'", author.strip())
    if "," in author:
        parts = [p.strip() for p in author.split(",")]
        if len(parts) >= 3 and parts[1] and parts[1].lower().split()[0] in PARTICLES:   # Bruggen, van, E.
            return f"{parts[1]} {parts[0]}"
        words = parts[0].split()
        n = len(words)
        while n > 1 and words[n - 1].lower() in PARTICLES:                              # Egmond van, P.
            n -= 1
        return " ".join(words[n:] + words[:n])
    words = author.split()
    for i in range(1, len(words)):                                                      # Anne van Kempen
        if words[i].lower() in PARTICLES:
            return " ".join(words[i:])
    return words[-1]


def name_of(author, year, title):
    # author-year-title, for the page and the pdf alike; of the title only the part before a colon, as far as it fits
    for mark in (":", ";", "?", " – ", " - ", ". "):
        part = title.split(mark)[0]
        if part != title and len(part.split()) >= 2:
            title = part
    words = []
    for word in plain(title).split("-"):
        if words and len("-".join(words + [word])) > TITLE_LENGTH:
            break
        words.append(word)
    while len(words) > 1 and words[-1] in LOOSE_WORDS:
        words.pop()
    return f"{plain(surname_of(author))}-{year}-{'-'.join(words)}"


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

    slug = name_of(author, date[:4], title)
    taken = {t.get("slug") for t in data["theses"]}
    base, number = slug, 1
    while slug in taken:
        number += 1
        slug = f"{base}-{number}"

    document = f"/files/theses/{slug}.pdf"
    download(links[0], f"static{document}", os.environ.get("GH_TOKEN"))
    add_to_list(document)

    entry = {"author": author, "title": title, "degree": answers.get("Degree", "").strip(), "programme": programme, "date": date, "year": int(date[:4])}
    supervisor = answers.get("Supervisor", "").strip()
    if supervisor and supervisor != "_No response_":
        entry["supervisor"] = supervisor
    entry["file"] = document
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
            fn.write(f"url=https://spinlab.vu.nl/supervised-theses/{slug}/\ndocument={document}\n")


if __name__ == "__main__":
    main()
