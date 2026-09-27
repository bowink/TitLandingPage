#!/usr/bin/env python3
"""Generate static collection and product pages from catalog/products.json.

Run from the repository root: python3 scripts/build_catalog.py
The already optimized photos live in assets/images/.
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://tangledintradition.com"
SHOP_BOOKS = "https://www.etsy.com/shop/favoritebookjournals"
SHOP_VINYL = "https://www.etsy.com/shop/vinylrecordnotebooks"

COLLECTIONS = {
    "vinyl": {
        "slug": "vinyl-record-journals",
        "title": "Upcycled Vinyl Record Journals",
        "eyebrow": "Real records · New stories",
        "intro": "Handmade journals made with actual upcycled vinyl records and album artwork. Explore photographed examples for music fans, record collectors, and concertgoers.",
        "shop": SHOP_VINYL,
        "shop_label": "Shop current vinyl journals on Etsy",
        "cards_title": "Explore vinyl journal examples",
    },
    "books": {
        "slug": "book-journals",
        "title": "Upcycled Book Journals",
        "eyebrow": "Favorite stories · New chapters",
        "intro": "Familiar book covers become handmade notebooks, journals, and keepsakes. Explore photographed examples from childhood favorites and memorable characters.",
        "shop": SHOP_BOOKS,
        "shop_label": "Shop current book journals on Etsy",
        "cards_title": "Explore book journal examples",
    },
    "playbills": {
        "slug": "playbill-journals",
        "title": "Upcycled Playbill Journals",
        "eyebrow": "A show worth remembering",
        "intro": "A playbill can hold more than a theater memory. See how real programs become handmade journals for notes and favorite moments.",
        "shop": SHOP_BOOKS,
        "shop_label": "Shop current playbill journals on Etsy",
        "cards_title": "Explore playbill journal examples",
    },
    "comics": {
        "slug": "comic-book-journals",
        "title": "Upcycled Comic Book Journals",
        "eyebrow": "Comic pages · Fresh ideas",
        "intro": "Our comic book journals give existing comics a new use as notebooks and keepsakes. Photographs of this collection are coming soon.",
        "shop": SHOP_BOOKS,
        "shop_label": "Browse comic journals in our Etsy shop",
        "cards_title": "Comic journal photographs coming soon",
    },
}


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def image(product: dict, number: int) -> str:
    return f"/assets/images/{product['slug']}-{number}.jpg"


def collection_url(key: str) -> str:
    return f"/collections/{COLLECTIONS[key]['slug']}.html"


def product_url(product: dict) -> str:
    return f"/products/{product['slug']}.html"


def breadcrumbs(items: list[tuple[str, str | None]]) -> str:
    bits = []
    for label, url in items:
        bits.append(
            f'<li><a href="{esc(url)}">{esc(label)}</a></li>'
            if url else f'<li aria-current="page">{esc(label)}</li>'
        )
    return '<ol class="crumbs" aria-label="Breadcrumb">' + "".join(bits) + "</ol>"


def page(title: str, description: str, path: str, body: str, graph: list[dict], image_url: str | None = None) -> str:
    canonical = SITE + path
    og_image = f'<meta property="og:image" content="{esc(SITE + image_url)}">\n' if image_url else ""
    schema = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False).replace("<", "\\u003c")
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} | Tangled in Tradition</title>
  <meta name="description" content="{esc(description)}">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <link rel="canonical" href="{esc(canonical)}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{esc(title)} | Tangled in Tradition">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(canonical)}">
{og_image}  <meta name="twitter:card" content="summary_large_image">
  <meta name="theme-color" content="#221b26">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600;700&amp;family=Instrument+Serif:ital@0;1&amp;family=Space+Mono&amp;display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/catalog.css?v=2">
  <script type="application/ld+json">{schema}</script>
</head>
<body>
  <header class="site-header">
    <div class="wrap header-row">
      <a class="brand" href="/">Tangled <em>in</em> Tradition</a>
      <nav class="nav" aria-label="Main navigation">
        <a href="/collections/vinyl-record-journals.html">Vinyl journals</a>
        <a href="/collections/book-journals.html">Book journals</a>
        <a href="/collections/playbill-journals.html">Playbills</a>
        <a href="/collections/comic-book-journals.html">Comics</a>
      </nav>
    </div>
  </header>
  <main class="wrap">
    {body}
  </main>
  <footer class="site-footer">
    <div class="wrap footer-row">
      <span>© Tangled in Tradition · Handmade with care</span>
      <nav class="footer-links" aria-label="Footer navigation">
        <a href="/">Home</a>
        <a href="/collections/vinyl-record-journals.html">Vinyl</a>
        <a href="/collections/book-journals.html">Books</a>
        <a href="/returns.html">Returns &amp; exchanges</a>
      </nav>
    </div>
  </footer>
</body>
</html>
'''


def card(product: dict) -> str:
    category = COLLECTIONS[product["collection"]]["title"]
    alt = f"{product['name']} photographed by Tangled in Tradition"
    return f'''<a class="product-card" href="{esc(product_url(product))}">
      <img src="{esc(image(product, 1))}" alt="{esc(alt)}" width="1448" height="1086" loading="lazy" decoding="async">
      <span class="card-copy"><span class="eyebrow">{esc(category)}</span>
        <h3>{esc(product["name"])}</h3>
        <p>{esc(product["intro"])}</p>
        <span class="card-more">View this journal →</span>
      </span>
    </a>'''


def build_collection(key: str, products: list[dict]) -> str:
    info = COLLECTIONS[key]
    path = collection_url(key)
    members = [p for p in products if p["collection"] == key]
    hero = f'<img class="hero-photo" src="{esc(image(members[0], 1))}" alt="{esc(members[0]["name"])}" width="1448" height="1086">' if members else (
        '<div class="placeholder" role="img" aria-label="Comic journal photos coming soon">'
        '<span class="placeholder-icon">✦</span><strong>More stories soon</strong><span>Comic journal photos are on their way.</span></div>'
    )
    listing = (
        '<div class="grid">' + "".join(card(p) for p in members) + "</div>"
        if members else
        '<p class="section-note">We have reserved this space for our comic book journal photos. '
        'You can browse the current selection in our Etsy shop in the meantime.</p>'
    )
    body = f'''{breadcrumbs([("Home", "/"), (info["title"], None)])}
    <section class="collection-hero collection-hero--split">
      <div>
        <p class="eyebrow">{esc(info["eyebrow"])}</p>
        <h1>{esc(info["title"])}</h1>
        <p class="lead">{esc(info["intro"])}</p>
        <a class="button" href="{esc(info["shop"])}" target="_blank" rel="noopener noreferrer">{esc(info["shop_label"])} ↗</a>
        <p class="buy-note">Prices, availability and ordering details are shown in our Etsy shop.</p>
      </div>
      {hero}
    </section>
    <section aria-labelledby="collection-list">
      <div class="section-header">
        <h2 id="collection-list">{esc(info["cards_title"])}</h2>
        <p class="section-note">Each photographed piece shows an example of our handmade work. Source materials and current stock can vary.</p>
      </div>
      {listing}
    </section>'''
    graph = [
        {"@type": "CollectionPage", "@id": SITE + path, "name": info["title"],
         "url": SITE + path, "description": info["intro"],
         "isPartOf": {"@id": SITE + "/#website"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": info["title"], "item": SITE + path},
        ]},
    ]
    if members:
        graph.append({"@type": "ItemList", "name": info["cards_title"], "itemListElement": [
            {"@type": "ListItem", "position": n, "name": p["name"], "url": SITE + product_url(p)}
            for n, p in enumerate(members, start=1)
        ]})
    return page(info["title"], info["intro"], path, body, graph, image(members[0], 1) if members else None)


def build_product(product: dict, products: list[dict]) -> str:
    key = product["collection"]
    info = COLLECTIONS[key]
    path = product_url(product)
    image_count = sum(f"image{n}" in product for n in (1, 2, 3))
    figures = []
    for n in range(1, image_count + 1):
        caption = "Photographed example" if n == 1 else "Another view of this journal"
        alt = f"{product['name']} — {'first view' if n == 1 else 'open or alternate view'}"
        figures.append(
            f'<figure><img src="{esc(image(product,n))}" alt="{esc(alt)}" width="1448" height="1086" '
            f'loading="{"eager" if n == 1 else "lazy"}" decoding="async"><figcaption>{caption}</figcaption></figure>'
        )
    gallery = figures[0] + (f'<div class="gallery-pair">{"".join(figures[1:])}</div>' if image_count > 1 else "")
    related = [p for p in products if p["collection"] == key and p["slug"] != product["slug"]][:3]
    material = "a real upcycled vinyl record and album artwork" if key == "vinyl" else (
        "an upcycled playbill" if key == "playbills" else "an upcycled book"
    )
    body = f'''{breadcrumbs([("Home", "/"), (info["title"], collection_url(key)), (product["name"], None)])}
    <article class="product-layout">
      <div class="gallery">{gallery}</div>
      <div class="product-info">
        <p class="eyebrow">{esc(product["eyebrow"])}</p>
        <h1>{esc(product["name"])}</h1>
        <p class="lead">{esc(product["intro"])}</p>
        <div class="detail-panel">
          <h2>Made from a favorite original</h2>
          <p>{esc(product["detail"])}</p>
          <p>Made by Tangled in Tradition using {esc(material)}.</p>
        </div>
        <a class="button" href="{esc(info["shop"])}" target="_blank" rel="noopener noreferrer">{esc(info["shop_label"])} ↗</a>
        <p class="buy-note">This is a photographed example of our work. Visit the shop for current availability, prices and product specifics.</p>
        <p class="disclaimer">Independently handmade from upcycled source material. Tangled in Tradition is not affiliated with the artist, publisher or rights holder represented by the source material.</p>
      </div>
    </article>
    <section class="related" aria-labelledby="related-title">
      <h2 id="related-title">More from this collection</h2>
      <div class="grid">{"".join(card(p) for p in related)}</div>
    </section>'''
    graph = [
        {"@type": "Product", "@id": SITE + path + "#product", "name": product["name"],
         "description": product["intro"], "image": [SITE + image(product, n) for n in range(1, image_count + 1)],
         "brand": {"@type": "Brand", "name": "Tangled in Tradition"},
         "category": info["title"], "url": SITE + path},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": info["title"], "item": SITE + collection_url(key)},
            {"@type": "ListItem", "position": 3, "name": product["name"], "item": SITE + path},
        ]},
    ]
    return page(product["name"], product["intro"], path, body, graph, image(product, 1))


def build_sitemap(products: list[dict]) -> str:
    ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    root = ET.Element(ns + "urlset")
    paths = ["/", "/returns.html"] + [collection_url(k) for k in COLLECTIONS] + [product_url(p) for p in products]
    for path in paths:
        entry = ET.SubElement(root, ns + "url")
        ET.SubElement(entry, ns + "loc").text = SITE + path
        ET.SubElement(entry, ns + "lastmod").text = "2026-09-22" if path == "/returns.html" else "2026-09-27"
    ET.indent(root, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode") + "\n"


def main() -> None:
    products = json.loads((ROOT / "catalog/products.json").read_text(encoding="utf-8"))
    slugs = [p["slug"] for p in products]
    if len(set(slugs)) != len(slugs):
        raise ValueError("Product slugs must be unique")
    for p in products:
        for n in (1, 2, 3):
            if f"image{n}" in p and not (ROOT / "assets/images" / f"{p['slug']}-{n}.jpg").exists():
                raise FileNotFoundError(f"Missing optimized photo: {p['slug']}-{n}.jpg")
    (ROOT / "collections").mkdir(exist_ok=True)
    (ROOT / "products").mkdir(exist_ok=True)
    for key, info in COLLECTIONS.items():
        (ROOT / "collections" / f"{info['slug']}.html").write_text(build_collection(key, products), encoding="utf-8")
    for p in products:
        (ROOT / "products" / f"{p['slug']}.html").write_text(build_product(p, products), encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(build_sitemap(products), encoding="utf-8")
    print(f"Generated {len(products)} product pages, {len(COLLECTIONS)} collections and a sitemap.")


if __name__ == "__main__":
    main()
