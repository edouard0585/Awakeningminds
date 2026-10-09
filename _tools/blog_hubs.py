#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pages thématiques du blog (une par thème et par langue) : /{lang}/blog/<thème>.html

Elles regroupent les articles publiés du thème (série du lundi + articles du mercredi/samedi),
avec une introduction écrite pour chaque langue (jamais traduite mot à mot), CollectionPage + ItemList
+ BreadcrumbList, et des liens vers les autres thèmes. Une page n'existe que si le thème compte au moins
2 articles publiés dans la langue (pas de page mince) ; elle grandit seule à chaque publication.
Appelé par blog_build.build(). Stdlib uniquement.
"""
import json, os, html
import blog_fr

E = html.escape
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIN_ARTICLES = 2

# Série trilingue du lundi → thème
SERIES_GROUP = {
    'intro': 'bases', 'posture': 'bases', 'respiration': 'bases', 'scan': 'bases', 'pensees': 'bases',
    'pleineconscience': 'bases', 'cinqminutes': 'bases', 'matin': 'bases', 'programme': 'bases',
    'techniques': 'bases', 'marche': 'bases', 'bienveillance': 'bases', 'quotidien': 'vie',
    'science': 'bases', 'histoire': 'bases', 'interactives': 'bases',
    'dormir': 'sommeil', 'reve': 'sommeil', 'emc': 'transe', 'chakras': 'energie', 'ombre': 'psy',
    'symboles': 'lieux', 'astral': 'astral',
}
ORDER = ['bases', 'sommeil', 'energie', 'psy', 'transe', 'vie', 'lieux', 'chamanisme', 'astral']

# Chaque langue a son propre angle de recherche : slug, titre Google (≤ 60), description (≤ 155), h1, intro.
HUBS = {
 'fr': {
  'bases': dict(slug='pratique-de-la-meditation',
    seo="Apprendre à méditer : guides pratiques pour débutants",
    desc="Posture, respiration, pensées, techniques : tous nos guides pour apprendre à méditer pas à pas, avec schémas, sans jargon et sans abonnement.",
    h1="Pratique de la méditation : les guides",
    intro="Méditer s'apprend comme un geste : on s'assoit, on revient au souffle, on recommence. Ces guides reprennent les bases une à une (posture, respiration, gestion des pensées, durée idéale, techniques classiques) pour vous permettre de pratiquer seul, chez vous, en quelques minutes par jour. Chaque article est illustré de schémas et se termine par une pratique concrète."),
  'sommeil': dict(slug='sommeil-et-reves',
    seo="Sommeil et rêves : méditer pour mieux dormir",
    desc="Insomnie, rituel du soir, rêve lucide, paralysie du sommeil, yoga nidra : comprendre la nuit et retrouver un sommeil apaisé grâce à la méditation.",
    h1="Sommeil et rêves",
    intro="La nuit occupe un tiers de notre vie, et c'est souvent là que le stress se voit le plus. Vous trouverez ici de quoi préparer le sommeil (rituel du soir, méditation guidée, NSDR), comprendre les phénomènes étranges de l'endormissement (hypnagogie, paralysie du sommeil) et explorer les rêves : s'en souvenir, les interpréter, devenir lucide."),
  'energie': dict(slug='chakras-et-energie',
    seo="Chakras, chi et kundalini : le guide honnête",
    desc="Chakra racine, chakra du cœur, troisième œil, chi, kundalini, aura, qi gong : traditions énergétiques expliquées avec rigueur et exercices concrets.",
    h1="Chakras et énergie",
    intro="Chakras, chi, kundalini, aura : ces cartes du corps viennent de traditions anciennes et parlent encore à beaucoup de pratiquants. Nos articles les présentent pour ce qu'elles sont, des outils symboliques d'attention, en distinguant ce que disent les traditions de ce que mesure la science, et en proposant à chaque fois des exercices simples à essayer."),
  'psy': dict(slug='emotions-et-vie-interieure',
    seo="Émotions et vie intérieure : apaiser son mental",
    desc="Travail de l'ombre, enfant intérieur, critique intérieur, peurs, rumination, larmes en méditation : des pratiques douces pour mieux vivre avec soi.",
    h1="Émotions et vie intérieure",
    intro="La méditation ne sert pas à ne plus rien ressentir : elle aide à rencontrer ce qui est là sans s'y noyer. Ces articles abordent les émotions, l'ombre, l'enfant intérieur, la rumination ou la peur avec des exercices courts, des repères issus de la psychologie et, quand c'est utile, une invitation claire à se faire accompagner."),
  'transe': dict(slug='transe-et-etats-de-conscience',
    seo="Transe et états modifiés de conscience : guide",
    desc="Transe, hypnose, flow, respiration holotropique, chant diphonique : comprendre les états modifiés de conscience, sans substance et en sécurité.",
    h1="Transe et états de conscience",
    intro="La transe n'est pas réservée aux chamanes : l'absorption dans un livre, le flow d'un sportif ou l'hypnose en sont des cousines. Ce thème explore les états modifiés de conscience sans substance, ce que la science en mesure, comment y entrer et en revenir en sécurité, et comment garder une trace de ses expériences."),
  'vie': dict(slug='meditation-au-quotidien',
    seo="Méditation au quotidien : travail, sport, études",
    desc="Méditer pour mieux travailler, décider, écouter, réviser ses examens ou progresser en sport : la pleine conscience appliquée à la vie de tous les jours.",
    h1="La méditation au quotidien",
    intro="La pratique prend tout son sens en dehors du coussin. Ces articles montrent comment la méditation s'invite au travail, dans le couple, chez les parents, dans les études ou le sport, avec des exercices de quelques minutes et ce que la recherche permet réellement d'en attendre, sans promesse miracle."),
  'lieux': dict(slug='lieux-sacres-et-sagesses',
    seo="Lieux sacrés, mythes et sagesses du monde",
    desc="Montagnes sacrées, Ryōan-ji, Compostelle, Atlantide, bain de forêt, silence, memento mori : voyages et idées qui nourrissent la vie intérieure.",
    h1="Lieux sacrés, mythes et sagesses",
    intro="Certains lieux et certaines idées traversent les siècles parce qu'ils parlent à quelque chose de profond en nous. Montagnes sacrées, jardins zen, chemins de pèlerinage, mythes comme l'Atlantide ou la bibliothèque d'Alexandrie : ces articles racontent leur histoire réelle et ce qu'ils peuvent apporter à une pratique méditative aujourd'hui."),
  'chamanisme': dict(slug='chamanisme',
    seo="Chamanisme : traditions, pratiques et respect",
    desc="Chamanisme sibérien, amazonien, celtique, coréen, tambour, animal de pouvoir, roue de médecine : comprendre les traditions et pratiquer avec respect.",
    h1="Chamanisme",
    intro="Du mot « chamane », né en Sibérie, aux mudang de Corée et aux icaros d'Amazonie, le chamanisme recouvre des traditions très différentes. Nos articles les présentent avec précision, expliquent les pratiques transmises (voyage au tambour, animal de pouvoir, offrandes) et posent la question essentielle du respect des cultures dont elles viennent."),
  'astral': dict(slug='voyage-astral-et-signes',
    seo="Voyage astral, sorties de corps et synchronicités",
    desc="Projection astrale, sortie de corps, rêve lucide, signes, synchronicités : ce que l'on sait, ce que l'on ignore et comment explorer prudemment.",
    h1="Voyage astral et signes",
    intro="Sorties de corps, voyage astral, plumes et synchronicités : ces expériences fascinent autant qu'elles intriguent. Ce thème présente les techniques décrites par les pratiquants, ce que la science a observé, et une façon d'explorer ces expériences avec curiosité tout en gardant son esprit critique."),
 },
 'en': {
  'bases': dict(slug='meditation-practice',
    seo="How to Meditate: Practical Guides for Beginners",
    desc="Posture, breathing, wandering thoughts, session length, techniques: step-by-step meditation guides with diagrams, free and jargon-free.",
    h1="Meditation practice guides",
    intro="Meditation is a skill you build one small repetition at a time: sit down, come back to the breath, start again. These guides cover the essentials (posture, breathing, handling thoughts, how long to sit, classic techniques) so you can practice on your own, at home, in just a few minutes a day. Each one comes with diagrams and a simple exercise."),
  'sommeil': dict(slug='sleep-and-dreams',
    seo="Sleep and Dreams: Meditation for Better Nights",
    desc="Insomnia, bedtime routines, lucid dreaming, sleep paralysis, yoga nidra and NSDR: understand your nights and sleep more peacefully with meditation.",
    h1="Sleep and dreams",
    intro="We spend a third of our lives asleep, and that is often where stress shows up first. Here you will find practical ways to wind down (bedtime routine, guided meditation, NSDR), clear explanations of the strange things that happen as you drift off (hypnagogia, sleep paralysis), and tools to explore your dreams: remembering them, interpreting them, becoming lucid."),
  'energie': dict(slug='chakras-and-energy',
    seo="Chakras, Chi and Kundalini: An Honest Guide",
    desc="Root and heart chakras, third eye, chi, kundalini, aura and qigong: energy traditions explained clearly, with simple exercises you can try today.",
    h1="Chakras and energy",
    intro="Chakras, chi, kundalini and the aura come from ancient traditions that still resonate with many practitioners. Our articles present them for what they are, symbolic maps that train attention, separating what the traditions teach from what science has measured, and always ending with simple practices you can try."),
  'psy': dict(slug='emotions-and-inner-life',
    seo="Emotions and Inner Life: Calm Your Mind Gently",
    desc="Shadow work, inner child, inner critic, fear, rumination, crying in meditation: gentle, practical tools to live more easily with yourself.",
    h1="Emotions and inner life",
    intro="Meditation is not about feeling nothing; it helps you meet what is there without drowning in it. These articles explore emotions, the shadow, the inner child, rumination and fear through short exercises, insights from psychology and, where it matters, a clear nudge toward professional support."),
  'transe': dict(slug='trance-and-altered-states',
    seo="Trance and Altered States of Consciousness",
    desc="Trance, hypnosis, flow, holotropic breathwork, overtone singing: understand altered states of consciousness, substance-free and safely.",
    h1="Trance and altered states",
    intro="Trance is not reserved for shamans: getting lost in a book, an athlete's flow and hypnosis are all close relatives. This topic explores substance-free altered states of consciousness, what research can actually measure, how to enter and come back safely, and how to keep a record of your experiences."),
  'vie': dict(slug='meditation-in-daily-life',
    seo="Meditation in Daily Life: Work, Sport, Study",
    desc="Meditation for focus at work, better decisions, deeper listening, exam stress and sports performance: mindfulness applied to everyday life.",
    h1="Meditation in daily life",
    intro="Practice really pays off once you step off the cushion. These articles show how meditation fits into work, relationships, parenting, studying and sport, with exercises that take a few minutes and an honest look at what the research supports, with no miracle promises."),
  'lieux': dict(slug='sacred-places-and-wisdom',
    seo="Sacred Places, Myths and World Wisdom",
    desc="Sacred mountains, Ryōan-ji, the Camino, Atlantis, forest bathing, silence and memento mori: journeys and ideas that feed the inner life.",
    h1="Sacred places, myths and wisdom",
    intro="Some places and ideas endure for centuries because they speak to something deep in us. Sacred mountains, Zen gardens, pilgrimage routes, myths like Atlantis or the Library of Alexandria: these articles tell their real history and what they can bring to a meditation practice today."),
  'chamanisme': dict(slug='shamanism',
    seo="Shamanism: Traditions, Practices and Respect",
    desc="Siberian, Amazonian, Celtic and Korean shamanism, the drum, power animals, the medicine wheel: understand the traditions and practice respectfully.",
    h1="Shamanism",
    intro="From the word “shaman”, born in Siberia, to Korea's mudang and the icaros of the Amazon, shamanism covers very different traditions. Our articles describe them accurately, explain the practices that have been passed down (drum journeys, power animals, offerings) and ask the essential question of respect for the cultures they come from."),
  'astral': dict(slug='astral-projection-and-signs',
    seo="Astral Projection, OBEs and Synchronicities",
    desc="Astral projection, out-of-body experiences, lucid dreams, everyday signs and synchronicities: what we know, what we don't, and how to explore carefully.",
    h1="Astral projection and signs",
    intro="Out-of-body experiences, astral projection, feathers and synchronicities fascinate as much as they puzzle. This topic covers the techniques practitioners describe, what science has observed, and a way to explore these experiences with curiosity while keeping a critical mind."),
 },
 'es': {
  'bases': dict(slug='practica-de-la-meditacion',
    seo="Cómo meditar: guías prácticas para principiantes",
    desc="Postura, respiración, pensamientos, técnicas: guías paso a paso para aprender a meditar en casa, con esquemas, sin tecnicismos y gratis.",
    h1="Práctica de la meditación: las guías",
    intro="Meditar se aprende como cualquier hábito: te sientas, vuelves a la respiración y empiezas de nuevo. Estas guías repasan lo esencial (postura, respiración, cómo manejar los pensamientos, técnicas clásicas) para que puedas practicar por tu cuenta, en casa, unos minutos al día. Cada artículo incluye esquemas y una práctica concreta."),
  'sommeil': dict(slug='sueno-y-suenos',
    seo="Dormir mejor con meditación: sueño y sueños",
    desc="Insomnio, rutina nocturna, sueño lúcido y meditación guiada para dormir: entiende tus noches y recupera un descanso tranquilo.",
    h1="Sueño y sueños",
    intro="Pasamos un tercio de la vida durmiendo, y es ahí donde el estrés suele notarse primero. Aquí encontrarás formas sencillas de prepararte para dormir, explicaciones claras de lo que ocurre al quedarte dormido y herramientas para explorar tus sueños, recordarlos e incluso volverte lúcido."),
  'energie': dict(slug='chakras-y-energia',
    seo="Chakras y energía: guía clara para meditar",
    desc="Los 7 chakras explicados con sencillez: un mapa simbólico del cuerpo para guiar la atención en la meditación, con ejercicios prácticos.",
    h1="Chakras y energía",
    intro="Los chakras y otras tradiciones energéticas proponen mapas del cuerpo que muchos practicantes usan para guiar la atención. Te los presentamos tal como son, herramientas simbólicas, distinguiendo lo que enseña la tradición de lo que ha medido la ciencia, y con ejercicios sencillos para probar."),
  'psy': dict(slug='emociones-y-vida-interior',
    seo="Emociones y vida interior: calmar la mente",
    desc="Trabajo con la sombra, emociones difíciles y pensamientos repetitivos: prácticas suaves de meditación para vivir mejor contigo mismo.",
    h1="Emociones y vida interior",
    intro="Meditar no consiste en dejar de sentir: ayuda a acoger lo que aparece sin ahogarse en ello. Estos artículos abordan las emociones, la sombra y los pensamientos repetitivos con ejercicios breves y referencias de la psicología, y te invitan a pedir ayuda profesional cuando hace falta."),
  'transe': dict(slug='trance-y-estados-de-conciencia',
    seo="Estados modificados de conciencia y trance",
    desc="Trance meditativo, hipnosis, flow: comprende los estados modificados de conciencia sin sustancias y cómo explorarlos con seguridad.",
    h1="Trance y estados de conciencia",
    intro="El trance no es exclusivo de los chamanes: concentrarse en un libro, el flow de un deportista o la hipnosis son parientes cercanos. Este tema explora los estados modificados de conciencia sin sustancias, lo que la ciencia puede medir y cómo practicarlos con seguridad."),
  'vie': dict(slug='meditacion-en-el-dia-a-dia',
    seo="Meditar cada día: crear un hábito que dure",
    desc="Cómo integrar la meditación en tu rutina diaria: el mejor momento, pocos minutos al día y trucos para no abandonar la práctica.",
    h1="La meditación en el día a día",
    intro="La práctica cobra sentido fuera del cojín. Estos artículos te ayudan a integrar la meditación en tu rutina, en el trabajo o en casa, con ejercicios de pocos minutos y expectativas realistas, sin promesas milagrosas."),
  'lieux': dict(slug='simbolos-y-sabiduria',
    seo="Símbolos, arquetipos y sabiduría del mundo",
    desc="Por qué la meditación habla con imágenes: símbolos, arquetipos, lugares sagrados y mundos interiores explicados con sencillez.",
    h1="Símbolos y sabiduría",
    intro="Templos, bosques, montañas: las meditaciones guiadas hablan con imágenes por una razón. Estos artículos explican el papel de los símbolos y los arquetipos, y lo que los grandes lugares y relatos de la humanidad pueden aportar hoy a tu práctica."),
  'chamanisme': dict(slug='chamanismo',
    seo="Chamanismo: tradiciones, prácticas y respeto",
    desc="Tradiciones chamánicas del mundo, el tambor, el animal de poder: comprende su historia y practica con respeto.",
    h1="Chamanismo",
    intro="El chamanismo reúne tradiciones muy distintas, de Siberia a la Amazonía. Nuestros artículos las presentan con rigor, explican las prácticas transmitidas y plantean la cuestión esencial del respeto a las culturas de las que proceden."),
  'astral': dict(slug='viaje-astral',
    seo="Viaje astral paso a paso, sin sensacionalismo",
    desc="De la relajación profunda a las técnicas de salida: la progresión del viaje astral, lo que se sabe y cómo explorar con prudencia.",
    h1="Viaje astral",
    intro="El viaje astral fascina e inquieta a partes iguales. Aquí encontrarás una progresión clara, de la relajación profunda a las técnicas que describen los practicantes, junto con lo que la ciencia ha observado y una invitación a explorar con espíritu crítico."),
 },
}
LBL = {'fr': dict(blog='Le blog', themes='Tous les thèmes', n='articles', read='Lire'),
       'en': dict(blog='The blog', themes='All topics', n='articles', read='Read'),
       'es': dict(blog='El blog', themes='Todos los temas', n='artículos', read='Leer')}


def items(bb, lang):
    """Articles publiés de la langue, par thème : [(date, ordre, dict)]."""
    by = {g: [] for g in ORDER}
    for a in bb.load():
        if not a.get('published'): continue
        g = SERIES_GROUP.get(a['id'], 'bases')
        img = None
        if a.get('image') is not None:
            img = f"{bb.SCHEMA_FILES[a['image']][lang]}-{lang}.webp"
        by[g].append((a['published'], '', dict(slug=a['slug'][lang], title=a['title'][lang], desc=a['desc'][lang], img=img)))
    if lang in ('fr', 'en', 'es'):
        for a0 in blog_fr.published(blog_fr.load(), lang):
            a = blog_fr.V(a0, lang)
            by[a0['group']].append((a['published'], a0.get('publish_at', ''),
                                    dict(slug=a['slug'], title=a['seo_title'], desc=a['desc'], img=a['photo']['src_s'])))
    for g in by: by[g].sort(key=lambda x: (x[0], x[1]), reverse=True)
    return by


def active(bb):
    """{lang: [groupes ayant assez d'articles]}"""
    out = {}
    for lang in ('fr', 'en', 'es'):
        by = items(bb, lang)
        out[lang] = [g for g in ORDER if len(by[g]) >= MIN_ARTICLES]
    return out


def hub_path(lang, g):
    return f"/{lang}/blog/{HUBS[lang][g]['slug']}.html"


def render(bb, lang, g, act, by):
    H = HUBS[lang][g]; L = LBL[lang]; BASE = bb.BASE
    langs = [x for x in ('fr', 'en', 'es') if g in act[x]]
    path_of = lambda x: hub_path(x, g)
    arts = by[g]
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'CollectionPage', 'name': H['h1'], 'description': H['desc'], 'url': BASE + path_of(lang), 'inLanguage': lang,
         'isPartOf': {'@type': 'Blog', 'url': f'{BASE}/{lang}/blog/'},
         'mainEntity': {'@type': 'ItemList', 'numberOfItems': len(arts), 'itemListElement': [
             {'@type': 'ListItem', 'position': i + 1, 'url': f"{BASE}/{lang}/blog/{x['slug']}.html", 'name': x['title']}
             for i, (_, _, x) in enumerate(arts)]}},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'MeditaDream', 'item': f'{BASE}/{lang}/'},
            {'@type': 'ListItem', 'position': 2, 'name': L['blog'], 'item': f'{BASE}/{lang}/blog/'},
            {'@type': 'ListItem', 'position': 3, 'name': H['h1']}]}]}
    ld_tag = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace('<', '\\u003c') + '</script>'
    first_img = next((x['img'] for _, _, x in arts if x['img']), None)
    img = f'/assets/blog/{first_img}' if first_img else '/assets/brand/og-image.jpg'
    h = bb.head(lang, H['seo'], H['desc'], path_of, path_of(lang), img, ld_tag, img_alt=H['h1'], og_type='website',
                langs=langs if langs != ['fr', 'en', 'es'] else None)
    h += bb.header_html(lang, lambda x: f'../../{x}/blog/{HUBS[x][g]["slug"]}.html' if x in langs else f'../../{x}/blog/')
    h += (f'<main class="wrap"><nav class="crumbs"><a href="../">MeditaDream</a><span>›</span>'
          f'<a href="./">{E(L["blog"])}</a></nav><h1>{E(H["h1"])}</h1>'
          f'<p class="lead">{E(H["intro"])}</p><p class="meta">{len(arts)} {E(L["n"])}</p><ul class="alist">')
    for _, _, x in arts:
        th = (f'<span class="th"><img src="../../assets/blog/{x["img"]}" alt="" loading="lazy" width="88" height="88"></span>'
              if x['img'] else '<span class="th n">✦</span>')
        h += (f'<li><a href="{x["slug"]}.html">{th}<span class="tw"><h2>{E(x["title"])}</h2>'
              f'<p>{E(x["desc"])}</p></span></a></li>')
    import app_pages
    h += '</ul>' + app_pages.practice_links(lang, g) + themes_nav(lang, act, current=g) + '</main>' + bb.footer_html(lang) + '</body></html>'
    return h


