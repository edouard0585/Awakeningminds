# -*- coding: utf-8 -*-
"""06-11 — pages « objectifs » (demande d'Edouard : « une page avec un super design et photo qui présente chacun des 14
objectifs de faire de la méditation… Comment MeditaDream t'aide à bien dormir, à réduire le stress… lister toutes les
fonctionnalités, catégories, méditations permettant d'y parvenir », d'après son document MeditaDream_14_objectifs.docx).

Une page d'ensemble + 14 pages par langue : /fr/objectifs/, /en/goals/, /es/objetivos/.
Données : _tools/objectifs_<langue>.json (textes, séances et intérêt de chaque séance pour l'objectif, mondes,
fonctionnalités ; fabriqué par ~/Documents/seo-meditadream-0611/outils/objectifs_site.py), _tools/icones_site.json
(icônes des fonctionnalités et des objectifs), _tools/icones_meditations.json (icône de chaque méditation),
_queue/photos.json (photos des pages). Les séances qui ne sont pas (encore) dans le catalogue filtré par
_tools/a_venir.json ne sont jamais montrées.
Appelé par app_pages.build() ; renvoie [(chemin, {langue: chemin})] pour le plan du site."""
import html, json, os, re

E = html.escape
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(ROOT, '_tools')
LANGS = ['fr', 'en', 'es']
DIR = {'fr': 'objectifs', 'en': 'goals', 'es': 'objetivos'}
DEPTH = 2

# photo d'en-tête (bibliothèque _queue/photos.json) et couleur d'accent de chaque objectif
PHOTO = {'hub': 'p18', '01': 'p06', '02': 'p26', '03': 'p41', '04': 'p40', '05': 'p24', '06': 'p47', '07': 'p33', '08': 'p02',
         '09': 'p13', '10': 'p43', '11': 'p30', '12': 'p38', '13': 'p12', '14': 'p50'}
ACC = {'hub': '212,175,106', '01': '142,167,255', '02': '125,200,170', '03': '120,190,220', '04': '230,170,120', '05': '240,140,150',
       '06': '200,150,255', '07': '230,120,80', '08': '212,175,106', '09': '240,170,70', '10': '110,200,230', '11': '245,190,90',
       '12': '160,140,255', '13': '180,200,220', '14': '120,220,190'}

# fonctionnalité (nom du document d'Edouard) → page du site qui la montre en détail
LIEN_THEME = {'Oracle émotionnel': 'oracle', 'Journaux personnels': 'journaux', 'Créateur de méditations': 'creer',
              'Dragon compagnon et île évolutive': 'dragon', 'Sons d’ambiance': 'sons', 'Minuteur et fondu sonore': 'sons'}
LIEN_PILIER = {'Carnet des guides': 'guides'}
# « Pour aller plus loin » : guides complets (piliers) et pages de fonctionnalités liés à chaque objectif
PLUS = {'01': (['reve'], ['sons', 'journaux']), '02': (['visualisation'], ['sons', 'oracle']), '03': (['emotions'], ['oracle', 'journaux']),
        '04': (['qigong', 'chakras'], ['sons']), '05': (['emotions'], ['gratitude', 'journaux']), '06': (['chakras', 'guides', 'astral'], ['journaux']),
        '07': (['transe', 'astral'], ['sons']), '08': (['visualisation'], ['oracle', 'dragon', 'creer']), '09': (['qigong'], ['gratitude']),
        '10': (['visualisation'], ['creer']), '11': (['emotions'], ['gratitude', 'dragon']), '12': (['reve'], ['journaux']),
        '13': (['emotions', 'guides'], ['journaux', 'gratitude']), '14': (['mondes', 'visualisation'], ['dragon'])}

OL = {
 'fr': dict(crumb='Objectifs', eye='Objectif {n} sur {t}', eye_hub='{t} objectifs, une seule application', seances='séances', seance='séance',
            cats='catégories', cat='catégorie', mondes='mondes immersifs', monde='monde immersif', free='Gratuit', noads='Sans pub', offline='Hors ligne',
            dl='Télécharger gratuitement', see='Voir les séances', toc='Sommaire', min='min',
            h_pitch='{t} : ce que MeditaDream change', h_seances='{t} : les séances de l’application', h_feat='{t} : les fonctionnalités qui t’aident',
            h_mondes='{t} : les mondes immersifs', h_etapes='{t} : mode d’emploi en 4 étapes',
            t_pitch='Pourquoi MeditaDream', t_seances='Les séances', t_feat='Les fonctionnalités', t_mondes='Les mondes', t_etapes='Mode d’emploi',
            faq='Questions fréquentes', voir_cat='Voir la catégorie', voir='En savoir plus', autres='Les autres objectifs',
            dans='dans cet objectif', hub_cta='Découvrir', hub_n='{a} séances · {b} mondes', h_hub='Choisis ton objectif',
            prog_eye='Ton programme', t_prog='Le programme', see_prog='Voir le programme', geste='Ton geste', repere='Ton repère',
            etapes_n='étapes', seances_cap='Séances de cette étape', prog_cta='Commencer le programme dans l’app', hub_prog='Programme'),
 'en': dict(crumb='Goals', eye='Goal {n} of {t}', eye_hub='{t} goals, one app', seances='sessions', seance='session',
            cats='categories', cat='category', mondes='immersive worlds', monde='immersive world', free='Free', noads='No ads', offline='Offline',
            dl='Download for free', see='See the sessions', toc='On this page', min='min',
            h_pitch='{t}: what MeditaDream changes', h_seances='{t}: the sessions in the app', h_feat='{t}: the features that help',
            h_mondes='{t}: the immersive worlds', h_etapes='{t}: how to use the app in 4 steps',
            t_pitch='Why MeditaDream', t_seances='Sessions', t_feat='Features', t_mondes='Worlds', t_etapes='How to use it',
            faq='Frequently asked questions', voir_cat='See the category', voir='Learn more', autres='Other goals',
            dans='for this goal', hub_cta='Explore', hub_n='{a} sessions · {b} worlds', h_hub='Choose your goal',
            prog_eye='Your program', t_prog='The program', see_prog='See the program', geste='Your habit', repere='Sign of progress',
            etapes_n='stages', seances_cap='Sessions for this stage', prog_cta='Start the program in the app', hub_prog='Program'),
 'es': dict(crumb='Objetivos', eye='Objetivo {n} de {t}', eye_hub='{t} objetivos, una sola app', seances='sesiones', seance='sesión',
            cats='categorías', cat='categoría', mondes='mundos inmersivos', monde='mundo inmersivo', free='Gratis', noads='Sin anuncios', offline='Sin conexión',
            dl='Descárgala gratis', see='Ver las sesiones', toc='En esta página', min='min',
            h_pitch='{t}: lo que cambia MeditaDream', h_seances='{t}: las sesiones de la app', h_feat='{t}: las funciones que te ayudan',
            h_mondes='{t}: los mundos inmersivos', h_etapes='{t}: cómo usar la app en 4 pasos',
            t_pitch='Por qué MeditaDream', t_seances='Las sesiones', t_feat='Las funciones', t_mondes='Los mundos', t_etapes='Cómo usarla',
            faq='Preguntas frecuentes', voir_cat='Ver la categoría', voir='Saber más', autres='Otros objetivos',
            dans='para este objetivo', hub_cta='Descubrir', hub_n='{a} sesiones · {b} mundos', h_hub='Elige tu objetivo',
            prog_eye='Tu programa', t_prog='El programa', see_prog='Ver el programa', geste='Tu hábito', repere='Señal de progreso',
            etapes_n='etapas', seances_cap='Sesiones de esta etapa', prog_cta='Empieza el programa en la app', hub_prog='Programa'),
}

