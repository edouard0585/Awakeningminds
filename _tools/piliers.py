#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pages piliers (23-10) : un guide complet par grand thème de l'application, dans chaque langue.

  mondes         → /{lang}/{mondes|worlds|mundos}/          (remplace l'ancien index des mondes)
  astral, qigong, transe, visualisation, guides, emotions → /{lang}/<slug>.html
  reve, chakras  → /{lang}/<slug>.html (mêmes adresses que les anciennes pages thématiques, refaites ici)

Textes : _tools/piliers_{fr,en,es}.json (écrits pour chaque langue, mots-clés Keyword Planner du 23-10).
Séances, catégories, mondes et articles du blog : lus dans les données (jamais recopiés à la main). Le bas de
chaque page liste les articles du blog sur le thème, publiés (avec aperçu) et à paraître : la page est
régénérée à chaque publication, car blog_build.build() → app_pages.build() → piliers.build().
Appelé par app_pages.build(). Stdlib uniquement (Python 3.9).
"""
import json, os, re, html, math
from datetime import date, datetime, timedelta

E = html.escape
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(ROOT, '_tools')
LANGS = ['fr', 'en', 'es']
ORDRE = ['mondes', 'astral', 'chakras', 'qigong', 'reve', 'transe', 'visualisation', 'guides', 'emotions']

# Configuration par thème : image d'en-tête, couleur d'accent, catégories et séances de l'app, mondes liés,
# articles du blog (thèmes du blog, série du lundi, motif sur l'adresse française de l'article).
CFG = {
 'mondes': dict(hero='skyIsland', acc='212,175,106', cats=['miniAdventures', 'sacred', 'visualisation'],
                seances=[], worlds=[], groups=['lieux'], series=['symboles', 'interactives'], rx=r'mondes-interieurs|lieux-sacres', ex=r'bonheur'),
 'astral': dict(hero='cosmicTemple', acc='142,167,255', cats=['astralJourneys', 'astralMicroDetach', 'cosmic'],
                seances=['microd01', 'astr01', 'cons03', 'astr04', 'cosmiq02'], worlds=['cosmicTemple', 'galaxy', 'celestialLibrary', 'mirrorDimension'],
                groups=[], series=['astral', 'emc'], rx=r'astral|projection|sortie-de-corps|hors-du-corps|decorporation'),
 'chakras': dict(hero='treeOfConsciousness', acc='190,140,255', cats=['calm', 'thirdEye', 'qigong'],
                 seances=['chakra01', 'chakra02', 'cons02', 'corpsc01', '3emeoe02'], worlds=['treeOfConsciousness', 'crystalCave', 'earthCore'],
                 groups=[], series=['chakras'], rx=r'chakra|kundalini|troisieme-oeil|aura-'),
 'qigong': dict(hero='himalayanMonastery', acc='127,200,169', cats=['qigong', 'calm'],
                seances=['chi01', 'chi02', 'chi03', 'chi04', 'corps01'], worlds=['himalayanMonastery', 'zenGarden', 'treeOfConsciousness'],
                groups=[], series=[], rx=r'qi-gong|qigong|chi-qi|s-ancrer'),
 'reve': dict(hero='mushroomForest', acc='180,156,255', cats=['calm', 'trance'],
              seances=['reves01', 'reves02', 'corpsc03', 'consci02', 'consci05'], worlds=['mushroomForest', 'skyIsland', 'galaxy'],
              groups=[], series=['reve'], rx=r'reve|paralysie|hypnagog|sommeil|nsdr|yoga-nidra'),
 'transe': dict(hero='wolfForest', acc='224,135,79', cats=['shamanic', 'tranceTechniques', 'trance'],
                seances=['shaman01', 'shaman04', 'trance01', 'trance02', 'trance03'], worlds=['wolfForest', 'jungleRuins', 'earthCore'],
                groups=['chamanisme', 'transe'], series=['emc'], rx=r'chaman|transe|tambour|animal-de-pouvoir'),
 'visualisation': dict(hero='galaxy', acc='111,211,224', cats=['visualisation', 'thirdEye', 'miniAdventures'],
                       seances=['visual02', 'visual03', 'visual04', 'visual05', 'visual07'], worlds=['galaxy', 'atlantis', 'antiqueTemple'],
                       groups=[], series=['symboles'], rx=r'visualis|imager|symbole|creativite|sport|mondes-interieurs'),
 'guides': dict(hero='antiqueTemple', acc='242,210,122', cats=['guides', 'higherKnowledge', 'shamanic'],
                seances=['guides04', 'guides03', 'guides02', 'guides05', 'savoir01'], worlds=['antiqueTemple', 'wolfForest', 'celestialLibrary'],
                groups=[], series=[], rx=r'guides?-spirit|(^|-)anges?(-|$)|esprits-allies|signes-de|synchronic|akashi|animal-de-pouvoir'),
 'emotions': dict(hero='zenGarden', acc='242,155,178', cats=['emotionalGrowth', 'shadow', 'fourMin'],
                  seances=['croiss01', 'croiss02', 'croiss03', 'ombre05', '4minut06'], worlds=['zenGarden', 'desertOasis', 'atlantis'],
                  groups=['psy'], series=['ombre', 'bienveillance'], rx=r'emotion|ombre|enfant-interieur|critique-interieur|peurs|pleurer|rumin|gratitude|tenir-un-journal|confiance-en-soi'),
}
# Séances qui relèvent vraiment du thème (catégories entières ou séances), pour le nombre affiché dans l'en-tête
CORE = {'astral': ['astralJourneys', 'astralMicroDetach'], 'chakras': ['chakra01', 'chakra02', 'cons02', 'corpsc01', 'thirdEye'],
        'qigong': ['qigong'], 'reve': ['reves01', 'reves02', 'corpsc03', 'consci02', 'consci05'],
        'transe': ['shamanic', 'tranceTechniques', 'trance'], 'visualisation': ['visualisation'], 'guides': ['guides'],
        'emotions': ['emotionalGrowth', 'shadow']}
# Thème du blog (blog_hubs.ORDER) → pages piliers, pour les liens « Pratiquer avec l'application » des articles
GROUP_PILIERS = {'astral': ['astral', 'reve'], 'energie': ['chakras', 'qigong'], 'sommeil': ['reve'], 'chamanisme': ['transe', 'guides'],
                 'transe': ['transe', 'astral'], 'psy': ['emotions'], 'lieux': ['mondes', 'visualisation'], 'vie': ['emotions'], 'bases': ['mondes']}
WIKI = {   # adresses vérifiées le 24-10 (HEAD 200)
 'mondes': {'fr': 'https://fr.wikipedia.org/wiki/M%C3%A9ditation', 'en': 'https://en.wikipedia.org/wiki/Guided_meditation', 'es': 'https://es.wikipedia.org/wiki/Meditaci%C3%B3n'},
 'astral': {'fr': 'https://fr.wikipedia.org/wiki/Voyage_astral', 'en': 'https://en.wikipedia.org/wiki/Astral_projection', 'es': 'https://es.wikipedia.org/wiki/Viaje_astral'},
 'chakras': {'fr': 'https://fr.wikipedia.org/wiki/Chakra', 'en': 'https://en.wikipedia.org/wiki/Chakra', 'es': 'https://es.wikipedia.org/wiki/Chakra'},
 'qigong': {'fr': 'https://fr.wikipedia.org/wiki/Qi_gong', 'en': 'https://en.wikipedia.org/wiki/Qigong', 'es': 'https://es.wikipedia.org/wiki/Qigong'},
 'reve': {'fr': 'https://fr.wikipedia.org/wiki/R%C3%AAve_lucide', 'en': 'https://en.wikipedia.org/wiki/Lucid_dream', 'es': 'https://es.wikipedia.org/wiki/Sue%C3%B1o_l%C3%BAcido'},
 'transe': {'fr': 'https://fr.wikipedia.org/wiki/Chamanisme', 'en': 'https://en.wikipedia.org/wiki/Shamanism', 'es': 'https://es.wikipedia.org/wiki/Chamanismo'},
 'visualisation': {'fr': 'https://fr.wikipedia.org/wiki/Imagerie_mentale', 'en': 'https://en.wikipedia.org/wiki/Guided_imagery', 'es': 'https://es.wikipedia.org/wiki/Visualizaci%C3%B3n_creativa'},
 'guides': {'en': 'https://en.wikipedia.org/wiki/Spirit_guide', 'es': 'https://es.wikipedia.org/wiki/Gu%C3%ADa_espiritual'},
 'emotions': {'fr': 'https://fr.wikipedia.org/wiki/R%C3%A9gulation_%C3%A9motionnelle', 'en': 'https://en.wikipedia.org/wiki/Emotional_self-regulation', 'es': 'https://es.wikipedia.org/wiki/Inteligencia_emocional'},
}
# Couleurs : chakras de la racine à la couronne ; roue de Plutchik (joie, confiance, peur, surprise, tristesse, dégoût, colère, anticipation)
CHAKRA_C = ['#E0524F', '#F08A3C', '#F2C94C', '#5DBB7A', '#4FA3E0', '#5B5FD6', '#A66BE0']
PLUTCHIK = ['#F6D55C', '#9BD18B', '#3E9E6A', '#55B6C9', '#4F7CC9', '#9A6FC1', '#D9534F', '#F0A04B']
# Parcours astral de l'app (écran « Transe & Voyage astral », onglet Astral) — app/astral/index.tsx
ASTRAL_ETAPES = [('astralMicroDetach', ['microd01', 'microd02', 'microd03', 'microd04', 'microd05']),
                 ('astralJourneys', ['astr01', 'astr02', 'astr03', 'cons03', 'cons04', 'cons05']),
                 ('astralJourneys', ['astr04', 'astr05', 'astr06', 'astr07', 'astr08'])]
SENS = ['visual02', 'visual03', 'visual04', 'visual05']   # vue, toucher, ouïe, trois sens réunis
# Articles généraux de la série du lundi : jamais rangés dans un thème par le motif de leur adresse
GENERAL = {'intro', 'posture', 'respiration', 'scan', 'pensees', 'pleineconscience', 'cinqminutes', 'matin', 'programme',
           'techniques', 'quotidien', 'science', 'histoire', 'interactives', 'marche', 'bienveillance', 'dormir'}

LBL = {
 'fr': dict(short={'mondes': 'Mondes immersifs', 'astral': 'Voyage astral', 'chakras': 'Chakras', 'qigong': 'Qi gong', 'reve': 'Rêve lucide',
                   'transe': 'Transe chamanique', 'visualisation': 'Visualisation', 'guides': 'Guides spirituels', 'emotions': 'Croissance émotionnelle'},
            guides='Guides', toc='Sommaire', defl='En bref', read_def='Lire la définition', practice='Pratiquer dans l’application',
            seances='séances', seance='séance', min='min', free='Gratuit', offline='Hors ligne', worlds_n='mondes',
            app_cats='Les catégories', app_seances='Les séances à essayer d’abord', app_feat='Les outils de l’application', app_worlds='Les mondes immersifs liés',
            see_cat='Voir la catégorie', faq='Questions fréquentes', blog_pub='Publié le', blog_soon='À paraître', blog_soon_d='À paraître le',
            blog_soon_s='Prochainement', read='Lire l’article', explore='Explorer les autres thèmes', range='{a} à {b} min',
            plutchik='de {a} à {b}', night='Une nuit de sommeil', axis='Axe du monde', step='Étape', listen='Écouter dans l’application',
            gallery_all='Les 17 mondes'),
 'en': dict(short={'mondes': 'Immersive worlds', 'astral': 'Astral projection', 'chakras': 'Chakras', 'qigong': 'Qigong', 'reve': 'Lucid dreaming',
                   'transe': 'Shamanic trance', 'visualisation': 'Visualization', 'guides': 'Spirit guides', 'emotions': 'Emotional growth'},
            guides='Guides', toc='On this page', defl='In short', read_def='Read the definition', practice='Practice in the app',
            seances='sessions', seance='session', min='min', free='Free', offline='Offline', worlds_n='worlds',
            app_cats='Categories', app_seances='Sessions to try first', app_feat='Tools in the app', app_worlds='Related immersive worlds',
            see_cat='See the category', faq='Frequently asked questions', blog_pub='Published', blog_soon='Coming soon', blog_soon_d='Coming',
            blog_soon_s='Soon', read='Read the article', explore='Explore the other themes', range='{a} to {b} min',
            plutchik='from {a} to {b}', night='One night of sleep', axis='World axis', step='Step', listen='Listen in the app',
            gallery_all='All 17 worlds'),
 'es': dict(short={'mondes': 'Mundos inmersivos', 'astral': 'Viaje astral', 'chakras': 'Chakras', 'qigong': 'Qigong', 'reve': 'Sueños lúcidos',
                   'transe': 'Trance chamánico', 'visualisation': 'Visualización', 'guides': 'Guías espirituales', 'emotions': 'Crecimiento emocional'},
            guides='Guías', toc='En esta página', defl='En resumen', read_def='Leer la definición', practice='Practicar en la app',
            seances='sesiones', seance='sesión', min='min', free='Gratis', offline='Sin conexión', worlds_n='mundos',
            app_cats='Las categorías', app_seances='Sesiones para empezar', app_feat='Las herramientas de la app', app_worlds='Mundos inmersivos relacionados',
            see_cat='Ver la categoría', faq='Preguntas frecuentes', blog_pub='Publicado el', blog_soon='Próximamente', blog_soon_d='Se publica el',
            blog_soon_s='Próximamente', read='Leer el artículo', explore='Explorar los otros temas', range='{a} a {b} min',
            plutchik='de {a} a {b}', night='Una noche de sueño', axis='Eje del mundo', step='Paso', listen='Escuchar en la app',
            gallery_all='Los 17 mundos'),
}


def typo(o):
    """Typographie française : espace insécable avant « : » et fine insécable avant « ; ! ? », dans les guillemets."""
    if isinstance(o, str):
        o = re.sub(r' ([:»])', '\u00a0\\1', o)
        o = re.sub(r' ([;!?])', '\u202f\\1', o)
        return o.replace('« ', '«\u00a0').replace("'", '’')
    if isinstance(o, list): return [typo(x) for x in o]
    if isinstance(o, dict): return {k: (v if k in ('slug', 'id', 'kw') else typo(v)) for k, v in o.items()}
    return o


_CACHE = {}


def charge(lang):
    f = os.path.join(T, f'piliers_{lang}.json')
    if not os.path.exists(f): return {}
    m = os.path.getmtime(f)
    if _CACHE.get(lang, (None,))[0] != m:
        d = json.load(open(f, encoding='utf-8'))
        _CACHE[lang] = (m, typo(d) if lang == 'fr' else d)
    return _CACHE[lang][1]


def path(ap, lang, key, D=None):
    """Adresse publique de la page pilier (None si la page n'existe pas dans cette langue)."""
    D = D if D is not None else charge(lang)
    if key not in D: return None
    if key == 'mondes': return ap.u(lang, 'world')
    return f'/{lang}/{D[key]["slug"]}.html'


def depth(key):
    return 2 if key == 'mondes' else 1


# ---------- texte enrichi : [ancre](/chemin) et **gras** ----------
LIEN = re.compile(r'\[([^\]]+)\]\((/[^)\s]+)\)')
GRAS = re.compile(r'\*\*(.+?)\*\*')


def rich(txt):
    out, pos = [], 0
    for m in LIEN.finditer(txt):
        out.append(GRAS.sub(r'<strong>\1</strong>', E(txt[pos:m.start()])))
        ancre = GRAS.sub(r'<strong>\1</strong>', E(m.group(1)))
        out.append(f'<a href="{E(m.group(2))}">{ancre}</a>')
        pos = m.end()
    out.append(GRAS.sub(r'<strong>\1</strong>', E(txt[pos:])))
    return ''.join(out)


def plain(txt):
    return GRAS.sub(r'\1', LIEN.sub(r'\1', txt))


# ---------- articles du blog liés au thème ----------
def paris_today():
    try:
        import blog_fr
        return blog_fr.paris_now().date()
    except Exception:
        return date.today()


def articles(bb, lang, key):
    """(publiés, à paraître) : listes de dict(slug, title, desc, img, alt, date, order) pour cette langue."""
    import blog_fr, blog_hubs
    c = CFG[key]; rx = re.compile(c['rx'])
    today = paris_today().isoformat()
    pub, soon = [], []
    # série trilingue du lundi (une par semaine, dans l'ordre du fichier)
    serie = bb.load()
    # la série du lundi publie le prochain article non publié chaque lundi (publish_next.py) : date prévue = n-ième lundi
    t0 = paris_today(); lundi = t0 + timedelta(days=(7 - t0.weekday()) % 7 or 7)
    rangs = {x['id']: i for i, x in enumerate(y for y in serie if not y.get('published'))}
    ex = re.compile(c['ex']) if c.get('ex') else None
    for a in serie:
        if a['id'] not in c['series'] and not rx.search(a['slug']['fr']): continue
        if ex and ex.search(a['slug']['fr']): continue
        if a['id'] in GENERAL and a['id'] not in c['series']:
            continue   # bases générales : jamais rangées par motif
        img = f"{bb.SCHEMA_FILES[a['image']][lang]}-{lang}.webp" if a.get('image') is not None and a['image'] in bb.SCHEMA_FILES else None
        alt = bb.HERO_ALTS.get((a.get('image'), lang), a['title'][lang]) if img else ''
        d = dict(slug=a['slug'][lang], title=a['title'][lang], desc=a['desc'][lang], img=img, alt=alt, date=a.get('published'), order='')
        if a.get('published'): pub.append(d)
        else:
            d['date'] = (lundi + timedelta(days=7 * rangs[a['id']])).isoformat(); d['order'] = '07:00'; soon.append(d)
    # articles du mercredi et du samedi (_queue/articles_fr.json), versions en/es quand elles existent
    for a0 in blog_fr.load():
        if not (a0.get('group') in c['groups'] or rx.search(a0['slug'])): continue
        if ex and ex.search(a0['slug']): continue
        if lang != 'fr' and not a0.get(lang): continue
        a = blog_fr.V(a0, lang)
        ph = a.get('photo') or a0.get('photo') or {}
        d = dict(slug=a['slug'], title=a.get('seo_title') or a['title'], desc=a['desc'], img=ph.get('src_s') or ph.get('src'),
                 alt=ph.get('alt', ''), date=a0.get('published'), order=a0.get('publish_at', ''))
        if a0.get('published') and a0['published'] <= today: pub.append(d)
        elif not a0.get('published'):
            d['date'] = (a0.get('publish_at') or '')[:10] or None; soon.append(d)
    pub.sort(key=lambda x: (x['date'] or '', x['order']), reverse=True)
    soon.sort(key=lambda x: (x['date'] or '9999', x['order']))
    return pub, soon


# ---------- figures propres à chaque thème ----------
def fig_chakras(lang, v):
    items = v.get('items', [])[:7]
    li = ''.join(f'<li style="--c:{CHAKRA_C[i]}"><span class="dot" aria-hidden="true"></span><div><b>{E(x["name"])}</b>'
                 f' <i lang="sa">{E(x["sk"])}</i><span>{E(x["place"])} · {E(x["theme"])}</span></div></li>'
                 for i, x in reversed(list(enumerate(items))))
    return (f'<figure class="pl-fig pl-chak"><figcaption class="ft">{E(v.get("title", ""))}</figcaption>'
            f'<ol>{li}</ol><p class="fc">{E(v.get("caption", ""))}</p></figure>')


def _secteur(cx, cy, r1, r2, a1, a2):
    p = lambda r, a: (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
    x1, y1 = p(r2, a1); x2, y2 = p(r2, a2); x3, y3 = p(r1, a2); x4, y4 = p(r1, a1)
    return (f'M{x1:.1f},{y1:.1f} A{r2},{r2} 0 0,1 {x2:.1f},{y2:.1f} L{x3:.1f},{y3:.1f} A{r1},{r1} 0 0,0 {x4:.1f},{y4:.1f} Z')


def _mix(hexc, t):
    """Mélange avec le blanc (t > 0) ou le noir (t < 0)."""
    r, g, b = int(hexc[1:3], 16), int(hexc[3:5], 16), int(hexc[5:7], 16)
    if t >= 0: r, g, b = [round(x + (255 - x) * t) for x in (r, g, b)]
    else: r, g, b = [round(x * (1 + t)) for x in (r, g, b)]
    return f'#{r:02x}{g:02x}{b:02x}'


def fig_emotions(lang, v):
    items = v.get('items', [])[:8]
    cx = cy = 210
    paths, texts = [], []
    for i, (base, doux, fort) in enumerate(items):
        a0 = -90 - 22.5 + i * 45 + 1.2; a1 = a0 + 45 - 2.4; am = (a0 + a1) / 2
        col = PLUTCHIK[i]
        paths.append(f'<path d="{_secteur(cx, cy, 34, 82, a0, a1)}" fill="{_mix(col, -0.28)}"/>')
        paths.append(f'<path d="{_secteur(cx, cy, 84, 142, a0, a1)}" fill="{col}"/>')
        paths.append(f'<path d="{_secteur(cx, cy, 144, 200, a0, a1)}" fill="{_mix(col, 0.5)}"/>')
        for r, txt, cls in ((113, base, 'b'), (172, doux, 'd')):
            x = cx + r * math.cos(math.radians(am)); y = cy + r * math.sin(math.radians(am))
            texts.append(f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}">{E(txt)}</text>')
    svg = (f'<svg viewBox="0 0 420 420" role="img" aria-label="{E(v.get("title", ""))}">'
           f'<circle cx="{cx}" cy="{cy}" r="32" fill="#151525"/>' + ''.join(paths) + ''.join(texts) + '</svg>')
    leg = ''.join(f'<li><span style="background:{PLUTCHIK[i]}"></span><b>{E(b)}</b> {E(LBL[lang]["plutchik"].format(a=d, b=f))}</li>'
                  for i, (b, d, f) in enumerate(items))
    return (f'<figure class="pl-fig pl-wheel"><figcaption class="ft">{E(v.get("title", ""))}</figcaption>{svg}'
            f'<ul class="lg">{leg}</ul><p class="fc">{E(v.get("caption", ""))}</p></figure>')


def fig_reve(lang, v):
    # 5 cycles de 90 min : sommeil lent puis sommeil paradoxal, qui s'allonge au fil de la nuit
    cycles = [(80, 10), (72, 18), (65, 25), (58, 32), (50, 40)]
    tot = 450
    seg = ''.join(f'<span class="n" style="width:{n / tot * 100:.2f}%"></span><span class="r" style="width:{r / tot * 100:.2f}%"></span>' for n, r in cycles)
    ticks = ''.join(f'<span style="left:{h * 60 / tot * 100:.2f}%">{h} {E(v.get("hour", "h"))}</span>' for h in range(0, 8))
    lbl = f'{v.get("deep", "")} / {v.get("rem", "")}'
    return (f'<figure class="pl-fig pl-night"><figcaption class="ft">{E(v.get("title", ""))}</figcaption>'
            f'<div class="bar" role="img" aria-label="{E(lbl)}">{seg}<i class="wb" style="left:{300 / tot * 100:.2f}%"><em>{E(v.get("wbtb", ""))}</em></i></div>'
            f'<div class="ticks">{ticks}</div>'
            f'<ul class="lg"><li><span class="n"></span>{E(v.get("deep", ""))}</li><li><span class="r"></span>{E(v.get("rem", ""))}</li></ul>'
            f'<p class="fc">{E(v.get("caption", ""))}</p></figure>')


def chip_seance(ap, lang, cat, P, mid):
    for cid, c in cat['categories'].items():
        for m in c['meds']:
            if m['id'] == mid:
                return (f'<a class="chip" href="{ap.u(lang, "med", P[lang]["categories"][cid]["slug"])}">'
                        f'{E(m["title"][lang])} · {m["dur"]} {E(LBL[lang]["min"])}</a>')
    return ''


def fig_transe(ap, lang, v, cat, P):
    lien = {0: 'trance03', 2: 'trance02'}
    tiers = ''.join(f'<li class="t{i}"><b>{E(n)}</b><p>{E(t)}</p>{chip_seance(ap, lang, cat, P, lien[i]) if i in lien else ""}</li>'
                    for i, (n, t) in enumerate(v.get('items', [])[:3]))
    return (f'<figure class="pl-fig pl-worlds3"><figcaption class="ft">{E(v.get("title", ""))}</figcaption>'
            f'<ol aria-label="{E(LBL[lang]["axis"])}">{tiers}</ol><p class="fc">{E(v.get("caption", ""))}</p></figure>')


def fig_astral(ap, lang, v, cat, P):
    meds = {m['id']: m for c in cat['categories'].values() for m in c['meds']}
    cols = ''
    for i, ((n, t), (cid, ids)) in enumerate(zip(v.get('steps', [])[:3], ASTRAL_ETAPES)):
        href = ap.u(lang, 'med', P[lang]['categories'][cid]['slug'])
        li = ''.join(f'<li><a href="{href}">{E(meds[x]["title"][lang])}</a><span>{meds[x]["dur"]} {E(LBL[lang]["min"])}</span></li>' for x in ids if x in meds)
        cols += f'<li><em>{E(LBL[lang]["step"])} {i + 1}</em><b>{E(n)}</b><p>{E(t)}</p><ul>{li}</ul></li>'
    return (f'<figure class="pl-fig pl-ladder"><figcaption class="ft">{E(v.get("title", ""))}</figcaption>'
            f'<ol>{cols}</ol><p class="fc">{E(v.get("caption", ""))}</p></figure>')


def fig_qigong(lang, v):
    glyph = ['身', '息', '心']
    li = ''.join(f'<li><span class="g" lang="zh" aria-hidden="true">{glyph[i]}</span><b>{E(n)}</b><i>{E(py)}</i><p>{E(t)}</p></li>'
                 for i, (n, py, t) in enumerate(v.get('items', [])[:3]))
    return (f'<figure class="pl-fig pl-three"><figcaption class="ft">{E(v.get("title", ""))}</figcaption>'
            f'<ol>{li}</ol><p class="fc">{E(v.get("caption", ""))}</p></figure>')


def fig_sens(ap, lang, v, cat, P):
    li = ''.join(f'<li><em>{i + 1}</em><b>{E(n)}</b><p>{E(t)}</p>{chip_seance(ap, lang, cat, P, SENS[i]) if i < len(SENS) else ""}</li>'
                 for i, (n, t) in enumerate(v.get('items', [])[:4]))
    return (f'<figure class="pl-fig pl-path"><figcaption class="ft">{E(v.get("title", ""))}</figcaption>'
            f'<ol>{li}</ol><p class="fc">{E(v.get("caption", ""))}</p></figure>')


def fig_guides(lang, v):
    li = ''.join(f'<li><span class="i" aria-hidden="true">{E(n[:1])}</span><b>{E(n)}</b><p>{E(t)}</p></li>' for n, t in v.get('items', [])[:6])
    return (f'<figure class="pl-fig pl-types"><figcaption class="ft">{E(v.get("title", ""))}</figcaption>'
            f'<ul>{li}</ul><p class="fc">{E(v.get("caption", ""))}</p></figure>')


def fig_mondes(ap, lang, v, cat, P):
    ws = cat['worlds']
    cards = ''.join(f'<li><a href="{ap.u(lang, "world", P[lang]["worlds"][k]["slug"])}">{ap.VIG_MONDE(k, lang)}'
                    f'<b>{E(w["name"][lang])}</b><span>{w["minutes"][lang]} {E(LBL[lang]["min"])} · {E(w["tagline"][lang])}</span></a></li>'
                    for k, w in ws.items() if k in P[lang]['worlds'])
    return (f'<figure class="pl-fig pl-gallery"><figcaption class="ft">{E(v.get("title", ""))}</figcaption>'
            f'<ul>{cards}</ul><p class="fc">{E(v.get("caption", ""))}</p></figure>')


def figure(ap, lang, key, v, cat, P):
    if not v: return ''
    if key == 'chakras': return fig_chakras(lang, v)
    if key == 'emotions': return fig_emotions(lang, v)
    if key == 'reve': return fig_reve(lang, v)
    if key == 'transe': return fig_transe(ap, lang, v, cat, P)
    if key == 'astral': return fig_astral(ap, lang, v, cat, P)
    if key == 'qigong': return fig_qigong(lang, v)
    if key == 'visualisation': return fig_sens(ap, lang, v, cat, P)
    if key == 'guides': return fig_guides(lang, v)
    if key == 'mondes': return fig_mondes(ap, lang, v, cat, P)
    return ''


# ---------- blocs de page ----------
def section_html(s):
    h = f'<section id="{E(s["id"])}"><h2>{E(s["h2"])}</h2>' + ''.join(f'<p>{rich(x)}</p>' for x in s.get('p', []))
    if s.get('ul'): h += '<ul>' + ''.join(f'<li>{rich(x)}</li>' for x in s['ul']) + '</ul>'
    if s.get('steps'): h += '<ol class="pl-steps">' + ''.join(f'<li><b>{E(a)}</b><p>{rich(b)}</p></li>' for a, b in s['steps']) + '</ol>'
    if s.get('table'):
        t = s['table']
        h += ('<div class="pl-table"><table><thead><tr>' + ''.join(f'<th scope="col">{E(c)}</th>' for c in t['head']) + '</tr></thead><tbody>'
              + ''.join('<tr>' + ''.join((f'<th scope="row">{rich(c)}</th>' if j == 0 else f'<td>{rich(c)}</td>') for j, c in enumerate(r)) + '</tr>' for r in t['rows'])
              + '</tbody></table></div>')
    if s.get('cards'): h += '<ul class="pl-cards">' + ''.join(f'<li><b>{E(a)}</b><p>{rich(b)}</p></li>' for a, b in s['cards']) + '</ul>'
    if s.get('tip'): h += f'<div class="tip">{rich(s["tip"])}</div>'
    if s.get('warn'): h += f'<div class="warn">{rich(s["warn"])}</div>'
    return h


def app_block(ap, lang, key, s, cat, P):
    c = CFG[key]; t = ap.L[lang]; lb = LBL[lang]; cats = cat['categories']
    a = s.get('app', {})
    h = f'<section id="app" class="pl-app"><h2>{E(a.get("h2", lb["practice"]))}</h2>' + ''.join(f'<p>{rich(x)}</p>' for x in a.get('intro', []))
    if c['cats']:
        h += f'<h3>{E(lb["app_cats"])}</h3><ul class="pl-catg">'
        for cid in c['cats']:
            x = cats[cid]; lv = ', '.join(t['level'][l] for l in x['levels'])
            h += (f'<li><a href="{ap.u(lang, "med", P[lang]["categories"][cid]["slug"])}">{ap.VIG_CAT(cid, lang).replace("../../", "../" * depth(key))}'
                  f'<span><b>{E(x["name"][lang])}</b><em>{x["count"]} {E(lb["seances"] if x["count"] > 1 else lb["seance"])} · '
                  f'{E(lb["range"].format(a=x["min"], b=x["max"]))} · {E(lv)}</em></span></a></li>')
        h += '</ul>'
    meds = {m['id']: (cid, m) for cid, x in cats.items() for m in x['meds']}
    sel = [meds[i] for i in c['seances'] if i in meds]
    if sel:
        h += f'<h3>{E(lb["app_seances"])}</h3><ol class="pl-med">' + ''.join(
            f'<li><a href="{ap.u(lang, "med", P[lang]["categories"][cid]["slug"])}"><b>{E(m["title"][lang])}</b>'
            f'<em>{m["dur"]} {E(lb["min"])} · {E(t["level"].get(m["level"], m["level"]))} · {E(cats[cid]["name"][lang])}</em>'
            f'<span>{E(m["desc"][lang])}</span></a></li>' for cid, m in sel) + '</ol>'
    if a.get('features'):
        h += f'<h3>{E(lb["app_feat"])}</h3><ul class="pl-feat">' + ''.join(f'<li><b>{E(n)}</b><p>{rich(d)}</p></li>' for n, d in a['features']) + '</ul>'
    ws = [w for w in c['worlds'] if w in cat['worlds'] and w in P[lang]['worlds']]
    if ws:
        h += f'<h3>{E(lb["app_worlds"])}</h3><ul class="pl-wstrip">' + ''.join(
            f'<li><a href="{ap.u(lang, "world", P[lang]["worlds"][k]["slug"])}">{ap.VIG_MONDE(k, lang).replace("../../", "../" * depth(key))}'
            f'<b>{E(cat["worlds"][k]["name"][lang])}</b><span>{cat["worlds"][k]["minutes"][lang]} {E(lb["min"])}</span></a></li>' for k in ws) + '</ul>'
    return h + '</section>'


def fmt(bb, d, lang):
    try: return bb.fmt_date(d, lang)
    except Exception: return d


def blog_block(ap, bb, lang, key, s):
    pub, soon = articles(bb, lang, key)
    if not pub and not soon: return ''
    lb = LBL[lang]; b = s.get('blog', {}); dp = '../' * depth(key)
    h = f'<section id="blog" class="pl-blog"><h2>{E(b.get("h2", "Blog"))}</h2>' + (f'<p>{rich(b["intro"])}</p>' if b.get('intro') else '')
    if pub:
        h += '<ul class="pl-posts">'
        for x in pub[:9]:
            img = ''
            if x['img']:
                src = f'/assets/blog/{x["img"]}'
                img = f'<img src="{dp}assets/blog/{x["img"]}" alt="{E(x["alt"] or x["title"])}" title="{E(x["title"][:70])}" loading="lazy" decoding="async"{ap.dims(src)}>'
            h += (f'<li><a href="/{lang}/blog/{x["slug"]}.html">{img or "<span class=noimg>✦</span>"}<span class="tx">'
                  f'<em>{E(lb["blog_pub"])} {E(fmt(bb, x["date"], lang))}</em><b>{E(x["title"])}</b><span>{E(x["desc"])}</span>'
                  f'<i>{E(lb["read"])} →</i></span></a></li>')
        h += '</ul>'
    if soon:
        h += f'<h3>{E(lb["blog_soon"])}</h3><ul class="pl-soon">' + ''.join(
            f'<li><em>{E(lb["blog_soon_d"] + " " + fmt(bb, x["date"], lang)) if x["date"] else E(lb["blog_soon_s"])}</em><b>{E(x["title"])}</b></li>'
            for x in soon[:5]) + '</ul>'
    return h + '</section>'


def explore_block(ap, lang, key, D, cat):
    lb = LBL[lang]; li = ''
    for k in ORDRE:
        if k == key or k not in D: continue
        hk = CFG[k]['hero']
        im = ap.img_tag(f'assets/worlds/{hk}.jpg', lang, 480, ap.img_world(hk), depth(key), ' loading="lazy" decoding="async"')
        li += (f'<li><a href="{path(ap, lang, k, D)}" style="--acc-rgb:{CFG[k]["acc"]}">{im}'
               f'<b>{E(lb["short"][k])}</b><span>{E(D[k].get("eyebrow", ""))}</span></a></li>')
    return f'<nav class="pl-explore" aria-label="{E(lb["explore"])}"><h2>{E(lb["explore"])}</h2><ul>{li}</ul></nav>'


def hero_img(ap, lang, key):
    k = f'assets/worlds/{CFG[key]["hero"]}.jpg'
    p480, p960 = ap.media(k, lang, 480)[0], ap.media(k, lang, 960)[0]
    dp = depth(key)
    ss = f' srcset="{ap.rel(p480, dp)} 480w, {ap.rel(p960, dp)} 960w" sizes="(max-width: 860px) 70vw, 380px"' if p480 and p960 else ''
    tag = ap.img_tag(k, lang, 960, ap.img_world(CFG[key]['hero']), dp, ss + ' fetchpriority="high" decoding="async"')
    src = p960 or ap.img_world(CFG[key]['hero'])
    return tag, src, ap.media(k, lang, 960)[1]


def facts(ap, lang, key, cat):
    lb = LBL[lang]; c = CFG[key]
    if key == 'mondes':
        ws = cat['worlds'].values(); mins = [w['minutes'][lang] for w in ws]
        out = [f'{len(cat["worlds"])} {lb["worlds_n"]}', lb['range'].format(a=min(mins), b=max(mins))]
    else:
        allm = {m['id']: m for x in cat['categories'].values() for m in x['meds']}
        ms = [m for x in CORE[key] for m in (cat['categories'][x]['meds'] if x in cat['categories'] else [allm[x]] if x in allm else [])]
        out = [f'{len(ms)} {lb["seances"]}', lb['range'].format(a=min(m['dur'] for m in ms), b=max(m['dur'] for m in ms))]
    return ''.join(f'<li>{E(x)}</li>' for x in out + [lb['free'], lb['offline']])


TOC_JS = ('<script>(function(){var l=document.querySelectorAll(".pl-toc a");if(!("IntersectionObserver"in window)||!l.length)return;'
          'var m={};l.forEach(function(a){m[a.getAttribute("href").slice(1)]=a});var o=new IntersectionObserver(function(es){es.forEach(function(e){'
          'if(e.isIntersecting){l.forEach(function(a){a.removeAttribute("aria-current")});var a=m[e.target.id];if(a)a.setAttribute("aria-current","true")}})},'
          '{rootMargin:"-30% 0px -60% 0px"});Object.keys(m).forEach(function(k){var s=document.getElementById(k);if(s)o.observe(s)})})();</script>')


def render(ap, bb, lang, key, D, cat, P):
    s = D[key]; lb = LBL[lang]; t = ap.L[lang]; c = CFG[key]
    me = path(ap, lang, key, D)
    alts = {x: path(ap, x, key, charge(x)) for x in LANGS if path(ap, x, key, charge(x))}
    tag, src, img_alt = hero_img(ap, lang, key)
    # ancres uniques : « definition », « app », « faq » et « blog » sont réservées aux blocs de la page
    vus = {'definition', 'app', 'faq', 'blog'}; sections = []
    for x in s.get('sections', []):
        i, n = x['id'], 2
        while i in vus: i = f'{x["id"]}-{n}'; n += 1
        vus.add(i); sections.append(dict(x, id=i))
    fig = figure(ap, lang, key, s.get('visual'), cat, P)
    corps = ''
    vu = False
    for x in sections:
        corps += section_html(x)
        if x.get('visual') and not vu: corps += fig; vu = True
        corps += '</section>'
    if not vu: corps = fig + corps
    toc = [('definition', lb['defl'])] + [(x['id'], x['h2']) for x in sections] + [('app', s.get('app', {}).get('h2', lb['practice']))]
    if s.get('faq'): toc.append(('faq', lb['faq']))
    blog = blog_block(ap, bb, lang, key, s)
    if blog: toc.append(('blog', s.get('blog', {}).get('h2', 'Blog')))
    bc = [(t['home'], f'/{lang}/'), (t['worlds'] if key == 'mondes' else lb['short'][key], None)]
    faq = [tuple(q) for q in s.get('faq', [])]
    body = (f'<div class="pl" style="--acc-rgb:{c["acc"]}">' + ap.crumbs(lang, bc)
            + f'<div class="pl-hero"><div class="pl-ht"><p class="pl-eye"><span aria-hidden="true">✦</span>{E(s.get("eyebrow", ""))}</p>'
            f'<h1>{E(s["h1"])}</h1><p class="pl-lead">{rich(s.get("lead", ""))}</p><ul class="pl-facts">{facts(ap, lang, key, cat)}</ul>'
            f'<p class="pl-cta"><a class="b1" href="/{lang}/#download">✦ {E(lb["practice"])}</a><a class="b2" href="#definition">{E(lb["read_def"])} ↓</a></p></div>'
            f'<figure class="pl-arch">{tag}</figure></div>'
            f'<div class="pl-body"><nav class="pl-toc" aria-label="{E(lb["toc"])}"><b>{E(lb["toc"])}</b><ol>'
            + ''.join(f'<li><a href="#{E(i)}">{E(n)}</a></li>' for i, n in toc) + '</ol></nav>'
            f'<article class="pl-art"><section id="definition" class="pl-def"><h2>{E(lb["defl"])}</h2><p>{rich(s.get("def", ""))}</p></section>'
            + corps + app_block(ap, lang, key, s, cat, P)
            + (ap.faq_html(lang, faq).replace('<section class="afaq">', '<section class="afaq" id="faq">') if faq else '')
            + blog + ap.cta(lang) + '</article></div>' + explore_block(ap, lang, key, D, cat) + '</div>' + TOC_JS)
    # données structurées
    url = bb.BASE + me
    about = {'@type': 'Thing', 'name': lb['short'][key]}
    if WIKI.get(key, {}).get(lang): about['sameAs'] = WIKI[key][lang]
    meds = {m['id']: m for x in cat['categories'].values() for m in x['meds']}
    graph = [{'@type': 'WebPage', '@id': url + '#page', 'name': s['h1'], 'headline': s['h1'], 'description': s['desc'], 'url': url, 'inLanguage': lang,
              'primaryImageOfPage': {'@type': 'ImageObject', 'url': bb.BASE + src, 'caption': img_alt or s['h1']}, 'about': about, 'keywords': s.get('kw', ''),
              'isPartOf': {'@type': 'WebSite', 'name': 'MeditaDream', 'url': bb.BASE + '/'},
              'mentions': {'@type': 'MobileApplication', 'name': 'MeditaDream', 'applicationCategory': 'LifestyleApplication',
                           'operatingSystem': 'iOS, Android', 'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR'}}},
             ap.bc_ld(bb, bc)]
    sel = [meds[i] for i in c['seances'] if i in meds]
    if key == 'mondes':
        graph.append({'@type': 'ItemList', 'name': lb['gallery_all'], 'numberOfItems': len(cat['worlds']), 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': w['name'][lang], 'url': bb.BASE + ap.u(lang, 'world', P[lang]['worlds'][k]['slug'])}
            for i, (k, w) in enumerate(cat['worlds'].items()) if k in P[lang]['worlds']]})
    elif sel:
        graph.append({'@type': 'ItemList', 'name': lb['app_seances'], 'numberOfItems': len(sel),
                      'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': m['title'][lang]} for i, m in enumerate(sel)]})
    if faq:
        graph.append({'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': plain(q), 'acceptedAnswer': {'@type': 'Answer', 'text': plain(r)}} for q, r in faq]})
    ld = ap.ld_tag({'@context': 'https://schema.org', '@graph': graph})
    h = bb.head(lang, s['seo'], s['desc'], lambda x: alts[x], me, src, ld, kw=s.get('kw', ''),
                img_alt=ap.og_alt(src, lang, s['h1']), og_type='article', langs=[x for x in LANGS if x in alts] if len(alts) < 3 else None)
    h = h.replace('</style>', ap.CSS + CSS + '</style>', 1)
    h += ap.header(lang, me, lambda x: alts.get(x, f'/{x}/'))
    foot = bb.footer_html(lang).replace('href="../"', f'href="/{lang}/"').replace('href="./"', f'href="/{lang}/blog/"')
    return h + '<main class="plm">' + body + '</main>' + foot + '</body></html>'


