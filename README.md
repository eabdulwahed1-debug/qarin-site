# قارن (qarin-site)

Bilingual (Arabic + English) product-review and buying-guide website for shoppers in Saudi Arabia, monetized through affiliate programs (Amazon.sa first).

## How it works
- `content/` — Arabic page sources (HTML with a JSON `<!--meta ... -->` header), published at `/<slug>/`.
- `content-en/` — English page sources with the same paths and slugs, published at `/en/<slug>/`. Every Arabic page must have an English twin (the build lists any that are missing).
- `assets/style.css` — site styles (RTL, light/dark).
- `site.json` — site name, domain (`base_url`) and the Amazon.sa tracking tag (`amazon_sa_tag`).
- `finder.json` — the home-page buying assistant (category → budget → use) and the shop-by-budget rows; budgets in SAR, Amazon price filter uses halalas (×100).
- `featured.json` — featured products of the week (refreshed by a scheduled task).
- `build.py` — generates the site into `docs/` (served by GitHub Pages from `main` / `docs`).

Build: `python3 build.py`

## Content rules
- Never invent product specifications, test results or reviews.
- Every guide shows the affiliate disclosure (added automatically).
- Amazon links use the `[[amz:search words|label]]` shortcode so the tracking tag is added in one place.

## Control documents
See `project-docs/` (document-control naming: `Doc-ID_Title_RevN`).
