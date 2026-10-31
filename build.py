#!/usr/bin/env python3
"""Build the bilingual static site into docs/ (served by GitHub Pages).

Arabic pages live in content/ and are published at /<slug>/.
English pages live in content-en/ (same relative paths and slugs) and are published at /en/<slug>/.

Each content file starts with a JSON header between <!--meta and -->:
<!--meta
{"slug": "guides/air-fryer", "title": "...", "description": "...", "category": "kitchen", "type": "guide", "date": "2026-10-31"}
-->

Shortcodes inside content:
  [[amz:search words|label]]  -> Amazon.sa search link (adds the tracking tag from site.json)
  [[guides:category]]          -> cards for all guides/comparisons/articles in that category ("all" for every one)
  [[list:type:category]]       -> cards for one content type (guide, comparison, article)
  {{root}}                     -> root of the current language (use for internal links)
"""
import json
import re
import shutil
from html import escape
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).parent
SOURCES = {"ar": ROOT / "content", "en": ROOT / "content-en"}
OUT = ROOT / "docs"
SITE = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))

CAT_STYLE = {
    "kitchen": ("🍳", "#ff7a1a"),
    "tech": ("📱", "#3b6cff"),
    "beauty": ("✨", "#e2468f"),
    "kids": ("🧸", "#12a594"),
    "health": ("🩺", "#18a058"),
    "digital": ("💻", "#7c4dff"),
    "books": ("📚", "#b5651d"),
    "sports": ("🏋️", "#e5383b"),
    "travel": ("✈️", "#0096c7"),
    "deals": ("🏷️", "#e8a400"),
}

L = {
    "ar": {
        "dir": "rtl",
        "site_name": "قارن",
        "logo": "ق",
        "tagline": "أدلة شراء ومقارنات عربية صادقة",
        "categories": {
            "kitchen": "المطبخ والمنزل", "tech": "جوالات ولابتوبات", "beauty": "الجمال والعطور",
            "kids": "الأطفال والأم", "health": "الصحة وكبار السن", "digital": "اشتراكات ومنتجات رقمية",
            "books": "الكتب والقراءة", "sports": "الرياضة واللياقة", "travel": "السفر", "deals": "العروض والمواسم",
        },
        "types": {"guide": "دليل شراء", "comparison": "مقارنة", "article": "مقال"},
        "cta": {"guide": "اعرض الدليل", "comparison": "قارن الآن", "article": "اقرأ المقال"},
        "arrow": "←",
        "nav": [("", "الرئيسية"), ("guides/", "أدلة الشراء"), ("comparisons/", "مقارنات"), ("picks/", "اختيارات قارن"),
                ("deals/", "العروض"), ("categories/", "الأقسام"), ("blog/", "المدونة"), ("search/", "بحث")],
        "empty": "أدلة هذا القسم قيد الإعداد وتُنشر قريباً.",
        "updated": "آخر تحديث",
        "disc": "ⓘ يحتوي على روابط عمولة لا تغيّر السعر عليك",
        "details": "التفاصيل",
        "search_ph": "ابحث عن منتج أو دليل…",
        "search": "بحث",
        "switch": "English",
        "footer_links": [("about/", "من نحن"), ("contact/", "تواصل معنا"), ("disclosure/", "الإفصاح عن العمولة"),
                         ("privacy/", "الخصوصية"), ("terms/", "الشروط")],
        "amazon_note": "بصفتنا مشاركين في برنامج أمازون للمسوقين بالعمولة، قد نحصل على عمولة من عمليات الشراء المؤهلة.",
        "price_note": "الأسعار والتوفر تتغير باستمرار؛ تحقق من صفحة المتجر قبل الشراء.",
        "font": "Tajawal",
    },
    "en": {
        "dir": "ltr",
        "site_name": "Qarin",
        "logo": "Q",
        "tagline": "Honest buying guides and comparisons for Saudi shoppers",
        "categories": {
            "kitchen": "Kitchen & Home", "tech": "Phones & Laptops", "beauty": "Beauty & Fragrance",
            "kids": "Baby & Kids", "health": "Health & Seniors", "digital": "Subscriptions & Digital",
            "books": "Books & Reading", "sports": "Sports & Fitness", "travel": "Travel", "deals": "Deals & Seasons",
        },
        "types": {"guide": "Buying guide", "comparison": "Comparison", "article": "Article"},
        "cta": {"guide": "Read the guide", "comparison": "Compare now", "article": "Read the article"},
        "arrow": "→",
        "nav": [("", "Home"), ("guides/", "Buying guides"), ("comparisons/", "Comparisons"), ("picks/", "Qarin picks"),
                ("deals/", "Deals"), ("categories/", "Categories"), ("blog/", "Blog"), ("search/", "Search")],
        "empty": "Guides for this section are being prepared and will be published soon.",
        "updated": "Last updated",
        "disc": "ⓘ Contains affiliate links that don't change your price",
        "details": "Details",
        "search_ph": "Search for a product or guide…",
        "search": "Search",
        "switch": "العربية",
        "footer_links": [("about/", "About"), ("contact/", "Contact"), ("disclosure/", "Affiliate disclosure"),
                         ("privacy/", "Privacy"), ("terms/", "Terms")],
        "amazon_note": "As an Amazon Associate we earn from qualifying purchases.",
        "price_note": "Prices and availability change often; check the store page before you buy.",
        "font": "Inter",
    },
}