def build(ap, bb, cat, P):
    """Écrit les pages piliers ; renvoie [(chemin, {langue: chemin})] pour le plan du site."""
    written = []
    for lang in LANGS:
        D = charge(lang)
        if not D or lang not in P: continue
        for key in ORDRE:
            if key not in D: continue
            me = path(ap, lang, key, D)
            alts = {x: path(ap, x, key, charge(x)) for x in LANGS if path(ap, x, key, charge(x))}
            f = me + ('index.html' if me.endswith('/') else '')
            os.makedirs(os.path.dirname(f'{ROOT}{f}'), exist_ok=True)
            ap._write(f, render(ap, bb, lang, key, D, cat, P))
            written.append((me, alts))
    return written


def links_li(ap, lang, keys):
    """<li> vers les pages piliers demandées (pour les autres pages du site)."""
    D = charge(lang)
    return ''.join(f'<li><a href="{path(ap, lang, k, D)}">{E(LBL[lang]["short"][k])}</a></li>' for k in keys if k in D)


MENU_L = {'fr': ('Guides', 'Les guides complets'), 'en': ('Guides', 'In-depth guides'), 'es': ('Guías', 'Guías completas')}


def menu_html(lang, current=None, extra=()):
    """Entrée « Guides » du menu principal (24-10) : panneau des 9 pages piliers, même rendu sur tout le site.
    extra = [(libellé, adresse)] : liens de l'en-tête repris dans le panneau sur téléphone (l'entrée s'appelle alors « Menu »)."""
    D = charge(lang)
    if not D: return ''
    from types import SimpleNamespace
    W = SimpleNamespace(u=lambda l, kind, slug=None: f'/{l}/' + {'fr': 'mondes', 'en': 'worlds', 'es': 'mundos'}[l] + '/')
    li = ''
    for k in ORDRE:
        if k not in D: continue
        h = path(W, lang, k, D)
        cur = ' aria-current="page"' if current and current in (h, h + 'index.html') else ''
        li += f'<li><a href="{h}" style="--acc-rgb:{CFG[k]["acc"]}"{cur}><i aria-hidden="true"></i>{E(LBL[lang]["short"][k])}</a></li>'
    t, tt = MENU_L[lang]
    x = ''.join(f'<li><a href="{h}">{E(n)}</a></li>' for n, h in extra)
    lab = f'<span class="mnu-d">{E(t)}</span><span class="mnu-m">Menu</span>' if extra else E(t)
    return (f'<details class="mnu"><summary>{lab}</summary><div class="mnu-p"><div class="mnu-in">'
            + (f'<ul class="mnu-x">{x}</ul>' if x else '')
            + f'<b class="mnu-t">{E(tt)}</b><ul>{li}</ul></div></div></details>')


