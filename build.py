#!/usr/bin/env python3
"""Build the static site from content/*.html into docs/ (served by GitHub Pages).

Each content file starts with a JSON header between <!--meta and -->:
<!--meta
{"slug": "guides/air-fryer", "title": "...", "description": "...", "category": "kitchen", "type": "guide", "date": "2026-10-31"}
-->

Shortcodes inside content:
  [[amz:search words|label]]  -> Amazon.sa search link (adds tracking tag when site.json has one)
  [[guides:category]]          -> list of guides in that category ("all" for every guide)
"""
import json
import re
import shutil
from html import escape
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
OUT = ROOT / "docs"
SITE = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))

CATEGORIES = {
    "kitchen": "المطبخ والمنزل",
    "tech": "جوالات ولابتوبات",
    "beauty": "الجمال والعطور",
    "kids": "الأطفال والأم",
    "health": "الصحة وكبار السن",
    "digital": "اشتراكات ومنتجات رقمية",
    "books": "الكتب والقراءة",
    "sports": "الرياضة واللياقة",
    "travel": "السفر",
    "deals": "العروض والمواسم",
}

NAV = [
    ("", "الرئيسية"),
    ("guides/", "أدلة الشراء"),
    ("comparisons/", "مقارنات"),
    ("picks/", "اختيارات قارن"),
    ("deals/", "العروض"),
    ("categories/", "الأقسام"),
    ("blog/", "المدونة"),
    ("search/", "بحث"),
]


def parse(path):
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"<!--meta\s*(\{.*?\})\s*-->\s*", raw, re.S)
    if not m:
        raise SystemExit(f"Missing meta header in {path}")
    meta = json.loads(m.group(1))
    meta["body"] = raw[m.end():]
    return meta


def rel(depth, target):
    return "../" * depth + target


def amz_link(words, label):
    url = "https://www.amazon.sa/s?k=" + quote_plus(words)
    if SITE.get("amazon_sa_tag"):
        url += "&tag=" + quote_plus(SITE["amazon_sa_tag"])
    return (f'<a class="buy" href="{escape(url)}" target="_blank" '
            f'rel="sponsored nofollow noopener">{escape(label)}</a>')


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

CONTENT_TYPES = {"guide": "دليل شراء", "comparison": "مقارنة", "article": "مقال", "picks": "اختيارات"}


def guide_cards(pages, category, depth, ctype=None):
    items = [p for p in pages if p.get("type") in CONTENT_TYPES
             and (ctype is None or p.get("type") == ctype)
             and (category == "all" or p.get("category") == category)]
    items.sort(key=lambda p: p.get("date", ""), reverse=True)
    if not items:
        return '<p class="muted">أدلة هذا القسم قيد الإعداد وتُنشر قريباً.</p>'
    cards = []
    for p in items:
        cat = CATEGORIES.get(p.get("category"), "")
        kind = CONTENT_TYPES.get(p.get("type"), "")
        icon, color = CAT_STYLE.get(p.get("category"), ("📘", "#3b6cff"))
        icon = p.get("icon", icon)
        cta = "قارن الآن" if p.get("type") == "comparison" else ("اقرأ المقال" if p.get("type") == "article" else "اعرض الدليل")
        cards.append(
            f'<a class="card" style="--c:{color}" href="{rel(depth, p["slug"] + "/")}" data-search="{escape(p["title"] + " " + p["description"] + " " + cat)}">'
            f'<div class="card-media"><span class="card-icon">{icon}</span><span class="badge">{escape(kind)}</span></div>'
            f'<div class="card-body"><span class="card-cat">{escape(cat)}</span>'
            f'<h3>{escape(p["title"])}</h3>'
            f'<p>{escape(p["description"])}</p>'
            f'<span class="card-cta">{cta} ←</span></div></a>')
    return '<div class="cards">' + "".join(cards) + "</div>"