CONTENT_TYPES = ("guide", "comparison", "article")


def parse(path, lang):
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"<!--meta\s*(\{.*?\})\s*-->\s*", raw, re.S)
    if not m:
        raise SystemExit(f"Missing meta header in {path}")
    meta = json.loads(m.group(1))
    meta["body"] = raw[m.end():]
    meta["lang"] = lang
    meta["slug"] = meta["slug"].strip("/")
    meta["out"] = meta["slug"] if lang == "ar" else ("en/" + meta["slug"]).strip("/")
    return meta


def rel(depth, target):
    return "../" * depth + target


def url_path(out):
    return (out + "/") if out else ""


def amz_link(words, label):
    url = "https://www.amazon.sa/s?k=" + quote_plus(words)
    if SITE.get("amazon_sa_tag"):
        url += "&tag=" + quote_plus(SITE["amazon_sa_tag"])
    return (f'<a class="buy" href="{escape(url)}" target="_blank" '
            f'rel="sponsored nofollow noopener" data-goatcounter-click="amz:{escape(words)}" '
            f'data-goatcounter-title="Amazon: {escape(label)}">{escape(label)}</a>')


def amz_url(path_or_query, is_path=False):
    if is_path:
        url = "https://www.amazon.sa" + path_or_query
        sep = "&" if "?" in url else "?"
    else:
        url = "https://www.amazon.sa/s?k=" + quote_plus(path_or_query)
        sep = "&"
    if SITE.get("amazon_sa_tag"):
        url += sep + "tag=" + quote_plus(SITE["amazon_sa_tag"])
    return url


# Direct-to-Amazon shopping tiles for the home page: (icon, color, ar label, en label, ar query, en query, path)
SHOP_TILES = [
    ("🔥", "#e5383b", "عروض اليوم", "Today's deals", None, None, "/deals"),
    ("🏆", "#e8a400", "الأكثر مبيعاً", "Best sellers", None, None, "/gp/bestsellers"),
    ("📱", "#3b6cff", "جوالات", "Phones", "جوالات", "smartphones", None),
    ("💻", "#5b4dff", "لابتوبات", "Laptops", "لابتوب", "laptop", None),
    ("🖥️", "#0f7bd8", "شاشات", "Monitors", "شاشة كمبيوتر", "computer monitor", None),
    ("🎧", "#7c4dff", "سماعات", "Earbuds", "سماعات لاسلكية", "wireless earbuds", None),
    ("⌚", "#12a594", "ساعات ذكية", "Smartwatches", "ساعة ذكية", "smartwatch", None),
    ("🍳", "#ff7a1a", "قلايات هوائية", "Air fryers", "قلاية هوائية", "air fryer", None),
    ("🤖", "#18a058", "مكانس روبوت", "Robot vacuums", "مكنسة روبوت", "robot vacuum", None),
    ("✨", "#e2468f", "عطور", "Fragrances", "عطور", "perfume", None),
    ("🧸", "#f2994a", "ألعاب أطفال", "Kids' toys", "ألعاب أطفال", "kids toys", None),
    ("🏋️", "#c0392b", "أدوات رياضية", "Fitness gear", "أدوات رياضية منزلية", "home fitness equipment", None),
    ("🧳", "#0096c7", "شنط سفر", "Luggage", "شنطة سفر", "luggage suitcase", None),
    ("📚", "#b5651d", "كتب", "Books", "كتب", "books", None),
]


