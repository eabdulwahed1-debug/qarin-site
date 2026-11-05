# AFF-001 — Affiliate Business Plan & Status — Rev 0

| Field | Value |
|---|---|
| Owner | Emad |
| Prepared by | Claude |
| Date | 2026-10-31 |
| Status | In progress |

## 0. Direction change — 2026-10-31 (brand renamed «قارن كيدز · Qarin Kids» by Qarin Group — earlier «خطوة», then «عالم طفلي» — both already used elsewhere, domain unchanged qarinsa.com)
Owner decision: the site is now **Mom & Kids only** (speech/talking aids, focus & attention aids, travel with kids, mom & baby, learning toys by age, home safety). All earlier general-category content (kitchen, tech, beauty, books, digital, sports, deals, blog, comparisons) was removed. Amazon.sa now; AliExpress Portals and eBay Partner Network under evaluation. Products are described as practice/routine aids, never as treatment.

## 1. Strategy (original, superseded by section 0)
- Channel: Arabic SEO content website (no social-media ads at start, so no Mawthooq licence needed for the site).
- Track A (local): home, kitchen, tech, health, kids, beauty products for Saudi shoppers → Amazon.sa Associates, later Noon / Boostiny.
- Track B (regional): digital tools (design, AI, freelancing) for the Arab world → Canva, Fiverr, PartnerStack programs.
- Content principle: honest guides based on published specs and verified buyer reviews; no invented testing or reviews.

## 2. Integration status (reviewed 2026-10-31)
| Integration | Status | Notes / required human action |
|---|---|---|
| GitHub repo `eabdulwahed1-debug/qarin-site` | CONNECTED | Pages from `main` / `docs` |
| Domain qarinsa.com + HTTPS | CONNECTED | DNS check OK, Enforce HTTPS on; http and www redirect to https://qarinsa.com. Renew before 2027-10-31 |
| Amazon.sa Associates (tag qarinsa-21) | CONNECTED | https://qarinsa.com added to the website list (2026-10-31). 3 qualifying sales needed by ~2027-04-29 |
| AliExpress Portals | PENDING | Application submitted by owner; waiting for approval → add tracking ID to site.json `aliexpress_tracking_id` |
| noon / eBay | ON HOLD | Removed from the site by owner decision until further notice |
| Google Search Console | CONNECTED | Property https://qarinsa.com/ verified (HTML file); sitemap.xml submitted — success, 26 pages |
| GoatCounter analytics | CONNECTED | Events: amz-momkid, pick, agent, search, compare |
| Scheduled tasks | CONNECTED | Monthly best products (1st, 10:13), weekly tip (Sun 09:47), weekly report (Thu 09:37); weekly featured task disabled |
| Boostiny / ArabClicks | PENDING | Owner to complete |

## 3. Content published (Rev 0)
1. How to choose an air fryer (kitchen)
2. How to choose a robot vacuum (kitchen)
3. White Friday smart shopping (deals)
4. How to choose a home blood-pressure monitor (health)
5. 2026-10-31: smartphones, laptops, monitors (tech); home gym (sports); travel essentials (travel); e-reader vs paper (books); digital subscriptions (digital)
6. 2026-10-31: whole site made bilingual — English version of all 37 pages under /en/, language switcher, hreflang tags, bilingual weekly reports.
7. 2026-10-31: concept change — home page is now a 3-step buying assistant (12 categories, budget, use → filtered Amazon.sa results sorted by reviews) + shop-by-budget rows + weekly featured products; guides moved below. Rebrand: Qarin logo, navy/orange theme.
8. 2026-10-31: full redesign to Mom & Kids — new warm theme, logo, hero art; 4 section pages (need/speech, focus, travel, mom); finder with 6 needs; shop-by-need tiles (momkid.json); top search goes straight to Amazon.sa with tag. Old content removed.
9. 2026-10-31: photo redesign (Unsplash), design system (Readex Pro + IBM Plex Sans Arabic), Khutwa assistant + instant search, price-compare page (Amazon + AliExpress), brand line 'by Qarin Group', monthly best-products block. Full review: 26 pages, 0 broken links, 72/72 Amazon links tagged, 0 JS errors, no mobile overflow.
10. 2026-11-01: weekly tip (speech) — «ألعاب تساعد الطفل على الكلام» / "Toys that help kids talk" at /tips/toys-that-help-kids-talk/ and /en/tips/toys-that-help-kids-talk/; added 'Helpful reads' list to the speech section page.
11. 2026-11-05: tip (travel) — «أفضل عربية أطفال للسفر» / "Best travel stroller" at /tips/best-travel-stroller/ (+ /en/); 'Helpful reads' added to travel section. Owner asked for more traffic: tip task raised to 3 pages/week (Sun/Tue/Thu), sections with most Amazon clicks first.
Plus (removed 2026-10-31): 2 comparisons (air fryer single vs dual basket; robot vacuum LiDAR vs camera), 1 blog article (spotting fake reviews), Picks page, Deals calendar, Categories, Blog, client-side Search, home, guides index, 7 category pages, about, contact, disclosure, privacy, terms.

## 4. Next actions
1. Owner: update site URL in Amazon Associates and add qarinsa.com property in Search Console.
2. Claude: set `base_url`, sitemap; add model comparison tables with verified prices.
3. Claude: recheck sitemap status in Search Console (first fetch showed 'couldn't fetch', usually temporary).
4. Claude: weekly scheduled content + link/price refresh + monthly report.
