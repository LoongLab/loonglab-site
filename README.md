# LoongLab website

Static marketing site for LoongLab and its products (starting with LoongCode).

Framework-free, by design: authored HTML in `public/`, shared regions injected
from `templates/`, output generated into `_site/`. No npm dependency, no bundler,
no runtime backend. Deployment is a static directory, so the same output works on
Vercel, Cloudflare Pages, or any static host.

## Layout

```
public/                 authored source
  index.html            home (hero + terminal demo + context + products)
  get-started/          install, model setup, first run
  first-investigation/  a guided first task
  guides/               workflow guides (index + fix-a-failing-test, refactor-a-module, track-down-a-bug, automate-in-ci)
  blog/                 index + "The context window is a budget"
  faq/                  objection-handling Q&A
  about/                company narrative (identity lives in the header/footer lockup)
  assets/               styles, theme/main/demo JS, favicon
templates/              shared header/footer partials
scripts/site.py         build / check / serve
evidence/               source-of-truth notes backing site claims
_site/                  generated output (gitignored)
vercel.json             Vercel config (framework: null, output: _site)
```

## Content honesty rules

- **No invented numbers.** The site states no token-saving percentage or absolute
  figure, because no benchmark has been run. Add a number only with a matching
  file in `evidence/`.
- **No invented case studies.** There is no showcase page until a real session is
  recorded and published with its transcript and usage.
- **The terminal demo is labelled illustrative.** It shows the tool loop; it is
  not a recorded run.
- Claims about context mechanics are backed by `evidence/context-management.md`,
  which cites the exact source files.


## Commands

```sh
python3 scripts/site.py check         # validate links, metadata, region markers
python3 scripts/site.py build         # render templates into _site/ (+ sitemap)
python3 scripts/site.py serve         # build if needed, then preview :4173
python3 scripts/site.py deploy-check  # check + build, then ready to deploy
```

Only the Python standard library is required.

## Adding a page

1. Add `public/<route>/index.html` with these markers where the shared chrome goes:

   ```html
   <!-- BEGIN:site-header --><!-- END:site-header -->
   ...
   <!-- BEGIN:site-footer --><!-- END:site-footer -->
   ```

2. Add a `<title>` and a `<meta name="description">` (both are checked).
3. Use relative links (`../../assets/...`); the checker resolves them.
4. Run `python3 scripts/site.py check`.

## Deploying to Vercel

Import this directory as a project. Vercel reads `vercel.json`, runs the build,
and serves `_site/`. No framework preset is needed.

## Notes

- `scripts/site.py` is modelled on REA's MIT-licensed website tooling; see
  [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
- The site is proprietary; the LoongCode product it describes is Apache-2.0.