def render(page, pages):
    slug = page["slug"].strip("/")
    depth = 0 if slug == "" else slug.count("/") + 1
    body = page["body"]
    body = re.sub(r"\[\[amz:([^|\]]+)\|([^\]]+)\]\]", lambda m: amz_link(m.group(1).strip(), m.group(2).strip()), body)
    body = re.sub(r"\[\[guides:(\w+)\]\]", lambda m: guide_cards(pages, m.group(1), depth), body)
    body = re.sub(r"\[\[list:(\w+):(\w+)\]\]", lambda m: guide_cards(pages, m.group(2), depth, m.group(1)), body)
    body = body.replace("{{root}}", rel(depth, ""))

    nav = "".join(f'<a href="{rel(depth, href)}">{escape(label)}</a>' for href, label in NAV)
    disclosure_note = ""
    if page.get("type") in CONTENT_TYPES:
        disclosure_note = ""
        small_disclosure = (
            f'<p class="disc-line">ⓘ يحتوي على روابط عمولة لا تغيّر السعر عليك · '
            f'<a href="{rel(depth, "disclosure/")}">التفاصيل</a></p>')
        updated = f'<p class="meta">آخر تحديث: {escape(page.get("date", ""))}</p>' + small_disclosure
    else:
        updated = ""

    title = page["title"] if slug == "" else f'{page["title"]} | {SITE["site_name"]}'
    canonical = ""
    if SITE.get("base_url"):
        canonical = f'<link rel="canonical" href="{escape(SITE["base_url"].rstrip("/") + "/" + (slug + "/" if slug else ""))}">'

    return f"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(page['description'])}">
{canonical}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel(depth, 'assets/style.css')}">
</head>
<body>
<header class="site-header">
  <div class="wrap topbar">
    <a class="brand" href="{rel(depth, '')}"><span class="logo">ق</span>{escape(SITE['site_name'])}</a>
    <form class="top-search" action="{rel(depth, 'search/')}" role="search">
      <input name="q" type="search" placeholder="ابحث عن منتج أو دليل…" aria-label="ابحث">
      <button type="submit" aria-label="بحث">🔍</button>
    </form>
  </div>
  <nav class="navbar"><div class="wrap">{nav}</div></nav>
</header>
<main class="wrap">
{disclosure_note}
<article class="{'doc' if page.get('type') in CONTENT_TYPES else ''}">
{updated}
{body}
</article>
</main>
<footer class="site-footer">
  <div class="wrap">
    <p class="foot-brand"><span class="logo">ق</span>{escape(SITE['site_name'])} — {escape(SITE['tagline'])}</p>
    <p><a href="{rel(depth, 'about/')}">من نحن</a> · <a href="{rel(depth, 'contact/')}">تواصل معنا</a> · <a href="{rel(depth, 'disclosure/')}">الإفصاح عن العمولة</a> · <a href="{rel(depth, 'privacy/')}">الخصوصية</a> · <a href="{rel(depth, 'terms/')}">الشروط</a></p>
    <p class="muted">بصفتنا مشاركين في برنامج أمازون للمسوقين بالعمولة، قد نحصل على عمولة من عمليات الشراء المؤهلة.</p>
    <p class="muted">© {SITE['year']} {escape(SITE['site_name'])}. الأسعار والتوفر تتغير باستمرار؛ تحقق من صفحة المتجر قبل الشراء.</p>
  </div>
</footer>
</body>
</html>
"""


def main():
    pages = [parse(p) for p in sorted(CONTENT.rglob("*.html"))]
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    for page in pages:
        slug = page["slug"].strip("/")
        target = OUT / slug / "index.html" if slug else OUT / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(page, pages), encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    # sitemap (only when the domain is known)
    if SITE.get("base_url"):
        base = SITE["base_url"].rstrip("/")
        urls = "".join(
            f"<url><loc>{base}/{(p['slug'].strip('/') + '/') if p['slug'].strip('/') else ''}</loc></url>"
            for p in pages)
        (OUT / "sitemap.xml").write_text(
            f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>',
            encoding="utf-8")
        (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n", encoding="utf-8")
    print(f"Built {len(pages)} pages into {OUT}")


if __name__ == "__main__":
    main()