MENU_JS = ('<script>(function(){var d=document.querySelectorAll("details.mnu");if(!d.length)return;'
           'document.addEventListener("click",function(e){d.forEach(function(x){if(x.open&&!x.contains(e.target))x.open=false})});'
           'document.addEventListener("keydown",function(e){if(e.key==="Escape")d.forEach(function(x){x.open=false})})})();</script>')

MENU_CSS = """
details.mnu{border:0;border-radius:0;background:none;margin:0;padding:0}
details.mnu>summary{padding:0;font-family:'Cormorant Garamond',Georgia,serif;font-size:17px;color:var(--ink)}
@media(max-width:600px){details.mnu>summary{font-size:15px}}
.mnu summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:7px;white-space:nowrap}
.mnu summary::-webkit-details-marker{display:none}
.mnu summary::after{content:"";width:6px;height:6px;border-right:1.5px solid currentColor;border-bottom:1.5px solid currentColor;transform:translateY(-2px) rotate(45deg);opacity:.7;transition:transform .2s}
.mnu[open] summary{color:var(--gold)}.mnu[open] summary::after{transform:translateY(1px) rotate(-135deg)}
.mnu summary:focus-visible{outline:2px solid var(--gold);outline-offset:4px;border-radius:4px}
.mnu .mnu-p{position:absolute;left:0;right:0;top:100%;background:#0c0c18;border-bottom:1px solid var(--line);box-shadow:0 30px 60px -24px rgba(0,0,0,.85);padding:18px 20px 22px;z-index:60}
.mnu .mnu-in{max-width:1100px;margin:0 auto}
.mnu .mnu-t{display:block;font:600 11px/1 'Avenir Next','Segoe UI',system-ui,sans-serif;letter-spacing:.16em;text-transform:uppercase;color:var(--gold);margin:0 0 10px 10px}
.mnu .mnu-p ul{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:2px 18px}
.mnu .mnu-p a{display:flex;align-items:center;gap:11px;padding:9px 10px;border-radius:12px;color:var(--ink);text-decoration:none;font:500 19px/1.2 'Cormorant Garamond',Georgia,serif;white-space:normal}
.mnu .mnu-p a:hover,.mnu .mnu-p a:focus-visible{background:rgba(255,255,255,.05);color:#fff}
.mnu .mnu-p a[aria-current]{color:var(--gold)}
.mnu .mnu-p a i{flex:0 0 9px;width:9px;height:9px;border-radius:50%;background:rgb(var(--acc-rgb));box-shadow:0 0 10px rgba(var(--acc-rgb),.7)}
@media(max-width:600px){.mnu .mnu-p ul{grid-template-columns:1fr 1fr}.mnu .mnu-p a{font-size:17px;padding:8px}}
.mnu .mnu-m,.mnu .mnu-x{display:none}
@media(max-width:600px){header .hx{display:none}.mnu .mnu-d{display:none}.mnu .mnu-m{display:inline}
 .mnu .mnu-p ul.mnu-x{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 14px;padding:0 0 14px;border-bottom:1px solid var(--line)}
 .mnu .mnu-p .mnu-x a{font:600 14px/1 'Avenir Next',sans-serif;border:1px solid var(--line);border-radius:99px;padding:9px 14px}}
"""