CSS = """
.ob .pl-hero h1{font-size:clamp(34px,5vw,56px)}
.ob .pl-arch img{aspect-ratio:4/5}
.ob-pitch{border:1px solid rgba(var(--acc-rgb),.38);background:radial-gradient(90% 120% at 0% 0%,rgba(var(--acc-rgb),.13),rgba(255,255,255,.015) 62%);border-radius:22px;padding:26px 30px 12px;margin:0 0 6px}
.pl-art .ob-pitch h2{margin-top:0}
.pl-art .ob-pitch p:first-of-type{font-family:'Cormorant Garamond',Georgia,serif;font-size:clamp(21px,2.4vw,25px);line-height:1.45;color:#fff7e8}
.ob-cat{margin:28px 0 8px}
.ob-cath{display:inline-flex;align-items:center;gap:12px;text-decoration:none;margin:0 0 12px}
.pl-art .ob-cath img{width:46px;height:46px;border-radius:12px;object-fit:cover;margin:0;border:1px solid var(--line)}
.ob-cath b{display:block;font:600 12px/1.3 'Avenir Next','Segoe UI',system-ui,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--gold)}
.ob-cath em{display:block;font:normal 13px/1.4 'Avenir Next',sans-serif;color:var(--dim);margin-top:2px}
.ob-cath:hover em{color:var(--ink)}
.ob-med{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:10px}
.ob-med a{display:grid;grid-template-columns:62px minmax(0,1fr);gap:14px;align-items:start;height:100%;box-sizing:border-box;border:1px solid var(--line);border-radius:16px;padding:12px 14px;text-decoration:none;background:rgba(255,255,255,.02)}
.ob-med a:hover{border-color:rgba(var(--acc-rgb),.65)}
.pl-art .ob-med img{width:62px;height:62px;margin:0;border:0;border-radius:14px;background:radial-gradient(circle,rgba(var(--acc-rgb),.18),rgba(0,0,0,0) 70%)}
.ob-med b{display:block;font-family:'Cormorant Garamond',Georgia,serif;font-size:20px;font-weight:600;color:#fff7e8;line-height:1.2}
.ob-med em{display:block;font:normal 12.5px/1.4 'Avenir Next',sans-serif;color:rgb(var(--acc-rgb));margin:3px 0 5px;font-variant-numeric:tabular-nums}
.ob-med span span{display:block;font:14px/1.5 'Avenir Next','Segoe UI',system-ui,sans-serif;color:var(--muted)}
.ob-feat{list-style:none;padding:0;margin:18px 0 22px;display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:12px}
.ob-feat li{display:grid;grid-template-columns:58px minmax(0,1fr);gap:14px;align-items:start;border:1px solid rgba(var(--acc-rgb),.28);border-radius:18px;padding:14px 16px;background:linear-gradient(180deg,rgba(var(--acc-rgb),.07),rgba(255,255,255,.01))}
.pl-art .ob-feat img{width:58px;height:58px;margin:0;border:0}
.ob-feat b{display:block;font-family:'Cormorant Garamond',Georgia,serif;font-size:20px;font-weight:600;color:#fff7e8;line-height:1.2;margin:2px 0 4px}
.pl-art .ob-feat p{font:14.5px/1.55 'Avenir Next','Segoe UI',system-ui,sans-serif;color:var(--muted);margin:0}
.pl-art .ob-feat a{display:inline-block;font:500 13px/1 'Avenir Next',sans-serif;color:var(--gold);text-decoration:none;margin-top:8px}
.pl-art .ob-feat a:hover{text-decoration:underline}
.pl-art .pl-steps.ob-steps li{padding-bottom:16px}
.ob-others{max-width:1180px;margin:40px auto 0;padding:0 20px}
.ob-others h2{font-size:clamp(26px,3.2vw,34px);color:#fff7e8;font-weight:500;margin:20px 0 18px;text-align:center}
.ob-others ul{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:10px}
.ob-others a{display:flex;align-items:center;gap:10px;height:100%;box-sizing:border-box;border:1px solid var(--line);border-radius:14px;padding:8px 12px 8px 8px;text-decoration:none;color:var(--ink);font:500 18px/1.2 'Cormorant Garamond',Georgia,serif;background:rgba(255,255,255,.02)}
.ob-others img{width:44px;height:44px;margin:0;border:0;flex:0 0 44px}
.ob-others a:hover{border-color:rgba(212,175,106,.6);color:#fff}
.ob-hub{list-style:none;padding:0;margin:8px 0 30px;display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
.ob-hub a{display:grid;grid-template-columns:76px minmax(0,1fr);gap:16px;align-items:start;height:100%;box-sizing:border-box;border:1px solid rgba(var(--acc-rgb),.32);border-radius:20px;padding:16px 18px;text-decoration:none;background:linear-gradient(180deg,rgba(var(--acc-rgb),.08),rgba(255,255,255,.01));transition:border-color .2s,box-shadow .2s}
.ob-hub a:hover{border-color:rgba(var(--acc-rgb),.75);box-shadow:0 18px 40px -26px rgba(var(--acc-rgb),.8)}
.ob-hub img{width:76px;height:76px;margin:0;border:0}
.ob-hub h2{font-family:'Cormorant Garamond',Georgia,serif;font-size:24px;font-weight:600;color:#fff7e8;margin:2px 0 6px;line-height:1.15}
.ob-hub p{font:14.5px/1.55 'Avenir Next','Segoe UI',system-ui,sans-serif;color:var(--muted);margin:0 0 8px}
.ob-hub em{font:normal 12.5px/1.3 'Avenir Next',sans-serif;color:rgb(var(--acc-rgb));font-variant-numeric:tabular-nums}
.ob-hubw{max-width:1180px;margin:0 auto;padding:0 20px}
.ob-hubw>h2{font-size:clamp(28px,3.6vw,36px);color:#fff7e8;font-weight:500;margin:10px 0 18px;text-align:center}
.ob-hubw .cta{max-width:760px;margin:10px auto 0}
.ob-prog{position:relative;margin:34px 0 6px;padding:28px 30px 24px;border-radius:26px;border:1px solid rgba(var(--acc-rgb),.42);
 background:radial-gradient(110% 70% at 100% 0%,rgba(var(--acc-rgb),.18),rgba(0,0,0,0) 60%),radial-gradient(80% 60% at 0% 100%,rgba(212,175,106,.10),rgba(0,0,0,0) 60%),#0f0e1c;
 box-shadow:0 30px 80px -50px rgba(var(--acc-rgb),.75)}
.ob-prog-eye{font:600 12px/1.2 'Avenir Next','Segoe UI',system-ui,sans-serif;letter-spacing:.18em;text-transform:uppercase;color:rgb(var(--acc-rgb));margin:0 0 8px}
.pl-art .ob-prog h2{margin:0 0 12px}.pl-art .ob-prog h2::before{display:none}
.pl-art .ob-prog .ob-prog-intro{font-size:17px;color:var(--muted);margin:0 0 16px}
.ob-prog-facts{list-style:none;display:flex;flex-wrap:wrap;gap:8px;padding:0;margin:0 0 26px}
.ob-prog-facts li{font:500 12.5px/1 'Avenir Next',sans-serif;color:var(--ink);border:1px solid rgba(var(--acc-rgb),.45);background:rgba(var(--acc-rgb),.10);border-radius:99px;padding:8px 13px;font-variant-numeric:tabular-nums}
.ob-road{list-style:none;padding:0;margin:0 0 28px;display:grid;grid-auto-flow:column;grid-auto-columns:minmax(0,1fr)}
.ob-road li{position:relative;padding:0 12px 0 0;min-width:0}
.ob-road li::after{content:"";position:absolute;left:38px;right:8px;top:15px;height:2px;border-radius:2px;background:linear-gradient(90deg,rgba(var(--acc-rgb),.9),rgba(var(--acc-rgb),.2))}
.ob-road li:last-child::after{display:none}
.ob-road b{display:flex;width:32px;height:32px;box-sizing:border-box;border-radius:50%;align-items:center;justify-content:center;border:2px solid rgb(var(--acc-rgb));background:rgba(var(--acc-rgb),.16);font:600 14px/1 'Avenir Next','Segoe UI',system-ui,sans-serif;color:#fff7e8;margin:0 0 10px;font-variant-numeric:lining-nums}
.ob-road span{display:block;font:600 10.5px/1.25 'Avenir Next','Segoe UI',system-ui,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:rgb(var(--acc-rgb))}
.ob-road em{display:block;font:italic 500 17px/1.25 'Cormorant Garamond',Georgia,serif;color:var(--ink);margin-top:4px}
.ob-tl{list-style:none;padding:0;margin:0;position:relative;counter-reset:tl}
.ob-tl::before{content:"";position:absolute;left:21px;top:24px;bottom:34px;width:2px;border-radius:2px;background:linear-gradient(180deg,rgb(var(--acc-rgb)),rgba(var(--acc-rgb),.28) 72%,rgba(212,175,106,.65))}
.ob-tl>li{position:relative;padding:0 0 16px 62px;counter-increment:tl}
.ob-tl>li::before{content:counter(tl);position:absolute;left:0;top:2px;width:44px;height:44px;box-sizing:border-box;border-radius:50%;display:flex;align-items:center;justify-content:center;background:#0f0e1c;border:2px solid rgb(var(--acc-rgb));box-shadow:0 0 0 5px #0f0e1c,0 0 22px rgba(var(--acc-rgb),.55);font:600 17px/1 'Avenir Next','Segoe UI',system-ui,sans-serif;font-variant-numeric:lining-nums;color:#fff7e8}
.ob-tl>li>div{border:1px solid var(--line);border-radius:18px;padding:16px 18px 14px;background:rgba(255,255,255,.025)}
.pl-art .ob-tl .ob-tl-p{font:600 11.5px/1.2 'Avenir Next','Segoe UI',system-ui,sans-serif;letter-spacing:.16em;text-transform:uppercase;color:rgb(var(--acc-rgb));margin:2px 0 6px}
.pl-art .ob-tl h3{font:600 23px/1.2 'Cormorant Garamond',Georgia,serif;color:#fff7e8;margin:0 0 8px}
.pl-art .ob-tl p{font-size:15.5px;line-height:1.65;margin:0 0 10px}
.ob-tl-s,.ob-tl-f{list-style:none;padding:0;margin:2px 0 10px;display:flex;flex-wrap:wrap;gap:8px}
.ob-tl-s a{display:flex;align-items:center;gap:9px;padding:4px 14px 4px 4px;border:1px solid rgba(var(--acc-rgb),.42);border-radius:99px;background:rgba(var(--acc-rgb),.08);text-decoration:none;color:var(--ink);font:500 13.5px/1.25 'Avenir Next','Segoe UI',system-ui,sans-serif}
.ob-tl-s a:hover{border-color:rgba(var(--acc-rgb),.9);background:rgba(var(--acc-rgb),.16)}
.pl-art .ob-tl-s img{width:34px;height:34px;flex:0 0 34px;margin:0;border:0;border-radius:50%;background:rgba(10,10,20,.45)}
.ob-tl-s em{display:block;font:normal 11.5px/1.2 'Avenir Next',sans-serif;color:var(--dim);margin-top:2px}
.ob-tl-f a,.ob-tl-f .nl{display:flex;align-items:center;gap:7px;padding:3px 12px 3px 3px;border:1px solid var(--line);border-radius:99px;color:var(--muted);text-decoration:none;font:500 12.5px/1.2 'Avenir Next','Segoe UI',system-ui,sans-serif}
.ob-tl-f a:hover{color:var(--gold);border-color:rgba(212,175,106,.6)}
.pl-art .ob-tl-f img{width:26px;height:26px;flex:0 0 26px;margin:0;border:0}
.ob-tl-gr{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:6px 0 2px}
.ob-tl-gr>div{border-radius:14px;padding:10px 13px;background:rgba(var(--acc-rgb),.07);border:1px solid rgba(var(--acc-rgb),.22)}
.ob-tl-gr>div+div{background:rgba(212,175,106,.07);border-color:rgba(212,175,106,.28)}
.ob-tl-gr b{display:block;font:600 10.5px/1.2 'Avenir Next',sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--gold);margin:0 0 4px}
.pl-art .ob-tl .ob-tl-gr p{margin:0;font-size:14px;line-height:1.5;color:var(--ink)}
.pl-art .ob-prog .ob-prog-fin{display:flex;gap:10px;align-items:flex-start;margin:6px 0 16px 62px;font-size:15.5px;color:var(--ink)}
.ob-prog-fin span{color:var(--gold)}
.pl-art .ob-prog .ob-prog-cta{margin:0 0 0 62px}
.pl-art .ob-prog-cta a{display:inline-block;font:600 15px/1 'Avenir Next','Segoe UI',system-ui,sans-serif;text-decoration:none;border-radius:99px;padding:13px 22px;background:linear-gradient(135deg,#D4AF6A,#b8934f);color:#161122}
.pl-art .ob-prog-cta a:hover{filter:brightness(1.08)}
.ob-hub-p{display:block;font:600 11.5px/1.3 'Avenir Next',sans-serif;letter-spacing:.06em;color:var(--gold);margin:0 0 6px}
@media(max-width:700px){.ob-road{display:none}}
@media(max-width:560px){.ob-prog{padding:22px 16px 18px;border-radius:20px}.ob-tl::before{left:17px}.ob-tl>li{padding-left:48px}
 .ob-tl>li::before{width:36px;height:36px;font-size:16px}.ob-tl>li>div{padding:14px 14px 12px}.ob-tl-gr{grid-template-columns:1fr}
 .pl-art .ob-prog .ob-prog-fin,.pl-art .ob-prog .ob-prog-cta{margin-left:0}}
@media(max-width:560px){.ob-pitch{padding:20px 18px 8px}.ob-med a{grid-template-columns:52px minmax(0,1fr);gap:12px}.pl-art .ob-med img{width:52px;height:52px}
 .ob-hub a{grid-template-columns:60px minmax(0,1fr)}.ob-hub img{width:60px;height:60px}}
"""

