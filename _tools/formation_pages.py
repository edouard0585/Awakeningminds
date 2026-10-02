#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pages « formation à la méditation » par ville (français seulement), demandées par Edouard le 2026-10-02.

  /fr/formation-meditation/               index : France, Belgique, Suisse romande, Luxembourg
  /fr/formation-meditation/<ville>.html   une page par ville (contexte local, sur site ou à distance, formulaire)

Données : _tools/formations_fr.json. Chaque ville a son propre texte (contexte, communes voisines, question) ;
les blocs communs tournent sur trois variantes pour que deux pages ne se répètent pas. Les pages restent
discrètes : un lien en pied de page et un lien sur la page « Méditation en entreprise ». Appelé par app_pages.build().
"""
import json, os

APP = ["Pour apprendre à méditer {a} sans attendre, l’application Awakening Minds est gratuite : sans abonnement, sans publicité, sans compte. Elle propose un parcours pour débutants, des séances de 4 minutes et plus de cent méditations guidées en français, et fonctionne hors ligne.",
       "Pas besoin d’attendre un atelier pour commencer : l’application Awakening Minds est gratuite, sans abonnement ni compte. On y trouve un parcours pour débutants, des séances de 4 minutes pour une pause, et plus de cent méditations guidées en français, à écouter même hors ligne.",
       "Entre deux séances, ou pour débuter seul {a}, l’application Awakening Minds accompagne chacun gratuitement : aucun abonnement, aucune publicité, aucun compte à créer. Parcours pour débutants, séances de 4 minutes, plus de cent méditations guidées en français, utilisables hors ligne."]
DEROULE = ["Tout commence par un échange sur vos attentes : taille de l’équipe, horaires, lieu. Nous vous adressons ensuite une proposition sur mesure. Entre deux séances, chacun continue librement avec l’application.",
           "Un premier échange permet de comprendre votre contexte : nombre de participants, moments possibles dans la journée, salle ou visioconférence. Vous recevez ensuite une proposition écrite, puis les séances démarrent à la date qui vous convient.",
           "Vous nous décrivez votre équipe et vos contraintes ; nous proposons un format, un rythme et un nombre de séances. Rien n’est imposé : on commence souvent par une séance de découverte, et l’on décide de la suite ensemble."]


def lieux(v):
    if v.get('lieux'): return v['lieux']
    if v.get('local'):
        return f"Les séances ont lieu dans vos locaux, {v['a']} et en proche banlieue ({v['voisins']}), ou à distance en visioconférence."
    if v['pays'] == 'France':
        return f"Les séances se tiennent à distance, en visioconférence, ou dans vos locaux {v['a']} et alentour ({v['voisins']}) lorsque le déplacement est possible."
    return f"Les séances se tiennent à distance, en visioconférence. Un déplacement dans vos locaux, {v['a']} et alentour ({v['voisins']}), s’organise sur demande."


def desc(v):
    fin = 'Pour apprendre seul : une application gratuite, sans abonnement.'
    if v.get('local'):
        return f"Formation et ateliers de méditation {v['a']}, dans vos locaux ou à distance. {fin}"
    if v['pays'] == 'France':
        return f"Formation et ateliers de méditation {v['a']}, en entreprise, à distance ou sur site. {fin}"
    return f"Formation et ateliers de méditation {v['a']}, à distance ou sur site sur demande. {fin}"


def form(ap, sujet):
    t, E = ap.L['fr'], ap.E
    return (f'<h2 id="contact-t">{E(t["form_t"])}</h2><form class="ap-form" id="contact" data-sujet="{E(sujet)}" data-ok="{E(t["sent"])}" data-err="{E(t["err"])}">'
            f'<label for="f-name">{E(t["name"])}</label><input id="f-name" name="name" autocomplete="name" maxlength="120">'
            f'<label for="f-co">{E(t["company"])}</label><input id="f-co" name="company" autocomplete="organization" maxlength="120">'
            f'<label for="f-mail">{E(t["email"])}</label><input id="f-mail" name="email" type="email" required autocomplete="email">'
            f'<label for="f-msg">{E(t["msg"])}</label><textarea id="f-msg" name="message" required></textarea>'
            f'<input type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;left:-9999px">'
            f'<p role="status" id="f-st"></p><button type="submit">{E(t["send"])}</button></form>'
            """<script>(function(){var f=document.getElementById('contact');f.addEventListener('submit',function(e){e.preventDefault();
var st=document.getElementById('f-st'),d=new FormData(f),co=d.get('company');d.set('lang','fr');d.set('topic',f.dataset.sujet+(co?' — '+co:''));
d.set('page',location.href);fetch('https://espace.awakeningminds.app/contact',{method:'POST',body:d,headers:{'Accept':'application/json'}})
.then(function(r){return r.json()}).then(function(j){st.textContent=j.ok?f.dataset.ok:(j.message||f.dataset.err);if(j.ok){f.reset();if(window.gtag)gtag('event','generate_lead',{form_id:'formation'})}})
.catch(function(){st.textContent=f.dataset.err})});})();</script>""")


def build(bb, ap):
    """Écrit l'index et les pages de villes ; rend [(chemin, {'fr': chemin})] pour le plan du site."""
    f = os.path.join(ap.T, 'formations_fr.json')
    if not os.path.exists(f): return []
    D = json.load(open(f, encoding='utf-8'))
    E, t = ap.E, ap.L['fr']
    cat, P = ap.load()
    hub, villes = D['hub'], D['villes']
    base = f'/fr/{hub["slug"]}/'
    os.makedirs(f'{ap.ROOT}{base}', exist_ok=True)
    teams = P['fr']['teams']
    img = ap.img_cat('calm')
    written = []
    org = {'@type': 'Organization', 'name': 'Awakening Minds', 'url': bb.BASE + '/'}
    cats = P['fr']['categories']
    app_links = ''.join(f'<li><a href="{ap.u("fr", "med", cats[k]["slug"])}">{E(cat["categories"][k]["name"]["fr"])}</a></li>' for k in ('learningBasics', 'fourMin', 'calm') if k in cats)
    app_links += f'<li><a href="{ap.u("fr", "med")}">Toutes les méditations</a></li>'
    pays = list(hub['pays'].keys())

    # --- une page par ville
    for i, v in enumerate(villes):
        path = f'{base}{v["slug"]}.html'
        titre = f'Formation méditation {v["nom"]} : ateliers et app gratuite'
        h1 = f'Formation méditation {v["a"]} : ateliers en entreprise et pratique gratuite'
        d = desc(v)
        bc = [(t['home'], '/fr/'), ('Formations à la méditation', base), (v['nom'], None)]
        q = [v['faq'],
             ['Combien coûte une formation ?', 'Chaque proposition est construite sur mesure, selon le format, la durée et le nombre de participants. L’application, elle, est gratuite pour tous, sans abonnement ni version payante.'],
             ['Quelles données sont collectées sur les participants ?', 'Aucune. L’application ne demande pas de compte et ne collecte aucune donnée personnelle : les données de pratique restent sur le téléphone de chacun.']]
        autres = [x for x in villes if x['pays'] == v['pays'] and x is not v] or [x for x in villes if x is not v][:6]
        liens = ''.join(f'<li><a href="{x["slug"]}.html">{E(x["nom"])}</a></li>' for x in autres)
        liens += f'<li><a href="./">Toutes les villes</a></li><li><a href="../{teams["slug"]}.html">{E(t["teams"])}</a></li>'
        body = (ap.crumbs('fr', bc) + f'<article><h1>{E(h1)}</h1><p class="lead">{E(d)}</p>'
                f'<h2>Méditer au travail {E(v["a"])}</h2><p>{E(v["contexte"])}</p>'
                f'<h2>Sur site ou à distance</h2><p>{E(lieux(v))}</p>'
                f'<h2>Au programme</h2><ul>' + ''.join(f'<li>{E(b)}</li>' for b in D['programme']) + f'</ul><p>{E(DEROULE[i % 3])}</p>'
                f'<h2>Apprendre à méditer {E(v["a"])}, gratuitement</h2><p>{E(APP[i % 3].format(a=v["a"]))}</p><ul class="ap-links">{app_links}</ul>'
                + form(ap, f'Formation méditation — {v["nom"]}') + ap.cta('fr') + ap.faq_html('fr', q)
                + f'<h2>Autres villes</h2><ul class="ap-links">{liens}</ul></article>')
        zone = {'@type': 'Country', 'name': 'Luxembourg'} if v['pays'] == 'Luxembourg' else {'@type': 'City', 'name': v['nom']}
        ld = ap.ld_tag({'@context': 'https://schema.org', '@graph': [
            {'@type': 'WebPage', 'name': h1, 'description': d, 'url': bb.BASE + path, 'inLanguage': 'fr'},
            {'@type': 'Service', 'name': f'Formation à la méditation {v["a"]}', 'serviceType': 'Formation et ateliers de méditation', 'areaServed': zone,
             'provider': org, 'availableLanguage': 'fr', 'url': bb.BASE + path},
            ap.bc_ld(bb, bc),
            {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': a, 'acceptedAnswer': {'@type': 'Answer', 'text': r}} for a, r in q]}]})
        ap._write(path, ap.page(bb, 'fr', titre, d, path, {'fr': path}, img, ld, body, h1))
        written.append((path, {'fr': path}))

    # --- index
    bc = [(t['home'], '/fr/'), ('Formations à la méditation', None)]
    formats = ''.join(f'<li><h3>{E(a)}</h3><p>{E(b)}</p></li>' for a, b in hub['formats'])
    blocs = ''
    for p in pays:
        vs = [x for x in villes if x['pays'] == p]
        blocs += (f'<h2>{E(p)}</h2><p>{E(hub["pays"][p])}</p><ul class="ap-links">'
                  + ''.join(f'<li><a href="{x["slug"]}.html">Formation méditation {E(x["a"])}</a></li>' for x in vs) + '</ul>')
    body = (ap.crumbs('fr', bc) + f'<article><h1>{E(hub["h1"])}</h1><p class="lead">{E(hub["intro"])}</p>'
            f'<h2>{E(hub["formats_h2"])}</h2><ul class="ap-list">{formats}</ul>{blocs}'
            f'<h2>Pour les entreprises</h2><p>Le détail des ateliers, le déroulement et le formulaire de contact se trouvent sur la page '
            f'<a href="../{teams["slug"]}.html">{E(teams["h1"].split(" :")[0])}</a>.</p>' + ap.cta('fr') + '</article>')
    ld = ap.ld_tag({'@context': 'https://schema.org', '@graph': [
        {'@type': 'CollectionPage', 'name': hub['h1'], 'description': hub['desc'], 'url': bb.BASE + base, 'inLanguage': 'fr'},
        ap.bc_ld(bb, bc),
        {'@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': n + 1, 'name': f'Formation méditation {x["a"]}', 'url': f'{bb.BASE}{base}{x["slug"]}.html'} for n, x in enumerate(villes)]}]})
    ap._write(base + 'index.html', ap.page(bb, 'fr', hub['seo'], hub['desc'], base, {'fr': base}, img, ld, body, hub['h1']))
    written.append((base, {'fr': base}))
    return written
