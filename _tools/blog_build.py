#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Générateur du blog MeditaDream — autonome (stdlib uniquement).

Lit `_queue/articles.json` + `_queue/sections/{lang}/*.html` et produit :
  {fr,en,es}/blog/<slug>.html   (articles publiés uniquement)
  {fr,en,es}/blog/index.html
  sitemap-blog.xml
Relancé à chaque publication : tout est régénéré, rien ne dérive.
"""
import json, os, re, html, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blog_fr
import blog_hubs
import app_pages
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://meditadream.com'
LANGS = ['fr', 'en', 'es']
E = html.escape
# Réglages partagés avec le générateur de l'accueil (nombre de méditations, magasins).
try:
    SITE_CFG = json.load(open(os.path.join(ROOT, '_tools', 'site.json'), encoding='utf-8'))
except Exception:
    SITE_CFG = {'total': 149, 'stores_live': False, 'app_store_id': '6808918209'}
TOTAL = SITE_CFG.get('total', 149)
HEAD_ICONES = ('<link rel="icon" href="/assets/brand/favicon-rond-48.png" type="image/png" sizes="48x48">'
               '<link rel="icon" href="/assets/brand/favicon-rond-96.png" type="image/png" sizes="96x96">'
               '<link rel="icon" href="/assets/brand/icon-192.png" type="image/png" sizes="192x192">'
               '<link rel="icon" href="/favicon.ico" sizes="16x16 32x32 48x48">'
               '<link rel="apple-touch-icon" href="/apple-touch-icon.png">'
               '<link rel="manifest" href="/site.webmanifest">')
BANNIERE = (f'<meta name="apple-itunes-app" content="app-id={SITE_CFG["app_store_id"]}">'
            if SITE_CFG.get('stores_live') else '')
OG_LOCALE = {'fr': 'fr_FR', 'en': 'en_US', 'es': 'es_ES'}


def webp_size(path):
    """Largeur et hauteur d'un WebP lues dans son en-tête (stdlib seulement, pour GitHub Actions)."""
    try:
        b = open(path, 'rb').read(30)
        if b[:4] != b'RIFF' or b[8:12] != b'WEBP': return None
        c = b[12:16]
        if c == b'VP8X': return 1 + int.from_bytes(b[24:27], 'little'), 1 + int.from_bytes(b[27:30], 'little')
        if c == b'VP8L':
            v = int.from_bytes(b[21:25], 'little'); return (v & 0x3FFF) + 1, ((v >> 14) & 0x3FFF) + 1
        if c == b'VP8 ': return int.from_bytes(b[26:28], 'little') & 0x3FFF, int.from_bytes(b[28:30], 'little') & 0x3FFF
    except Exception: pass
    return None