_C = {}


def charge(nom):
    f = os.path.join(T, nom)
    if not os.path.exists(f): return None
    m = os.path.getmtime(f)
    if _C.get(nom, (None,))[0] != m:
        _C[nom] = (m, json.load(open(f, encoding='utf-8')))
    return _C[nom][1]


def textes(lang):
    return charge(f'objectifs_{lang}.json')


def chemin(lang, num=None, D=None):
    """Adresse publique : page d'ensemble (num=None) ou page d'un objectif ; None si absente dans cette langue."""
    D = D if D is not None else textes(lang)
    if not D: return None
    if num is None: return f'/{lang}/{DIR[lang]}/'
    o = D['objectifs'].get(num)
    return f'/{lang}/{DIR[lang]}/{o["slug"]}.html' if o else None


def boutons(lang):
    """[(numéro, libellé court, adresse, icône)] des 14 objectifs, pour l'accueil et les menus."""
    D = textes(lang); I = charge('icones_site.json') or {}
    if not D: return []
    return [(n, o['titre_court'], chemin(lang, n, D), (I.get('objectifs', {}).get(n) or {}).get('src'))
            for n, o in sorted(D['objectifs'].items())]


def par_seance(lang):
    """{id de séance: [(numéro, libellé court, adresse, intérêt pour cet objectif)]} pour les pages catégories."""
    D = textes(lang)
    if not D: return {}
    cle = ('par_seance', lang, _C.get(f'objectifs_{lang}.json', (None,))[0])
    if cle in _C: return _C[cle]
    out = {}
    for n, o in sorted(D['objectifs'].items()):
        for mid, interet in o['seances'] + o.get('a_venir', []):
            out.setdefault(mid, []).append((n, o['titre_court'], chemin(lang, n, D), interet))
    _C[cle] = out
    return out