def shop_tiles(lang):
    out = []
    for icon, color, ar, en, q_ar, q_en, path in SHOP_TILES:
        label = ar if lang == "ar" else en
        url = amz_url(path, True) if path else amz_url(q_ar if lang == "ar" else q_en)
        out.append(
            f'<a class="shop-tile" style="--c:{color}" href="{escape(url)}" target="_blank" '
            f'rel="sponsored nofollow noopener" data-goatcounter-click="amz-tile:{escape(en)}" '
            f'data-goatcounter-title="Amazon tile: {escape(en)}"><span class="ic">{icon}</span><b>{escape(label)}</b></a>')
    return '<div class="shop-tiles">' + "".join(out) + "</div>"


FEATURED = json.loads((ROOT / "featured.json").read_text(encoding="utf-8")) if (ROOT / "featured.json").exists() else {"items": []}


def featured_cards(lang, lang_root):
    items = FEATURED.get("items", [])[:4]
    if not items:
        return ""
    btn = "شوف السعر في أمازون" if lang == "ar" else "See price on Amazon"
    more = "اقرأ الدليل" if lang == "ar" else "Read the guide"
    out = []
    for it in items:
        icon = it.get("icon") or CAT_STYLE.get(it.get("category"), ("⭐", ""))[0]
        color = CAT_STYLE.get(it.get("category"), ("", "#ff9900"))[1]
        url = amz_url(f"/dp/{it['asin']}", True)
        name = it["name_" + lang]
        guide = f'<a class="feat-more" href="{lang_root}{it["guide"]}/">{more}</a>' if it.get("guide") else ""
        out.append(
            f'<div class="feat-card" style="--c:{color}"><div class="feat-icon">{icon}</div>'
            f'<div class="feat-body"><h3>{escape(name)}</h3><p>{escape(it["why_" + lang])}</p>'
            f'<div class="feat-actions"><a class="buy" href="{escape(url)}" target="_blank" rel="sponsored nofollow noopener" '
            f'data-goatcounter-click="amz-featured:{it["asin"]}" data-goatcounter-title="Featured: {escape(it["name_en"])}">{btn}</a>{guide}</div></div></div>')
    return '<div class="feat-grid">' + "".join(out) + "</div>"


def guide_cards(pages, lang, category, depth, ctype=None):
    t = L[lang]
    items = [p for p in pages if p["lang"] == lang and p.get("type") in CONTENT_TYPES
             and (ctype is None or p.get("type") == ctype)
             and (category == "all" or p.get("category") == category)]
    items.sort(key=lambda p: (p.get("date", ""), p["slug"]), reverse=True)
    if not items:
        return f'<p class="muted">{escape(t["empty"])}</p>'
    cards = []
    for p in items:
        cat = t["categories"].get(p.get("category"), "")
        kind = t["types"].get(p.get("type"), "")
        icon, color = CAT_STYLE.get(p.get("category"), ("📘", "#3b6cff"))
        icon = p.get("icon", icon)
        cards.append(
            f'<a class="card" style="--c:{color}" href="{rel(depth, url_path(p["out"]))}" '
            f'data-search="{escape(p["title"] + " " + p["description"] + " " + cat)}">'
            f'<div class="card-media"><span class="card-icon">{icon}</span><span class="badge">{escape(kind)}</span></div>'
            f'<div class="card-body"><span class="card-cat">{escape(cat)}</span>'
            f'<h3>{escape(p["title"])}</h3>'
            f'<p>{escape(p["description"])}</p>'
            f'<span class="card-cta">{escape(t["cta"][p["type"]])} {t["arrow"]}</span></div></a>')
    return '<div class="cards">' + "".join(cards) + "</div>"


