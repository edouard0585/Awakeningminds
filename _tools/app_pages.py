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
            cta_b="Découvrir l'application", scene='La scène', goal='L’intention', inter='Ce que tu y fais', sound='L’ambiance sonore',
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
XL = {  # libellés des blocs ajoutés le 09-10 (mondes étoffés, pages thématiques)
 'fr': dict(qui='Pour qui, et à quel moment', deroule='Comment se déroule la séance', conseils='Conseils pour en profiter',
            sons='Les sons de l’application', fam={'nature': 'Nature', 'instruments_et_voix': 'Instruments et voix', 'nappes_et_drones': 'Nappes et drones'},
            minuteur='Minuteur « son seul » : 5, 10, 15, 20, 30, 45 ou 60 minutes, puis le son s’éteint en fondu.',
            seances='Les séances de l’application', voir='Voir la catégorie', themes='Autres thèmes'),
 'en': dict(qui='Who it is for, and when', deroule='How the session unfolds', conseils='Tips to make the most of it',
            sons='The sounds in the app', fam={'nature': 'Nature', 'instruments_et_voix': 'Instruments & voices', 'nappes_et_drones': 'Soundscapes & drones'},
            minuteur='Sound-only timer: 5, 10, 15, 20, 30, 45 or 60 minutes, then the sound fades out.',
            seances='Sessions in the app', voir='See the category', themes='More themes'),
 'es': dict(qui='Para quién y en qué momento', deroule='Cómo transcurre la sesión', conseils='Consejos para aprovecharla',
            sons='Los sonidos de la app', fam={'nature': 'Naturaleza', 'instruments_et_voix': 'Instrumentos y voces', 'nappes_et_drones': 'Texturas y drones'},
            minuteur='Temporizador «solo sonido»: 5, 10, 15, 20, 30, 45 o 60 minutos, y el sonido se apaga en fundido.',
            seances='Las sesiones de la app', voir='Ver la categoría', themes='Otros temas'),
}
# Pages thématiques (mots-clés des recherches réelles, 09-10) : textes dans _tools/themes_<langue>.json ;
# séances et sons ajoutés ici depuis les données de l'app (jamais recopiés à la main).
THEMES = ('sons', 'reve', 'chakras', 'gratitude')
THEME_IMG = {'sons': 'assets/worlds/mushroomForest.jpg', 'reve': 'assets/cats/catart-trance.png',
             'chakras': 'assets/cats/catart-calm.png', 'gratitude': 'assets/cats/catart-emotionalGrowth.png'}
THEME_SEANCES = {'reve': ['reves01', 'reves02', 'corpsc03', 'consci02', 'consci05'],
                 'chakras': ['chakra01', 'chakra02', 'cons02', 'corpsc01'],
                 'gratitude': ['croiss03', '4minut03', 'guides01', 'croiss02', 'cons06']}
THEME_CATS = {'sons': ['calm', 'fourMin'], 'reve': ['calm', 'trance'], 'chakras': ['calm', 'thirdEye', 'qigong'], 'gratitude': ['emotionalGrowth', 'fourMin']}
SONS = [('nature', ['sousbois', 'grandsBois', 'apresAverse', 'torrent', 'ressac']),
        ('instruments_et_voix', ['resonance', 'dizi', 'xiao', 'khoomei', 'feerie']),
        ('nappes_et_drones', ['nebuleuse', 'theta', 'monolithe'])]


def charge(nom, lang):
    f = os.path.join(T, f'{nom}_{lang}.json')
    return json.load(open(f, encoding='utf-8')) if os.path.exists(f) else None


