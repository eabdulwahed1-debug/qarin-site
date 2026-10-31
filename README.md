# قارن (qarin-site)

Arabic product-review and buying-guide website for shoppers in Saudi Arabia, monetized through affiliate programs (Amazon.sa first).

## How it works
- `content/` — page sources (HTML with a JSON `<!--meta ... -->` header).
- `assets/style.css` — site styles (RTL, light/dark).
- `site.json` — site name, domain (`base_url`) and the Amazon.sa tracking tag (`amazon_sa_tag`).
- `build.py` — generates the site into `docs/` (served by GitHub Pages from `main` / `docs`).

Build: `python3 build.py`

## Content rules
- Never invent product specifications, test results or reviews.
- Every guide shows the affiliate disclosure (added automatically).
- Amazon links use the `[[amz:search words|label]]` shortcode so the tracking tag is added in one place.

## Control documents
See `project-docs/` (document-control naming: `Doc-ID_Title_RevN`).