def render(page, pages, index):
    lang = page["lang"]
    t = L[lang]
    out = page["out"]
    depth = 0 if out == "" else out.count("/") + 1
    lang_root = rel(depth, "" if lang == "ar" else "en/")

    body = page["body"]
    body = re.sub(r"\[\[amz:([^|\]]+)\|([^\]]+)\]\]", lambda m: amz_link(m.group(1).strip(), m.group(2).strip()), body)
    body = body.replace("[[shop]]", shop_tiles(lang))
    body = body.replace("[[featured]]", featured_cards(lang, lang_root))
    body = re.sub(r"\[\[guides:(\w+)\]\]", lambda m: guide_cards(pages, lang, m.group(1), depth), body)
    body = re.sub(r"\[\[list:(\w+):(\w+)\]\]", lambda m: guide_cards(pages, lang, m.group(2), depth, m.group(1)), body)
    body = body.replace("{{root}}", lang_root)

    nav = "".join(f'<a href="{lang_root}{href}">{escape(label)}</a>' for href, label in t["nav"])

    # language switcher: counterpart page if it exists, otherwise the other language's home
    other = "en" if lang == "ar" else "ar"
    counterpart = index.get((other, page["slug"]))
    other_out = counterpart["out"] if counterpart else ("" if other == "ar" else "en")
    switch_href = rel(depth, url_path(other_out))

    if page.get("type") in CONTENT_TYPES:
        updated = (f'<p class="meta">{t["updated"]}: {escape(page.get("date", ""))}</p>'
                   f'<p class="disc-line">{t["disc"]} · <a href="{lang_root}disclosure/">{t["details"]}</a></p>')
    else:
        updated = ""

    title = page["title"] if page["slug"] == "" else f'{page["title"]} | {t["site_name"]}'
    head_links = ""
    if SITE.get("base_url"):
        base = SITE["base_url"].rstrip("/") + "/"
        head_links += f'<link rel="canonical" href="{escape(base + url_path(out))}">\n'
        for lg in ("ar", "en"):
            p2 = index.get((lg, page["slug"]))
            if p2:
                head_links += f'<link rel="alternate" hreflang="{lg}" href="{escape(base + url_path(p2["out"]))}">\n'
        ar_page = index.get(("ar", page["slug"]))
        if ar_page:
            head_links += f'<link rel="alternate" hreflang="x-default" href="{escape(base + url_path(ar_page["out"]))}">\n'

    # Open Graph / social cards
    if SITE.get("base_url"):
        page_url = SITE["base_url"].rstrip("/") + "/" + url_path(out)
        head_links += (f'<meta property="og:type" content="{"article" if page.get("type") in CONTENT_TYPES else "website"}">\n'
                       f'<meta property="og:site_name" content="{escape(t["site_name"])}">\n'
                       f'<meta property="og:title" content="{escape(page["title"])}">\n'
                       f'<meta property="og:description" content="{escape(page["description"])}">\n'
                       f'<meta property="og:url" content="{escape(page_url)}">\n'
                       f'<meta property="og:locale" content="{"ar_SA" if lang == "ar" else "en_US"}">\n'
                       f'<meta name="twitter:card" content="summary">\n')
        # JSON-LD structured data
        base = SITE["base_url"].rstrip("/") + "/"
        home_url = base + ("" if lang == "ar" else "en/")
        graph = [{"@type": "Organization", "@id": base + "#org", "name": "Qarin / قارن", "url": base,
                  "logo": base + "assets/favicon.svg"}]
        if page["slug"] == "":
            graph.append({"@type": "WebSite", "name": t["site_name"], "url": home_url, "inLanguage": lang,
                          "publisher": {"@id": base + "#org"},
                          "potentialAction": {"@type": "SearchAction",
                                              "target": home_url + "search/?q={search_term_string}",
                                              "query-input": "required name=search_term_string"}})
        if page.get("type") in CONTENT_TYPES:
            graph.append({"@type": "Article", "headline": page["title"], "description": page["description"],
                          "inLanguage": lang, "datePublished": page.get("date"), "dateModified": page.get("date"),
                          "mainEntityOfPage": page_url, "author": {"@id": base + "#org"},
                          "publisher": {"@id": base + "#org"}})
            crumbs = [(t["nav"][0][1], home_url)]
            if page.get("category"):
                crumbs.append((t["categories"].get(page["category"], ""), home_url + "category/" + page["category"] + "/"))
            crumbs.append((page["title"], page_url))
            graph.append({"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]})
        head_links += ('<script type="application/ld+json">' +
                       json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False) +
                       "</script>\n")
    head_links += f'<link rel="icon" href="{rel(depth, "assets/favicon.svg")}" type="image/svg+xml">\n'

    font_css = ("Tajawal:wght@400;500;700;800" if lang == "ar" else "Inter:wght@400;500;700;800")
    footer_links = " · ".join(f'<a href="{lang_root}{h}">{escape(lbl)}</a>' for h, lbl in t["footer_links"])

    return f"""<!doctype html>
<html lang="{lang}" dir="{t['dir']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(page['description'])}">
{head_links}<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family={font_css}&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel(depth, 'assets/style.css')}">
<script data-goatcounter="https://qarinsa.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
</head>
<body class="lang-{lang}">
<header class="site-header">
  <div class="wrap topbar">
    <a class="brand" href="{lang_root}"><span class="logo">{t['logo']}</span>{escape(t['site_name'])}</a>
    <form class="top-search" action="{lang_root}search/" role="search">
      <input name="q" type="search" placeholder="{escape(t['search_ph'])}" aria-label="{escape(t['search'])}">
      <button type="submit" aria-label="{escape(t['search'])}">🔍</button>
    </form>
    <a class="lang-switch" href="{switch_href}" hreflang="{other}" lang="{other}">🌐 {t['switch']}</a>
  </div>
  <nav class="navbar"><div class="wrap">{nav}</div></nav>
</header>
<main class="wrap">
<article class="{'doc' if page.get('type') in CONTENT_TYPES else ''}">
{updated}
{body}
</article>
</main>
<footer class="site-footer">
  <div class="wrap">
    <p class="foot-brand"><span class="logo">{t['logo']}</span>{escape(t['site_name'])} — {escape(t['tagline'])}</p>
    <p>{footer_links} · <a href="{switch_href}" lang="{other}">{t['switch']}</a></p>
    <p class="muted">{escape(t['amazon_note'])}</p>
    <p class="muted">© {SITE['year']} {escape(t['site_name'])}. {escape(t['price_note'])}</p>
  </div>
</footer>
</body>
</html>
"""


def main():
    pages = []
    for lang, src in SOURCES.items():
        if src.exists():
            pages += [parse(p, lang) for p in sorted(src.rglob("*.html"))]
    index = {(p["lang"], p["slug"]): p for p in pages}

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    if (ROOT / "static").exists():
        for f in (ROOT / "static").iterdir():
            shutil.copy(f, OUT / f.name)
    for page in pages:
        target = OUT / page["out"] / "index.html" if page["out"] else OUT / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(page, pages, index), encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    if SITE.get("base_url"):
        base = SITE["base_url"].rstrip("/") + "/"
        def entry(p):
            alts = "".join(
                f'<xhtml:link rel="alternate" hreflang="{lg}" href="{base}{url_path(index[(lg, p["slug"])]["out"])}"/>'
                for lg in ("ar", "en") if (lg, p["slug"]) in index)
            lastmod = f"<lastmod>{p['date']}</lastmod>" if p.get("date") else ""
            return f"<url><loc>{base}{url_path(p['out'])}</loc>{lastmod}{alts}</url>"
        urls = "".join(entry(p) for p in pages)
        (OUT / "sitemap.xml").write_text(
            f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">{urls}</urlset>',
            encoding="utf-8")
        (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base}sitemap.xml\n", encoding="utf-8")

    counts = {lg: sum(1 for p in pages if p["lang"] == lg) for lg in SOURCES}
    missing = [p["slug"] or "(home)" for p in pages if p["lang"] == "ar" and ("en", p["slug"]) not in index]
    print(f"Built {len(pages)} pages into {OUT} — {counts}")
    if missing:
        print("No English version yet:", ", ".join(missing))


if __name__ == "__main__":
    main()