CSS = """
.ap-theme img.hero{width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;border-radius:18px;margin:4px 0 22px}
.ap-sons{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;margin:10px 0 24px}
.ap-sons div{border:1px solid var(--line);border-radius:14px;padding:12px 16px;background:rgba(255,255,255,.02)}
.ap-sons b{display:block;font-family:'Cormorant Garamond',Georgia,serif;font-size:19px;color:#fff7e8;margin-bottom:4px}
.ap-sons span{font-family:'Avenir Next',sans-serif;font-size:13.5px;color:var(--muted)}
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


# Texte alternatif, titre et nom de fichier de chaque image, PAR LANGUE (fabriqué par scripts/site/medias_data.py ;
# copies WebP nommées dans la langue de la page : assets/o/<langue>/<nom>-<largeur>.webp, faites par build_site.py)
try:
    MEDIAS = json.load(open(os.path.join(T, 'medias.json'), encoding='utf-8'))
except FileNotFoundError:
    MEDIAS = {}


def media(key, lang, largeur):
    """(chemin de la copie nommée dans la langue, alt, title) ; chemin None si la copie n'existe pas encore."""
    m = MEDIAS.get(key, {}).get(lang)
    if not m: return None, '', ''
    p = f'assets/o/{lang}/{m["slug"]}-{largeur}.webp'
    return ('/' + p if os.path.exists(os.path.join(ROOT, p)) else None), m['alt'], m['title']


def cat_key(cid):
    return f'assets/cats/catart-{cid}.png' if f'assets/cats/catart-{cid}.png' in MEDIAS else f'assets/cats/icon-{cid}.png'


def img_tag(key, lang, largeur, fallback, depth, extra=''):
    """Balise <img> complète : copie nommée dans la langue si elle existe, sinon l'image d'origine ; alt + title toujours."""
    p, alt, title = media(key, lang, largeur)
    src = p or fallback
    t = f' title="{E(title)}"' if title else ''
    return f'<img src="{rel(src, depth)}" alt="{E(alt)}"{t}{dims(src)}{extra}>'