def ty(lang, s):
    """Typographie française des pages piliers (espaces insécables avant : ; ! ?)."""
    if lang != 'fr' or not isinstance(s, str): return s
    s = re.sub(r' ([:»])', ' \\1', s)
    s = re.sub(r' ([;!?])', ' \\1', s)
    return s.replace('« ', '« ').replace("'", '’')


def photo(ap, lang, key, sujet=None):
    """(balise <img> de l'en-tête, chemin, alt) depuis _queue/photos.json : WebP 760 px et 440 px.
    07-11 : « sujet » (l'objectif de la page) précède la description de la photo dans l'alt, comme le mot principal."""
    P = {x['id']: x for x in json.load(open(os.path.join(ROOT, '_queue', 'photos.json'), encoding='utf-8'))}
    x = P[PHOTO[key]]
    src, s440 = '/assets/blog/' + x['src'], '/assets/blog/' + x['src_s']
    alt = x.get(f'alt_{lang}') or x['alt_fr']
    if sujet:
        alt = f"{sujet}{' : ' if lang == 'fr' else ': '}{alt[0].lower()}{alt[1:]}"
    titre = alt if len(alt) <= 70 else alt[:alt.rfind(' ', 0, 66)].rstrip(' ,;:') + '…'
    tag = (f'<img src="{ap.rel(src, DEPTH)}" srcset="{ap.rel(s440, DEPTH)} 440w, {ap.rel(src, DEPTH)} 760w" sizes="(max-width: 860px) 62vw, 360px" '
           f'alt="{E(alt)}" title="{E(titre)}"{ap.dims(src)} fetchpriority="high" decoding="async">')
    return tag, src, alt


