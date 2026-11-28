# -*- coding: utf-8 -*-
"""28-11 — une page par SÉANCE, seulement pour les séances dont le sujet a une vraie recherche (chantier SEO du 27-11).
Edouard : « vois si utile de créer une page par méditation […] quand tu cliques cela ouvre un panneau qui n'est pas inclus dans
le référencement ». Les catégories et les mondes ont déjà leur page ; ici, les séances qui répondent à une recherche propre.

Données par langue, _tools/seances_<langue>.json (chaque langue a ses séances et ses mots, jamais de traduction) :
    {"<id de séance>": {"slug": "…", "seo": "balise title", "desc": "méta description", "h1": "…", "lead": "chapeau",
                        "sections": [{"h2": "…", "p": ["paragraphe", …]}, …], "faq": [["question", "réponse"], …],
                        "principal": "mot principal", "second": "second mot ou null"}}
Adresse : /fr/seances/<slug>.html · /en/sessions/<slug>.html · /es/sesiones/<slug>.html
Chaque page : fil d'Ariane (catégorie), durée et niveau, chapeau, extrait à écouter s'il existe (_tools/extraits.json), sections,
fiche de l'app et objectifs, bouton vers l'app, autres séances de la catégorie, FAQ, données structurées.
"""
import json, os

DIR = {'fr': 'seances', 'en': 'sessions', 'es': 'sesiones'}
T_ = {
    'fr': dict(bref='La séance en bref', duree='Durée', niveau='Niveau', categorie='Catégorie', meme='Dans la même catégorie',
               toutes='Toutes les séances de la catégorie « {cat} »', seance='Séance guidée'),
    'en': dict(bref='The session at a glance', duree='Length', niveau='Level', categorie='Category', meme='In the same category',
               toutes='All sessions in “{cat}”', seance='Guided session'),
    'es': dict(bref='La sesión en breve', duree='Duración', niveau='Nivel', categorie='Categoría', meme='En la misma categoría',
               toutes='Todas las sesiones de «{cat}»', seance='Sesión guiada'),
}
_C = {}


def charge(lang):
    """textes des pages de séance d'une langue ({} si le fichier n'existe pas)."""
    f = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'seances_{lang}.json')
    if not os.path.exists(f): return {}
    cle = (lang, os.path.getmtime(f))
    if cle not in _C: _C[cle] = json.load(open(f, encoding='utf-8'))
    return _C[cle]


def chemin(lang, slug=None):
    return f'/{lang}/{DIR[lang]}/' + (f'{slug}.html' if slug else '')


def lien(lang, mid):
    """adresse de la page d'une séance, ou None si elle n'a pas de page dans cette langue."""
    s = charge(lang).get(mid)
    return chemin(lang, s['slug']) if s else None


def build(ap, bb, cat, P):
    E = ap.E
    ou = {m['id']: (cid, m) for cid, c in cat['categories'].items() for m in c['meds']}
    written = []
    for lang, p in P.items():
        S = charge(lang)
        if not S: continue
        t, tx = ap.L[lang], T_[lang]
        os.makedirs(f'{ap.ROOT}{chemin(lang)}', exist_ok=True)
        import objectifs
        obs_de = objectifs.par_seance(lang)
        for mid, s in S.items():
            if mid not in ou or not ou[mid][1]['title'].get(lang): continue
            cid, m = ou[mid]
            c, pc = cat['categories'][cid], p['categories'][cid]
            path = chemin(lang, s['slug'])
            alts = {x: chemin(x, charge(x)[mid]['slug']) for x in P if mid in charge(x)}
            cat_url = ap.u(lang, 'med', pc['slug'])
            niveau = t['level'].get(m['level'], m['level'])
            meta = (f'<div class="ap-meta"><span>{ap.dmin(m, lang)} {E(t["min"])}</span><span>{E(niveau)}</span>'
                    f'<span><a href="{cat_url}">{E(c["name"][lang])}</a></span></div>')
            ext_html, ext_ld = ap.extrait_audio(bb, lang, mid, ap.dmin(m, lang), m['title'][lang]) if ap.extrait_de(lang, [mid]) else ('', None)
            secs = ''.join(f'<h2>{E(x["h2"])}</h2>' + ''.join(f'<p>{E(q)}</p>' for q in x['p']) for x in s.get('sections', []))
            obs = obs_de.get(mid, [])
            ob = ('<div class="ap-ob"><b>' + E(ap.OB_T[lang]) + '</b><ul>' + ''.join(
                f'<li><a href="{h}" style="--acc-rgb:{objectifs.ACC[n]}">{E(objectifs.ty(lang, nom))}</a><span>{E(objectifs.ty(lang, interet))}</span></li>'
                for n, nom, h, interet in obs) + '</ul></div>') if obs else ''
            fiche = (f'<h2>{E(tx["bref"])}</h2><dl class="ap-dl"><dt>{E(tx["seance"])}</dt><dd>{E(m["title"][lang])}</dd>'
                     f'<dt>{E(tx["duree"])}</dt><dd>{ap.dmin(m, lang)} {E(t["min"])}</dd><dt>{E(tx["niveau"])}</dt><dd>{E(niveau)}</dd>'
                     f'<dt>{E(tx["categorie"])}</dt><dd><a href="{cat_url}">{E(c["name"][lang])}</a></dd></dl>'
                     f'<p class="intro">{E(m["desc"][lang])}</p>{ob}')
            voisines = [x for x in c['meds'] if x['id'] != mid and x['id'] in S and x['title'].get(lang)]
            meme = (f'<h2>{E(tx["meme"])}</h2><ul class="ap-links">'
                    + ''.join(f'<li><a href="{chemin(lang, S[x["id"]]["slug"])}">{E(S[x["id"]]["h1"])}</a></li>' for x in voisines)
                    + f'<li><a href="{cat_url}">{E(tx["toutes"].format(cat=c["name"][lang]))}</a></li></ul>')
            faq = [tuple(q) for q in s.get('faq', [])]
            bc = [(t['home'], f'/{lang}/'), (t['med'], ap.u(lang, 'med')), (c['name'][lang], cat_url), (m['title'][lang], None)]
            body = (ap.crumbs(lang, bc) + f'<article><div class="ap-hero">{ap.HERO_CAT(cid, lang)}<div><h1>{E(s["h1"])}</h1>{meta}</div></div>'
                    + f'<p class="lead">{E(s["lead"])}</p>' + ext_html + secs + fiche + ap.cta(lang) + meme + ap.faq_html(lang, faq) + '</article>')
            ld = ap.ld_tag({'@context': 'https://schema.org', '@graph': [
                {'@type': 'WebPage', 'name': s['h1'], 'description': s['desc'], 'url': bb.BASE + path, 'inLanguage': lang,
                 'isPartOf': {'@type': 'CollectionPage', 'name': c['name'][lang], 'url': bb.BASE + cat_url}},
                ap.bc_ld(bb, bc)] + ([ext_ld] if ext_ld else [])
                + ([{'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': r}} for q, r in faq]}] if faq else [])})
            ap._write(path, ap.page(bb, lang, s['seo'], s['desc'], path, alts, ap.img_cat(cid), ld, body, m['title'][lang]))
            written.append((path, alts))
    return written
