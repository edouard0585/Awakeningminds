#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Articles du blog écrits en français seulement (file `_queue/articles_fr.json`).

Chaque entrée : num, slug, title (h1), seo_title, desc, kw, group, publish_at (heure de Paris),
published (date ou null), photo, schemas [{src, alt}], insert {src, alt} | null, faq, sources.
Le corps est dans `_queue/sections/fr-blog/<num>.html` (titres h2.sec numérotés).
Pages produites : fr/blog/<slug>.html — pas de version anglaise ni espagnole, donc hreflang fr seul.
Appelé par blog_build.build() ; stdlib uniquement (GitHub Actions).
"""
import json, os, re, html
from datetime import datetime, timedelta, timezone

E = html.escape
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE = f'{ROOT}/_queue/articles_fr.json'

GROUP_LABEL_EN = {
    'bases': 'Meditation practice', 'energie': 'Energy and chakras', 'transe': 'Trance and consciousness',
    'psy': 'Emotions and inner life', 'sommeil': 'Sleep and dreams', 'lieux': 'Places, myths and wisdom',
    'chamanisme': 'Shamanism', 'vie': 'Meditation in daily life', 'astral': 'Astral travel and signs',
}
LBL = {'fr': dict(toc='Dans cet article', src='Sources'), 'en': dict(toc='In this article', src='Sources')}
GROUP_LABEL = {
    'bases': 'Pratique de la méditation', 'energie': 'Énergie et chakras', 'transe': 'Transe et conscience',
    'psy': 'Émotions et vie intérieure', 'sommeil': 'Sommeil et rêves', 'lieux': 'Lieux, mythes et sagesse',
    'chamanisme': 'Chamanisme', 'vie': 'Méditation au quotidien', 'astral': 'Voyage astral et signes',
}

CSS_FR = """
article .hero-photo{margin:4px 0 24px}
article .hero-photo img{width:100%;aspect-ratio:1376/768;object-fit:cover;margin:0;border-radius:18px}
article h2.sec{display:flex;align-items:baseline;gap:12px;border-bottom:1px solid rgba(212,175,106,.28);padding-bottom:10px;margin:42px 0 16px}
article h2.sec .num{font-family:'Avenir Next','Segoe UI',sans-serif;font-size:14px;color:var(--gold);border:1.5px solid var(--gold);border-radius:50%;min-width:32px;height:32px;display:inline-flex;align-items:center;justify-content:center;flex-shrink:0;transform:translateY(-3px)}
article h3{font-size:21px;margin:22px 0 8px}
article p.key{color:var(--ink);background:linear-gradient(90deg,rgba(212,175,106,.10),rgba(212,175,106,0));border-left:3px solid var(--gold);border-radius:0 12px 12px 0;padding:10px 16px;margin:16px 0}
article figure.schema img{background:#fff;border-color:rgba(212,175,106,.3)}
article figure.illus{max-width:440px;margin:26px auto}
article figure.illus img{width:100%}
article figure.illus figcaption,article figure.schema figcaption{text-align:center}
article figure.video video{width:100%;border-radius:14px;border:1px solid var(--line);background:#000;display:block}
article figure.photo img{width:100%}
article .tbl{overflow-x:auto;margin:14px 0 20px;border:1px solid var(--line);border-radius:14px}
article table{border-collapse:collapse;width:100%;font-family:'Avenir Next','Segoe UI',sans-serif;font-size:14.5px}
article th{background:rgba(212,175,106,.12);color:var(--gold);text-align:left;padding:10px 12px;font-weight:600}
article td{color:var(--muted);padding:9px 12px;border-top:1px solid var(--line);vertical-align:top}
.sources{margin:30px 0 0;padding:16px 20px;border:1px solid var(--line);border-radius:14px;background:rgba(255,255,255,.02)}
.sources b{display:block;color:var(--gold);font-size:13px;letter-spacing:.08em;text-transform:uppercase;margin-bottom:8px;font-family:'Avenir Next',sans-serif}
.sources ul{margin:0;padding-left:18px}
.sources li{font-size:13.5px;color:var(--dim);margin:5px 0;line-height:1.55}
.cat{display:inline-block;font-family:'Avenir Next',sans-serif;font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--gold);border:1px solid rgba(212,175,106,.4);border-radius:99px;padding:3px 11px;margin-bottom:12px}
"""



def paris_now():
    """Heure de Paris, sans tzdata : UTC+2 du dernier dimanche de mars au dernier dimanche d'octobre (1 h UTC)."""
    u = datetime.now(timezone.utc)
    def last_sunday(y, m):
        d = datetime(y, m + 1, 1, tzinfo=timezone.utc) - timedelta(days=1)
        return d - timedelta(days=(d.weekday() + 1) % 7)
    start = last_sunday(u.year, 3).replace(hour=1); end = last_sunday(u.year, 10).replace(hour=1)
    return (u + timedelta(hours=2 if start <= u < end else 1)).replace(tzinfo=None)


def load():
    if not os.path.exists(QUEUE): return []
    return json.load(open(QUEUE, encoding='utf-8'))


def published(arts, lang='fr'):
    return [a for a in arts if a.get('published') and (lang == 'fr' or a.get(lang))]


def V(a, lang):
    """Champs de l'article dans la langue demandée (la version anglaise vit dans a['en'])."""
    if lang == 'fr': return a
    v = dict(a[lang]); v['num'] = a['num']; v['group'] = a['group']; v['published'] = a['published']
    v.setdefault('photo', a['photo']); v.setdefault('insert', None)
    return v


def body_html(a, lang='fr'):
    return open(f'{ROOT}/_queue/sections/{lang}-blog/{a["num"]}.html', encoding='utf-8').read()


def _fig(m, cls, lazy=True):
    dim = m.get('w') and f' width="{m["w"]}" height="{m["h"]}"' or ''
    lz = ' loading="lazy"' if lazy else ''
    return (f'<figure class="{cls}"><img src="../../assets/blog/{m["src"]}" alt="{E(m["alt"])}"{dim}'
            f'{lz} decoding="async">'
            + (f'<figcaption>{E(m["cap"])}</figcaption>' if m.get('cap') else '') + '</figure>')


def place_media(body, a):
    """Répartit schémas et illustration dans le texte : fin de la section ~30 %, ~55 %, ~80 %.
    Si l'article a été mis en page dans l'éditeur de l'espace privé (media_inline), le corps contient
    déjà ses images à leur place : on n'ajoute rien."""
    if a.get('media_inline'):
        return body
    parts = re.split(r'(?=<h2 class="sec")', body)
    head, secs = parts[0], parts[1:]
    n = len(secs)
    slots = []
    sch = a.get('schemas') or []
    if sch: slots.append(('schema', sch[0]))
    if a.get('insert'): slots.append(('illus', a['insert']))
    if len(sch) > 1: slots.append(('schema', sch[1]))
    if not slots or n == 0: return body
    fr = {1: [0.5], 2: [0.34, 0.75], 3: [0.3, 0.55, 0.8]}[len(slots)]
    used = set()
    for (cls, m), f in zip(slots, fr):
        k = min(n - 1, max(0, round(n * f) - 1))
        while k in used and k < n - 1: k += 1
        used.add(k)
        secs[k] = secs[k] + _fig(m, cls)
    return head + ''.join(secs)


def toc_and_ids(body, lang='fr'):
    heads = []
    def anchor(m):
        n, txt = m.group(1), m.group(2)
        hid = f's{n}'
        heads.append((hid, re.sub('<[^>]+>', '', txt)))
        return f'<h2 class="sec" id="{hid}" data-n="{n}"><span class="num">{n}</span>{txt}</h2>'
    body = re.sub(r'<h2 class="sec" data-n="(\d+)"><span class="num">\d+</span>(.*?)</h2>', anchor, body)
    toc = ''
    if len(heads) >= 3:
        items = ''.join(f'<li><a href="#{h}">{t}</a></li>' for h, t in heads)
        toc = f'<nav class="toc"><b>{LBL[lang]["toc"]}</b><ul>{items}</ul></nav>'
    return toc, body


def related(a, arts, lang='fr'):
    pub = [o for o in published(arts, lang) if o['num'] != a['num']]
    same = [o for o in pub if o['group'] == a['group']]
    same.sort(key=lambda o: abs(o['num'] - a['num']))
    out = same[:3]
    if len(out) < 3:
        rest = [o for o in reversed(pub) if o not in out]
        out += rest[:3 - len(out)]
    return [V(o, lang) for o in out]


def render_article(bb, a0, arts, lang='fr'):
    """bb = module blog_build (head, footer, CSS, T…). a0 = entrée de la file ; lang = 'fr' ou 'en'."""
    a = V(a0, lang); t = bb.T[lang]; BASE = bb.BASE
    langs = ['fr'] + (['en'] if a0.get('en') else [])
    paths = {'fr': f'/fr/blog/{a0["slug"]}.html'}
    if a0.get('en'): paths['en'] = f'/en/blog/{a0["en"]["slug"]}.html'
    url = paths[lang]
    GL = GROUP_LABEL if lang == 'fr' else GROUP_LABEL_EN
    body = place_media(body_html(a0, lang), a)
    toc, body = toc_and_ids(body, lang)
    mins = max(3, round(bb.words(body) / 220))
    img = f'/assets/blog/{a["photo"]["src"]}'
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'BlogPosting', 'headline': a['title'][:110], 'description': a['desc'], 'image': BASE + img,
         'datePublished': a['published'], 'dateModified': a.get('modified', a['published']), 'inLanguage': lang,
         'keywords': a.get('kw', ''), 'articleSection': GL.get(a['group'], 'Meditation'),
         'mainEntityOfPage': BASE + url, 'wordCount': bb.words(body),
         'author': {'@type': 'Organization', 'name': 'Awakening Minds', 'url': BASE + '/'},
         'publisher': {'@type': 'Organization', 'name': 'Awakening Minds',
                       'logo': {'@type': 'ImageObject', 'url': f'{BASE}/assets/brand/logo.png'}}},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Awakening Minds', 'item': f'{BASE}/{lang}/'},
            {'@type': 'ListItem', 'position': 2, 'name': t['blog'], 'item': f'{BASE}/{lang}/blog/'},
            {'@type': 'ListItem', 'position': 3, 'name': a['seo_title']}]},
    ] + ([{'@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': r}} for q, r in a['faq']]}]
         if a.get('faq') else [])}
    ld_tag = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace('<', '\\u003c') + '</script>'
    h = bb.head(lang, a['seo_title'], a['desc'], lambda x: paths[x], url, img, ld_tag,
                kw=a.get('kw', ''), img_alt=a['photo']['alt'], langs=langs)
    h = h.replace('</style>', CSS_FR + '</style>', 1)
    h += bb.header_html(lang, lambda x: f'../..{paths[x]}' if x in paths else f'../../{x}/blog/')
    import blog_hubs as hubs
    hl = hubs.group_link(lang, a['group'], getattr(bb, 'HUB_ACT', {}))
    h += (f'<main class="wrap"><article><nav class="crumbs"><a href="../">Awakening Minds</a>'
          f'<span>›</span><a href="./">{E(t["blog"])}</a>'
          + (f'<span>›</span><a href="{hl}">{E(hubs.HUBS[lang][a["group"]]["h1"])}</a>' if hl else '')
          + '</nav>'
          + (f'<a class="cat" href="{hl}">' if hl else '<span class="cat">') + E(GL.get(a["group"], "Meditation"))
          + ('</a>' if hl else '</span>') + f'<h1>{E(a["title"])}</h1>')
    h += f'<div class="meta">{E(t["published_on"])} {E(bb.fmt_date(a["published"], lang))} · {mins} {E(t["read"])}</div>'
    p = a['photo']
    h += (f'<figure class="hero-photo"><img src="../../assets/blog/{p["src"]}" '
          f'srcset="../../assets/blog/{p["src_s"]} 640w, ../../assets/blog/{p["src"]} 1200w" sizes="(max-width:800px) 100vw, 780px" '
          f'alt="{E(p["alt"])}" width="{p["w"]}" height="{p["h"]}" fetchpriority="high" decoding="async"></figure>')
    h += f'<p class="lead">{E(a["desc"])}</p>'
    h += toc + body
    if a.get('faq'):
        qa = ''.join(f'<details><summary>{E(q)}</summary><p>{E(r)}</p></details>' for q, r in a['faq'])
        h += f'<section class="afaq"><h2>{E(bb.FAQ_LABEL[lang])}</h2>{qa}</section>'
    if a.get('sources'):
        h += f'<aside class="sources"><b>{LBL[lang]["src"]}</b><ul>' + ''.join(f'<li>{s}</li>' for s in a['sources']) + '</ul></aside>'
    h += f'<div class="cta"><h2>{E(t["cta_t"])}</h2><p>{E(t["cta_p"])}</p><a href="../#download">✦ {E(t["cta_b"])}</a></div>'
    rel = related(a0, arts, lang)
    if rel:
        h += f'<h2>{E(t["other"])}</h2><ul class="alist">'
        for o in rel:
            h += (f'<li><a href="{o["slug"]}.html"><span class="th"><img src="../../assets/blog/{o["photo"]["src_s"]}" alt="" loading="lazy" width="88" height="88"></span>'
                  f'<span class="tw"><h3>{E(o["seo_title"])}</h3><p>{E(o["desc"])}</p></span></a></li>')
        h += '</ul>'
    h += '</article></main>' + bb.footer_html(lang) + '</body></html>'
    return h


