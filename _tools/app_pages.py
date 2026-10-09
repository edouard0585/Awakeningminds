#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pages de l'application, par langue : catégories de méditation, mondes immersifs, page « équipes / entreprise ».

  /{lang}/{meditations|meditaciones}/            index des 19 catégories
  /{lang}/{meditations|meditaciones}/<slug>.html une page par catégorie (séances réelles, durées, niveau, FAQ)
  /{lang}/{mondes|worlds|mundos}/                index des 17 mondes
  /{lang}/{mondes|worlds|mundos}/<slug>.html     une page par monde (textes de l'application)
  /{lang}/<slug équipes>.html                    méditation en entreprise (fr) / pour les équipes (en, es)

Données : _tools/app_catalog.json (exporté de l'application) + _tools/pages_{fr,en,es}.json (textes SEO
écrits pour chaque langue). Même charte que le blog. Appelé par blog_build.build(). Stdlib uniquement.
"""
import json, os, html
E = html.escape
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(ROOT, '_tools')
LANGS = ['fr', 'en', 'es']
DIR = {'med': {'fr': 'meditations', 'en': 'meditations', 'es': 'meditaciones'},
       'world': {'fr': 'mondes', 'en': 'worlds', 'es': 'mundos'}}
# Catégorie de l'app → thème du blog (pour relier les deux, dans les deux sens)
CAT_GROUP = {'learningBasics': 'bases', 'fourMin': 'bases', 'calm': 'sommeil', 'emotionalGrowth': 'psy', 'shadow': 'psy',
             'sacred': 'lieux', 'guides': 'chamanisme', 'higherKnowledge': 'astral', 'shamanic': 'chamanisme',
             'buddhist': 'bases', 'qigong': 'energie', 'visualisation': 'lieux', 'miniAdventures': 'lieux',
             'thirdEye': 'energie', 'cosmic': 'astral', 'trance': 'transe', 'tranceTechniques': 'transe',
             'astralMicroDetach': 'astral', 'astralJourneys': 'astral'}
L = {
 'fr': dict(home='MeditaDream', med='Méditations', worlds='Mondes immersifs', blog='Blog', sessions='séances', min='min',
            to='à', level={'beginner': 'débutant', 'intermediate': 'intermédiaire', 'advanced': 'avancé'},
            list='Les séances', faq='Questions fréquentes', other='Autres catégories', otherw='Autres mondes',
            read='Pour aller plus loin', cta_t='Pratiquer gratuitement',
            cta_p="Toutes ces séances sont dans l'application MeditaDream : gratuite, sans abonnement, sans publicité ni compte, et utilisable hors ligne.",
            cta_b="Découvrir l'application", scene='La scène', goal='L’intention', inter='Ce que vous y faites', sound='L’ambiance sonore',
            visual='Les couleurs du monde', end='Au moment de partir', duration='Durée', moods='Ambiance', practice='Pratiquer avec l’application',
            teams='Méditation en entreprise', form_t='Parlons de votre projet', name='Votre nom', company='Entreprise', email='Votre email',
            msg='Votre projet (taille de l’équipe, objectifs, sur site ou à distance…)', send='Envoyer', sent='Merci, votre message est bien reçu. Nous vous répondons rapidement.',
            err='Envoi impossible pour le moment. Écrivez-nous : edouard@meditadream.com'),
 'en': dict(home='MeditaDream', med='Meditations', worlds='Immersive worlds', blog='Blog', sessions='sessions', min='min',
            to='to', level={'beginner': 'beginner', 'intermediate': 'intermediate', 'advanced': 'advanced'},
            list='The sessions', faq='Frequently asked questions', other='Other categories', otherw='Other worlds',
            read='Read more', cta_t='Practice for free',
            cta_p='Every session is in the MeditaDream app: free, no subscription, no ads, no account, and it works offline.',
            cta_b='Discover the app', scene='The scene', goal='The intention', inter='What you do there', sound='The soundscape',
            visual='The colors of this world', end='As you leave', duration='Length', moods='Mood', practice='Practice with the app',
            teams='For teams', form_t='', name='', company='', email='', msg='', send='', sent='', err=''),
 'es': dict(home='MeditaDream', med='Meditaciones', worlds='Mundos inmersivos', blog='Blog', sessions='sesiones', min='min',
            to='a', level={'beginner': 'principiante', 'intermediate': 'intermedio', 'advanced': 'avanzado'},
            list='Las sesiones', faq='Preguntas frecuentes', other='Otras categorías', otherw='Otros mundos',
            read='Para profundizar', cta_t='Practica gratis',
            cta_p='Todas estas sesiones están en la app MeditaDream: gratis, sin suscripción, sin anuncios ni cuenta, y funciona sin conexión.',
            cta_b='Descubre la app', scene='La escena', goal='La intención', inter='Lo que haces allí', sound='El paisaje sonoro',
            visual='Los colores de este mundo', end='Al despedirte', duration='Duración', moods='Ambiente', practice='Practica con la app',
            teams='Para equipos', form_t='', name='', company='', email='', msg='', send='', sent='', err=''),
}
CSS = """
.ap-hero{display:grid;grid-template-columns:auto 1fr;gap:20px;align-items:center;margin:6px 0 22px}
.ap-hero img{width:120px;height:120px;border-radius:22px;border:1px solid var(--line);object-fit:cover;margin:0}
@media(max-width:520px){.ap-hero{grid-template-columns:1fr}.ap-hero img{width:96px;height:96px}}
.ap-meta{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 18px}
.ap-meta span{font-family:'Avenir Next',sans-serif;font-size:12.5px;color:var(--muted);border:1px solid var(--line);border-radius:99px;padding:4px 11px}
.ap-list{list-style:none;padding:0;margin:10px 0 26px;display:grid;gap:10px}
.ap-list li{border:1px solid var(--line);border-radius:14px;padding:14px 18px;background:rgba(255,255,255,.02)}
.ap-list h3{font-size:20px;margin:0 0 4px;color:#fff7e8}
.ap-list .d{font-family:'Avenir Next',sans-serif;font-size:12.5px;color:var(--gold);margin-bottom:6px}
.ap-list p{margin:0;font-size:15px}
.ap-grid{list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px;margin:18px 0 26px}
.ap-grid a{display:grid;gap:8px;border:1px solid var(--line);border-radius:16px;padding:14px;text-decoration:none;background:rgba(255,255,255,.02);height:100%}
.ap-grid a:hover{border-color:rgba(212,175,106,.5)}
.ap-grid img{width:100%;height:auto;aspect-ratio:16/10;object-fit:cover;border-radius:12px;margin:0;border:0}
.ap-grid img.sq{aspect-ratio:1;max-width:96px}
.ap-grid b{font-family:'Cormorant Garamond',Georgia,serif;font-size:21px;color:#fff7e8;font-weight:500}
.ap-grid span{font-family:'Avenir Next',sans-serif;font-size:13px;color:var(--muted)}
.ap-world img.hero{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:18px;margin:4px 0 22px}
.ap-scene{font-style:italic;font-size:21px;color:#fff7e8;border-left:2px solid var(--gold);padding:4px 0 4px 18px;margin:8px 0 20px;font-family:'Cormorant Garamond',Georgia,serif}
.ap-dl{display:grid;grid-template-columns:minmax(150px,220px) 1fr;gap:10px 22px;margin:14px 0 24px;font-family:'Avenir Next',sans-serif;font-size:15px}
.ap-dl dt{color:var(--gold)}.ap-dl dd{margin:0;color:var(--muted)}
@media(max-width:560px){.ap-dl{grid-template-columns:1fr}.ap-dl dd{margin-bottom:8px}}
.ap-links{display:flex;flex-wrap:wrap;gap:8px;list-style:none;padding:0;margin:8px 0 22px}
.ap-links a{display:inline-block;border:1px solid var(--line);border-radius:99px;padding:6px 14px;font-family:'Avenir Next',sans-serif;font-size:13.5px;color:var(--muted);text-decoration:none}
.ap-links a:hover{border-color:var(--gold);color:var(--gold)}
.ap-form{display:grid;gap:10px;max-width:560px;margin:10px 0 26px;font-family:'Avenir Next',sans-serif}
.ap-form label{font-size:13.5px;color:var(--muted)}
.ap-form input,.ap-form textarea{width:100%;background:#0e0c1c;border:1px solid var(--line);border-radius:10px;color:var(--ink);padding:10px 12px;font:15px 'Avenir Next',sans-serif}
.ap-form textarea{min-height:130px}
.ap-form button{justify-self:start;background:linear-gradient(135deg,#D4AF6A,#b8934f);color:#161122;border:0;border-radius:99px;padding:11px 24px;font-weight:600;cursor:pointer;font-size:15px}
.ap-form [role=status]{font-size:14px;color:var(--gold)}
nav.lgx{display:flex;gap:8px;margin-left:auto}
"""


def load():
    cat = json.load(open(f'{T}/app_catalog.json', encoding='utf-8'))
    P = {l: json.load(open(f'{T}/pages_{l}.json', encoding='utf-8')) for l in LANGS if os.path.exists(f'{T}/pages_{l}.json')}
    return cat, P


def u(lang, kind, slug=None):
    d = DIR[kind][lang]
    return f'/{lang}/{d}/' + (f'{slug}.html' if slug else '')


def img_cat(cid):
    for p in (f'assets/o/cats/catart-{cid}.webp', f'assets/cats/catart-{cid}.png', f'assets/o/cats/icon-{cid}.webp', f'assets/cats/icon-{cid}.png'):
        if os.path.exists(os.path.join(ROOT, p)): return '/' + p
    return '/assets/brand/og-image.jpg'


def img_world(wid):
    for p in (f'assets/o/worlds/{wid}.webp', f'assets/worlds/{wid}.jpg'):
        if os.path.exists(os.path.join(ROOT, p)): return '/' + p
    return '/assets/brand/og-image.jpg'


def dims(p):
    """Largeur et hauteur d'une image du site (WebP ou PNG), lues dans l'en-tête ; '' si inconnues."""
    f = os.path.join(ROOT, p.lstrip('/'))
    try:
        b = open(f, 'rb').read(32)
        if b[:8] == b'\x89PNG\r\n\x1a\n':
            w, h = int.from_bytes(b[16:20], 'big'), int.from_bytes(b[20:24], 'big')
        else:
            import blog_build
            w, h = blog_build.webp_size(f) or (0, 0)
        return f' width="{w}" height="{h}"' if w and h else ''
    except Exception:
        return ''


def rel(p, depth):
    """Chemin relatif depuis une page située à `depth` dossiers sous la racine (/fr/x.html = 1)."""
    return '../' * depth + p.lstrip('/')


def header(lang, here, alt_of):
    t = L[lang]
    lg = ''.join(f'<a href="{alt_of(x)}" class="{"on" if x == lang else ""}">{x.upper()}</a>' for x in LANGS)
    return (f'<header><div class="wrap"><a href="/{lang}/" class="b">← {E(t["home"])}</a>'
            f'<a href="{u(lang, "med")}">{E(t["med"])}</a><a href="/{lang}/blog/">{E(t["blog"])}</a>'
            f'<div class="lg">{lg}</div></div></header>')


def page(bb, lang, title, desc, path, alt_paths, img, ld, body, img_alt):
    langs = [x for x in LANGS if x in alt_paths]
    h = bb.head(lang, title, desc, lambda x: alt_paths[x], path, img, ld, img_alt=img_alt, og_type='website',
                langs=langs if langs != LANGS else None)
    h = h.replace('</style>', CSS + '</style>', 1)
    h += header(lang, path, lambda x: alt_paths.get(x, f'/{x}/'))
    return h + '<main class="wrap">' + body + '</main>' + bb.footer_html(lang).replace('href="../"', f'href="/{lang}/"').replace('href="./"', f'href="/{lang}/blog/"') + '</body></html>'


def ld_tag(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace('<', '\\u003c') + '</script>'


def crumbs(lang, items):
    return '<nav class="crumbs">' + '<span>›</span>'.join(f'<a href="{h}">{E(n)}</a>' if h else f'<span>{E(n)}</span>' for n, h in items) + '</nav>'


def bc_ld(bb, items):
    return {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, **({'item': bb.BASE + h} if h else {})} for i, (n, h) in enumerate(items)]}


def cta(lang):
    t = L[lang]
    return f'<div class="cta"><h2>{E(t["cta_t"])}</h2><p>{E(t["cta_p"])}</p><a href="/{lang}/#download">✦ {E(t["cta_b"])}</a></div>'


def faq_html(lang, faq):
    if not faq: return ''
    qa = ''.join(f'<details><summary>{E(q)}</summary><p>{E(r)}</p></details>' for q, r in faq)
    return f'<section class="afaq"><h2>{E(L[lang]["faq"])}</h2>{qa}</section>'


LASTMOD_F = os.path.join(T, 'app_pages_lastmod.json')
_LM = {}


def _write(path, html_):
    """Écrit la page et met sa date de mise à jour à aujourd'hui seulement si son contenu a changé."""
    import hashlib
    from datetime import date
    open(f'{ROOT}{path}', 'w', encoding='utf-8').write(html_)
    key = path[:-len('index.html')] if path.endswith('index.html') else path
    hsh = hashlib.sha1(html_.encode('utf-8')).hexdigest()[:16]
    old = _LM.get(key)
    _LM[key] = old if old and old[0] == hsh else [hsh, date.today().isoformat()]


def build(bb):
    import blog_hubs
    _LM.clear()
    if os.path.exists(LASTMOD_F): _LM.update(json.load(open(LASTMOD_F, encoding='utf-8')))
    cat, P = load()
    act = getattr(bb, 'HUB_ACT', {})
    written = []
    for lang, p in P.items():
        t = L[lang]
        os.makedirs(f'{ROOT}{u(lang, "med")}', exist_ok=True); os.makedirs(f'{ROOT}{u(lang, "world")}', exist_ok=True)
        cats = cat['categories']
        # --- pages catégories ---
        for cid, c in cats.items():
            s = p['categories'][cid]
            path = u(lang, 'med', s['slug'])
            alts = {x: u(x, 'med', P[x]['categories'][cid]['slug']) for x in P}
            lv = ', '.join(t['level'][x] for x in c['levels'])
            meta = f'<div class="ap-meta"><span>{c["count"]} {E(t["sessions"])}</span><span>{c["min"]} {E(t["to"])} {c["max"]} {E(t["min"])}</span><span>{E(lv)}</span></div>'
            items = ''.join(f'<li><h3>{E(m["title"][lang])}</h3><div class="d">{m["dur"]} {E(t["min"])} · {E(t["level"].get(m["level"], m["level"]))}</div>'
                            f'<p>{E(m["desc"][lang])}</p></li>' for m in c['meds'] if m['title'][lang])
            g = CAT_GROUP.get(cid); hl = blog_hubs.group_link(lang, g, act) if g else None
            read = (f'<h2>{E(t["read"])}</h2><ul class="ap-links"><li><a href="/{lang}/blog/{hl}">{E(blog_hubs.HUBS[lang][g]["h1"])}</a></li></ul>') if hl else ''
            sib = [k for k in cats if k != cid and CAT_GROUP.get(k) == g][:3] or [k for k in cats if k != cid][:3]
            others = ''.join(f'<li><a href="{u(lang, "med", p["categories"][k]["slug"])}">{E(cats[k]["name"][lang])}</a></li>' for k in sib)
            bc = [(t['home'], f'/{lang}/'), (t['med'], u(lang, 'med')), (cats[cid]['name'][lang], None)]
            body = (crumbs(lang, bc) + f'<article><div class="ap-hero"><img src="{rel(img_cat(cid), 2)}" alt=""{dims(img_cat(cid))}>'
                    f'<div><h1>{E(s["h1"])}</h1>{meta}</div></div>'
                    + ''.join(f'<p class="lead">{E(x)}</p>' if i == 0 else f'<p class="intro">{E(x)}</p>' for i, x in enumerate(s['intro']))
                    + f'<h2>{E(t["list"])}</h2><ol class="ap-list">{items}</ol>' + cta(lang) + read
                    + f'<h2>{E(t["other"])}</h2><ul class="ap-links">{others}</ul>' + faq_html(lang, s.get('faq')) + '</article>')
            ld = ld_tag({'@context': 'https://schema.org', '@graph': [
                {'@type': 'CollectionPage', 'name': s['h1'], 'description': s['desc'], 'url': bb.BASE + path, 'inLanguage': lang,
                 'mainEntity': {'@type': 'ItemList', 'numberOfItems': len(c['meds']), 'itemListElement': [
                     {'@type': 'ListItem', 'position': i + 1, 'name': m['title'][lang]} for i, m in enumerate(c['meds'])]}},
                bc_ld(bb, bc)] + ([{'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': r}} for q, r in s['faq']]}] if s.get('faq') else [])})
            _write(path, page(bb, lang, s['seo'], s['desc'], path, alts, img_cat(cid), ld, body, cats[cid]['name'][lang]))
            written.append((path, alts))
        # --- index des catégories ---
        s = p['meditations_index']; path = u(lang, 'med'); alts = {x: u(x, 'med') for x in P}
        cards = ''.join(f'<li><a href="{p["categories"][k]["slug"]}.html"><img class="sq" src="{rel(img_cat(k), 2)}" alt=""{dims(img_cat(k))} loading="lazy">'
                        f'<b>{E(c["name"][lang])}</b><span>{c["count"]} {E(t["sessions"])} · {c["min"]}–{c["max"]} {E(t["min"])}</span></a></li>' for k, c in cats.items())
        bc = [(t['home'], f'/{lang}/'), (t['med'], None)]
        body = (crumbs(lang, bc) + f'<h1>{E(s["h1"])}</h1><p class="lead">{E(s["intro"])}</p><ul class="ap-grid">{cards}</ul>'
                + f'<ul class="ap-links"><li><a href="{u(lang, "world")}">{E(t["worlds"])}</a></li><li><a href="/{lang}/{p["teams"]["slug"]}.html">{E(p["teams"]["h1"])}</a></li></ul>' + cta(lang))
        ld = ld_tag({'@context': 'https://schema.org', '@graph': [{'@type': 'CollectionPage', 'name': s['h1'], 'description': s['desc'], 'url': bb.BASE + path, 'inLanguage': lang}, bc_ld(bb, bc)]})
        _write(path + 'index.html', page(bb, lang, s['seo'], s['desc'], path, alts, img_cat('calm'), ld, body, s['h1']))
        written.append((path, alts))
        # --- pages mondes ---
        ws = cat['worlds']
        for wid, w in ws.items():
            if wid not in p['worlds']: continue
            s = p['worlds'][wid]; path = u(lang, 'world', s['slug'])
            alts = {x: u(x, 'world', P[x]['worlds'][wid]['slug']) for x in P if wid in P[x]['worlds']}
            dl = ''.join(f'<dt>{E(t[k])}</dt><dd>{E(w[f][lang])}</dd>' for k, f in (('goal', 'objective'), ('inter', 'interactions'), ('sound', 'soundDesign'), ('visual', 'visualAtmosphere')) if w.get(f, {}).get(lang))
            dl += f'<dt>{E(t["duration"])}</dt><dd>{w["minutes"][lang]} {E(t["min"])}</dd><dt>{E(t["moods"])}</dt><dd>{E(", ".join(w["moods"][lang]))}</dd>'
            others = ''.join(f'<li><a href="{u(lang, "world", p["worlds"][k]["slug"])}">{E(ws[k]["name"][lang])}</a></li>' for k in list(ws)[:0] or [k for k in ws if k != wid][:6] if k in p['worlds'])
            bc = [(t['home'], f'/{lang}/'), (t['worlds'], u(lang, 'world')), (w['name'][lang], None)]
            body = (crumbs(lang, bc) + f'<article class="ap-world"><h1>{E(s["h1"])}</h1><p class="lead">{E(w["tagline"][lang])}</p>'
                    f'<img class="hero" src="{rel(img_world(wid), 2)}" alt="{E(w["name"][lang])}"{dims(img_world(wid))} fetchpriority="high">'
                    f'<p class="intro">{E(w["description"][lang])}</p><h2>{E(t["scene"])}</h2><p class="ap-scene">{E(w["openingScene"][lang])}</p>'
                    f'<dl class="ap-dl">{dl}</dl><h2>{E(t["end"])}</h2><p class="intro">{E(w["endingNote"][lang])}</p>' + cta(lang)
                    + f'<h2>{E(t["otherw"])}</h2><ul class="ap-links">{others}</ul></article>')
            ld = ld_tag({'@context': 'https://schema.org', '@graph': [{'@type': 'WebPage', 'name': s['h1'], 'description': s['desc'], 'url': bb.BASE + path, 'inLanguage': lang,
                         'primaryImageOfPage': bb.BASE + img_world(wid)}, bc_ld(bb, bc)]})
            _write(path, page(bb, lang, s['seo'], s['desc'], path, alts, img_world(wid), ld, body, w['name'][lang]))
            written.append((path, alts))
        # --- index des mondes ---
        s = p['worlds_index']; path = u(lang, 'world'); alts = {x: u(x, 'world') for x in P}
        cards = ''.join(f'<li><a href="{p["worlds"][k]["slug"]}.html"><img src="{rel(img_world(k), 2)}" alt=""{dims(img_world(k))} loading="lazy">'
                        f'<b>{E(w["name"][lang])}</b><span>{E(w["tagline"][lang])}</span></a></li>' for k, w in ws.items() if k in p['worlds'])
        bc = [(t['home'], f'/{lang}/'), (t['worlds'], None)]
        body = crumbs(lang, bc) + f'<h1>{E(s["h1"])}</h1><p class="lead">{E(s["intro"])}</p><ul class="ap-grid">{cards}</ul>' + cta(lang)
        ld = ld_tag({'@context': 'https://schema.org', '@graph': [{'@type': 'CollectionPage', 'name': s['h1'], 'description': s['desc'], 'url': bb.BASE + path, 'inLanguage': lang}, bc_ld(bb, bc)]})
        _write(path + 'index.html', page(bb, lang, s['seo'], s['desc'], path, alts, img_world('zenGarden'), ld, body, s['h1']))
        written.append((path, alts))
        # --- équipes / entreprise ---
        s = p['teams']; path = f'/{lang}/{s["slug"]}.html'; alts = {x: f'/{x}/{P[x]["teams"]["slug"]}.html' for x in P}
        secs = ''.join(f'<h2>{E(x["h2"])}</h2>' + (f'<p>{E(x["p"])}</p>' if x.get('p') else '')
                       + (('<ul>' + ''.join(f'<li>{E(b)}</li>' for b in x['bullets']) + '</ul>') if x.get('bullets') else '') for x in s['sections'])
        form = ''
        if lang == 'fr':
            form = (f'<h2>{E(t["form_t"])}</h2><form class="ap-form" id="contact" data-ok="{E(t["sent"])}" data-err="{E(t["err"])}">'
                    f'<label for="f-name">{E(t["name"])}</label><input id="f-name" name="name" autocomplete="name" maxlength="120">'
                    f'<label for="f-co">{E(t["company"])}</label><input id="f-co" name="company" autocomplete="organization" maxlength="120">'
                    f'<label for="f-mail">{E(t["email"])}</label><input id="f-mail" name="email" type="email" required autocomplete="email">'
                    f'<label for="f-msg">{E(t["msg"])}</label><textarea id="f-msg" name="message" required></textarea>'
                    f'<input type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;left:-9999px">'
                    f'<p role="status" id="f-st"></p><button type="submit">{E(t["send"])}</button></form>'
                    """<script>(function(){var f=document.getElementById('contact');f.addEventListener('submit',function(e){e.preventDefault();
var st=document.getElementById('f-st'),d=new FormData(f),co=d.get('company');d.set('lang','fr');d.set('topic','Méditation en entreprise'+(co?' — '+co:''));
d.set('page',location.href);fetch('https://espace.awakeningminds.app/contact',{method:'POST',body:d,headers:{'Accept':'application/json'}})
.then(function(r){return r.json()}).then(function(j){st.textContent=j.ok?f.dataset.ok:(j.message||f.dataset.err);if(j.ok){f.reset();if(window.gtag)gtag('event','generate_lead',{form_id:'entreprise'})}})
.catch(function(){st.textContent=f.dataset.err})});})();</script>""")
        bc = [(t['home'], f'/{lang}/'), (s['h1'], None)]
        villes = '<p class="more"><a href="formation-meditation/">Formations à la méditation par ville : France, Belgique, Suisse, Luxembourg →</a></p>' if lang == 'fr' and os.path.exists(f'{T}/formations_fr.json') else ''
        body = crumbs(lang, bc) + f'<article><h1>{E(s["h1"])}</h1><p class="lead">{E(s["desc"])}</p>{secs}{form}' + cta(lang) + faq_html(lang, s.get('faq')) + villes + '</article>'
        ld = ld_tag({'@context': 'https://schema.org', '@graph': [{'@type': 'WebPage', 'name': s['h1'], 'description': s['desc'], 'url': bb.BASE + path, 'inLanguage': lang}, bc_ld(bb, bc)]
                     + ([{'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': r}} for q, r in s['faq']]}] if s.get('faq') else [])})
        _write(path, page(bb, lang, s['seo'], s['desc'], path, alts, img_cat('calm'), ld, body, s['h1']))
        written.append((path, alts))
    import sys, formation_pages  # formations par ville (fr), liées depuis le pied de page
    written += formation_pages.build(bb, sys.modules[__name__])
    json.dump(_LM, open(LASTMOD_F, 'w', encoding='utf-8'), indent=0, sort_keys=True)
    return written


def practice_links(lang, group):
    """Liens « Pratiquer avec l'application » pour une page thématique du blog."""
    try:
        cat, P = load()
    except Exception:
        return ''
    if lang not in P: return ''
    ks = [k for k, g in CAT_GROUP.items() if g == group][:3]
    if not ks: return ''
    li = ''.join(f'<li><a href="{u(lang, "med", P[lang]["categories"][k]["slug"])}">{E(cat["categories"][k]["name"][lang])}</a></li>' for k in ks)
    return f'<h2>{E(L[lang]["practice"])}</h2><ul class="ap-links">{li}</ul>'


def sitemap_urls(bb, written):
    out = []
    for path, alts in written:
        a = ''.join(f'<xhtml:link rel="alternate" hreflang="{x}" href="{bb.BASE}{p}"/>' for x, p in alts.items())
        if 'en' in alts: a += f'<xhtml:link rel="alternate" hreflang="x-default" href="{bb.BASE}{alts["en"]}"/>'
        lm = _LM.get(path, [None, None])[1]
        out.append(f'<url><loc>{bb.BASE}{path}</loc>' + (f'<lastmod>{lm}</lastmod>' if lm else '') + f'{a}</url>')
    return out