T = {
 'fr': dict(blog='Le blog', back='← MeditaDream', idx_title="Le blog — apprendre à méditer",
   idx_seo="Apprendre à méditer : guides gratuits · MeditaDream",
   idx_desc="Guides gratuits pour apprendre à méditer : posture, respiration, pensées, techniques, avec schémas. Par MeditaDream, l'app 100 % gratuite en français.",
   read='min de lecture', published_on='Publié le', soon="De nouveaux articles arrivent chaque semaine.",
   cta_t="Envie de pratiquer plutôt que de lire ?",
   cta_p="Tout ce que décrit cet article se pratique dans MeditaDream, application de méditation gratuite : {meds} méditations guidées et {worlds} mondes immersifs en français, sans abonnement, sans publicité, sans compte, et tout fonctionne hors ligne.",
   cta_b="Découvrir l'application gratuite", other="À lire ensuite"),
 'en': dict(blog='The blog', back='← MeditaDream', idx_title="The blog — learning to meditate",
   idx_seo="How to Meditate: Free Guides & Diagrams · MeditaDream",
   idx_desc="Free guides on how to meditate: posture, breathing, dealing with thoughts, techniques — with diagrams, from the completely free MeditaDream app.",
   read='min read', published_on='Published', soon="More articles are coming — one every week.",
   cta_t="Rather practice than read?",
   cta_p="Everything in this article can be practiced in MeditaDream, a free meditation app: {meds} guided meditations and {worlds} immersive worlds, with no subscription, no ads, no account, and fully offline.",
   cta_b="Discover the free app", other="Read next"),
 'es': dict(blog='El blog', back='← MeditaDream', idx_title="El blog — aprender a meditar",
   idx_seo="Cómo meditar: guías gratis en español · MeditaDream",
   idx_desc="Guías gratis para aprender a meditar: postura, respiración, pensamientos, técnicas — con esquemas, de la app 100 % gratis MeditaDream.",
   read='min de lectura', published_on='Publicado el', soon="Llegan más artículos — uno por semana.",
   cta_t="¿Prefieres practicar antes que leer?",
   cta_p="Todo lo que describe este artículo se practica en MeditaDream, una app de meditación gratis: {meds} meditaciones guiadas y {worlds} mundos inmersivos en español, sin suscripción, sin anuncios, sin cuenta y sin conexión.",
   cta_b="Descubre la app gratis", other="Sigue leyendo"),
}
WORLDS = SITE_CFG.get('worlds', 17)
MEDS = SITE_CFG.get('meds', TOTAL - WORLDS)   # comme dans l'app : « 129 méditations guidées et 17 mondes »
for _l in T: T[_l]['cta_p'] = T[_l]['cta_p'].replace('{total}', str(TOTAL)).replace('{meds}', str(MEDS)).replace('{worlds}', str(WORLDS))
SITE_KW = {
 'fr': "méditation gratuite, application méditation gratuite, méditation guidée, méditation sans abonnement, méditation hors ligne, méditation pour dormir, respiration guidée, méditation débutant, pleine conscience, relaxation profonde",
 'en': "free meditation app, guided meditation, meditation app no subscription, offline meditation app, meditation without ads, guided sleep meditation, breathing exercises, meditation for beginners, mindfulness, deep relaxation",
 'es': "meditación guiada gratis, app de meditación gratis, meditación sin suscripción, meditación sin conexión, meditación sin anuncios, meditación para dormir, respiración guiada, meditación para principiantes, atención plena, relajación profunda",
}
SECTION_LABEL = {'fr': 'Apprendre à méditer', 'en': 'Learning to meditate', 'es': 'Aprender a meditar'}
FAQ_LABEL = {'fr': 'Questions fréquentes', 'en': 'Frequently asked questions', 'es': 'Preguntas frecuentes'}
TAKE_LABEL = {'fr': 'À retenir', 'en': 'Key takeaways', 'es': 'Para recordar'}
TOC_LABEL = {'fr': 'Dans cet article', 'en': 'In this article', 'es': 'En este artículo'}
# Maillage interne thématique : liens contextuels entre articles (ancres = titres).
RELATED = {
 'intro': ['posture', 'respiration', 'programme'], 'posture': ['respiration', 'scan', 'intro'],
 'respiration': ['dormir', 'posture', 'pensees'], 'pensees': ['pleineconscience', 'respiration', 'techniques'],
 'programme': ['intro', 'cinqminutes', 'quotidien'], 'techniques': ['scan', 'marche', 'bienveillance'],
 'quotidien': ['cinqminutes', 'programme', 'dormir'], 'science': ['techniques', 'respiration', 'histoire'],
 'histoire': ['science', 'emc', 'symboles'], 'emc': ['histoire', 'astral', 'chakras'],
 'chakras': ['emc', 'techniques', 'symboles'], 'reve': ['dormir', 'emc', 'symboles'],
 'ombre': ['pensees', 'techniques', 'symboles'], 'symboles': ['ombre', 'reve', 'histoire'],
 'astral': ['emc', 'reve', 'chakras'], 'interactives': ['intro', 'quotidien', 'techniques'],
 'dormir': ['scan', 'respiration', 'reve'], 'cinqminutes': ['matin', 'quotidien', 'respiration'],
 'scan': ['dormir', 'techniques', 'posture'], 'matin': ['cinqminutes', 'quotidien', 'respiration'],
 'pleineconscience': ['pensees', 'intro', 'quotidien'],
 'marche': ['techniques', 'scan', 'cinqminutes'],
 'bienveillance': ['techniques', 'ombre', 'pleineconscience'],
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
:root{--bg:#0A0A14;--ink:#F5E6C8;--muted:rgba(245,230,200,.72);--dim:rgba(245,230,200,.58);--gold:#D4AF6A;--line:rgba(255,255,255,.09);--surface:#151525;--radius:16px}
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
.crumbs{font-family:'Avenir Next',sans-serif;font-size:13px;color:var(--dim);display:flex;gap:8px;margin-bottom:14px}
.crumbs a{color:var(--dim);text-decoration:none}
.crumbs a:hover{color:var(--gold)}
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
.themes{margin:34px 0 10px}.themes h2{font-size:22px;color:var(--gold);margin:0 0 12px;font-weight:500}
.themes .pill-list a{color:var(--muted);text-decoration:none}.themes .pill-list li:hover{border-color:var(--gold)}
.themes .pill-list a[aria-current]{color:var(--gold)}
.topnav{margin:0 0 26px}.topnav .pill-list li{font-size:13px}.topnav a{color:var(--muted);text-decoration:none}
a.cat{text-decoration:none}a.cat:hover{border-color:var(--gold)}
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
.alist a{display:flex;gap:18px;align-items:flex-start;border:1px solid var(--line);border-radius:var(--radius);padding:18px 20px;text-decoration:none;background:rgba(255,255,255,.02)}
.alist .th{flex:0 0 88px;width:88px;height:88px;border-radius:14px;overflow:hidden;border:1px solid var(--line);background:#0e0c1c;display:flex;align-items:center;justify-content:center}
.alist .th img{width:100%;height:100%;object-fit:cover;object-position:top}
.alist .th.n{color:var(--gold);font-family:'Cormorant Garamond',Georgia,serif;font-size:26px;border-color:rgba(212,175,106,.35)}
.alist .tw{flex:1;min-width:0}
@media(max-width:480px){.alist .th{flex-basis:64px;width:64px;height:64px}}
.alist a:hover{border-color:rgba(212,175,106,.45)}
.alist h2,.alist h3{font-size:24px;color:#fff7e8;margin:0 0 6px;font-weight:500}
.alist p{color:var(--muted);font-size:15px;margin:0 0 6px}
.alist .d{color:var(--dim);font-size:13px;font-family:'Avenir Next',sans-serif}
footer{border-top:1px solid var(--line);margin-top:40px}
footer .wrap{padding:22px 20px;color:var(--dim);font-size:14px;font-family:'Avenir Next',sans-serif;display:flex;gap:10px;flex-wrap:wrap}
footer a{color:var(--muted)}
"""

# Mise en page éditoriale des articles (classe .post sur <article>) et de l'index (.bidx).
# Portée limitée à ces classes : les pages de l'application et des formations ne changent pas.
POST_CSS = """
@media(max-width:600px){header a{font-size:15px;white-space:nowrap}header .wrap{gap:10px}header .lg{gap:5px}header .lg a{padding:3px 8px}}
.progress{position:fixed;top:0;left:0;right:0;height:3px;z-index:20;pointer-events:none}
.progress span{display:block;height:100%;width:0;background:linear-gradient(90deg,#b8934f,#F3D9A4);box-shadow:0 0 12px rgba(212,175,106,.6)}
main.post-main{padding-top:28px;position:relative}
main.post-main::before{content:"";position:absolute;inset:0 0 auto 0;height:520px;z-index:-1;pointer-events:none;
 background:radial-gradient(60% 70% at 50% 0%,rgba(122,96,180,.20),rgba(10,10,20,0) 70%),radial-gradient(40% 50% at 85% 10%,rgba(212,175,106,.10),rgba(10,10,20,0) 70%)}
article.post{max-width:740px;margin:0 auto}
article.post .post-head{text-align:center;margin:6px auto 26px;max-width:700px}
article.post .crumbs{justify-content:center;flex-wrap:wrap}
article.post .cat{margin:4px 0 16px}
article.post h1{font-size:clamp(34px,5.6vw,52px);line-height:1.08;letter-spacing:-.005em;margin:0 0 16px;
 background:linear-gradient(180deg,#fff9ec 30%,#E9CF98);-webkit-background-clip:text;background-clip:text;color:transparent}
article.post .meta{display:flex;justify-content:center;flex-wrap:wrap;gap:6px 16px;font-size:13.5px;letter-spacing:.02em;margin:0}
article.post .meta span{display:inline-flex;align-items:center;gap:6px}
article.post .meta span+span::before{content:"✦";color:var(--gold);font-size:10px;margin-right:10px}
article.post .hero-photo,article.post figure.hero{margin:0 -40px 30px;position:relative}
article.post .hero-photo img,article.post figure.hero img{width:100%;border-radius:22px;border:1px solid rgba(212,175,106,.22);
 box-shadow:0 30px 80px -30px rgba(0,0,0,.8),0 0 0 6px rgba(255,255,255,.015);margin:0}
article.post .lead{font-family:'Cormorant Garamond',Georgia,serif;font-size:clamp(21px,2.6vw,25px);line-height:1.5;font-style:italic;
 color:#f1e3c4;text-align:center;max-width:640px;margin:0 auto 30px;padding:0 0 26px;position:relative}
article.post .lead::after{content:"";position:absolute;left:50%;bottom:0;width:64px;height:1px;transform:translateX(-50%);
 background:linear-gradient(90deg,transparent,var(--gold),transparent)}
article.post .intro{font-size:17.5px;line-height:1.8;color:rgba(245,230,200,.86)}
article.post p,article.post ul,article.post ol{font-size:17.5px;line-height:1.82;color:rgba(245,230,200,.86)}
article.post p{margin:0 0 16px}
article.post li{margin:8px 0}
article.post b,article.post strong{color:#fff4dc;font-weight:600}
article.post a{color:#E9CF98;text-decoration:underline;text-decoration-color:rgba(212,175,106,.45);text-underline-offset:3px}
article.post a:hover{text-decoration-color:var(--gold)}
article.post .crumbs a,article.post a.cat,article.post .toc a,.rel-grid a,article.post .cta a{text-decoration:none}
article.post>ul:not(.alist),article.post .body ul{list-style:none;padding-left:4px}
article.post .body ul,article.post .body ol,article.post p.key{display:flow-root}
article.post .body ul>li{position:relative;padding-left:26px}
article.post .body ul>li::before{content:"";position:absolute;left:4px;top:.72em;width:8px;height:8px;border-radius:50%;
 background:radial-gradient(circle,#F3D9A4,#b8934f);box-shadow:0 0 8px rgba(212,175,106,.55)}
article.post .body ol{padding-left:26px}
article.post .body ol>li::marker{color:var(--gold);font-weight:600}
article.post .body>p:first-of-type::first-letter,article.post .body>h2.sec:first-child+p::first-letter{
 font-family:'Cormorant Garamond',Georgia,serif;float:left;font-size:4.1em;line-height:.82;margin:.08em .1em 0 0;color:var(--gold)}
article.post h2.sec{display:block;text-align:left;border:0;padding:0;margin:64px 0 22px;font-size:clamp(27px,3.6vw,34px);line-height:1.18;color:#fff3da}
article.post h2.sec::before{content:"";display:block;height:1px;margin:0 0 40px;
 background:linear-gradient(90deg,transparent,rgba(212,175,106,.45) 20%,rgba(212,175,106,.45) 80%,transparent)}
article.post .body>h2.sec:first-child{margin-top:20px}
article.post .body>h2.sec:first-child::before{display:none}
article.post h2.sec .num{display:flex;width:auto;height:auto;min-width:0;border:0;border-radius:0;transform:none;margin:0 0 10px;
 font-family:'Avenir Next','Segoe UI',sans-serif;font-size:12px;font-weight:600;letter-spacing:.22em;text-transform:uppercase;color:var(--gold);align-items:center;gap:10px}
article.post h2.sec .num::before{content:attr(data-l)}
article.post h2.sec .num::after{content:"";width:34px;height:1px;background:var(--gold);opacity:.6}
article.post h3{font-size:24px;color:#F0D9A6;margin:30px 0 10px}
article.post p.key{position:relative;font-family:'Cormorant Garamond',Georgia,serif;font-size:clamp(21px,2.5vw,24px);line-height:1.45;color:#fff1d6;
 background:linear-gradient(135deg,rgba(212,175,106,.13),rgba(122,96,180,.10));border:1px solid rgba(212,175,106,.28);border-left:0;
 border-radius:18px;padding:26px 28px 24px 64px;margin:30px 0}
article.post p.key::before{content:"“";position:absolute;left:20px;top:8px;font-size:62px;line-height:1;color:var(--gold);font-family:Georgia,serif;opacity:.85}
article.post p.key strong,article.post p.key b{color:#fff7e4}
article.post figure{margin:34px 0}
article.post figure img{display:block;margin:0 auto}
article.post figure.schema,article.post figure.illus{background:linear-gradient(180deg,rgba(255,255,255,.035),rgba(255,255,255,.01));
 border:1px solid rgba(212,175,106,.2);border-radius:22px;padding:14px}
article.post figure.schema img{border-radius:14px;border:0;width:100%}
article.post figure.illus{max-width:460px;margin-left:auto;margin-right:auto}
article.post figure.illus img{border:0;border-radius:14px}
article.post figcaption{text-align:center;font-size:13.5px;color:var(--dim);margin-top:10px;font-style:italic}
article.post figure.ph{width:43%;margin:6px 0 18px;shape-outside:inset(0 round 20px)}
article.post figure.ph.r{float:right;margin-left:30px;margin-right:-34px}
article.post figure.ph.l{float:left;margin-right:30px;margin-left:-34px}
article.post figure.ph img{width:100%;border-radius:20px;border:1px solid rgba(212,175,106,.25);margin:0;
 box-shadow:0 24px 50px -24px rgba(0,0,0,.9)}
article.post figure.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:38px -34px;clear:both}
article.post figure.pair img{width:100%;border-radius:20px;border:1px solid rgba(212,175,106,.25);margin:0;box-shadow:0 24px 50px -24px rgba(0,0,0,.9)}
article.post figure.pair img:nth-child(2){transform:translateY(28px)}
article.post figure.pair{margin-bottom:62px}
article.post h2.sec,article.post .section-head,article.post .tbl,article.post figure.schema,article.post .afaq,article.post .cta,article.post .sources{clear:both}
@media(max-width:720px){
 article.post .hero-photo,article.post figure.hero{margin:0 -20px 26px}
 article.post .hero-photo img,article.post figure.hero img{border-radius:0;border-left:0;border-right:0}
 article.post figure.ph,article.post figure.ph.r,article.post figure.ph.l{float:none;width:78%;margin:26px auto}
 article.post figure.pair{margin:30px 0 50px;gap:10px}
 article.post p.key{padding:22px 20px 20px 52px}
 article.post p.key::before{left:14px;font-size:52px}
}
article.post .toc{background:linear-gradient(180deg,rgba(255,255,255,.04),rgba(255,255,255,.015));border:1px solid rgba(212,175,106,.22);border-radius:20px;padding:22px 26px;margin:0 0 34px}
article.post .toc ul{columns:1;counter-reset:toc}
article.post .toc li{counter-increment:toc;display:flex;gap:12px;align-items:baseline;margin:2px 0;padding:7px 0;border-bottom:1px dashed rgba(255,255,255,.07)}
article.post .toc li:last-child{border-bottom:0}
article.post .toc li::before{content:counter(toc,decimal-leading-zero);font-size:12px;color:var(--gold);font-weight:600;letter-spacing:.06em;min-width:22px}
article.post .toc a{font-size:15px;color:rgba(245,230,200,.82);text-decoration:none}
article.post .toc a:hover{color:#F3D9A4}
article.post .tbl{border-radius:16px;border-color:rgba(212,175,106,.22);margin:26px 0}
article.post table{font-size:15px}
article.post tr:nth-child(even) td{background:rgba(255,255,255,.025)}
article.post td{color:rgba(245,230,200,.84);padding:11px 14px}
article.post th{padding:12px 14px;letter-spacing:.02em}
article.post .card{background:linear-gradient(180deg,rgba(255,255,255,.04),rgba(255,255,255,.015));border-color:rgba(212,175,106,.16);border-radius:20px;padding:26px}
article.post .section-head{border-bottom:0;margin:60px 0 22px;flex-direction:column;align-items:flex-start;gap:8px}
article.post .section-head::before{content:"";display:block;width:100%;height:1px;margin-bottom:30px;
 background:linear-gradient(90deg,transparent,rgba(212,175,106,.45) 20%,rgba(212,175,106,.45) 80%,transparent)}
article.post .section-head h2{font-size:clamp(27px,3.6vw,34px);color:#fff3da}
article.post .take{border-radius:20px;padding:24px 28px;background:linear-gradient(135deg,rgba(212,175,106,.12),rgba(122,96,180,.08))}
article.post .afaq{margin-top:56px}
article.post .afaq>h2{font-size:30px;color:#fff3da;text-align:center;margin-bottom:20px}
article.post details{border:1px solid rgba(212,175,106,.18);border-radius:16px;padding:0 20px;margin:0 0 12px;background:rgba(255,255,255,.025);transition:background .2s}
article.post details[open]{background:rgba(212,175,106,.06)}
article.post summary{list-style:none;display:flex;justify-content:space-between;gap:16px;align-items:center;padding:16px 0;font-size:16px;color:#fff1d6}
article.post summary::-webkit-details-marker{display:none}
article.post summary::after{content:"+";color:var(--gold);font-size:22px;line-height:1;transition:transform .2s}
article.post details[open] summary::after{transform:rotate(45deg)}
article.post details p{font-size:16px;padding-bottom:16px;margin:0}
article.post .sources{background:transparent;border-color:rgba(255,255,255,.08);margin-top:36px}
article.post .sources li{font-size:13.5px}
article.post .cta{position:relative;overflow:hidden;border-radius:24px;padding:40px 30px;margin:60px 0 30px;
 background:radial-gradient(80% 120% at 50% 0%,rgba(212,175,106,.20),rgba(0,0,0,0) 60%),linear-gradient(135deg,#1b1631,#261d44);
 box-shadow:0 30px 80px -40px rgba(122,96,180,.7)}
article.post .cta::before{content:"✦";display:block;color:var(--gold);font-size:22px;margin-bottom:10px}
article.post .cta h2{font-size:clamp(26px,3.4vw,32px)}
article.post .cta p{font-size:16px;color:rgba(245,230,200,.8)}
article.post .cta a{text-decoration:none;box-shadow:0 10px 30px -8px rgba(212,175,106,.6);transition:transform .2s}
article.post .cta a:hover{transform:translateY(-2px)}
.rel{margin:50px 0 10px}
.rel>h2{font-size:28px;color:#fff3da;text-align:center;margin:0 0 22px;font-weight:500}
.rel-grid{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.rel-grid a{display:flex;flex-direction:column;height:100%;text-decoration:none;border:1px solid rgba(212,175,106,.18);border-radius:18px;overflow:hidden;
 background:rgba(255,255,255,.025);transition:transform .25s,border-color .25s}
.rel-grid a:hover{transform:translateY(-4px);border-color:rgba(212,175,106,.5)}
.rel-grid img{width:100%;aspect-ratio:16/10;object-fit:cover;display:block;border:0;border-radius:0;margin:0}
.rel-grid .n{aspect-ratio:16/10;display:flex;align-items:center;justify-content:center;font-size:40px;color:var(--gold);background:linear-gradient(135deg,#1b1631,#261d44)}
.rel-grid h3{font-size:19px!important;line-height:1.25;color:#fff3da!important;margin:14px 16px 16px!important;font-weight:500}
@media(max-width:720px){.rel-grid{grid-template-columns:1fr}.rel-grid a{flex-direction:row}.rel-grid img,.rel-grid .n{width:120px;aspect-ratio:1;flex:0 0 120px}.rel-grid h3{font-size:17px!important;margin:12px 14px!important}}
.bidx .alist{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.bidx .alist li{margin:0}
.bidx .alist a{flex-direction:column;gap:0;padding:0;overflow:hidden;height:100%;border-radius:20px;border-color:rgba(212,175,106,.16);transition:transform .25s,border-color .25s}
.bidx .alist a:hover{transform:translateY(-4px)}
.bidx .alist .th{width:100%;height:auto;flex:none;aspect-ratio:16/10;border:0;border-radius:0}
.bidx .alist .th img{object-position:center}
.bidx .alist .tw{padding:16px 20px 20px}
.bidx .alist h2{font-size:23px;line-height:1.2}
.bidx .alist li:first-child{grid-column:1/-1}
.bidx .alist li:first-child .th{aspect-ratio:21/9}
.bidx .alist li:first-child h2{font-size:30px}
@media(max-width:640px){.bidx .alist{grid-template-columns:1fr}.bidx .alist li:first-child .th{aspect-ratio:16/10}}
"""
PROGRESS_JS = ('<div class="progress" aria-hidden="true"><span></span></div><script>(function(){var b=document.querySelector(".progress span");'
               'function u(){var d=document.documentElement,h=d.scrollHeight-d.clientHeight;b.style.width=(h>0?Math.min(100,d.scrollTop/h*100):0)+"%"}'
               'addEventListener("scroll",u,{passive:true});u()})();</script>')
SEC_LABEL = {'fr': 'Partie', 'en': 'Part', 'es': 'Parte'}

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
    # Hiérarchie des titres sans saut (h2 → h4 devient h2 → h3) : lecteurs d'écran et moteurs.
    niveau = [1]
    def suite(m):
        n = int(m.group(1)); n = min(n, niveau[0] + 1); niveau[0] = n
        return f'<h{n}{m.group(2)}>{m.group(3)}</h{n}>'
    body = re.sub(r'<h([2-6])([^>]*)>(.*?)</h\1>', suite, body, flags=re.S)
    toc = ''
    if len(heads) >= 4:
        items = ''.join(f'<li><a href="#{h}">{E(t)}</a></li>' for h, t in heads)
        toc = f'<nav class="toc"><b>{E(TOC_LABEL[lang])}</b><ul>{items}</ul></nav>'
    return toc, body

def words(txt):
    return len(re.sub('<[^>]+>', ' ', txt).split())

def head(lang, title, desc, path_of, canonical, image, extra_ld='', kw='', img_alt='', og_type='article', langs=None, img_wh=None):
    """path_of(x) → chemin de la version dans la langue x (pour hreflang)."""
    alts = ''.join(f'<link rel="alternate" hreflang="{x}" href="{BASE}{path_of(x)}">' for x in (langs or LANGS))
    if not langs or 'en' in langs:  # article en français seul : pas de x-default vers l'anglais
        alts += f'<link rel="alternate" hreflang="x-default" href="{BASE}{path_of("en")}">'
    kw_tag = f'<meta name="keywords" content="{E(kw)}">' if kw else ''
    if img_wh is None and image.startswith('/assets/'):
        img_wh = webp_size(ROOT + image)
    mime = {'webp': 'image/webp', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png'}.get(image.rsplit('.', 1)[-1].lower())
    img_dim = ((f'<meta property="og:image:width" content="{img_wh[0]}"><meta property="og:image:height" content="{img_wh[1]}">' if img_wh else '')
               + (f'<meta property="og:image:type" content="{mime}">' if mime else ''))
    alt_tag = (f'<meta property="og:image:alt" content="{E(img_alt)}">'
               f'<meta name="twitter:image:alt" content="{E(img_alt)}">') if img_alt else ''
    return f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}">
<link rel="canonical" href="{BASE}{canonical}">{alts}
<meta name="robots" content="index,follow,max-image-preview:large"><meta name="theme-color" content="#0A0A14">{kw_tag}
<meta property="og:type" content="{og_type}"><meta property="og:site_name" content="MeditaDream">
<meta property="og:url" content="{BASE}{canonical}"><meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}"><meta property="og:image" content="{BASE}{image}">{img_dim}{alt_tag}
<meta property="og:locale" content="{OG_LOCALE[lang]}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{E(title)}"><meta name="twitter:description" content="{E(desc)}"><meta name="twitter:image" content="{BASE}{image}">
{extra_ld}
{HEAD_ICONES}{BANNIERE}
<link rel="alternate" type="application/rss+xml" title="MeditaDream" href="{BASE}/{lang}/blog/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&display=swap" onload="this.onload=null;this.rel='stylesheet'"><noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&display=swap"></noscript>
<style>{CSS}{POST_CSS}</style></head><body>"""

def header_html(lang, blog_path_of):
    t = T[lang]
    lg = ''.join(f'<a href="{blog_path_of(x)}" class="{"on" if x == lang else ""}">{x.upper()}</a>' for x in LANGS)
    return f'<header><div class="wrap"><a href="../" class="b">{E(t["back"])}</a><a href="./">{E(t["blog"])}</a><div class="lg">{lg}</div></div></header>'

def footer_html(lang):
    villes = '<a href="/fr/formation-meditation/">Formations par ville</a>' if lang == 'fr' else ''
    return f'<footer><div class="wrap"><span>MeditaDream</span><a href="../">meditadream.com/{lang}</a><a href="./">{E(T[lang]["blog"])}</a>{villes}</div></footer>'

def render_article(a, lang, arts):
    t = T[lang]
    body = ''.join(section_html(lang, sid) for sid in a['sections'])
    mins = max(2, round(words(body) / 200))
    img = f'/assets/blog/{_img_slug(a, lang)}' if a.get('image') is not None else '/assets/brand/og-image.jpg'
    ld = {
        '@context': 'https://schema.org',
        '@graph': [
            {'@type': 'Article', 'headline': a['title'][lang], 'description': a['desc'][lang],
             'image': BASE + img, 'datePublished': a['published'], 'dateModified': a.get('modified', a['published']), 'inLanguage': lang,
             'keywords': a.get('kw', {}).get(lang, ''), 'articleSection': SECTION_LABEL[lang],
             'mainEntityOfPage': f'{BASE}/{lang}/blog/{a["slug"][lang]}.html',
             'author': {'@type': 'Organization', 'name': 'MeditaDream', 'url': BASE + '/'},
             'publisher': {'@type': 'Organization', 'name': 'MeditaDream',
                           'logo': {'@type': 'ImageObject', 'url': f'{BASE}/assets/brand/logo.png'}}},
            {'@type': 'WebSite', 'name': 'MeditaDream', 'url': BASE + '/', 'inLanguage': lang},
            {'@type': 'BreadcrumbList', 'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': 'MeditaDream', 'item': f'{BASE}/{lang}/'},
                {'@type': 'ListItem', 'position': 2, 'name': T[lang]['blog'], 'item': f'{BASE}/{lang}/blog/'},
                {'@type': 'ListItem', 'position': 3, 'name': a['title'][lang]}]},
        ] + ([{'@type': 'FAQPage', 'mainEntity': [
                {'@type': 'Question', 'name': q,
                 'acceptedAnswer': {'@type': 'Answer', 'text': r}}
                for q, r in a['faq'][lang]]}] if a.get('faq') else []),
    }
    ld_tag = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace('<', '\\u003c') + '</script>'
    path_of = lambda x: f'/{x}/blog/{a["slug"][x]}.html'
    art_kw = ', '.join(x for x in (a.get('kw', {}).get(lang, ''), SITE_KW[lang].split(', ', 1)[0]) if x)
    img_alt = HERO_ALTS.get((a.get('image'), lang), a['title'][lang]) if a.get('image') is not None else a['title'][lang]
    h = head(lang, a['title'][lang], a['desc'][lang], path_of, path_of(lang), img, ld_tag, kw=art_kw, img_alt=img_alt)
    h += header_html(lang, lambda x: f'../../{x}/blog/{a["slug"][x]}.html')
    g = blog_hubs.SERIES_GROUP.get(a['id'], 'bases'); hl = blog_hubs.group_link(lang, g, HUB_ACT)
    h += PROGRESS_JS
    h += (f'<main class="wrap post-main"><article class="post"><div class="post-head"><nav class="crumbs"><a href="../">MeditaDream</a>'
          f'<span>›</span><a href="./">{E(T[lang]["blog"])}</a>'
          + (f'<span>›</span><a href="{hl}">{E(blog_hubs.HUBS[lang][g]["h1"])}</a>' if hl else '')
          + f'</nav><h1>{E(a["title"][lang])}</h1>')
    h += (f'<div class="meta"><span>{E(t["published_on"])} {E(fmt_date(a["published"], lang))}</span>'
          f'<span>{mins} {E(t["read"])}</span></div></div>')
    h += f'<p class="lead">{E(a["desc"][lang])}</p>'
    if a.get('intro'):
        h += f'<p class="intro">{E(a["intro"][lang])}</p>'
    if a.get('hero') is not None:
        sl = SCHEMA_FILES[a['hero']][lang]
        alt = HERO_ALTS.get((a['hero'], lang), a['title'][lang])
        cap = SCHEMA_PREFIX.sub('', alt)
        dim = webp_size(f'{ROOT}/assets/blog/{sl}-{lang}.webp')
        wh = f'width="{dim[0]}" height="{dim[1]}"' if dim else 'width="960"'
        h += (f'<figure class="hero"><img src="../../assets/blog/{sl}-{lang}.webp" alt="{E(alt)}" '
              f'{wh} fetchpriority="high" decoding="async"><figcaption>{E(cap)}</figcaption></figure>')
    toc, body = enrich_body(body, lang)
    figs = blog_fr.photo_figs(a.get('photos'), lang, a['title'][lang])
    if figs:
        # photos d'ambiance : une paire au milieu de l'article, entre deux blocs
        cuts = [m.start() for m in re.finditer(r'\n\s*<div class="(?:card|section-head)"', body)]
        pos = cuts[max(2, round(len(cuts) * 0.55))] if len(cuts) >= 4 else (cuts[-1] if cuts else len(body))
        cls = 'pair' if len(figs) > 1 else 'ph r'
        body = body[:pos] + f'<figure class="{cls}">{"".join(figs[:2])}</figure>' + body[pos:]
    h += toc + f'<div class="body">{body}</div>'
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
        h += f'<section class="rel"><h2>{E(t["other"])}</h2><ul class="rel-grid">'
        for o in others:
            th = (f'<img src="../../assets/blog/{_img_slug(o, lang)}" alt="" loading="lazy" width="640" height="400">'
                  if o.get('image') is not None else '<span class="n">✦</span>')
            h += f'<li><a href="{o["slug"][lang]}.html">{th}<h3>{E(o["title"][lang])}</h3></a></li>'
        h += '</ul></section>'
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
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'Blog', 'name': t['idx_title'], 'description': t['idx_desc'], 'url': f'{BASE}/{lang}/blog/',
         'inLanguage': lang, 'publisher': {'@type': 'Organization', 'name': 'MeditaDream', 'url': BASE + '/'},
         'blogPost': [{'@type': 'BlogPosting', 'headline': a['title'][lang], 'url': f'{BASE}/{lang}/blog/{a["slug"][lang]}.html',
                       'datePublished': a['published'], 'description': a['desc'][lang]} for a in reversed(pub)]},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'MeditaDream', 'item': f'{BASE}/{lang}/'},
            {'@type': 'ListItem', 'position': 2, 'name': t['blog']}]}]}
    ld_tag = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace('<', '\\u003c') + '</script>'
    h = head(lang, t['idx_seo'], t['idx_desc'], path_of, path_of(lang), '/assets/brand/og-image.jpg',
             ld_tag, kw=SITE_KW[lang], img_alt='MeditaDream', og_type='website')
    h += header_html(lang, lambda x: f'../../{x}/blog/')
    h += f'<main class="wrap bidx"><h1>{E(t["idx_title"])}</h1><p class="lead">{E(t["idx_desc"])}</p>'
    nav = blog_hubs.themes_nav(lang, HUB_ACT)
    if nav: h += nav.replace('class="themes"', 'class="themes topnav"', 1)
    h += '<ul class="alist">'
    fr_items = blog_fr.index_items(blog_fr.load(), lang) if lang in ('fr', 'en', 'es') else []
    entries = [('a', a['published'], '', a) for a in pub] + [('f', x['published'], x['order'], x) for x in fr_items]
    entries.sort(key=lambda e: (e[1], e[2]))
    for i, (kind, _, _, a) in enumerate(reversed(entries)):
        if kind == 'f':
            th = f'<span class="th"><img src="../../assets/blog/{a["thumb"]}" alt="{E(a["alt"])}" loading="lazy" width="640" height="400"></span>'
            h += (f'<li><a href="{a["slug"]}.html">{th}<span class="tw"><h2>{E(a["title"])}</h2>'
                  f'<p>{E(a["desc"])}</p><span class="d">{E(fmt_date(a["published"], lang))}</span></span></a></li>')
            continue
        if a.get('image') is not None:
            sl = SCHEMA_FILES[a['image']][lang]
            alt = SCHEMA_PREFIX.sub('', HERO_ALTS.get((a['image'], lang), a['title'][lang]))
            th = f'<span class="th"><img src="../../assets/blog/{sl}-{lang}.webp" alt="{E(alt)}" loading="lazy" width="88" height="88"></span>'
        else:
            th = f'<span class="th n">{len(entries)-i:02d}</span>'
        h += (f'<li><a href="{a["slug"][lang]}.html">{th}<span class="tw"><h2>{E(a["title"][lang])}</h2>'
              f'<p>{E(a["desc"][lang])}</p><span class="d">{E(fmt_date(a["published"], lang))}</span></span></a></li>')
    h += f'</ul><p class="lead" style="font-size:16px">{E(t["soon"])}</p></main>'
    h += footer_html(lang) + '</body></html>'
    return h

def render_sitemap(arts):
    urls = []
    def block(path_of):
        alts = ''.join(f'<xhtml:link rel="alternate" hreflang="{x}" href="{BASE}{path_of(x)}"/>' for x in LANGS)
        alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{BASE}{path_of("en")}"/>'
        return alts
    fr_seuls = blog_fr.load()
    dern = max([a['published'] for a in arts if a.get('published')] + [a['published'] for a in fr_seuls if a.get('published')], default=None)
    lm = f'<lastmod>{dern}</lastmod>' if dern else ''
    for x in LANGS:
        urls.append(f'<url><loc>{BASE}/{x}/blog/</loc>{lm}{block(lambda y: f"/{y}/blog/")}</url>')
    for a in arts:
        if not a.get('published'):
            continue
        pa = lambda y, a=a: f'/{y}/blog/{a["slug"][y]}.html'
        for x in LANGS:
            urls.append(f'<url><loc>{BASE}{pa(x)}</loc><lastmod>{a["published"]}</lastmod>{block(pa)}</url>')
    urls += blog_fr.sitemap_urls(sys.modules[__name__], fr_seuls)
    urls += blog_hubs.sitemap_urls(sys.modules[__name__], HUB_ACT)
    urls += app_pages.sitemap_urls(sys.modules[__name__], APP_WRITTEN)
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">' + ''.join(urls) + '</urlset>')

APP_WRITTEN = []  # pages de l'application écrites (chemin, versions par langue)
HUB_ACT = {}  # thèmes ayant une page, par langue (rempli par build)
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

def render_feed(lang, arts):
    t = T[lang]
    pub = [a for a in arts if a.get('published')]
    items = ''
    entries = [(a['published'], '', a['slug'][lang], a['title'][lang], a['desc'][lang]) for a in pub]
    if lang in ('fr', 'en', 'es'):
        entries += [(x['published'], x['order'], x['slug'], x['title'], x['desc']) for x in blog_fr.index_items(blog_fr.load(), lang)]
    entries.sort()
    for d, _, slug, title, desc in reversed(entries):
        link = f'{BASE}/{lang}/blog/{slug}.html'
        items += (f'<item><title>{E(title)}</title><link>{link}</link>'
                  f'<guid isPermaLink="true">{link}</guid>'
                  f'<pubDate>{d}T07:00:00Z</pubDate>'
                  f'<description>{E(desc)}</description></item>')
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>'
            f'<title>{E(t["idx_seo"])}</title><link>{BASE}/{lang}/blog/</link>'
            f'<description>{E(t["idx_desc"])}</description><language>{lang}</language>'
            f'<atom:link href="{BASE}/{lang}/blog/feed.xml" rel="self" type="application/rss+xml"/>'
            + items + '</channel></rss>')

def build():
    global SCHEMA_FILES
    SCHEMA_FILES = {int(k): v for k, v in _load_schema_files().items()}
    _scan_hero_alts()
    arts = load()
    global HUB_ACT
    HUB_ACT = blog_hubs.active(sys.modules[__name__])
    for lang in LANGS:
        os.makedirs(f'{ROOT}/{lang}/blog', exist_ok=True)
        open(f'{ROOT}/{lang}/blog/index.html', 'w', encoding='utf-8').write(render_index(lang, arts))
        open(f'{ROOT}/{lang}/blog/feed.xml', 'w', encoding='utf-8').write(render_feed(lang, arts))
        for a in arts:
            if a.get('published'):
                open(f'{ROOT}/{lang}/blog/{a["slug"][lang]}.html', 'w', encoding='utf-8').write(render_article(a, lang, arts))
    fr_seuls = blog_fr.build(sys.modules[__name__])
    blog_hubs.build(sys.modules[__name__])
    global APP_WRITTEN
    APP_WRITTEN = app_pages.build(sys.modules[__name__])
    print(f'✓ pages de l’application (catégories, mondes, équipes) : {len(APP_WRITTEN)}')
    open(f'{ROOT}/sitemap-blog.xml', 'w', encoding='utf-8').write(render_sitemap(arts))
    print('✓ pages thématiques : ' + ', '.join(f'{l} {len(v)}' for l, v in HUB_ACT.items()))
    print(f'✓ articles en français seul : {len(blog_fr.published(fr_seuls))} publié(s), {len(fr_seuls) - len(blog_fr.published(fr_seuls))} programmé(s)')
    pub = sum(1 for a in arts if a.get('published'))
    print(f'✓ blog reconstruit : {pub} article(s) publié(s) × 3 langues + index + sitemap-blog.xml')
    import seo_medias; seo_medias.main()  # texte alternatif + titre de chaque image, sitemaps images et vidéos
    import mesure; mesure.main(False)  # balise Google Analytics + consentement sur toutes les pages

if __name__ == '__main__':
    build()
