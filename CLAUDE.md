# spinlab.vu.nl: instructions for Claude

The site of the Spatial Information Laboratory at Vrije Universiteit Amsterdam. It replaced a WordPress
install. The generator is a trimmed copy of the one behind objectvision.nl (`ObjectVision/ObjectVisionWebsite`),
with its own look: VU colours, real land-use maps, no monospace labels or numbered cards.

The language of the site is English. Some older news items and archived pages are in Dutch and stay so.

## Building and checking

```
pip install -r requirements.txt
python build.py --check    # renders into _site/ and fails on internal links that lead nowhere
python build.py --serve    # and serves it on port 8000
```

There is no test suite. `--check` is the test: a broken link is the failure mode this generator has.
Look at a changed page in a browser too, also at phone width.

Only what ends up in `_site/` is deployed: pages from `content/`, styling from `theme/`, pictures of the
design from `assets/`, documents from `static/files/`. Anything else is in git but not on the server.

## How it fits together

| where | what |
|---|---|
| `content/` | one markdown file per page; the folders follow the url. `news/` files start with their date, which stays out of the url |
| `data/people.yaml` | the People page |
| `data/publications_latest.json` | recent publications from the research portal; refreshed at each build by `tools/fetch_pure.py`, and this committed copy is the fallback when the portal refuses |
| `data/redirects.yaml` | old addresses. Pages get a small html page at the old address, which works on any server; files go through `.htaccess` |
| `theme/` | the two page templates and the stylesheet |
| `tools/make_maps.py` | draws the map pictures in `assets/map/`; needs the CBS land-use raster, which is not in the repository |

A page uses these tokens on a line of their own: `{{news}}`, `{{news:theme}}`, `{{chips}}`, `{{people}}`,
`{{publications}}`, `{{publications:theme}}`, `{{theses}}`, `{{children}}`. `{{publications:theme}}` picks from the portal's
list by the words in `THEME_WORDS` in `build.py`. The side menu and the breadcrumbs come from the folder structure, so a
new page appears there without further work. The top menu is `NAV` in `build.py`.

A page with `archived: true` in its front matter shows a notice that it is no longer updated, with a link to
the page above it. `banner: name` puts a map from `assets/map/` on top of a page.

Research has its six themes side by side plus the archive, and Tools is a section of its own. Keep the tree that shallow: a page belongs under the section a visitor would look for it in, because the side menu and the breadcrumbs follow the folders.

## Theses

The theses are the main reason this site exists: they are handed in at the university but not published
anywhere else, so this is the only place where they are public. Treat their addresses as permanent, and do
not change the `slug` of a thesis that is online.

`data/theses.yaml` is the list. Each thesis with a pdf gets its own page under `/supervised-theses/`, with
the `citation_*` tags Google Scholar reads, and a place in the sitemap and the search index. The pdfs are in
`static/files/theses/`. `.github/workflows/thesis-from-issue.yml` adds one from the Thesis form. Students give
permission for publication when they hand in their thesis at the VU, and the form asks to confirm that.

## Documents

Link to a DOI or to the research portal rather than hosting a pdf. `static/files/` holds what has no other
home. Keep the repository under 1 GB, GitHub's recommended limit. Pictures are at most 1600 pixels on the
long side.

## Publishing

`.github/workflows/build-and-deploy.yml`. A push to `main` publishes, once the variable `DEPLOY_ENABLED` is
true; until then it only builds. The upload is rsync over ssh with a key made for this purpose; the VU server
takes keys, not passwords. Its target must be a folder of its own, because `--delete` empties it of everything
that is not in the site. The first real upload has to be checked by hand, including whether `.htaccess` works
(old file addresses, security headers).

`.github/workflows/news-from-issue.yml` turns an issue made with the News item form into a page when
somebody adds the label `publish`, and `thesis-from-issue.yml` does the same for a thesis. The labels `publish`,
`news` and `thesis` have to exist in the repository. The issue text is untrusted
input: it goes in through environment variables and only ever ends up in a markdown file.

## Before going live

- `data/people.yaml` has `verified: false`: it is the list the old site showed in June 2026, the last copy in the Internet Archive. The build warns until it has been checked.
- The web server: see Publishing.
- Set `SITE_URL` right if the address changes.

The conversion from WordPress was one-off and its scripts are not in this repository. `content/` is now the
source; a full copy of the old site was kept outside the repository.