def icone(ap, src, alt, titre, extra=''):
    if not src: return ''
    return f'<img src="{ap.rel(src, DEPTH)}" alt="{E(alt)}" title="{E(titre[:70])}"{ap.dims(src)} loading="lazy" decoding="async"{extra}>'


def icone_med(ap, lang, mid, titre):
    IM = charge('icones_meditations.json') or {}
    v = IM.get(mid)
    if not v: return ''
    src = v if isinstance(v, str) else v.get('src')
    alt = (v.get('alt') or {}).get(lang) if isinstance(v, dict) else None
    if not alt:
        alt = {'fr': f'Symbole de la méditation « {titre} »', 'en': f'Symbol of the meditation “{titre}”', 'es': f'Símbolo de la meditación «{titre}»'}[lang]
    return icone(ap, src, alt, titre)


def lien_fonction(ap, lang, nom_fr, P):
    import piliers
    if nom_fr in LIEN_THEME:
        return ap.theme_path(lang, LIEN_THEME[nom_fr])
    if nom_fr in LIEN_PILIER:
        return piliers.path(ap, lang, LIEN_PILIER[nom_fr])
    if nom_fr == 'Mondes immersifs':
        return ap.u(lang, 'world')
    if nom_fr == 'Catalogue multithématique':
        return ap.u(lang, 'med')
    return None


def faits(lang, n_seances, n_cats, n_mondes):
    o = OL[lang]
    out = [f'{n_seances} {o["seances"] if n_seances > 1 else o["seance"]}']
    if n_cats: out.append(f'{n_cats} {o["cats"] if n_cats > 1 else o["cat"]}')
    if n_mondes: out.append(f'{n_mondes} {o["mondes"] if n_mondes > 1 else o["monde"]}')
    return ''.join(f'<li data-calc>{E(x)}</li>' for x in out) + ''.join(f'<li>{E(x)}</li>' for x in (o['free'], o['noads'], o['offline']))


def seances_visibles(o, meds):
    """Séances de l'objectif présentes dans le catalogue filtré (a_venir.json) : [(cid, med, intérêt)] dans l'ordre du document."""
    out = []
    for mid, interet in o['seances'] + o.get('a_venir', []):
        if mid in meds:
            cid, m = meds[mid]
            out.append((cid, m, interet))
    return out


def programme_html(ap, lang, o, meds, P):
    """06-11 (Edouard : « sur chacune des 14 pages objectif, ajoute un programme en plusieurs étapes pour réussir à cet objectif…
    design super, optimisé par rapport aux statistiques des mots-clés ») : parcours en 3 à 5 étapes (période, but, séances
    avec icône, fonctionnalités, geste du jour, repère de progrès), titre bâti sur les recherches réelles (défi méditation,
    daily meditation, rutina para dormir…). Seules les séances du catalogue filtré (a_venir.json) sont montrées."""
    import piliers   # rich() : [ancre](/chemin) → lien interne vers la page qui porte le mot-clé
    pr = o.get('programme')
    if not pr: return ''
    ol = OL[lang]; I = charge('icones_site.json') or {}
    noms = {f[0]: f[1] for f in o['fonctions']}
    etapes, n_s = '', 0
    for e in pr['etapes']:
        ss = ''
        for mid in e['seances']:
            if mid not in meds: continue
            cid, m = meds[mid]; n_s += 1
            url = ap.u(lang, 'med', P[lang]['categories'][cid]['slug']) + '#' + mid
            ss += (f'<li><a href="{url}">{icone_med(ap, lang, mid, m["title"][lang])}<span>{E(m["title"][lang])}'
                   f'<em>{m["dur"]} {E(ol["min"])} · {E(ap.L[lang]["level"].get(m["level"], m["level"]))}</em></span></a></li>')
        fs = ''
        for nf in e.get('fonctions', []):
            ic = (I.get('fonctions') or {}).get(nf) or {}
            nom = noms.get(nf, nf)
            h = lien_fonction(ap, lang, nf, P)
            dedans = icone(ap, ic.get('src'), (ic.get('alt') or {}).get(lang, nom), nom) + f'<span>{E(ty(lang, nom))}</span>'
            fs += '<li>' + (f'<a href="{h}">{dedans}</a>' if h else f'<span class="nl">{dedans}</span>') + '</li>'
        etapes += (f'<li><div><p class="ob-tl-p">{E(ty(lang, e["periode"]))}</p><h3>{E(ty(lang, e["titre"]))}</h3><p>{piliers.rich(ty(lang, e["texte"]))}</p>'
                   + (f'<ul class="ob-tl-s" aria-label="{E(ol["seances_cap"])}">{ss}</ul>' if ss else '')
                   + (f'<ul class="ob-tl-f">{fs}</ul>' if fs else '')
                   + f'<div class="ob-tl-gr"><div><b>{E(ol["geste"])}</b><p>{E(ty(lang, e["geste"]))}</p></div>'
                   f'<div><b>{E(ol["repere"])}</b><p>{E(ty(lang, e["repere"]))}</p></div></div></div></li>')
    faits_p = ''.join(f'<li>{E(ty(lang, x))}</li>' for x in (pr['duree'], pr['rythme'])) + \
        f'<li>{len(pr["etapes"])} {E(ol["etapes_n"])}</li><li data-calc>{n_s} {E(ol["seances"] if n_s > 1 else ol["seance"])}</li>'
    return (f'<section id="programme" class="ob-prog"><p class="ob-prog-eye"><span aria-hidden="true">✦</span> {E(ol["prog_eye"])}</p>'
            f'<h2>{E(ty(lang, pr["titre"]))}</h2><p class="ob-prog-intro">{E(ty(lang, pr["intro"]))}</p><ul class="ob-prog-facts">{faits_p}</ul>'
            + '<ol class="ob-road" aria-hidden="true">' + ''.join(
                f'<li><b>{i}</b><span>{E(ty(lang, e["periode"]))}</span><em>{E(ty(lang, e["titre"]))}</em></li>' for i, e in enumerate(pr['etapes'], 1)) + '</ol>'
            f'<ol class="ob-tl">{etapes}</ol><p class="ob-prog-fin"><span aria-hidden="true">✦</span>{E(ty(lang, pr["apres"]))}</p>'
            f'<p class="ob-prog-cta"><a href="/{lang}/#download">✦ {E(ol["prog_cta"])}</a></p></section>')


