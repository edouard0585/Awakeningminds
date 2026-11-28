#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Outils en ligne du site, par langue (27-11-2026) : des pages où l'on PRATIQUE tout de suite, dans le navigateur.

  « respiration » : cohérence cardiaque (5-5), respiration 4-7-8, respiration carrée (4-4-4-4), guidées par un cercle
      /fr/exercice-de-respiration.html   /en/breathing-exercise.html   /es/ejercicio-de-respiracion.html

Textes : _tools/outils_<langue>.json, une clé par outil :
  slug, seo (balise title), desc, h1, fil (fil d'Ariane), lead (la phrase sous le H1), image_alt (image de partage),
  mots (mot principal, second et autres mots visés, avec leurs volumes : pour mémoire, rien n'en est affiché),
  outil (libellés du guide : techniques, temps, boutons, message de fin, texte sans JavaScript, ordre des techniques),
  sections [{id, h2, rythme, p, ol, ul, p2, essayer, essayer_t, monde, monde_cap}], seances_t, faq [[question, réponse]].
Écrits pour chaque langue, jamais traduits : chaque langue vise ses propres recherches. Liens [texte](/adresse) permis
dans p, ol, ul, p2. Jetons {meds} {cats} {worlds} remplis depuis le catalogue. Un texte {"si": "gong", "t": "…"} décrit
une fonction de l'app : il se cache en ajoutant "fonctions": ["gong"] à _tools/a_venir.json.
Rythmes et durées : TECHNIQUES ci-dessous, seule source (affichés dans la page ET envoyés au script).
Script : assets/outils/respiration.js (aucune dépendance, aucun fichier audio). Style : CSS ci-dessous, mis dans
l'en-tête de la page (aucune requête de plus, aucun décalage à l'affichage).
Même enveloppe que les pages thématiques : app_pages.page(), fil d'Ariane, encadré « cta », FAQ, données structurées
(WebPage + WebApplication + BreadcrumbList + FAQPage, et la liste des séances de l'app citées ; pas de HowTo).

Appelé par app_pages.build() :  written += outils.build(sys.modules[__name__], bb, P)
→ [(chemin, {langue: chemin})], pour le plan du site. Pour relier l'outil depuis une autre page : outils.chemin(langue).
Stdlib uniquement.
"""
import hashlib, html, json, os, re

E = html.escape
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(ROOT, '_tools')
OUTILS = ('respiration',)
SCRIPT = 'assets/outils/respiration.js'

# Les trois respirations : temps d'un cycle (nom du temps, secondes) et durées au choix (« min » = minutes, « cycles » =
# nombre de cycles ; « defaut » = rang du choix présélectionné). Une durée en minutes est arrondie au cycle entier
# supérieur : l'exercice ne s'arrête jamais au milieu d'une respiration (carrée : 2 min → 8 cycles = 2 min 08).
TECHNIQUES = {
    'coherence': {'phases': [('inspire', 5), ('expire', 5)], 'choix': [('min', 3), ('min', 5), ('min', 10)], 'defaut': 1},
    '478': {'phases': [('inspire', 4), ('retiens', 7), ('expire', 8)], 'choix': [('cycles', 4), ('cycles', 8)], 'defaut': 0},
    'carree': {'phases': [('inspire', 4), ('retiens', 4), ('expire', 4), ('pause', 4)], 'choix': [('min', 2), ('min', 4), ('min', 5)], 'defaut': 1},
}
# Dans la page : image de partage (le cercle de l'outil, 1200 × 630, sans texte ; à défaut un monde de l'app), image d'un
# monde de l'app dans la section sur l'app (clé « monde » de la section : pas de capture d'écran, leurs chiffres vieillissent),
# séances de l'app autour du souffle, catégories et objectifs liés en bas de page.
PARTAGE = 'assets/outils/respiration-cercle.jpg'      # texte alternatif : clé « image_alt » de outils_<langue>.json
IMAGE = 'assets/worlds/antiqueTemple.jpg'             # secours si l'image de partage n'existe pas
SEANCES = ['appren02', 'corps01', 'corps04']
CATEGORIES = ['calm', 'fourMin', 'learningBasics']
OBJECTIFS = ['02', '03', '01']          # réduire le stress, apaiser l'anxiété, mieux dormir
THEMES = ['minuteur', 'sons']           # pages thématiques liées, quand elles existent dans la langue
PILIERS = ['emotions', 'qigong']
# Fonctions de l'app pas encore sorties dans les deux magasins : un texte marqué "si": "<nom>" est caché tant que le nom
# figure dans la liste « fonctions » de _tools/a_venir.json (même principe que ses catégories et ses méditations).
# « gong » = le gong alterné du Minuteur (app/timer.tsx du 22-11 : version 2.0.1 de l'app).

CSS = """
main.wrap:has(.ol-page){padding-top:24px}
.ol-page h1{margin-bottom:10px}
.ol-page .lead{font-size:17px;line-height:1.55;margin-bottom:16px}
.resp{position:relative;margin:0 0 34px;padding:14px;border:1px solid rgba(212,175,106,.4);border-radius:22px;scroll-margin-top:74px;
 background:radial-gradient(120% 70% at 50% 0%,rgba(122,96,180,.2),rgba(10,10,20,0) 72%),linear-gradient(180deg,#15142a,#0e0d1b);
 font-family:'Avenir Next','Segoe UI',system-ui,sans-serif;font-size:15px;line-height:1.4;color:var(--ink)}
.resp [hidden]{display:none!important}
.resp-sr{position:absolute;width:1px;height:1px;margin:-1px;padding:0;overflow:hidden;clip:rect(0 0 0 0);clip-path:inset(50%);white-space:nowrap;border:0}
.resp input[type=radio]{position:absolute;width:1px;height:1px;margin:0;opacity:0;pointer-events:none}
.resp label,.resp button{-webkit-tap-highlight-color:transparent;cursor:pointer}
.resp button{font-family:inherit}
.resp input:focus-visible+label,.resp button:focus-visible,.resp a:focus-visible,.resp-fin:focus-visible{outline:2px solid #F3D9A4;outline-offset:2px}
.resp-tech{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
.resp-tech label{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;min-height:68px;padding:8px 4px;text-align:center;
 border:1px solid rgba(255,255,255,.16);border-radius:14px;background:rgba(255,255,255,.03);color:var(--muted);font-size:14px;line-height:1.2}
.resp-tech label b{font-weight:500}
.resp-tech label small{font-size:12px;letter-spacing:.06em;color:var(--dim);font-variant-numeric:tabular-nums;white-space:nowrap}
.resp input:checked+label{border-color:var(--gold);background:rgba(212,175,106,.14);color:#fff7e8}
.resp input:checked+label small{color:var(--gold)}
.resp-duree{display:flex;flex-wrap:wrap;justify-content:center;gap:8px;margin:12px 0 0}
.resp-duree label{display:inline-flex;align-items:center;justify-content:center;min-width:78px;min-height:44px;padding:0 14px;white-space:nowrap;
 border:1px solid rgba(255,255,255,.16);border-radius:99px;color:var(--muted);font-size:14.5px;font-variant-numeric:tabular-nums}
.resp-rythme{display:flex;flex-wrap:wrap;justify-content:center;gap:2px 16px;margin:12px 0 0;font-size:13.5px;line-height:1.5;color:var(--muted)}
.resp-rythme span{white-space:nowrap}
.resp-scene{position:relative;width:100%;max-width:300px;margin:16px auto 14px}
.resp-scene::before{content:"";display:block;padding-top:100%}
.resp-anneau,.resp-disque,.resp-centre{position:absolute;top:0;right:0;bottom:0;left:0}
.resp-anneau{border:1px dashed rgba(212,175,106,.32);border-radius:50%}
.resp-disque{border:1.5px solid rgba(212,175,106,.85);border-radius:50%;transform:scale(.56);will-change:transform;
 background:radial-gradient(circle at 50% 40%,rgba(243,217,164,.3),rgba(212,175,106,.13) 58%,rgba(122,96,180,.16));
 box-shadow:0 0 46px rgba(212,175,106,.22),inset 0 0 34px rgba(212,175,106,.12)}
.resp-centre{display:flex;flex-direction:column;align-items:center;justify-content:center;padding:0 14%;text-align:center}
.resp-mot{font-family:'Cormorant Garamond',Georgia,serif;font-size:30px;font-weight:600;line-height:1.08;color:#fff7e8}
.resp-compte{margin-top:2px;font-size:44px;font-weight:500;line-height:1.05;color:#F3D9A4;font-variant-numeric:tabular-nums}
.resp-compte:empty{display:none}
.resp[data-etat=repos] .resp-mot{max-width:62%;font-size:22px;text-wrap:balance}
.resp[data-etat=fin] .resp-mot{font-size:34px;color:var(--gold)}
.resp-phase{display:none;height:8px;max-width:300px;margin:0 auto 12px;overflow:hidden;border-radius:99px;background:rgba(255,255,255,.12)}
.resp-phase i{display:block;width:0;height:100%;border-radius:99px;background:var(--gold)}
.resp-etat{display:flex;justify-content:space-between;gap:10px;max-width:320px;margin:0 auto 8px;font-size:14px;color:var(--muted);font-variant-numeric:tabular-nums}
.resp-etat b{font-weight:600;color:#fff7e8}
.resp-total{height:4px;max-width:320px;margin:0 auto;overflow:hidden;border-radius:99px;background:rgba(255,255,255,.12)}
.resp-total i{display:block;width:0;height:100%;background:linear-gradient(90deg,#b8934f,#F3D9A4)}
.resp-cmd{display:flex;justify-content:center;gap:10px;max-width:340px;margin:14px auto 0}
.resp-go{flex:1 1 0;min-width:0;min-height:50px;padding:0 12px;border:0;border-radius:99px;background:linear-gradient(135deg,#E2C285,#b8934f);color:#161122;
 font-size:16.5px;font-weight:600;box-shadow:0 10px 28px -10px rgba(212,175,106,.7)}
.resp-re{flex:1 1 0;min-width:0;min-height:50px;padding:0 12px;border:1px solid rgba(212,175,106,.6);border-radius:99px;background:transparent;color:var(--ink);font-size:15px}
.resp-son{display:flex;align-items:center;justify-content:center;gap:10px;min-height:44px;margin:8px auto 0;padding:0 8px;border:0;background:none;color:var(--muted);font-size:14.5px}
.resp-son i{position:relative;flex:none;width:42px;height:24px;border:1px solid rgba(255,255,255,.4);border-radius:99px;background:rgba(255,255,255,.1);transition:background .15s}
.resp-son i::after{content:"";position:absolute;top:3px;left:3px;width:16px;height:16px;border-radius:50%;background:#F5E6C8;transition:transform .15s}
.resp-son[aria-checked=true]{color:#fff7e8}
.resp-son[aria-checked=true] i{border-color:#D4AF6A;background:#b8934f}
.resp-son[aria-checked=true] i::after{transform:translateX(18px)}
.resp-fin{max-width:440px;margin:0 auto;padding:6px 10px 12px;border-radius:16px;text-align:center}
.resp-fin strong{display:block;font-family:'Cormorant Garamond',Georgia,serif;font-size:27px;font-weight:600;line-height:1.15;color:#fff7e8}
.resp-fin>span{display:block;margin:8px 0 16px;font-size:15px;line-height:1.55;color:var(--muted);text-wrap:balance}
.resp-app{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:50px;padding:0 24px;border-radius:99px;text-decoration:none;
 background:linear-gradient(135deg,#E2C285,#b8934f);color:#161122;font-size:15.5px;font-weight:600}
.resp[data-etat=fin] .resp-b{display:none}
.resp-sansjs{display:none;padding:6px 4px;font-size:15px;line-height:1.6;color:var(--muted)}
.resp-sansjs div+div{margin-top:8px}
.resp-sansjs b{display:block;font-weight:600;color:#fff7e8}
html:not(.js) .resp-ui{display:none}
html:not(.js) .resp-sansjs{display:block}
.ol-nb{white-space:nowrap}
.ol-rythme{display:flex;flex-wrap:wrap;gap:8px;margin:2px 0 16px}
.ol-rythme span{display:inline-flex;align-items:baseline;gap:6px;padding:5px 13px;border:1px solid rgba(212,175,106,.4);border-radius:99px;white-space:nowrap;
 font-family:'Avenir Next','Segoe UI',system-ui,sans-serif;font-size:14px;color:var(--muted)}
.ol-rythme b{font-weight:600;color:var(--gold);font-variant-numeric:tabular-nums}
.ol-essayer{display:inline-block;margin:4px 0 6px;padding:11px 20px;border:1px solid rgba(212,175,106,.6);border-radius:99px;
 text-decoration:none;font-family:'Avenir Next','Segoe UI',system-ui,sans-serif;font-size:14.5px;font-weight:600;line-height:1.5;color:var(--gold)}
.ol-essayer:hover{background:rgba(212,175,106,.12)}
@media(max-width:349px){.resp{padding:12px 10px}.resp-tech{grid-template-columns:1fr}
 .resp-tech label{flex-direction:row;justify-content:space-between;min-height:46px;padding:6px 14px;text-align:left}}
@media(min-width:641px){.ol-page .ap-shot{width:min(32%,190px)}}
@media(min-width:760px){
 .ol-page .lead{font-size:18.5px}
 .resp{padding:26px 28px}
 .resp-ui{display:grid;grid-template-columns:300px minmax(0,1fr);column-gap:34px;align-items:center;
  grid-template-areas:"scene a" "scene b" "scene fin" "scene cmd" "scene son"}
 .resp-a{grid-area:a;align-self:end}
 .resp-b{grid-area:b;margin-top:22px}
 .resp-fin{grid-area:fin;margin:16px 0 0 -10px;text-align:left}
 .resp-cmd{grid-area:cmd;justify-content:flex-start;max-width:none;margin:18px 0 0}
 .resp-son{grid-area:son;justify-self:start;margin:6px 0 0 -8px}
 .resp-scene{grid-area:scene;margin:0}
 .resp-go{flex:0 1 176px;min-width:120px;padding:0 20px}
 .resp-re{flex:0 1 auto;padding:0 22px}
 .resp-duree{justify-content:flex-start}
 .resp-rythme{justify-content:flex-start}
 .resp-phase,.resp-etat,.resp-total{max-width:none}
}
@media(prefers-reduced-motion:reduce){
 .resp-disque{transform:scale(.8)!important;will-change:auto}
 .resp-phase{display:block}
 .resp[data-etat=repos] .resp-phase,.resp[data-etat=fin] .resp-phase{visibility:hidden}
 .resp-son i,.resp-son i::after{transition:none}
}
"""

_C = {}


def charge(lang):
    """Textes des outils d'une langue ({} sans fichier)."""
    f = os.path.join(T, f'outils_{lang}.json')
    if not os.path.exists(f): return {}
    m = os.path.getmtime(f)
    if _C.get(lang, (None,))[0] != m:
        _C[lang] = (m, json.load(open(f, encoding='utf-8')))
    return _C[lang][1]


def chemin(lang, cle='respiration'):
    """Adresse publique de l'outil dans cette langue (None s'il n'existe pas)."""
    d = charge(lang).get(cle)
    return f'/{lang}/{d["slug"]}.html' if d else None


def a_venir():
    """Fonctions de l'app pas encore sorties (liste « fonctions » de _tools/a_venir.json ; vide si absente)."""
    try:
        return set(json.load(open(os.path.join(T, 'a_venir.json'), encoding='utf-8')).get('fonctions', []))
    except Exception:
        return set()


def typo(ap, lang, o):
    """Typographie des textes affichés : en français, espaces insécables avant « : ; ! ? » et dans les guillemets (comme les
    pages piliers) ; partout, un nombre reste sur la même ligne que le mot qui le suit (« 5 s », « 4 cycles », « 100 % »)."""
    if isinstance(o, list): return [typo(ap, lang, x) for x in o]
    if isinstance(o, dict): return {k: typo(ap, lang, v) for k, v in o.items()}
    if not isinstance(o, str): return o
    liens = []   # les adresses des liens [texte](/adresse) ne sont jamais touchées
    o = re.sub(r'\]\((/[^)\s]+)\)', lambda m: liens.append(m.group(1)) or f']({len(liens) - 1}\x00)', o)
    if lang == 'fr': o = ap.piliers.typo(o)
    o = re.sub(r'(?<!-)(\d) (?=[\w%])', '\\1\u00a0', o)
    return re.sub(r'\]\((\d+)\x00\)', lambda m: f']({liens[int(m.group(1))]})', o)


def insecable(h):
    """« 4-7-8 » ne se coupe jamais en fin de ligne : chaque suite chiffre-tiret-chiffre du texte est tenue sur une ligne
    (les balises, leurs attributs et le contenu des scripts ne sont pas touchés)."""
    out = []
    for bloc in re.split(r'(<script\b.*?</script>)', h, flags=re.S):
        if bloc.startswith('<script'):
            out.append(bloc); continue
        out.append(''.join(x if x.startswith('<') else re.sub(r'\d(?:-\d)+', lambda m: f'<span class="ol-nb">{m.group(0)}</span>', x)
                           for x in re.split(r'(<[^>]+>)', bloc)))
    return ''.join(out)


def jetons(o, d):
    """{meds}, {cats}, {worlds} remplis depuis le catalogue (les textes restent justes quand l'app grandit)."""
    if isinstance(o, list): return [jetons(x, d) for x in o]
    if isinstance(o, dict): return {k: jetons(v, d) for k, v in o.items()}
    if isinstance(o, str):
        for k, v in d.items(): o = o.replace('{' + k + '}', str(v))
    return o


def sans_liens(ap, txt):
    """Texte nu (sans [liens](…) ni **gras**), pour les données structurées."""
    return ap.piliers.plain(txt)


def cycles(tech, genre, n):
    """Nombre de cycles d'un choix de durée (minutes arrondies au cycle entier supérieur)."""
    c = sum(s for _, s in TECHNIQUES[tech]['phases'])
    return n if genre == 'cycles' else -(-n * 60 // c)


def horloge(s):
    return f'{s // 60}:{s % 60:02d}'


def rythme(o, tech, sep=' · '):
    """« Inspire 5 s · Expire 5 s » : le rythme d'une technique, en mots (chaque temps reste sur une ligne)."""
    return sep.join(f'{o["phases"][nom]}\u00a0{s}\u00a0s' for nom, s in TECHNIQUES[tech]['phases'])


def lu(o, tech):
    """« inspire 5 secondes, expire 5 secondes » : le rythme tel qu'un lecteur d'écran le dit (nom des onglets)."""
    return ', '.join(f'{o["phases"][nom].lower()} {s} {o["secondes"]}' for nom, s in TECHNIQUES[tech]['phases'])


def ordre(o):
    """Ordre des techniques dans la langue (clé « ordre » ; la première est présélectionnée)."""
    return [k for k in o.get('ordre', []) if k in TECHNIQUES and k in o['techniques']] or [k for k in TECHNIQUES if k in o['techniques']]


def donnees(o):
    """Réglages envoyés au script : techniques (temps, durées), ordre, libellés."""
    tech = {}
    for k in ordre(o):
        t = TECHNIQUES[k]
        tech[k] = {'nom': o['techniques'][k], 'phases': [[n, s] for n, s in t['phases']], 'defaut': t['defaut'],
                   'choix': [{'t': o[g].replace('{n}', str(n)), 'c': cycles(k, g, n)} for g, n in t['choix']]}
    libelles = {k: o[k] for k in ('phases', 'pret', 'demarrer', 'pause', 'reprendre', 'en_pause', 'cycle', 'dire_pause', 'dire_fin')}
    return {'ordre': ordre(o), 'techniques': tech, 't': libelles}


def version():
    """Empreinte du script : l'adresse change quand il change (le cache des navigateurs ne garde jamais l'ancien)."""
    try:
        return hashlib.md5(open(os.path.join(ROOT, SCRIPT), 'rb').read()).hexdigest()[:8]
    except OSError:
        return '0'


def outil_html(o):
    """Le guide de respiration, déjà dessiné dans son état de départ (première technique, durée par défaut) : rien ne bouge
    quand le script arrive. Ordre du balisage = ordre sur téléphone : techniques, durées, boutons (visibles sans faire
    défiler), cercle, temps restant, son, message de fin ; sur grand écran la grille CSS met le cercle à gauche.
    Sans JavaScript : un texte qui donne les rythmes. Ni <p> ni <li> ici : les liens internes automatiques
    (liens_auto.py) ne passent pas dans l'outil."""
    D = donnees(o); k0 = D['ordre'][0]; t0 = D['techniques'][k0]
    c0 = t0['choix'][t0['defaut']]
    total = c0['c'] * sum(s for _, s in t0['phases'])
    onglets = ''.join(
        f'<input type="radio" name="resp-tech" id="resp-t-{k}" value="{k}"' + (' checked' if k == k0 else '')
        + f' aria-label="{E(D["techniques"][k]["nom"] + ", " + lu(o, k))}"><label for="resp-t-{k}"><b>{E(D["techniques"][k]["nom"])}</b>'
        + f'<small aria-hidden="true">{" · ".join(str(s) for _, s in D["techniques"][k]["phases"])}</small></label>' for k in D['ordre'])
    durees = ''.join(
        f'<input type="radio" name="resp-duree" id="resp-d-{i}" value="{i}"' + (' checked' if i == t0['defaut'] else '')
        + f'><label for="resp-d-{i}">{E(c["t"])}</label>' for i, c in enumerate(t0['choix']))
    sansjs = (f'<div class="resp-sansjs"><div>{E(o["sansjs"])}</div>'
              + ''.join(f'<div><b>{E(D["techniques"][k]["nom"])}</b> {E(rythme(o, k))}</div>' for k in D['ordre']) + '</div>')
    return (
        f'<section class="resp" id="outil" aria-label="{E(o["aria"])}" data-etat="repos"><div class="resp-ui">'
        f'<div class="resp-a"><div class="resp-tech" role="radiogroup" aria-label="{E(o["technique"])}">{onglets}</div>'
        f'<div class="resp-duree" role="radiogroup" aria-label="{E(o["duree"])}">{durees}</div>'
        '<div class="resp-rythme" aria-hidden="true">' + ''.join(f'<span>{E(o["phases"][n])}\u00a0{s}\u00a0s</span>' for n, s in TECHNIQUES[k0]['phases']) + '</div></div>'
        f'<div class="resp-cmd"><button type="button" class="resp-go">{E(o["demarrer"])}</button>'
        f'<button type="button" class="resp-re" hidden>{E(o["recommencer"])}</button></div>'
        '<div class="resp-scene" aria-hidden="true"><span class="resp-anneau"></span><span class="resp-disque"></span>'
        f'<div class="resp-centre"><span class="resp-mot">{E(o["pret"])}</span><span class="resp-compte"></span></div></div>'
        '<div class="resp-b"><div class="resp-phase" aria-hidden="true"><i></i></div>'
        f'<div class="resp-etat"><span>{E(o["restant"])} <b class="resp-restant">{horloge(total)}</b></span>'
        f'<span class="resp-cycle">{E(o["cycle"].replace("{i}", "1").replace("{n}", str(c0["c"])))}</span></div>'
        '<div class="resp-total" aria-hidden="true"><i></i></div></div>'
        f'<button type="button" class="resp-son" role="switch" aria-checked="false"><i aria-hidden="true"></i>{E(o["son"])}</button>'
        f'<div class="resp-fin" tabindex="-1" hidden><strong>{E(o["fin_t"])}</strong><span>{E(o["fin_p"])}</span>'
        f'<a class="resp-app" href="/app/"><span aria-hidden="true">✦</span>{E(o["fin_b"])}</a></div>'
        '<span class="resp-sr resp-dire" role="status" aria-live="polite" aria-atomic="true"></span></div>'
        + sansjs
        + '<script type="application/json" id="resp-donnees">' + json.dumps(D, ensure_ascii=False).replace('<', '\\u003c') + '</script>'
        + f'<script src="/{SCRIPT}?v={version()}" defer onerror="document.documentElement.classList.remove(\'js\')"></script></section>')


def section_html(ap, lang, x, o, cache, cat, P):
    """Une section de texte : intertitre (avec ancre), rythme de la technique en pastilles, image d'un monde de l'app (nom,
    image et lien tirés du catalogue), paragraphes (liens [texte](/adresse) permis), étapes numérotées, liste, bouton
    « Lancer » qui règle l'outil sur la technique."""
    vu = lambda y: not (isinstance(y, dict) and y.get('si') in cache)
    tx = lambda y: y['t'] if isinstance(y, dict) else y
    R = ap.piliers.rich
    h = f'<h2 id="{E(x["id"])}">{E(x["h2"])}</h2>'
    if x.get('rythme') in TECHNIQUES:
        h += '<div class="ol-rythme">' + ''.join(f'<span>{E(o["phases"][n])} <b>{s}\u00a0s</b></span>' for n, s in TECHNIQUES[x['rythme']]['phases']) + '</div>'
    wid = x.get('monde')
    if wid in cat['worlds'] and wid in P[lang]['worlds']:
        avant, _, apres = x.get('monde_cap', '{monde}').partition('{monde}')
        lien = f'<a href="{ap.u(lang, "world", P[lang]["worlds"][wid]["slug"])}">{E(cat["worlds"][wid]["name"][lang])}</a>'
        h += ('<figure class="ap-shot">' + ap.img_tag(f'assets/worlds/{wid}.jpg', lang, 480, ap.img_world(wid), 1, ' loading="lazy" decoding="async"')
              + f'<figcaption>{E(avant)}{lien}{E(apres)}</figcaption></figure>')
    h += ''.join(f'<p>{R(tx(q))}</p>' for q in x.get('p', []) if vu(q))
    if x.get('ol'): h += '<ol class="ap-etapes">' + ''.join(f'<li>{R(tx(b))}</li>' for b in x['ol'] if vu(b)) + '</ol>'
    if x.get('ul'): h += '<ul>' + ''.join(f'<li>{R(tx(b))}</li>' for b in x['ul'] if vu(b)) + '</ul>'
    h += ''.join(f'<p>{R(tx(q))}</p>' for q in x.get('p2', []) if vu(q))
    if x.get('essayer') in TECHNIQUES and x['essayer'] in o['techniques']:
        h += f'<a class="ol-essayer" href="#outil" data-resp="{x["essayer"]}"><span aria-hidden="true">↑ </span>{E(x["essayer_t"])}</a>'
    return h + '<div class="ap-clear"></div>'


def seances_html(ap, lang, cat, P, titre):
    """Séances de l'app autour du souffle : titre, durée, niveau, catégorie (lien vers la séance sur sa page), description —
    tout vient du catalogue de l'app. (html, [titres]) ; ('', []) si aucune n'est visible."""
    t = ap.L[lang]; p = P[lang]
    ms = [(cid, m) for mid in SEANCES for cid, c in cat['categories'].items() for m in c['meds']
          if m['id'] == mid and m['title'].get(lang) and cid in p['categories']]
    if not ms: return '', []
    li = ''.join(
        f'<li><h3>{E(m["title"][lang])}</h3><div class="d">{ap.dmin(m, lang)} {E(t["min"])} · {E(t["level"].get(m["level"], m["level"]))} · '
        f'<a href="{ap.u(lang, "med", p["categories"][cid]["slug"])}#{E(m["id"])}">{E(cat["categories"][cid]["name"][lang])}</a></div>'
        f'<p>{E(m["desc"][lang])}</p></li>' for cid, m in ms)
    return f'<h2 id="seances">{E(titre)}</h2><ol class="ap-list">{li}</ol>', [m['title'][lang] for _, m in ms]


def liens_html(ap, lang, cat, P, cle):
    """Bas de page : catégories de séances, objectifs, pages thématiques et guides liés, autres outils."""
    import objectifs
    p = P[lang]; li = ''
    for c in CATEGORIES:
        if c in cat['categories'] and c in p['categories']:
            li += f'<li><a href="{ap.u(lang, "med", p["categories"][c]["slug"])}">{E(ap.ancre(p["categories"][c], cat["categories"][c]["name"][lang]))}</a></li>'
    OB = objectifs.textes(lang) or {}
    for n in OBJECTIFS:
        ob = (OB.get('objectifs') or {}).get(n)
        if ob: li += f'<li><a href="{objectifs.chemin(lang, n, OB)}">{E(objectifs.ty(lang, ob["titre_court"]))}</a></li>'
    TH = ap.charge('themes', lang) or {}
    li += ''.join(f'<li><a href="/{lang}/{TH[k]["slug"]}.html">{E(TH[k]["h1"])}</a></li>' for k in THEMES if k in TH)
    li += ap.piliers.links_li(ap, lang, PILIERS)
    D = charge(lang)
    li += ''.join(f'<li><a href="{chemin(lang, k)}">{E(D[k]["fil"])}</a></li>' for k in OUTILS if k != cle and k in D)
    return f'<h2>{E(ap.XL[lang]["themes"])}</h2><ul class="ap-links">{li}</ul>' if li else ''


def respiration(ap, bb, lang, cat, P, alts):
    """La page « exercice de respiration » d'une langue (HTML complet)."""
    brut = charge(lang)['respiration']
    path = alts[lang]; url = bb.BASE + path
    cats = cat['categories']
    nombres = dict(meds=sum(len(c['meds']) for c in cats.values()), cats=len(cats), worlds=len(cat['worlds']))
    brut = jetons(brut, nombres)
    d = typo(ap, lang, {k: v for k, v in brut.items() if k not in ('slug', 'seo', 'desc', 'mots', 'image_alt')})   # textes affichés
    o = d['outil']
    cache = a_venir()
    # image de partage (non affichée : l'outil occupe le haut de la page) : le cercle de l'outil, sinon un monde de l'app
    # dans sa copie nommée dans la langue
    if os.path.exists(os.path.join(ROOT, PARTAGE)) and brut.get('image_alt'):
        src, alt_img = '/' + PARTAGE, brut['image_alt']
    else:
        p_img, alt_img, _ = ap.media(IMAGE, lang, 960)
        src = p_img or ap.img_world(IMAGE.split('/')[-1][:-4])
    secs = ''.join(section_html(ap, lang, x, o, cache, cat, P) for x in d['sections'])
    seances, titres = seances_html(ap, lang, cat, P, d['seances_t'])
    bc = [(ap.L[lang]['home'], f'/{lang}/'), (brut['fil'], None)]
    faq = [tuple(q) for q in d.get('faq', [])]
    body = (ap.crumbs(lang, bc) + insecable(
            f'<article class="ap-theme ol-page"><h1>{E(d["h1"])}</h1><p class="lead">{E(d["lead"])}</p>'
            '<script>document.documentElement.className+=" js"</script>'
            + outil_html(o) + secs + seances + ap.cta(lang) + ap.faq_html(lang, faq) + liens_html(ap, lang, cat, P, 'respiration') + '</article>'))
    faq_ld = [tuple(q) for q in brut.get('faq', [])]
    graph = [
        {'@type': 'WebPage', 'name': brut['h1'], 'description': brut['desc'], 'url': url, 'inLanguage': lang, 'primaryImageOfPage': bb.BASE + src,
         'isPartOf': {'@type': 'WebSite', 'name': 'MeditaDream', 'url': bb.BASE + '/'}, 'mainEntity': {'@id': url + '#outil'}},
        {'@type': 'WebApplication', '@id': url + '#outil', 'name': brut['outil']['nom'], 'url': url, 'description': brut['desc'],
         'applicationCategory': 'HealthApplication', 'operatingSystem': 'Any', 'browserRequirements': 'Requires JavaScript', 'inLanguage': lang,
         'isAccessibleForFree': True, 'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR'},
         'featureList': [brut['outil']['techniques'][k] for k in ordre(brut['outil'])],
         'publisher': {'@type': 'Organization', 'name': 'MeditaDream', 'url': bb.BASE + '/'}},
        ap.bc_ld(bb, bc)]
    if titres:
        graph.append({'@type': 'ItemList', 'name': brut['seances_t'], 'numberOfItems': len(titres),
                      'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n} for i, n in enumerate(titres)]})
    if faq_ld:
        graph.append({'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': sans_liens(ap, r)}}
                                                         for q, r in faq_ld]})
    ld = ap.ld_tag({'@context': 'https://schema.org', '@graph': graph})
    page = ap.page(bb, lang, brut['seo'], brut['desc'], path, alts, src, ld, body, alt_img or brut['h1'])
    return page.replace('</style>', CSS + '</style>', 1)


RENDU = {'respiration': respiration}


def build(ap, bb, P):
    """Écrit la page de chaque outil dans chaque langue ; renvoie [(chemin, {langue: chemin})] pour le plan du site."""
    written = []
    cat = ap.load()[0]
    for cle in OUTILS:
        alts = {l: chemin(l, cle) for l in P if chemin(l, cle)}
        for lang in alts:
            ap._write(alts[lang], RENDU[cle](ap, bb, lang, cat, P, alts))
            written.append((alts[lang], alts))
    return written
