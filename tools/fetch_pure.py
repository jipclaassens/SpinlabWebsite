"""Refreshes data/publications_latest.json from the rss feeds of the VU research portal (Pure), one
feed per person marked `feed: true` in data/people.yaml.

    python tools/fetch_pure.py

The site never asks Pure anything while it is being visited. This script writes a file that goes
into the repository, so a build keeps working when the portal refuses a request. The portal refuses
the parameters in the other order (format before page) with a 403.
"""
import html
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "publications_latest.json")
KEEP = 40
HEADERS = {"User-Agent": "Mozilla/5.0 (spinlab.vu.nl site build)"}


def meta_line(description):
    # the feed's description is the citation as html: title, then authors, then journal
    text = re.sub(r"<h3.*?</h3>", " ", html.unescape(description or ""), flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    text = re.split(r"\s*\.?\s*Research output\s*:", text)[0].strip(" ,.")
    return re.sub(r"\s+([,.])", r"\1", text)[:180]


def main():
    people = yaml.safe_load(open(os.path.join(ROOT, "data", "people.yaml"), encoding="utf-8"))["people"]
    found, failed = {}, []
    for person in people:
        if not person.get("feed") or not person.get("pure"):
            continue
        url = f"https://research.vu.nl/en/persons/{person['pure']}/publications/?page=0&format=rss"
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=60) as answer:
                items = ET.fromstring(answer.read()).findall(".//item")
        except Exception as error:
            failed.append(f"{person['pure']}: {error}")
            continue
        for item in items:
            link = (item.findtext("link") or "").split("?")[0]
            date = item.findtext("{http://purl.org/dc/elements/1.1/}date") or ""
            found[link] = {"title": re.sub(r"\s+", " ", item.findtext("title") or "").strip(), "url": link, "date": date[:10], "meta": meta_line(item.findtext("description"))}
    if not found:
        print("nothing fetched, keeping the existing file:", failed)
        sys.exit(0)
    items = sorted(found.values(), key=lambda i: i["date"], reverse=True)[:KEEP]
    with open(OUT, "w", encoding="utf-8", newline="\n") as fn:
        json.dump({"source": "research.vu.nl", "items": items}, fn, ensure_ascii=False, indent=1)
        fn.write("\n")
    print(f"{len(items)} publications written; failed feeds: {failed}")


if __name__ == "__main__":
    main()