def cat_piliers(cid):
    return [k for k in ORDRE if cid in CFG[k]['cats']]


CSS = """
main.plm{padding:22px 0 10px;overflow:clip}
.pl .crumbs{max-width:1180px;margin:0 auto 6px;padding:0 20px;flex-wrap:wrap}
.pl-hero{position:relative;max-width:1180px;margin:0 auto;padding:16px 20px 46px;display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:56px;align-items:center;isolation:isolate}
.pl-hero::before{content:"";position:absolute;inset:-80px -30vw -10px;z-index:-1;pointer-events:none;
 background:radial-gradient(42% 58% at 74% 46%,rgba(var(--acc-rgb),.22),rgba(10,10,20,0) 70%),radial-gradient(38% 52% at 12% 8%,rgba(122,96,180,.20),rgba(10,10,20,0) 70%)}
.pl-eye{font:600 12px/1.2 'Avenir Next','Segoe UI',system-ui,sans-serif;letter-spacing:.18em;text-transform:uppercase;color:var(--gold);display:flex;gap:10px;align-items:center;margin:0 0 16px}
.pl-eye span{color:rgb(var(--acc-rgb));font-size:14px;letter-spacing:0}
.pl-hero h1{font-size:clamp(36px,5.4vw,60px);line-height:1.05;letter-spacing:-.01em;margin:0 0 18px;text-wrap:balance;
 background:linear-gradient(180deg,#fff9ec 35%,#E9CF98);-webkit-background-clip:text;background-clip:text;color:transparent}
.pl-lead{font:400 18.5px/1.6 'Avenir Next','Segoe UI',system-ui,sans-serif;color:var(--muted);max-width:60ch;margin:0 0 20px}
.pl-lead a{color:var(--gold)}
.pl-facts{list-style:none;display:flex;flex-wrap:wrap;gap:8px;margin:0 0 24px;padding:0}
.pl-facts li{font:500 12.5px/1 'Avenir Next',sans-serif;color:var(--ink);border:1px solid rgba(var(--acc-rgb),.38);background:rgba(var(--acc-rgb),.07);border-radius:99px;padding:7px 12px;font-variant-numeric:tabular-nums}
.pl-cta{display:flex;flex-wrap:wrap;gap:12px;margin:0}
.pl-cta a{font:600 15px/1 'Avenir Next',sans-serif;text-decoration:none;border-radius:99px;padding:13px 22px}
.pl-cta .b1{background:linear-gradient(135deg,#D4AF6A,#b8934f);color:#161122}
.pl-cta .b2{border:1px solid var(--line);color:var(--ink)}
.pl-cta a:hover{filter:brightness(1.08)}.pl-cta .b2:hover{border-color:var(--gold);color:var(--gold)}
.pl-cta a:focus-visible,.pl a:focus-visible{outline:2px solid var(--gold);outline-offset:3px}
.pl-arch{position:relative;justify-self:center;width:min(100%,360px);margin:0}
.pl-arch img{display:block;width:100%;height:auto;aspect-ratio:2/3;object-fit:cover;border-radius:999px 999px 24px 24px;border:1px solid rgba(212,175,106,.38);box-shadow:0 40px 90px -40px rgba(0,0,0,.9),0 0 70px -20px rgba(var(--acc-rgb),.45);margin:0;background:#0e0c1c}
.pl-arch::after{content:"";position:absolute;inset:-13px;border:1px solid rgba(212,175,106,.20);border-radius:999px 999px 32px 32px;pointer-events:none}
@media(max-width:860px){.pl-hero{grid-template-columns:1fr;gap:30px;padding-bottom:30px}.pl-arch{width:min(62%,270px)}}
.pl-body{max-width:1180px;margin:0 auto;padding:0 20px;display:grid;grid-template-columns:220px minmax(0,720px);gap:60px;justify-content:center}
.pl-toc{position:sticky;top:84px;align-self:start;font-family:'Avenir Next','Segoe UI',system-ui,sans-serif;max-height:calc(100vh - 110px);overflow:auto;padding-right:6px}
.pl-toc b{display:block;font-size:11.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--gold);margin:4px 0 12px}
.pl-toc ol{list-style:none;padding:0;margin:0;border-left:1px solid var(--line)}
.pl-toc a{display:block;padding:6px 0 6px 14px;margin-left:-1px;border-left:1px solid transparent;color:var(--dim);text-decoration:none;font-size:13.5px;line-height:1.35}
.pl-toc a:hover{color:var(--ink)}
.pl-toc a[aria-current]{color:var(--ink);border-left-color:rgb(var(--acc-rgb))}
@media(max-width:1020px){.pl-body{grid-template-columns:minmax(0,720px);gap:0}
 .pl-toc{position:static;max-height:none;overflow:visible;margin:0 0 26px;padding:0}
 .pl-toc ol{display:flex;gap:8px;overflow-x:auto;border:0;padding:2px 0 8px;scrollbar-width:thin}
 .pl-toc li{flex:0 0 auto}.pl-toc a{border:1px solid var(--line);border-radius:99px;padding:6px 12px;margin:0;white-space:nowrap}}
.pl-art{min-width:0}
.pl-art section{scroll-margin-top:84px}
.pl-art h2{font-size:clamp(28px,3.6vw,36px);color:#fff7e8;font-weight:500;margin:52px 0 16px;line-height:1.15;text-wrap:balance}
.pl-art h2::before{content:"✦";display:block;font-size:13px;color:rgb(var(--acc-rgb));margin:0 0 10px;letter-spacing:0}
.pl-art h3{font-size:24px;color:#fff7e8;font-weight:500;margin:30px 0 12px}
.pl-art p{font-size:17px;line-height:1.75;color:var(--muted);margin:0 0 14px}
.pl-art ul,.pl-art ol{font-size:17px}
.pl-art strong{color:var(--ink);font-weight:600}
.pl-art a{color:var(--gold);text-underline-offset:3px}
.pl-def{border:1px solid rgba(212,175,106,.38);background:linear-gradient(180deg,rgba(212,175,106,.08),rgba(212,175,106,.02));border-radius:20px;padding:24px 28px;margin:0 0 10px}
.pl-def h2{font:600 11.5px/1 'Avenir Next',sans-serif;letter-spacing:.18em;text-transform:uppercase;color:var(--gold);margin:0 0 12px}
.pl-def h2::before{display:none}
.pl-def p{font-family:'Cormorant Garamond',Georgia,serif;font-size:clamp(20px,2.4vw,24px);line-height:1.45;color:#fff7e8;margin:0}
.pl-def strong{color:#fff;font-weight:600}
.pl-steps{list-style:none;counter-reset:st;padding:0;margin:18px 0 22px}
.pl-steps li{counter-increment:st;position:relative;padding:0 0 18px 52px;margin:0}
.pl-steps li::before{content:counter(st);position:absolute;left:0;top:0;width:34px;height:34px;border-radius:50%;border:1.5px solid rgb(var(--acc-rgb));color:var(--ink);display:flex;align-items:center;justify-content:center;font:500 15px/1 Georgia,serif}
.pl-steps li::after{content:"";position:absolute;left:17px;top:38px;bottom:4px;width:1px;background:var(--line)}
.pl-steps li:last-child::after{display:none}
.pl-steps b{display:block;font-family:'Cormorant Garamond',Georgia,serif;font-size:21px;font-weight:600;color:#fff7e8;margin:2px 0 4px}
.pl-steps p{margin:0}
.pl-table{overflow-x:auto;margin:18px 0 24px;border:1px solid var(--line);border-radius:16px}
.pl-table table{width:100%;border-collapse:collapse;font:15px/1.5 'Avenir Next','Segoe UI',system-ui,sans-serif;min-width:520px}
.pl-table th,.pl-table td{padding:12px 16px;text-align:left;vertical-align:top;border-top:1px solid var(--line);color:var(--muted)}
.pl-table thead th{border-top:0;color:var(--gold);font-weight:600;font-size:12.5px;letter-spacing:.08em;text-transform:uppercase;background:rgba(255,255,255,.02)}
.pl-table tbody th{color:var(--ink);font-weight:600}
.pl-cards,.pl-feat{list-style:none;padding:0;margin:18px 0 22px;display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px}
.pl-cards li,.pl-feat li{border:1px solid var(--line);border-radius:16px;padding:16px 18px;background:rgba(255,255,255,.02)}
.pl-cards b,.pl-feat b{display:block;font-family:'Cormorant Garamond',Georgia,serif;font-size:21px;font-weight:600;color:#fff7e8;margin:0 0 6px;line-height:1.2}
.pl-cards p,.pl-feat p{font-size:15px;line-height:1.6;margin:0}
.pl-feat li{border-color:rgba(var(--acc-rgb),.28)}
.pl-fig{margin:30px 0 34px;padding:26px;border:1px solid var(--line);border-radius:22px;background:radial-gradient(80% 90% at 50% 0%,rgba(var(--acc-rgb),.09),rgba(255,255,255,.015) 70%)}
.pl-fig .ft{font:600 11.5px/1.3 'Avenir Next',sans-serif;letter-spacing:.16em;text-transform:uppercase;color:var(--gold);margin:0 0 18px}
.pl-fig .fc{font:14px/1.6 'Avenir Next',sans-serif;color:var(--dim);margin:18px 0 0}
.pl-fig ol,.pl-fig ul{list-style:none;padding:0;margin:0}
.pl-chak ol{position:relative;display:grid;gap:14px;padding-left:4px}
.pl-chak ol::before{content:"";position:absolute;left:12px;top:10px;bottom:10px;width:2px;border-radius:2px;background:linear-gradient(180deg,#A66BE0,#5B5FD6,#4FA3E0,#5DBB7A,#F2C94C,#F08A3C,#E0524F)}
.pl-chak li{position:relative;display:grid;grid-template-columns:20px 1fr;gap:16px;align-items:start}
.pl-chak .dot{width:18px;height:18px;border-radius:50%;background:var(--c);box-shadow:0 0 0 4px var(--bg),0 0 18px var(--c);margin-top:4px;position:relative;z-index:1}
.pl-chak b{font-family:'Cormorant Garamond',Georgia,serif;font-size:21px;font-weight:600;color:#fff7e8}
.pl-chak i{font-family:'Cormorant Garamond',Georgia,serif;font-size:18px;color:var(--c)}
.pl-chak span:not(.dot){display:block;font:14.5px/1.5 'Avenir Next',sans-serif;color:var(--muted)}
.pl-wheel svg{display:block;width:100%;max-width:420px;height:auto;margin:0 auto}
.pl-wheel text{font:600 12.5px 'Avenir Next','Segoe UI',system-ui,sans-serif;fill:#141220;text-anchor:middle;dominant-baseline:middle}
.pl-wheel text.d{font-weight:500;font-size:10.5px}
.pl-wheel .lg{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:6px 18px;margin-top:18px;font:14px/1.5 'Avenir Next',sans-serif;color:var(--muted)}
.pl-wheel .lg li{display:flex;gap:8px;align-items:baseline;flex-wrap:wrap}
.pl-wheel .lg span{width:10px;height:10px;border-radius:50%;flex:0 0 10px;transform:translateY(1px)}
.pl-wheel .lg b{color:var(--ink);font-weight:600}
.pl-night .bar{position:relative;display:flex;height:46px;border-radius:12px;overflow:visible;margin:46px 0 6px}
.pl-night .bar>span{height:100%}
.pl-night .bar .n{background:#232848}.pl-night .bar .r{background:rgb(var(--acc-rgb));box-shadow:0 0 16px rgba(var(--acc-rgb),.5)}
.pl-night .bar>span:first-child{border-radius:12px 0 0 12px}.pl-night .bar>span:nth-last-child(2){border-radius:0 12px 12px 0}
.pl-night .wb{position:absolute;top:-38px;bottom:-6px;width:0;border-left:1.5px dashed var(--gold)}
.pl-night .wb em{position:absolute;bottom:100%;left:-8px;transform:translateY(-4px);white-space:nowrap;font:600 12.5px 'Avenir Next',sans-serif;color:var(--gold);font-style:normal}
@media(max-width:560px){.pl-night .wb em{white-space:normal;width:150px;left:auto;right:-6px;text-align:right}}
.pl-night .ticks{position:relative;height:20px;font:12px 'Avenir Next',sans-serif;color:var(--dim);font-variant-numeric:tabular-nums}
.pl-night .ticks span{position:absolute;transform:translateX(-50%)}.pl-night .ticks span:first-child{transform:none}
.pl-night .lg{display:flex;flex-wrap:wrap;gap:8px 20px;margin-top:12px;font:14px 'Avenir Next',sans-serif;color:var(--muted)}
.pl-night .lg li{display:flex;gap:8px;align-items:center}.pl-night .lg span{width:14px;height:14px;border-radius:4px}
.pl-night .lg .n{background:#232848}.pl-night .lg .r{background:rgb(var(--acc-rgb))}
.pl-worlds3 ol{position:relative;display:grid;gap:14px}
.pl-worlds3 ol::before{content:"";position:absolute;left:50%;top:-6px;bottom:-6px;width:2px;background:linear-gradient(180deg,rgba(var(--acc-rgb),.0),rgba(var(--acc-rgb),.6),rgba(var(--acc-rgb),.0));transform:translateX(-1px)}
.pl-worlds3 li{position:relative;border:1px solid var(--line);border-radius:18px;padding:16px 20px;background:#11111f;text-align:center}
.pl-worlds3 li.t0{background:linear-gradient(180deg,rgba(142,167,255,.12),#11111f)}.pl-worlds3 li.t2{background:linear-gradient(0deg,rgba(var(--acc-rgb),.14),#11111f)}
.pl-worlds3 b{display:block;font-family:'Cormorant Garamond',Georgia,serif;font-size:23px;font-weight:600;color:#fff7e8}
.pl-worlds3 p{font:15px/1.6 'Avenir Next',sans-serif;color:var(--muted);margin:6px auto 0;max-width:52ch}
.pl-fig .chip{display:inline-block;margin-top:12px;font:500 13px/1 'Avenir Next',sans-serif;color:var(--gold);border:1px solid rgba(212,175,106,.4);border-radius:99px;padding:7px 12px;text-decoration:none}
.pl-fig .chip:hover{background:rgba(212,175,106,.1)}
.pl-ladder ol{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.pl-ladder li{border:1px solid var(--line);border-radius:18px;padding:16px;background:#11111f;position:relative}
.pl-ladder em{font:600 11px/1 'Avenir Next',sans-serif;letter-spacing:.14em;text-transform:uppercase;color:rgb(var(--acc-rgb));font-style:normal}
.pl-ladder b{display:block;font-family:'Cormorant Garamond',Georgia,serif;font-size:22px;font-weight:600;color:#fff7e8;margin:8px 0 6px;line-height:1.15}
.pl-ladder p{font:14px/1.55 'Avenir Next',sans-serif;color:var(--muted);margin:0 0 10px}
.pl-ladder ul{display:grid;gap:4px;border-top:1px solid var(--line);padding-top:10px}
.pl-ladder ul li{border:0;padding:0;background:none;display:flex;justify-content:space-between;gap:8px;font:13px/1.4 'Avenir Next',sans-serif}
.pl-ladder ul a{color:var(--ink);text-decoration:none}.pl-ladder ul a:hover{color:var(--gold)}
.pl-ladder ul span{color:var(--dim);white-space:nowrap;font-variant-numeric:tabular-nums}
@media(max-width:760px){.pl-ladder ol{grid-template-columns:1fr}}
.pl-three ol{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.pl-three li{border:1px solid var(--line);border-radius:18px;padding:18px;background:#11111f;text-align:center}
.pl-three .g{display:block;font-size:44px;line-height:1.1;color:rgb(var(--acc-rgb));margin-bottom:6px;font-family:'Songti SC','Noto Serif CJK SC','Noto Serif SC',serif}
.pl-three b{display:block;font-family:'Cormorant Garamond',Georgia,serif;font-size:22px;font-weight:600;color:#fff7e8}
.pl-three i{display:block;font:italic 14px 'Avenir Next',sans-serif;color:var(--gold);margin:2px 0 8px}
.pl-three p{font:14.5px/1.55 'Avenir Next',sans-serif;color:var(--muted);margin:0}
@media(max-width:640px){.pl-three ol{grid-template-columns:1fr}}
.pl-path ol{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;position:relative}
.pl-path li{position:relative;border:1px solid var(--line);border-radius:18px;padding:16px;background:#11111f}
.pl-path li em{display:flex;width:30px;height:30px;border-radius:50%;align-items:center;justify-content:center;border:1.5px solid rgb(var(--acc-rgb));color:var(--ink);font:500 14px Georgia,serif;font-style:normal;margin-bottom:10px}
.pl-path b{display:block;font-family:'Cormorant Garamond',Georgia,serif;font-size:21px;font-weight:600;color:#fff7e8}
.pl-path p{font:14px/1.55 'Avenir Next',sans-serif;color:var(--muted);margin:6px 0 0}
.pl-path .chip{font-size:12px;padding:6px 10px;line-height:1.3}
@media(max-width:820px){.pl-path ol{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:480px){.pl-path ol{grid-template-columns:1fr}}
.pl-types ul{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}
.pl-types li{border:1px solid var(--line);border-radius:18px;padding:16px;background:#11111f}
.pl-types .i{display:flex;width:40px;height:40px;border-radius:50%;align-items:center;justify-content:center;font:600 22px 'Cormorant Garamond',Georgia,serif;color:#161122;background:linear-gradient(135deg,rgb(var(--acc-rgb)),#D4AF6A);margin-bottom:10px}
.pl-types b{display:block;font-family:'Cormorant Garamond',Georgia,serif;font-size:21px;font-weight:600;color:#fff7e8}
.pl-types p{font:14px/1.55 'Avenir Next',sans-serif;color:var(--muted);margin:4px 0 0}
.pl-gallery ul{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:14px}
.pl-gallery a{display:grid;gap:6px;text-decoration:none}
.pl-gallery img,.pl-wstrip img{width:100%;height:auto;aspect-ratio:3/4;object-fit:cover;border-radius:999px 999px 14px 14px;border:1px solid var(--line);margin:0;background:#0e0c1c;transition:border-color .2s}
.pl-gallery a:hover img,.pl-wstrip a:hover img{border-color:rgba(212,175,106,.6)}
.pl-gallery b,.pl-wstrip b{font-family:'Cormorant Garamond',Georgia,serif;font-size:19px;font-weight:600;color:#fff7e8;line-height:1.2}
.pl-gallery span,.pl-wstrip span{font:13px/1.45 'Avenir Next',sans-serif;color:var(--dim)}
.pl-app h3{font:600 12px/1.3 'Avenir Next',sans-serif;letter-spacing:.16em;text-transform:uppercase;color:var(--gold);margin:30px 0 12px}
.pl-catg{list-style:none;padding:0;margin:0;display:grid;gap:10px}
.pl-catg a{display:flex;gap:16px;align-items:center;border:1px solid var(--line);border-radius:18px;padding:10px 16px 10px 10px;text-decoration:none;background:rgba(255,255,255,.02)}
.pl-catg a:hover{border-color:rgba(212,175,106,.5)}
.pl-catg img{width:72px;height:72px;border-radius:14px;object-fit:cover;margin:0;border:0;flex:0 0 72px}
.pl-catg b{display:block;font-family:'Cormorant Garamond',Georgia,serif;font-size:22px;font-weight:600;color:#fff7e8;line-height:1.2}
.pl-catg em{display:block;font:normal 13.5px/1.4 'Avenir Next',sans-serif;color:var(--dim);margin-top:2px;font-variant-numeric:tabular-nums}
.pl-med{list-style:none;padding:0;margin:0;display:grid;gap:10px;counter-reset:md}
.pl-med a{display:block;border:1px solid var(--line);border-radius:16px;padding:14px 18px;text-decoration:none;background:rgba(255,255,255,.02)}
.pl-med a:hover{border-color:rgba(212,175,106,.5)}
.pl-med b{display:block;font-family:'Cormorant Garamond',Georgia,serif;font-size:21px;font-weight:600;color:#fff7e8;line-height:1.25}
.pl-med em{display:block;font:normal 12.5px/1.4 'Avenir Next',sans-serif;color:var(--gold);margin:4px 0 6px}
.pl-med span{display:block;font:14.5px/1.55 'Avenir Next',sans-serif;color:var(--muted)}
.pl-wstrip{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:14px}
.pl-wstrip a{display:grid;gap:6px;text-decoration:none}
.pl-blog .pl-posts{list-style:none;padding:0;margin:18px 0 8px;display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:16px}
.pl-posts a{display:flex;flex-direction:column;height:100%;border:1px solid var(--line);border-radius:18px;overflow:hidden;text-decoration:none;background:rgba(255,255,255,.02)}
.pl-posts a:hover{border-color:rgba(212,175,106,.5)}
.pl-posts img{width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;margin:0;border:0;border-radius:0}
.pl-posts .noimg{display:flex;aspect-ratio:16/9;align-items:center;justify-content:center;color:var(--gold);font-size:28px;background:#11111f}
.pl-posts .tx{display:flex;flex-direction:column;gap:6px;padding:14px 16px 16px;flex:1}
.pl-posts em{font:normal 12px/1.3 'Avenir Next',sans-serif;color:var(--dim)}
.pl-posts b{font-family:'Cormorant Garamond',Georgia,serif;font-size:20px;font-weight:600;color:#fff7e8;line-height:1.2}
.pl-posts .tx>span{font:14px/1.55 'Avenir Next',sans-serif;color:var(--muted);display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.pl-posts i{margin-top:auto;font:normal 600 13px 'Avenir Next',sans-serif;color:var(--gold)}
.pl-soon{list-style:none;padding:0;margin:0;display:grid;gap:8px}
.pl-soon li{display:grid;grid-template-columns:minmax(150px,auto) 1fr;gap:4px 16px;border-top:1px solid var(--line);padding:10px 0 2px;font-family:'Avenir Next',sans-serif}
.pl-soon em{font:normal 13px/1.5 'Avenir Next',sans-serif;color:rgb(var(--acc-rgb));white-space:nowrap}
.pl-soon b{font-family:'Cormorant Garamond',Georgia,serif;font-size:19px;font-weight:500;color:var(--ink);line-height:1.3}
@media(max-width:560px){.pl-soon li{grid-template-columns:1fr}}
.pl-explore{max-width:1180px;margin:30px auto 0;padding:0 20px}
.pl-explore h2{font-size:clamp(26px,3.2vw,34px);color:#fff7e8;font-weight:500;margin:20px 0 18px;text-align:center}
.pl-explore ul{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:14px}
.pl-explore a{display:grid;gap:4px;text-decoration:none;text-align:center}
.pl-explore img{width:100%;height:auto;aspect-ratio:1/1;object-fit:cover;border-radius:50%;border:1px solid var(--line);margin:0 0 6px;background:#0e0c1c;box-shadow:0 0 0 0 rgba(var(--acc-rgb),0);transition:box-shadow .25s,border-color .25s}
.pl-explore a:hover img{border-color:rgba(var(--acc-rgb),.7);box-shadow:0 0 34px -6px rgba(var(--acc-rgb),.6)}
.pl-explore b{font-family:'Cormorant Garamond',Georgia,serif;font-size:20px;font-weight:600;color:#fff7e8}
.pl-explore span{font:12px/1.4 'Avenir Next',sans-serif;color:var(--dim);letter-spacing:.06em;text-transform:uppercase}
.pl .afaq h2{margin-top:52px}
.pl .cta{margin-top:52px}
.pl-art .cta a{color:#161122;text-decoration:none}
@media(prefers-reduced-motion:reduce){.pl *{transition:none!important}}
"""