def themes_nav(lang, act, current=None):
    if not act.get(lang): return ''
    L = LBL[lang]
    cur = ' aria-current="page"'
    li = ''.join(f'<li><a href="{HUBS[lang][g]["slug"]}.html"{cur if g == current else ""}>{E(HUBS[lang][g]["h1"])}</a></li>'
                 for g in act[lang])
    return f'<nav class="themes" aria-label="{E(L["themes"])}"><h2>{E(L["themes"])}</h2><ul class="pill-list">{li}</ul></nav>'


def group_link(lang, g, act):
    """Lien vers la page du thème (pour l'étiquette des articles), ou None si la page n'existe pas."""
    return f'{HUBS[lang][g]["slug"]}.html' if g in act.get(lang, []) else None


def build(bb):
    act = active(bb)
    for lang in ('fr', 'en', 'es'):
        by = items(bb, lang)
        for g in act[lang]:
            open(f'{ROOT}{hub_path(lang, g)}', 'w', encoding='utf-8').write(render(bb, lang, g, act, by))
    return act


def sitemap_urls(bb, act):
    urls = []
    for lang in ('fr', 'en', 'es'):
        by = items(bb, lang)
        for g in act[lang]:
            langs = [x for x in ('fr', 'en', 'es') if g in act[x]]
            alts = ''.join(f'<xhtml:link rel="alternate" hreflang="{x}" href="{bb.BASE}{hub_path(x, g)}"/>' for x in langs)
            if 'en' in langs: alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{bb.BASE}{hub_path("en", g)}"/>'
            urls.append(f'<url><loc>{bb.BASE}{hub_path(lang, g)}</loc><lastmod>{by[g][0][0]}</lastmod>{alts}</url>')
    return urls
