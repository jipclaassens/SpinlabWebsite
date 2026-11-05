# How to update the SPINlab website

Every page of [spinlab.vu.nl](https://spinlab.vu.nl) is a text file in this repository. You change a file here on GitHub, in your browser, and a few minutes later the site is updated. You do not need to install anything.

**What you need:** a free GitHub account, and write access to this repository. Ask a colleague who already has access to add you.

**If something goes wrong:** a mistake cannot take the site down. If a change contains an error, the old site simply stays online and GitHub sends you an email. Every earlier version is kept, so anything can be undone.

## Add a thesis

Theses are the part of the site that changes most, and this site is the only place where they are public.

1. Open **Issues**, click **New issue** and choose **Thesis**.
2. Fill in the form and drag the pdf into the box.
3. Click **Create**, then add the label **publish** on the right.

The thesis gets its own page, which search engines and Google Scholar can find.

## Post a news item

1. Open **Issues**, click **New issue** and choose **News item**.
2. Write your text and drag your pictures into the box.
3. Click **Create**, then add the label **publish**. Without that label it waits, so a colleague can read it first.

## Add or remove a person

Open the file `data/people.yaml` and click the pencil icon. The instructions are at the top of the file.

- Someone joins: copy a block and change the name and role.
- Someone leaves: change their `group` to `former`.
- A photo: upload it to `static/files/people/` and add a `photo:` line.

Phone numbers and publication lists are not kept here. They come from the [VU research portal](https://research.vu.nl/), so they stay correct by themselves.

## Change the text of a page

Open the folder `content/`. The folders follow the web address: `spinlab.vu.nl/research/spatial-planning/` is the file `content/research/spatial-planning/index.md`. Open the file and click the pencil icon.

The text is plain, with a few marks:

```
## A heading

A [link](https://example.org) and a list:

- first point
- second point
```

Click **Commit changes** when you are done. Leave the lines at the very top, between the two `---` lines, as they are, unless you want to change the title.

## Add a page

Go to the right folder under `content/`, choose **Add file**, and give the file a short name ending in `.md`. Start it like this:

```
---
title: The title of the page
description: One sentence about the page.
---

Your text.
```

It appears in the side menu by itself.

## Good to know

- **Publications** on the home page and the research pages come from the research portal by themselves. Add a publication to the portal and it appears here within a week.
- **Documents:** link to a publication where it already lives, preferably its DOI or its page in the research portal. Upload a pdf only if it has no other home.
- **Everything you commit is public** within minutes, so do not treat a commit as a draft. To try something out first, use an issue.
- **Stuck?** Open an issue here and describe what you wanted to do.

## Credits

The map pictures are drawn from CBS Bestand Bodemgebruik 2022, Natuurnetwerk Nederland and the BAG. The texts, pictures and documents remain with their authors.