HERO_CAT = lambda cid, lang: img_tag(cat_key(cid), lang, 260, img_cat(cid), 2, ' fetchpriority="high" decoding="async"')
VIG_CAT = lambda k, lang: img_tag(cat_key(k), lang, 260, img_cat(k), 2, ' class="sq" loading="lazy" decoding="async"')
HERO_MONDE = lambda wid, lang: img_tag(f'assets/worlds/{wid}.jpg', lang, 960, img_world(wid), 2, ' class="hero" fetchpriority="high" decoding="async"')
VIG_MONDE = lambda k, lang: img_tag(f'assets/worlds/{k}.jpg', lang, 480, img_world(k), 2, ' loading="lazy" decoding="async"')


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
            # pages thématiques liées à cette catégorie (sons pour dormir, rêve lucide, chakras, gratitude)
            TH = charge('themes', lang) or {}
            lt = ''.join(f'<li><a href="/{lang}/{TH[k]["slug"]}.html">{E(TH[k]["h1"])}</a></li>' for k in THEMES if k in TH and cid in THEME_CATS.get(k, []))
            if lt: read += f'<h2>{E(XL[lang]["themes"])}</h2><ul class="ap-links">{lt}</ul>'
            sib = [k for k in cats if k != cid and CAT_GROUP.get(k) == g][:3] or [k for k in cats if k != cid][:3]
            others = ''.join(f'<li><a href="{u(lang, "med", p["categories"][k]["slug"])}">{E(cats[k]["name"][lang])}</a></li>' for k in sib)
            bc = [(t['home'], f'/{lang}/'), (t['med'], u(lang, 'med')), (cats[cid]['name'][lang], None)]
            body = (crumbs(lang, bc) + f'<article><div class="ap-hero">{HERO_CAT(cid, lang)}'
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
        cards = ''.join(f'<li><a href="{p["categories"][k]["slug"]}.html">{VIG_CAT(k, lang)}'
                        f'<b>{E(c["name"][lang])}</b><span>{c["count"]} {E(t["sessions"])} · {c["min"]}–{c["max"]} {E(t["min"])}</span></a></li>' for k, c in cats.items())
        bc = [(t['home'], f'/{lang}/'), (t['med'], None)]
        body = (crumbs(lang, bc) + f'<h1>{E(s["h1"])}</h1><p class="lead">{E(s["intro"])}</p><ul class="ap-grid">{cards}</ul>'
                + f'<ul class="ap-links"><li><a href="{u(lang, "world")}">{E(t["worlds"])}</a></li><li><a href="/{lang}/{p["teams"]["slug"]}.html">{E(p["teams"]["h1"])}</a></li></ul>' + cta(lang))
        ld = ld_tag({'@context': 'https://schema.org', '@graph': [{'@type': 'CollectionPage', 'name': s['h1'], 'description': s['desc'], 'url': bb.BASE + path, 'inLanguage': lang}, bc_ld(bb, bc)]})
        _write(path + 'index.html', page(bb, lang, s['seo'], s['desc'], path, alts, img_cat('calm'), ld, body, s['h1']))
        written.append((path, alts))
        # --- pages mondes ---
        ws = cat['worlds']
        MX = charge('mondes', lang) or {}
        for wid, w in ws.items():
            if wid not in p['worlds']: continue
            x = MX.get(wid) or {}
            xl = XL[lang]
            extra = ((f'<h2>{E(xl["qui"])}</h2><p class="intro">{E(x["pour_qui"])}</p>' if x.get('pour_qui') else '')
                     + (f'<h2>{E(xl["deroule"])}</h2><p class="intro">{E(x["deroule"])}</p>' if x.get('deroule') else '')
                     + (f'<h2>{E(xl["conseils"])}</h2><ul>' + ''.join(f'<li>{E(c)}</li>' for c in x['conseils']) + '</ul>' if x.get('conseils') else ''))
            wfaq = [tuple(q) for q in x.get('faq', [])]
            s = p['worlds'][wid]; path = u(lang, 'world', s['slug'])
            alts = {x: u(x, 'world', P[x]['worlds'][wid]['slug']) for x in P if wid in P[x]['worlds']}
            dl = ''.join(f'<dt>{E(t[k])}</dt><dd>{E(w[f][lang])}</dd>' for k, f in (('goal', 'objective'), ('inter', 'interactions'), ('sound', 'soundDesign'), ('visual', 'visualAtmosphere')) if w.get(f, {}).get(lang))
            dl += f'<dt>{E(t["duration"])}</dt><dd>{w["minutes"][lang]} {E(t["min"])}</dd><dt>{E(t["moods"])}</dt><dd>{E(", ".join(w["moods"][lang]))}</dd>'
            others = ''.join(f'<li><a href="{u(lang, "world", p["worlds"][k]["slug"])}">{E(ws[k]["name"][lang])}</a></li>' for k in list(ws)[:0] or [k for k in ws if k != wid][:6] if k in p['worlds'])
            bc = [(t['home'], f'/{lang}/'), (t['worlds'], u(lang, 'world')), (w['name'][lang], None)]
            body = (crumbs(lang, bc) + f'<article class="ap-world"><h1>{E(s["h1"])}</h1><p class="lead">{E(w["tagline"][lang])}</p>'
                    f'{HERO_MONDE(wid, lang)}'
                    f'<p class="intro">{E(w["description"][lang])}</p><h2>{E(t["scene"])}</h2><p class="ap-scene">{E(w["openingScene"][lang])}</p>'
                    f'<dl class="ap-dl">{dl}</dl>' + extra + f'<h2>{E(t["end"])}</h2><p class="intro">{E(w["endingNote"][lang])}</p>' + cta(lang)
                    + faq_html(lang, wfaq) + f'<h2>{E(t["otherw"])}</h2><ul class="ap-links">{others}</ul></article>')
            ld = ld_tag({'@context': 'https://schema.org', '@graph': [{'@type': 'WebPage', 'name': s['h1'], 'description': s['desc'], 'url': bb.BASE + path, 'inLanguage': lang,
                         'primaryImageOfPage': bb.BASE + img_world(wid)}, bc_ld(bb, bc)]
                         + ([{'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': r}} for q, r in wfaq]}] if wfaq else [])})
            _write(path, page(bb, lang, s['seo'], s['desc'], path, alts, img_world(wid), ld, body, w['name'][lang]))
            written.append((path, alts))
        # --- index des mondes ---
        s = p['worlds_index']; path = u(lang, 'world'); alts = {x: u(x, 'world') for x in P}
        cards = ''.join(f'<li><a href="{p["worlds"][k]["slug"]}.html">{VIG_MONDE(k, lang)}'
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
var st=document.getElementById('f-st'),d=new FormData(f),co=d.get('company')||'',sujet='Méditation en entreprise'+(co?' — '+co:'');
if(d.get('website')){st.textContent=f.dataset.ok;f.reset();return}
var o={name:d.get('name')||'',company:co,email:d.get('email'),message:d.get('message'),topic:sujet,lang:'fr',page:location.href,_subject:'MeditaDream — '+sujet,_template:'table',_captcha:'false',_replyto:d.get('email')};
fetch('https://formsubmit.co/ajax/edouard@meditadream.com',{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(o)})
.then(function(r){return r.json()}).then(function(j){var ok=j&&String(j.success)==='true';st.textContent=ok?f.dataset.ok:f.dataset.err;if(ok){f.reset();if(window.gtag)gtag('event','generate_lead',{form_id:'entreprise'})}})
.catch(function(){st.textContent=f.dataset.err})});})();</script>""")
        bc = [(t['home'], f'/{lang}/'), (s['h1'], None)]
        villes = '<p class="more"><a href="formation-meditation/">Formations à la méditation par ville : France, Belgique, Suisse, Luxembourg →</a></p>' if lang == 'fr' and os.path.exists(f'{T}/formations_fr.json') else ''
        body = crumbs(lang, bc) + f'<article><h1>{E(s["h1"])}</h1><p class="lead">{E(s["desc"])}</p>{secs}{form}' + cta(lang) + faq_html(lang, s.get('faq')) + villes + '</article>'
        ld = ld_tag({'@context': 'https://schema.org', '@graph': [{'@type': 'WebPage', 'name': s['h1'], 'description': s['desc'], 'url': bb.BASE + path, 'inLanguage': lang}, bc_ld(bb, bc)]
                     + ([{'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': r}} for q, r in s['faq']]}] if s.get('faq') else [])})
        _write(path, page(bb, lang, s['seo'], s['desc'], path, alts, img_cat('calm'), ld, body, s['h1']))
        written.append((path, alts))
    written += themes(bb, cat, P)
    import sys, formation_pages  # formations par ville (fr), liées depuis le pied de page
    written += formation_pages.build(bb, sys.modules[__name__])
    json.dump(_LM, open(LASTMOD_F, 'w', encoding='utf-8'), indent=0, sort_keys=True)
    return written


def theme_path(lang, key):
    d = charge('themes', lang)
    return f'/{lang}/{d[key]["slug"]}.html' if d and key in d else None


def themes(bb, cat, P):
    """Pages thématiques par langue (sons pour dormir, rêve lucide, chakras, journal de gratitude)."""
    written = []
    meds = {m['id']: (cid, m) for cid, c in cat['categories'].items() for m in c['meds']}
    I18N_SONS = json.load(open(os.path.join(T, 'sons_app.json'), encoding='utf-8')) if os.path.exists(os.path.join(T, 'sons_app.json')) else {}
    for lang in P:
        D = charge('themes', lang)
        if not D: continue
        t = L[lang]; xl = XL[lang]; p = P[lang]
        for key in THEMES:
            if key not in D: continue
            s = D[key]; path = f'/{lang}/{s["slug"]}.html'
            alts = {x: theme_path(x, key) for x in P if theme_path(x, key)}
            ik = THEME_IMG[key]
            p_img, alt_img, titre_img = media(ik, lang, 960 if 'worlds' in ik else 640)
            src = p_img or (img_world(ik.split('/')[-1][:-4]) if 'worlds' in ik else img_cat(ik.split('catart-')[-1][:-4]))
            hero = f'<img class="hero" src="{rel(src, 1)}" alt="{E(alt_img)}" title="{E(titre_img)}"{dims(src)} fetchpriority="high" decoding="async">'
            secs = ''.join(f'<h2>{E(x["h2"])}</h2>' + ''.join(f'<p>{E(q)}</p>' for q in x.get('p', []))
                           + (('<ul>' + ''.join(f'<li>{E(b)}</li>' for b in x['ul']) + '</ul>') if x.get('ul') else '') for x in s['sections'])
            bloc = ''
            items = []
            if key == 'sons' and I18N_SONS:
                bloc = f'<h2>{E(xl["sons"])}</h2>' + ''.join(
                    f'<h3>{E(xl["fam"][fam])}</h3><div class="ap-sons">' + ''.join(
                        f'<div><b>{E(I18N_SONS[i]["nom"][lang])}</b><span>{E(I18N_SONS[i]["note"][lang])}</span></div>' for i in ids) + '</div>'
                    for fam, ids in SONS) + f'<p class="intro">{E(xl["minuteur"])}</p>'
            elif key in THEME_SEANCES:
                ms = [meds[i] for i in THEME_SEANCES[key] if i in meds]
                items = [m['title'][lang] for _, m in ms]
                bloc = (f'<h2>{E(xl["seances"])}</h2><ol class="ap-list">' + ''.join(
                    f'<li><h3>{E(m["title"][lang])}</h3><div class="d">{m["dur"]} {E(t["min"])} · {E(t["level"].get(m["level"], m["level"]))} · '
                    f'<a href="{u(lang, "med", p["categories"][cid]["slug"])}">{E(cat["categories"][cid]["name"][lang])}</a></div><p>{E(m["desc"][lang])}</p></li>'
                    for cid, m in ms) + '</ol>')
            liens = ''.join(f'<li><a href="{u(lang, "med", p["categories"][c]["slug"])}">{E(cat["categories"][c]["name"][lang])}</a></li>' for c in THEME_CATS.get(key, []))
            liens += ''.join(f'<li><a href="{theme_path(lang, k)}">{E(D[k]["h1"])}</a></li>' for k in THEMES if k != key and k in D)
            bc = [(t['home'], f'/{lang}/'), (s['h1'], None)]
            faq = [tuple(q) for q in s.get('faq', [])]
            body = (crumbs(lang, bc) + f'<article class="ap-theme"><h1>{E(s["h1"])}</h1><p class="lead">{E(s["lead"])}</p>{hero}{secs}{bloc}'
                    + cta(lang) + faq_html(lang, faq) + f'<h2>{E(xl["themes"])}</h2><ul class="ap-links">{liens}</ul></article>')
            graph = [{'@type': 'WebPage', 'name': s['h1'], 'description': s['desc'], 'url': bb.BASE + path, 'inLanguage': lang,
                      'primaryImageOfPage': bb.BASE + src, 'isPartOf': {'@type': 'WebSite', 'name': 'MeditaDream', 'url': bb.BASE + '/'},
                      'about': {'@type': 'MobileApplication', 'name': 'MeditaDream', 'applicationCategory': 'LifestyleApplication',
                                'operatingSystem': 'iOS, Android', 'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR'}}},
                     bc_ld(bb, bc)]
            if items:
                graph.append({'@type': 'ItemList', 'name': xl['seances'], 'numberOfItems': len(items),
                              'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n} for i, n in enumerate(items)]})
            if faq:
                graph.append({'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': r}} for q, r in faq]})
            ld = ld_tag({'@context': 'https://schema.org', '@graph': graph})
            html_ = page(bb, lang, s['seo'], s['desc'], path, alts, src, ld, body, alt_img or s['h1'])
            _write(path, html_)
            written.append((path, alts))
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