def index_items(arts, lang='fr'):
    """Entrées pour l'index et le flux de la langue : (date, ordre, dict)."""
    out = []
    for a0 in published(arts, lang):
        a = V(a0, lang)
        out.append({'published': a['published'], 'order': a0.get('publish_at', ''), 'slug': a['slug'],
                    'title': a['seo_title'], 'desc': a['desc'], 'thumb': a['photo']['src_s'],
                    'alt': a['photo']['alt']})
    return out


def sitemap_urls(bb, arts):
    urls = []
    for a in published(arts):
        locs = {'fr': f'{bb.BASE}/fr/blog/{a["slug"]}.html'}
        if a.get('en'): locs['en'] = f'{bb.BASE}/en/blog/{a["en"]["slug"]}.html'
        alts = ''.join(f'<xhtml:link rel="alternate" hreflang="{x}" href="{u}"/>' for x, u in locs.items())
        if 'en' in locs: alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{locs["en"]}"/>'
        for lang, u in locs.items():
            v = V(a, lang)
            imgs = [v['photo']['src']] + [x['src'] for x in v.get('schemas', [])]
            im = ''.join(f'<image:image><image:loc>{bb.BASE}/assets/blog/{x}</image:loc></image:image>' for x in imgs if not x.startswith('http'))
            urls.append(f'<url><loc>{u}</loc><lastmod>{a.get("modified", a["published"])}</lastmod>{alts}{im}</url>')
    return urls


def build(bb):
    arts = load()
    # feuille de style du blog, lue par l'éditeur visuel de l'espace privé (aperçu identique au site)
    open(f'{ROOT}/_tools/blog_preview.css', 'w', encoding='utf-8').write(bb.CSS + CSS_FR)
    for a in published(arts):
        open(f'{ROOT}/fr/blog/{a["slug"]}.html', 'w', encoding='utf-8').write(render_article(bb, a, arts))
        if a.get('en'):
            open(f'{ROOT}/en/blog/{a["en"]["slug"]}.html', 'w', encoding='utf-8').write(render_article(bb, a, arts, 'en'))
    return arts