def plus_loin(ap, bb, lang, num, sel):
    """Guides complets et pages de fonctionnalités du thème, puis les articles du blog de la catégorie principale de l'objectif."""
    import piliers
    from collections import Counter
    pl, th = PLUS.get(num, ([], []))
    li = piliers.links_li(ap, lang, pl)
    TH = ap.charge('themes', lang) or {}
    li += ''.join(f'<li><a href="{ap.theme_path(lang, k)}">{E(TH[k]["h1"])}</a></li>' for k in th if k in TH)
    h = f'<section id="plus"><h2>{E(ap.L[lang]["read"])}</h2><ul class="ap-links">{li}</ul></section>' if li else ''
    if sel:
        cid = Counter(c for c, _, _ in sel).most_common(1)[0][0]
        h += ap.blog_cat_html(bb, lang, cid)
    return h


def render(ap, bb, lang, num, D, cat, P):
    import piliers
    o = D['objectifs'][num]; ol = OL[lang]; t = ap.L[lang]
    me = chemin(lang, num, D)
    alts = {x: chemin(x, num) for x in LANGS if chemin(x, num)}
    meds = {m['id']: (cid, m) for cid, c in cat['categories'].items() for m in c['meds']}
    sel = seances_visibles(o, meds)
    I = charge('icones_site.json') or {}
    tc = ty(lang, o['titre_court'])
    tag, src, img_alt = photo(ap, lang, num, o.get('titre_court'))
    # séances, rangées par catégorie (dans l'ordre où le document les cite)
    groupes = {}
    for cid, m, interet in sel:
        groupes.setdefault(cid, []).append((m, interet))
    bloc_seances = ''
    for cid, ms in groupes.items():
        url_cat = ap.u(lang, 'med', P[lang]['categories'][cid]['slug'])
        nom_cat = cat['categories'][cid]['name'][lang]
        vig = ap.img_tag(ap.cat_key(cid), lang, 260, ap.img_cat(cid), DEPTH, ' loading="lazy" decoding="async"')
        bloc_seances += (f'<div class="ob-cat"><a class="ob-cath" href="{url_cat}">{vig}<span><b>{E(nom_cat)}</b>'
                         f'<em data-calc>{len(ms)} {E(ol["seances"] if len(ms) > 1 else ol["seance"])} {E(ol["dans"])} · {E(ol["voir_cat"])} →</em></span></a>'
                         '<ol class="ob-med">' + ''.join(
                             f'<li><a href="{url_cat}#{E(m["id"])}">{icone_med(ap, lang, m["id"], m["title"][lang])}<span><b>{E(m["title"][lang])}</b>'
                             f'<em>{m["dur"]} {E(ol["min"])} · {E(t["level"].get(m["level"], m["level"]))}</em><span>{E(ty(lang, interet))}</span></span></a></li>'
                             for m, interet in ms) + '</ol></div>')
    # fonctionnalités
    bloc_feat = '<ul class="ob-feat">'
    for nom_fr, nom, pourquoi in o['fonctions']:
        ic = (I.get('fonctions') or {}).get(nom_fr) or {}
        h = lien_fonction(ap, lang, nom_fr, P)
        bloc_feat += (f'<li>{icone(ap, ic.get("src"), (ic.get("alt") or {}).get(lang, nom), nom)}<div><b>{E(ty(lang, nom))}</b>'
                      f'<p>{E(ty(lang, pourquoi))}</p>' + (f'<a href="{h}">{E(ol["voir"])} →</a>' if h else '') + '</div></li>')
    bloc_feat += '</ul>'
    # mondes immersifs
    ws = [w for w in o['mondes'] if w in cat['worlds'] and w in P[lang]['worlds']]
    bloc_mondes = ('<ul class="pl-wstrip">' + ''.join(
        f'<li><a href="{ap.u(lang, "world", P[lang]["worlds"][k]["slug"])}">{ap.VIG_MONDE(k, lang)}'
        f'<b>{E(cat["worlds"][k]["name"][lang])}</b><span>{cat["worlds"][k]["minutes"][lang]} {E(ol["min"])}</span></a></li>' for k in ws) + '</ul>') if ws else ''
    faq = [(ty(lang, q), ty(lang, r)) for q, r in o['faq']]
    prog = programme_html(ap, lang, o, meds, P)
    toc = [('pourquoi', ol['t_pitch'])] + ([('programme', ol['t_prog'])] if prog else []) + [('seances', ol['t_seances']), ('fonctionnalites', ol['t_feat'])]
    if bloc_mondes: toc.append(('mondes', ol['t_mondes']))
    toc += [('mode-d-emploi', ol['t_etapes']), ('faq', ol['faq'])]
    autres = ''.join(
        f'<li><a href="{chemin(lang, n, D)}" style="--acc-rgb:{ACC[n]}">'
        + icone(ap, ((I.get('objectifs') or {}).get(n) or {}).get('src'), ((I.get('objectifs') or {}).get(n) or {}).get('alt', {}).get(lang, x['titre_court']), x['titre_court'])
        + f'{E(ty(lang, x["titre_court"]))}</a></li>' for n, x in sorted(D['objectifs'].items()) if n != num)
    nb_cats = len(groupes)
    bc = [(t['home'], f'/{lang}/'), (ol['crumb'], chemin(lang, None, D)), (o['titre_court'], None)]
    body = (f'<div class="pl ob" style="--acc-rgb:{ACC[num]}">' + ap.crumbs(lang, bc)
            + f'<div class="pl-hero"><div class="pl-ht"><p class="pl-eye"><span aria-hidden="true">✦</span>{E(ol["eye"].format(n=int(num), t=len(D["objectifs"])))}</p>'
            f'<h1>{E(ty(lang, o["h1"]))}</h1><p class="pl-lead">{E(ty(lang, o["accroche"]))}</p><ul class="pl-facts">{faits(lang, len(sel), nb_cats, len(ws))}</ul>'
            f'<p class="pl-cta"><a class="b1" href="/{lang}/#download">✦ {E(ol["dl"])}</a>'
            + (f'<a class="b2" href="#programme">{E(ol["see_prog"])} ↓</a>' if prog else f'<a class="b2" href="#seances">{E(ol["see"])} ↓</a>') + '</p></div>'
            f'<figure class="pl-arch">{tag}</figure></div>'
            f'<div class="pl-body"><nav class="pl-toc" aria-label="{E(ol["toc"])}"><b>{E(ol["toc"])}</b><ol>'
            + ''.join(f'<li><a href="#{i}">{E(n)}</a></li>' for i, n in toc) + '</ol></nav><article class="pl-art">'
            + f'<section id="pourquoi" class="ob-pitch"><h2>{E(ol["h_pitch"].format(t=tc))}</h2>' + ''.join(f'<p>{E(ty(lang, x))}</p>' for x in o['pitch']) + '</section>'
            + prog
            + f'<section id="seances"><h2>{E(ol["h_seances"].format(t=tc))}</h2>{bloc_seances}</section>'
            + f'<section id="fonctionnalites"><h2>{E(ol["h_feat"].format(t=tc))}</h2>{bloc_feat}</section>'
            + (f'<section id="mondes"><h2>{E(ol["h_mondes"].format(t=tc))}</h2>{bloc_mondes}</section>' if bloc_mondes else '')
            + f'<section id="mode-d-emploi"><h2>{E(ol["h_etapes"].format(t=tc))}</h2><ol class="pl-steps ob-steps">'
            + ''.join(f'<li><p>{E(ty(lang, x))}</p></li>' for x in o['etapes']) + '</ol></section>'
            + ap.faq_html(lang, faq).replace('<section class="afaq">', '<section class="afaq" id="faq">')
            + plus_loin(ap, bb, lang, num, sel)
            + ap.cta(lang) + '</article></div>'
            + f'<nav class="ob-others" aria-label="{E(ol["autres"])}"><h2>{E(ol["autres"])}</h2><ul>{autres}</ul></nav></div>' + piliers.TOC_JS)
    url = bb.BASE + me
    graph = [{'@type': 'WebPage', '@id': url + '#page', 'name': o['h1'], 'headline': o['h1'], 'description': o['desc'], 'url': url, 'inLanguage': lang,
              'primaryImageOfPage': {'@type': 'ImageObject', 'url': bb.BASE + src, 'caption': img_alt},
              'isPartOf': {'@type': 'WebSite', 'name': 'MeditaDream', 'url': bb.BASE + '/'},
              'about': {'@type': 'MobileApplication', 'name': 'MeditaDream', 'applicationCategory': 'LifestyleApplication',
                        'operatingSystem': 'iOS, Android', 'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR'}}},
             ap.bc_ld(bb, bc),
             {'@type': 'ItemList', 'name': ol['h_seances'].format(t=o['titre_court']), 'numberOfItems': len(sel), 'itemListElement': [
                 {'@type': 'ListItem', 'position': i + 1, 'name': m['title'][lang],
                  'url': bb.BASE + ap.u(lang, 'med', P[lang]['categories'][cid]['slug']) + '#' + m['id']} for i, (cid, m, _) in enumerate(sel)]},
             ({'@type': 'HowTo', 'name': o['programme']['titre'], 'description': o['programme']['intro'], 'step': [
                 {'@type': 'HowToStep', 'position': i + 1, 'name': e['titre'], 'text': piliers.plain(e['texte'])} for i, e in enumerate(o['programme']['etapes'])]}
              if o.get('programme') else
              {'@type': 'HowTo', 'name': ol['h_etapes'].format(t=o['titre_court']), 'step': [
                 {'@type': 'HowToStep', 'position': i + 1, 'text': x} for i, x in enumerate(o['etapes'])]}),
             {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': r}} for q, r in o['faq']]}]
    ld = ap.ld_tag({'@context': 'https://schema.org', '@graph': graph})
    return page(ap, bb, lang, o['seo'], o['desc'], me, alts, src, ld, body, img_alt)


def render_hub(ap, bb, lang, D, cat, P):
    import piliers
    h = D['hub']; ol = OL[lang]; t = ap.L[lang]
    me = chemin(lang, None, D)
    alts = {x: chemin(x) for x in LANGS if chemin(x)}
    meds = {m['id']: (cid, m) for cid, c in cat['categories'].items() for m in c['meds']}
    I = charge('icones_site.json') or {}
    tag, src, img_alt = photo(ap, lang, 'hub')
    cartes = ''
    for n, o in sorted(D['objectifs'].items()):
        ic = (I.get('objectifs') or {}).get(n) or {}
        nb = len(seances_visibles(o, meds)); nw = len([w for w in o['mondes'] if w in cat['worlds']])
        cartes += (f'<li><a href="{chemin(lang, n, D)}" style="--acc-rgb:{ACC[n]}">{icone(ap, ic.get("src"), (ic.get("alt") or {}).get(lang, o["titre_court"]), o["titre_court"])}'
                   f'<div><h2>{E(ty(lang, o["titre_court"]))}</h2><p>{E(ty(lang, o["accroche"]))}</p>'
                   + (f'<span class="ob-hub-p">✦ {E(ol["hub_prog"])} · {E(ty(lang, o["programme"]["duree"]))}</span>' if o.get('programme') else '')
                   + f'<em data-calc>{E(ol["hub_n"].format(a=nb, b=nw))} →</em></div></a></li>')
    total = sum(len(c['meds']) for c in cat['categories'].values())
    bc = [(t['home'], f'/{lang}/'), (ol['crumb'], None)]
    body = (f'<div class="pl ob" style="--acc-rgb:{ACC["hub"]}">' + ap.crumbs(lang, bc)
            + f'<div class="pl-hero"><div class="pl-ht"><p class="pl-eye"><span aria-hidden="true">✦</span>{E(ol["eye_hub"].format(t=len(D["objectifs"])))}</p>'
            f'<h1>{E(ty(lang, h["h1"]))}</h1><p class="pl-lead">{E(ty(lang, h["intro"]))}</p><ul class="pl-facts">{faits(lang, total, len(cat["categories"]), len(cat["worlds"]))}</ul>'
            f'<p class="pl-cta"><a class="b1" href="/{lang}/#download">✦ {E(ol["dl"])}</a><a class="b2" href="#objectifs">{E(ol["h_hub"])} ↓</a></p></div>'
            f'<figure class="pl-arch">{tag}</figure></div>'
            f'<div class="ob-hubw" id="objectifs"><ul class="ob-hub">{cartes}</ul>{ap.cta(lang)}</div></div>')
    url = bb.BASE + me
    graph = [{'@type': 'CollectionPage', 'name': h['h1'], 'description': h['desc'], 'url': url, 'inLanguage': lang,
              'primaryImageOfPage': {'@type': 'ImageObject', 'url': bb.BASE + src, 'caption': img_alt},
              'isPartOf': {'@type': 'WebSite', 'name': 'MeditaDream', 'url': bb.BASE + '/'},
              'mainEntity': {'@type': 'ItemList', 'numberOfItems': len(D['objectifs']), 'itemListElement': [
                  {'@type': 'ListItem', 'position': i + 1, 'name': o['h1'], 'url': bb.BASE + chemin(lang, n, D)} for i, (n, o) in enumerate(sorted(D['objectifs'].items()))]}},
             ap.bc_ld(bb, bc)]
    ld = ap.ld_tag({'@context': 'https://schema.org', '@graph': graph})
    return page(ap, bb, lang, h['seo'], h['desc'], me, alts, src, ld, body, img_alt)


def page(ap, bb, lang, title, desc, me, alts, src, ld, body, img_alt):
    import piliers
    langs = [x for x in LANGS if x in alts]
    h = bb.head(lang, title, desc, lambda x: alts[x], me, src, ld, img_alt=img_alt, og_type='website', langs=langs if langs != LANGS else None)
    h = h.replace('</style>', ap.CSS + piliers.CSS + CSS + '</style>', 1)
    h += ap.header(lang, me, lambda x: alts.get(x, f'/{x}/'))
    foot = bb.footer_html(lang).replace('href="../"', f'href="/{lang}/"').replace('href="./"', f'href="/{lang}/blog/"')
    return h + '<main class="plm">' + body + '</main>' + foot + '</body></html>'


# 07-11 : adresses renommées pour porter le mot principal (pages créées le 06-11) ; l'ancienne adresse renvoie vers la nouvelle
ANCIENNES = {'fr': {'14': ['evasion-mondes-immersifs']}, 'en': {'05': ['emotional-balance']}}


def renvoi(lang, ancien, nouveau, titre):
    """page de renvoi à l'ancienne adresse : rafraîchissement immédiat, canonique vers la nouvelle, hors index."""
    url = f'{BASE_SITE}/{lang}/{DIR[lang]}/{nouveau}.html'
    return (f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><title>{E(titre)}</title>'
            f'<link rel="canonical" href="{url}"><meta name="robots" content="noindex">'
            f'<meta http-equiv="refresh" content="0; url={nouveau}.html"></head>'
            f'<body><p><a href="{nouveau}.html">{E(titre)}</a></p></body></html>')


BASE_SITE = 'https://meditadream.com'


def build(ap, bb, cat, P):
    written = []
    for lang in LANGS:
        D = textes(lang)
        if not D or lang not in P: continue
        os.makedirs(f'{ROOT}/{lang}/{DIR[lang]}', exist_ok=True)
        for num, anciens in ANCIENNES.get(lang, {}).items():
            o = D['objectifs'].get(num)
            for ancien in anciens:
                if o and o['slug'] != ancien:
                    open(f'{ROOT}/{lang}/{DIR[lang]}/{ancien}.html', 'w', encoding='utf-8').write(renvoi(lang, ancien, o['slug'], o['h1']))
        me = chemin(lang, None, D)
        ap._write(me + 'index.html', render_hub(ap, bb, lang, D, cat, P))
        written.append((me, {x: chemin(x) for x in LANGS if chemin(x)}))
        for num in sorted(D['objectifs']):
            me = chemin(lang, num, D)
            ap._write(me, render(ap, bb, lang, num, D, cat, P))
            written.append((me, {x: chemin(x, num) for x in LANGS if chemin(x, num)}))
    return written
