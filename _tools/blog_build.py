#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Générateur du blog Awakening Minds — autonome (stdlib uniquement).

Lit `_queue/articles.json` + `_queue/sections/{lang}/*.html` et produit :
  {fr,en,es}/blog/<slug>.html   (articles publiés uniquement)
  {fr,en,es}/blog/index.html
  sitemap-blog.xml
Relancé à chaque publication : tout est régénéré, rien ne dérive.
"""
import json, os, re, html
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://awakeningminds.app'
LANGS = ['fr', 'en', 'es']
E = html.escape

T = {
 'fr': dict(blog='Le blog', back='← Awakening Minds', idx_title="Le blog — apprendre à méditer",
   idx_seo="Blog méditation : apprendre à méditer, guides et schémas — Awakening Minds",
   idx_desc="Guides gratuits pour apprendre à méditer : posture, respiration, gestion des pensées, techniques — avec schémas, par l'application 100 % gratuite Awakening Minds.",
   read='min de lecture', published_on='Publié le', soon="D'autres articles arrivent — un par semaine.",
   cta_t="Envie de pratiquer plutôt que de lire ?",
   cta_p="Tout ce que décrit cet article se pratique dans Awakening Minds, application de méditation gratuite : 195 méditations guidées en français — sommeil, respiration guidée, mondes immersifs — sans abonnement, sans publicité, sans compte, et tout fonctionne hors ligne.",
   cta_b="Découvrir l'application gratuite", other="À lire ensuite"),
 'en': dict(blog='The blog', back='← Awakening Minds', idx_title="The blog — learning to meditate",
   idx_seo="Meditation blog: how to meditate, free guides with diagrams — Awakening Minds",
   idx_desc="Free guides on how to meditate: posture, breathing, dealing with thoughts, techniques — with diagrams, from the completely free Awakening Minds app.",
   read='min read', published_on='Published', soon="More articles are coming — one every week.",
   cta_t="Rather practice than read?",
   cta_p="Everything in this article can be practiced in Awakening Minds, a free meditation app: 195 guided meditations — sleep, breathing, immersive worlds — no subscription, no ads, no account, and fully offline.",
   cta_b="Discover the free app", other="Read next"),
 'es': dict(blog='El blog', back='← Awakening Minds', idx_title="El blog — aprender a meditar",
   idx_seo="Blog de meditación: cómo meditar, guías gratis con esquemas — Awakening Minds",
   idx_desc="Guías gratis para aprender a meditar: postura, respiración, pensamientos, técnicas — con esquemas, de la app 100 % gratis Awakening Minds.",
   read='min de lectura', published_on='Publicado el', soon="Llegan más artículos — uno por semana.",
   cta_t="¿Prefieres practicar antes que leer?",
   cta_p="Todo lo que describe este artículo se practica en Awakening Minds, una app de meditación gratis: 195 meditaciones guiadas en español — dormir, respiración guiada, mundos inmersivos — sin suscripción, sin anuncios, sin cuenta y sin conexión.",
   cta_b="Descubre la app gratis", other="Sigue leyendo"),
}
FAQ_LABEL = {'fr': 'Questions fréquentes', 'en': 'Frequently asked questions', 'es': 'Preguntas frecuentes'}
TAKE_LABEL = {'fr': 'À retenir', 'en': 'Key takeaways', 'es': 'Para recordar'}
TOC_LABEL = {'fr': 'Dans cet article', 'en': 'In this article', 'es': 'En este artículo'}
# Maillage interne thématique : liens contextuels entre articles (ancres = titres).
RELATED = {
 'intro': ['posture', 'respiration', 'programme'], 'posture': ['respiration', 'intro', 'techniques'],
 'respiration': ['posture', 'pensees', 'techniques'], 'pensees': ['respiration', 'techniques', 'quotidien'],
 'programme': ['intro', 'posture', 'quotidien'], 'techniques': ['pensees', 'programme', 'science'],
 'quotidien': ['programme', 'pensees', 'interactives'], 'science': ['techniques', 'respiration', 'histoire'],
 'histoire': ['science', 'emc', 'symboles'], 'emc': ['histoire', 'astral', 'chakras'],
 'chakras': ['emc', 'techniques', 'symboles'], 'reve': ['emc', 'symboles', 'quotidien'],
 'ombre': ['pensees', 'techniques', 'symboles'], 'symboles': ['ombre', 'reve', 'histoire'],
 'astral': ['emc', 'reve', 'chakras'], 'interactives': ['intro', 'quotidien', 'techniques'],
}
MONTHS = {
 'fr': ['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'],
 'es': ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'],
 'en': ['January','February','March','April','May','June','July','August','September','October','November','December'],
}

def fmt_date(iso, lang):
    y, m, d = (int(x) for x in iso.split('-'))
    if lang == 'en':
        return f'{MONTHS["en"][m-1]} {d}, {y}'
    return f'{d} de {MONTHS["es"][m-1]} de {y}' if lang == 'es' else f'{d} {MONTHS["fr"][m-1]} {y}'

CSS = """
:root{--bg:#0A0A14;--ink:#F5E6C8;--muted:rgba(245,230,200,.72);--dim:rgba(245,230,200,.45);--gold:#D4AF6A;--line:rgba(255,255,255,.09);--surface:#151525;--radius:16px}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--ink);font-family:'Cormorant Garamond',Georgia,serif;line-height:1.7;font-size:19px;overflow-x:hidden}
.sans,p,li,td,figcaption,.badge,.meta,.card p,.card li{font-family:'Avenir Next','Segoe UI',system-ui,sans-serif}
.wrap{max-width:780px;margin:0 auto;padding:0 20px}
header{position:sticky;top:0;background:rgba(10,10,20,.92);backdrop-filter:blur(12px);border-bottom:1px solid var(--line);z-index:10}
header .wrap{display:flex;align-items:center;gap:14px;height:60px}
header a{color:var(--ink);text-decoration:none;font-size:17px}
header .b{color:var(--gold)}
header .lg{margin-left:auto;display:flex;gap:8px}
header .lg a{font-size:13px;border:1px solid var(--line);border-radius:99px;padding:4px 10px;color:var(--muted)}
header .lg a.on{color:var(--gold);border-color:var(--gold)}
main{padding:40px 0 20px}
h1{font-size:clamp(32px,5vw,46px);line-height:1.12;font-weight:500;color:#fff7e8;margin-bottom:14px}
.meta{color:var(--dim);font-size:14px;margin-bottom:30px}
.lead{font-size:20px;color:var(--muted);margin-bottom:26px}
article h2{font-size:29px;color:var(--gold);font-weight:500;margin:38px 0 14px;line-height:1.2}
article h3{font-size:23px;color:var(--gold);font-weight:500;margin:6px 0 10px}
article h4{font-size:16.5px;color:var(--ink);margin:16px 0 6px;font-family:'Avenir Next',sans-serif;font-weight:600}
article p{color:var(--muted);margin:0 0 12px;font-size:16.5px}
article ul,article ol{padding-left:22px;color:var(--muted);margin:8px 0 14px;font-size:16.5px}
article li{margin:6px 0}
article b,article strong{color:var(--ink)}
article a{color:var(--gold)}
article img{max-width:100%;height:auto;border-radius:14px;border:1px solid var(--line);background:#0e0c1c;margin:10px 0}
.section-head{border-bottom:2px solid rgba(212,175,106,.35);padding-bottom:10px;margin:34px 0 20px;display:flex;align-items:baseline;gap:12px}
.section-head .num{font-size:14px;color:var(--gold);border:1.5px solid var(--gold);border-radius:50%;min-width:32px;height:32px;display:inline-flex;align-items:center;justify-content:center;flex-shrink:0}
.section-head h2{margin:0}
.section-head .sub{font-size:14px;color:var(--muted);font-family:'Avenir Next',sans-serif}
.card{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:22px;margin-bottom:18px}
.grid2,.grid3{display:grid;grid-template-columns:1fr;gap:16px}
@media(min-width:640px){.grid2{grid-template-columns:1fr 1fr}.grid3{grid-template-columns:repeat(3,1fr)}}
.badges{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0 14px}
.badge{font-size:11px;font-weight:600;letter-spacing:.05em;padding:3px 10px;border-radius:20px}
.b-deb{background:rgba(157,196,140,.18);color:#a8d69a}.b-int{background:rgba(212,175,106,.15);color:var(--gold)}
.b-adv{background:rgba(192,122,107,.18);color:#e6a397}.b-time{background:rgba(157,138,201,.18);color:#c8b8e6}
.b-cat{background:rgba(255,255,255,.08);color:var(--muted)}
ol.steps{list-style:none;counter-reset:step;padding-left:0}
ol.steps li{counter-increment:step;position:relative;padding:0 0 14px 44px;border-left:2px solid rgba(212,175,106,.35);margin-left:16px}
ol.steps li:last-child{border-left-color:transparent}
ol.steps li::before{content:counter(step);position:absolute;left:-17px;top:-2px;width:32px;height:32px;border-radius:50%;background:var(--bg);border:1.5px solid var(--gold);color:var(--gold);display:flex;align-items:center;justify-content:center;font-size:14px;font-family:Georgia,serif}
.warn,.tip,.quote,.science{border-radius:14px;padding:14px 18px;margin:14px 0;font-size:15.5px;font-family:'Avenir Next',sans-serif;color:var(--muted)}
.warn{background:rgba(192,122,107,.12);border:1px solid rgba(192,122,107,.35)}
.tip{background:rgba(157,196,140,.10);border:1px solid rgba(157,196,140,.3)}
.quote{background:rgba(157,138,201,.10);border:1px solid rgba(157,138,201,.3);font-style:italic}
.science{background:rgba(255,255,255,.04);border:1px solid var(--line)}
.warn b,.tip b{display:block;margin-bottom:4px;color:var(--ink)}
details{border:1px solid var(--line);border-radius:12px;background:rgba(255,255,255,.02);margin:0 0 10px;padding:2px 16px}
summary{cursor:pointer;color:var(--ink);padding:11px 0;font-family:'Avenir Next',sans-serif;font-size:15.5px}
details p{padding-bottom:12px}
.pill-list{display:flex;flex-wrap:wrap;gap:8px;list-style:none;padding:0}
.pill-list li{border:1px solid var(--line);border-radius:99px;padding:5px 13px;font-size:13.5px;color:var(--muted)}
.media-slot{display:none}
.intro{color:var(--muted);font-size:16.5px;margin:0 0 22px;font-family:'Avenir Next','Segoe UI',system-ui,sans-serif}
article figure{margin:16px 0 20px}
article figure.hero{margin:4px 0 26px}
article figcaption{font-size:13.5px;color:var(--dim);margin-top:8px;line-height:1.5;font-family:'Avenir Next',sans-serif}
.toc{border:1px solid var(--line);border-radius:14px;background:rgba(255,255,255,.02);padding:16px 20px;margin:0 0 26px;font-family:'Avenir Next',sans-serif}
.toc b{display:block;color:var(--gold);font-size:13px;letter-spacing:.08em;text-transform:uppercase;margin-bottom:8px}
.toc ul{list-style:none;padding:0;margin:0;columns:2;column-gap:26px}
.toc li{margin:4px 0;break-inside:avoid}
.toc a{color:var(--muted);text-decoration:none;font-size:14px}
.toc a:hover{color:var(--gold)}
@media(max-width:600px){.toc ul{columns:1}}
article :target{scroll-margin-top:80px}
.take{border:1px solid rgba(212,175,106,.35);border-radius:14px;background:rgba(212,175,106,.06);padding:18px 22px;margin:30px 0}
.take b{display:block;color:var(--gold);font-size:13px;letter-spacing:.08em;text-transform:uppercase;margin-bottom:8px;font-family:'Avenir Next',sans-serif}
.take ul{margin:0;padding-left:20px;color:var(--muted);font-size:15.5px}
.take li{margin:5px 0}
.afaq{margin:34px 0 0}
.cta{background:linear-gradient(135deg,#1c1830,#241d3f);border:1px solid rgba(212,175,106,.35);border-radius:var(--radius);padding:26px;margin:44px 0 20px;text-align:center}
.cta h2{margin:0 0 8px;font-size:26px;color:#fff7e8}
.cta p{color:var(--muted);font-size:15.5px;max-width:560px;margin:0 auto 16px}
.cta a{display:inline-block;background:linear-gradient(135deg,#D4AF6A,#b8934f);color:#161122;text-decoration:none;font-weight:600;font-family:'Avenir Next',sans-serif;font-size:15px;padding:12px 26px;border-radius:99px}
.alist{list-style:none;padding:0}
.alist li{margin:0 0 16px}
.alist a{display:block;border:1px solid var(--line);border-radius:var(--radius);padding:20px 22px;text-decoration:none;background:rgba(255,255,255,.02)}
.alist a:hover{border-color:rgba(212,175,106,.45)}
.alist h2{font-size:24px;color:#fff7e8;margin:0 0 6px;font-weight:500}
.alist p{color:var(--muted);font-size:15px;margin:0 0 6px}
.alist .d{color:var(--dim);font-size:13px;font-family:'Avenir Next',sans-serif}
footer{border-top:1px solid var(--line);margin-top:40px}
footer .wrap{padding:22px 20px;color:var(--dim);font-size:14px;font-family:'Avenir Next',sans-serif;display:flex;gap:10px;flex-wrap:wrap}
footer a{color:var(--muted)}
"""

def load():
    arts = json.load(open(f'{ROOT}/_queue/articles.json', encoding='utf-8'))
    return arts

def section_html(lang, sid):
    return open(f'{ROOT}/_queue/sections/{lang}/{sid}.html', encoding='utf-8').read()

SCHEMA_PREFIX = re.compile(r'^(Schéma|Diagram|Esquema|Sch&#x27;ema)\s*[—-]\s*', re.I)

def _slugify(txt):
    import unicodedata
    t = unicodedata.normalize('NFKD', re.sub('<[^>]+>', '', txt)).encode('ascii', 'ignore').decode()
    t = re.sub(r'[^a-zA-Z0-9]+', '-', t).strip('-').lower()
    return t[:60] or 'section'

def enrich_body(body, lang):
    """Corps prêt pour le web : chaque schéma devient une figure légendée,
    chaque h3 reçoit une ancre, et un sommaire s'ajoute si l'article est long."""
    def fig(m):
        tag, alt = m.group(0), m.group(1)
        cap = SCHEMA_PREFIX.sub('', alt)
        return f'<figure>{tag}<figcaption>{cap}</figcaption></figure>'
    body = re.sub(r'<img [^>]*alt="([^"]+)"[^>]*/?>(?!\s*<figcaption)', fig, body)
    heads, seen = [], set()
    def anchor(m):
        txt = m.group(1)
        base = _slugify(txt); hid = base; k = 2
        while hid in seen: hid = f'{base}-{k}'; k += 1
        seen.add(hid)
        heads.append((hid, re.sub('<[^>]+>', '', txt)))
        return f'<h3 id="{hid}">{txt}</h3>'
    body = re.sub(r'<h3>(.*?)</h3>', anchor, body)
    toc = ''
    if len(heads) >= 4:
        items = ''.join(f'<li><a href="#{h}">{E(t)}</a></li>' for h, t in heads)
        toc = f'<nav class="toc"><b>{E(TOC_LABEL[lang])}</b><ul>{items}</ul></nav>'
    return toc, body

def words(txt):
    return len(re.sub('<[^>]+>', ' ', txt).split())

def head(lang, title, desc, path_of, canonical, image, extra_ld=''):
    """path_of(x) → chemin de la version dans la langue x (pour hreflang)."""
    alts = ''.join(f'<link rel="alternate" hreflang="{x}" href="{BASE}{path_of(x)}">' for x in LANGS)
    alts += f'<link rel="alternate" hreflang="x-default" href="{BASE}{path_of("en")}">'
    return f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}">
<link rel="canonical" href="{BASE}{canonical}">{alts}
<meta name="robots" content="index,follow,max-image-preview:large"><meta name="theme-color" content="#0A0A14">
<meta property="og:type" content="article"><meta property="og:site_name" content="Awakening Minds">
<meta property="og:url" content="{BASE}{canonical}"><meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}"><meta property="og:image" content="{BASE}{image}">
<meta name="twitter:card" content="summary_large_image">
{extra_ld}
<link rel="icon" href="{BASE}/assets/brand/app-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>"""

def header_html(lang, blog_path_of):
    t = T[lang]
    lg = ''.join(f'<a href="{blog_path_of(x)}" class="{"on" if x == lang else ""}">{x.upper()}</a>' for x in LANGS)
    return f'<header><div class="wrap"><a href="../" class="b">{E(t["back"])}</a><a href="./">{E(t["blog"])}</a><div class="lg">{lg}</div></div></header>'

def footer_html(lang):
    return f'<footer><div class="wrap"><span>Awakening Minds</span><a href="../">awakeningminds.app/{lang}</a><a href="./">{E(T[lang]["blog"])}</a></div></footer>'

def render_article(a, lang, arts):
    t = T[lang]
    body = ''.join(section_html(lang, sid) for sid in a['sections'])
    mins = max(2, round(words(body) / 200))
    img = f'/assets/blog/{_img_slug(a, lang)}' if a.get('image') is not None else '/assets/brand/og-image.jpg'
    ld = {
        '@context': 'https://schema.org',
        '@graph': [
            {'@type': 'Article', 'headline': a['title'][lang], 'description': a['desc'][lang],
             'image': BASE + img, 'datePublished': a['published'], 'dateModified': a['published'], 'inLanguage': lang,
             'mainEntityOfPage': f'{BASE}/{lang}/blog/{a["slug"][lang]}.html',
             'author': {'@type': 'Organization', 'name': 'Awakening Minds', 'url': BASE + '/'},
             'publisher': {'@type': 'Organization', 'name': 'Awakening Minds',
                           'logo': {'@type': 'ImageObject', 'url': f'{BASE}/assets/brand/logo.png'}}},
            {'@type': 'WebSite', 'name': 'Awakening Minds', 'url': BASE + '/', 'inLanguage': lang},
            {'@type': 'BreadcrumbList', 'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': 'Awakening Minds', 'item': f'{BASE}/{lang}/'},
                {'@type': 'ListItem', 'position': 2, 'name': T[lang]['blog'], 'item': f'{BASE}/{lang}/blog/'},
                {'@type': 'ListItem', 'position': 3, 'name': a['title'][lang]}]},
        ] + ([{'@type': 'FAQPage', 'mainEntity': [
                {'@type': 'Question', 'name': q,
                 'acceptedAnswer': {'@type': 'Answer', 'text': r}}
                for q, r in a['faq'][lang]]}] if a.get('faq') else []),
    }
    ld_tag = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace('<', '\\u003c') + '</script>'
    path_of = lambda x: f'/{x}/blog/{a["slug"][x]}.html'
    h = head(lang, a['title'][lang], a['desc'][lang], path_of, path_of(lang), img, ld_tag)
    h += header_html(lang, lambda x: f'../../{x}/blog/{a["slug"][x]}.html')
    h += f'<main class="wrap"><article><h1>{E(a["title"][lang])}</h1>'
    h += f'<div class="meta">{E(t["published_on"])} {E(fmt_date(a["published"], lang))} · {mins} {E(t["read"])}</div>'
    h += f'<p class="lead">{E(a["desc"][lang])}</p>'
    if a.get('intro'):
        h += f'<p class="intro">{E(a["intro"][lang])}</p>'
    if a.get('hero') is not None:
        sl = SCHEMA_FILES[a['hero']][lang]
        alt = HERO_ALTS.get((a['hero'], lang), a['title'][lang])
        cap = SCHEMA_PREFIX.sub('', alt)
        h += (f'<figure class="hero"><img src="../../assets/blog/{sl}-{lang}.webp" alt="{E(alt)}" '
              f'width="960" loading="eager"><figcaption>{E(cap)}</figcaption></figure>')
    toc, body = enrich_body(body, lang)
    h += toc + body
    if a.get('takeaways'):
        pts = ''.join(f'<li>{E(x)}</li>' for x in a['takeaways'][lang])
        h += f'<aside class="take"><b>{E(TAKE_LABEL[lang])}</b><ul>{pts}</ul></aside>'
    if a.get('faq'):
        qa = ''.join(f'<details><summary>{E(q)}</summary><p>{E(r)}</p></details>' for q, r in a['faq'][lang])
        h += f'<section class="afaq"><h2>{E(FAQ_LABEL[lang])}</h2>{qa}</section>'
    h += f'<div class="cta"><h2>{E(t["cta_t"])}</h2><p>{E(t["cta_p"])}</p><a href="../#download">✦ {E(t["cta_b"])}</a></div>'
    by_id = {o['id']: o for o in arts}
    others = [by_id[r] for r in RELATED.get(a['id'], []) if by_id.get(r, {}).get('published')]
    if not others:
        others = [o for o in arts if o.get('published') and o['id'] != a['id']][-3:]
    if others:
        h += f'<h2>{E(t["other"])}</h2><ul class="alist">'
        for o in others:
            h += f'<li><a href="{o["slug"][lang]}.html"><h2>{E(o["title"][lang])}</h2><p>{E(o["desc"][lang])}</p></a></li>'
        h += '</ul>'
    h += '</article></main>' + footer_html(lang) + '</body></html>'
    return h

def _img_slug(a, lang):
    # le nom du fichier image du schéma d'ouverture, dans la langue de la page
    from_slug = SCHEMA_FILES[a['image']][lang]
    return f'{from_slug}-{lang}.webp'

def render_index(lang, arts):
    t = T[lang]
    pub = [a for a in arts if a.get('published')]
    path_of = lambda x: f'/{x}/blog/'
    h = head(lang, t['idx_seo'], t['idx_desc'], path_of, path_of(lang), '/assets/brand/og-image.jpg')
    h += header_html(lang, lambda x: f'../../{x}/blog/')
    h += f'<main class="wrap"><h1>{E(t["idx_title"])}</h1><p class="lead">{E(t["idx_desc"])}</p><ul class="alist">'
    for a in reversed(pub):
        h += (f'<li><a href="{a["slug"][lang]}.html"><h2>{E(a["title"][lang])}</h2>'
              f'<p>{E(a["desc"][lang])}</p><span class="d">{E(fmt_date(a["published"], lang))}</span></a></li>')
    h += f'</ul><p class="lead" style="font-size:16px">{E(t["soon"])}</p></main>'
    h += footer_html(lang) + '</body></html>'
    return h

def render_sitemap(arts):
    urls = []
    def block(path_of):
        alts = ''.join(f'<xhtml:link rel="alternate" hreflang="{x}" href="{BASE}{path_of(x)}"/>' for x in LANGS)
        alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{BASE}{path_of("en")}"/>'
        return alts
    for x in LANGS:
        urls.append(f'<url><loc>{BASE}/{x}/blog/</loc>{block(lambda y: f"/{y}/blog/")}</url>')
    for a in arts:
        if not a.get('published'):
            continue
        pa = lambda y, a=a: f'/{y}/blog/{a["slug"][y]}.html'
        for x in LANGS:
            urls.append(f'<url><loc>{BASE}{pa(x)}</loc><lastmod>{a["published"]}</lastmod>{block(pa)}</url>')
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:xhtml="http://www.w3.org/1999/xhtml">' + ''.join(urls) + '</urlset>')

SCHEMA_FILES = {}  # rempli au chargement depuis assets/blog (slug sans -lang)
def _load_schema_files():
    import collections
    files = os.listdir(f'{ROOT}/assets/blog')
    # reconstruit {n: {lang: slug}} n'est pas nécessaire : articles.json référence
    # l'index du schéma ; la table est fournie ici, figée à la génération.
    return json.load(open(f'{ROOT}/_queue/schema_files.json', encoding='utf-8'))

HERO_ALTS = {}
def _scan_hero_alts():
    """Alt réel de chaque schéma, relevé dans la langue de la page."""
    inv = {v[lang]: (n, lang) for n, v in SCHEMA_FILES.items() for lang in LANGS}
    for lang in LANGS:
        d = f'{ROOT}/_queue/sections/{lang}'
        for fn in os.listdir(d):
            for m in re.finditer(r'src="\.\./\.\./assets/blog/([^"]+)-(?:fr|en|es)\.webp"[^>]*alt="([^"]+)"',
                                 open(f'{d}/{fn}', encoding='utf-8').read()):
                key = inv.get(m.group(1))
                if key and key not in HERO_ALTS:
                    HERO_ALTS[key] = m.group(2)

def build():
    global SCHEMA_FILES
    SCHEMA_FILES = {int(k): v for k, v in _load_schema_files().items()}
    _scan_hero_alts()
    arts = load()
    for lang in LANGS:
        os.makedirs(f'{ROOT}/{lang}/blog', exist_ok=True)
        open(f'{ROOT}/{lang}/blog/index.html', 'w', encoding='utf-8').write(render_index(lang, arts))
        for a in arts:
            if a.get('published'):
                open(f'{ROOT}/{lang}/blog/{a["slug"][lang]}.html', 'w', encoding='utf-8').write(render_article(a, lang, arts))
    open(f'{ROOT}/sitemap-blog.xml', 'w', encoding='utf-8').write(render_sitemap(arts))
    pub = sum(1 for a in arts if a.get('published'))
    print(f'✓ blog reconstruit : {pub} article(s) publié(s) × 3 langues + index + sitemap-blog.xml')

if __name__ == '__main__':
    build()
