# spinlab.vu.nl

Source of the website of the Spatial Information Laboratory (SPINlab), Vrije Universiteit Amsterdam.
Pages are text files in `content/`. GitHub turns them into plain web pages and uploads them to the
server. You need a free GitHub account with write access to this repository, and nothing else: no
installation, and no WordPress.

A change you commit is online within a few minutes. If you make a mistake that breaks the build, the
old site simply stays up and GitHub sends you an email.

## Post a news item

The easiest way: open [Issues](../../issues/new/choose), choose **News item**, write your text and drag
your pictures into the box. Add the label `publish` and it goes online. Without that label it waits,
so a colleague can read it first.

If you prefer files: in `content/news/` choose **Add file**, name it like
`2026-11-05-short-title.md`, and start it like this:

```
---
title: The title of the item
date: 2026-11-05
description: One sentence for the news list.
---

Your text.
```

## Change who works here

Open [`data/people.yaml`](data/people.yaml) and click the pencil. The instructions are at the top of the
file: someone joining is a new block, someone leaving is `group: former`. Addresses, phone numbers and
publication lists are not kept here, because they live in the research portal.

## Change a page

Find the page in `content/` (the folders follow the web address) and click the pencil. Headings start
with `#`, links look like `[text](https://example.org)`, and a table is a few lines with `|`.

## Add a thesis

This site is the only place where these theses are public, so this is the page that matters most.

The easiest way: open [Issues](../../issues/new/choose), choose **Thesis**, fill in the form and drag the
pdf into the box. Add the label `publish` and it goes online, with its own page that search engines and
Google Scholar can find. Only do this if the student agreed to it being public.

To do it by hand, upload the pdf to `static/files/theses/` and add a block to
[`data/theses.yaml`](data/theses.yaml); the instructions are at the top of that file.

## Documents

Link to a publication where it already lives, preferably its DOI or its page in the
[research portal](https://research.vu.nl/), instead of uploading the pdf here. Upload a document only if
it has no other home.

## Recent publications

The list on the home page and on Publications comes from the research portal: everyone marked
`feed: true` in `data/people.yaml`. Add a publication to the portal and it appears here within a week.

## Credits

The map pictures are drawn from CBS Bestand Bodemgebruik 2022. The texts, pictures and documents remain with their authors.
