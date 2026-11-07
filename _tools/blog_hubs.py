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
# 06-11 (Edouard : « pour le blog MeditaDream, divise les articles en catégories ») : nom court de chaque catégorie,
# propre à chaque langue, et une phrase d'accroche (accueil du blog, étiquette de catégorie des articles).
CATS = {
 'fr': {'bases': ('Apprendre à méditer', 'Posture, respiration, pensées, techniques : les bases pour méditer seul, pas à pas.'),
        'sommeil': ('Sommeil et rêves', 'Méditation pour dormir, rituel du soir, rêve lucide, yoga nidra : tout pour mieux dormir.'),
        'energie': ('Chakras et énergie', 'Chakras, chi, kundalini, troisième œil : les cartes du corps énergétique et des exercices concrets.'),
        'psy': ('Émotions et vie intérieure', 'Gérer ses émotions, travail de l’ombre, enfant intérieur, peurs : des pratiques douces.'),
        'transe': ('Transe et états de conscience', 'Transe, hypnose, flow, états modifiés de conscience : comprendre et pratiquer sans risque.'),
        'vie': ('Méditation au quotidien', 'Travail, concentration, sport, études : la méditation dans la vraie vie.'),
        'lieux': ('Lieux sacrés et pèlerinages', 'Temples, chemins de pèlerinage et lieux sacrés du monde, à visiter en méditation.'),
        'chamanisme': ('Chamanisme', 'Voyage chamanique, tambour, animal de pouvoir, trois mondes : le chamanisme expliqué.'),
        'astral': ('Voyage astral', 'Projection astrale, sortie hors du corps, rêve lucide : techniques et précautions.')},
 'en': {'bases': ('How to meditate', 'Posture, breathing, thoughts and techniques: the basics to meditate on your own.'),
        'sommeil': ('Sleep and dreams', 'Sleep meditation, bedtime routine, lucid dreaming and yoga nidra for better nights.'),
        'energie': ('Chakras and energy', 'Chakras, qi, kundalini and the third eye, explained with simple practices.'),
        'psy': ('Emotions and inner life', 'Emotional regulation, shadow work, inner child and fear, with gentle practices.'),
        'transe': ('Trance and consciousness', 'Trance, hypnosis, flow and altered states of consciousness, explained safely.'),
        'vie': ('Everyday meditation', 'Meditation for work, focus, sport and study.'),
        'lieux': ('Sacred places and pilgrimages', 'Temples, pilgrim roads and sacred places to visit in meditation.'),
        'chamanisme': ('Shamanism', 'Shamanic journeys, drumming, power animals and the three worlds.'),
        'astral': ('Astral projection', 'Astral projection, out-of-body experiences and lucid dreams: techniques and safety.')},
 'es': {'bases': ('Cómo meditar', 'Postura, respiración, pensamientos y técnicas: lo básico para meditar a solas.'),
        'sommeil': ('Sueño y sueños', 'Meditación para dormir, rutina nocturna, sueños lúcidos y yoga nidra.'),
        'energie': ('Chakras y energía', 'Chakras, chi, kundalini y tercer ojo, con ejercicios concretos.'),
        'psy': ('Emociones y vida interior', 'Gestión emocional, trabajo de sombra, niño interior y miedos, con prácticas suaves.'),
        'transe': ('Trance y estados de conciencia', 'Trance, hipnosis, flow y estados modificados de conciencia, sin riesgos.'),
        'vie': ('Meditación en el día a día', 'Meditación para el trabajo, la concentración, el deporte y los estudios.'),
        'lieux': ('Lugares sagrados y peregrinaciones', 'Templos, caminos de peregrinación y lugares sagrados para visitar meditando.'),
        'chamanisme': ('Chamanismo', 'Viaje chamánico, tambor, animal de poder y los tres mundos.'),
        'astral': ('Viaje astral', 'Viaje astral, experiencias fuera del cuerpo y sueños lúcidos: técnicas y precauciones.')},
}
CATS_T = {'fr': ('Les catégories du blog', 'Tous les articles « {n} »'), 'en': ('Blog categories', 'All “{n}” articles'),
          'es': ('Las categorías del blog', 'Todos los artículos «{n}»')}

# Chaque langue a son propre angle de recherche : slug, titre Google (≤ 60), description (≤ 155), h1, intro.
HUBS = {
 'fr': {
  'bases': dict(slug='pratique-de-la-meditation',
    seo="Comment pratiquer la méditation : guides pour débutants",
    desc="Comment pratiquer la méditation chez toi, même cinq minutes par jour : posture, marche méditative, méditation du matin. Des guides pour apprendre à méditer.",
    h1="Comment pratiquer la méditation, pas à pas",
    intro="Comment pratiquer la méditation quand tu débutes ? Tu t'assois, tu reviens au souffle et tu recommences. Ces guides reprennent les bases une à une, de la posture aux pensées, pour méditer à ton rythme. Tu y trouveras des schémas clairs et des exercices de quelques minutes."),
  'sommeil': dict(slug='sommeil-et-reves',
    seo="Sommeil et rêves : comprendre et apaiser tes nuits",
    desc="Sommeil et rêves : un rituel du soir pour t'endormir, le yoga nidra pour te reposer, le rêve lucide pour explorer. Des guides clairs, sans promesse magique.",
    h1="Sommeil et rêves, du coucher au réveil",
    intro="Entre sommeil et rêves, la nuit occupe un tiers de ta vie : c'est souvent là que le stress se montre. Ces articles t'aident d'abord à te préparer : rituel du soir, méditation guidée ou repos profond. Ils éclairent aussi ce qui se passe à l'endormissement, de l'hypnagogie à la paralysie du sommeil. Et ils t'invitent à explorer tes rêves : t'en souvenir, les comprendre, peut-être devenir lucide."),
  'energie': dict(slug='chakras-et-energie',
    seo="Énergie vitale : qi, kundalini et aura, ce qu'on en sait",
    desc="L'énergie vitale vue par les traditions, des chakras à la kundalini : ce qu'en dit la science, et des exercices simples pour la sentir dans ton corps.",
    h1="L'énergie vitale, entre tradition et science",
    intro="L'énergie vitale porte plusieurs noms selon les cultures : qi en Chine, prana en Inde. Ces articles explorent ses cartes les plus connues, des chakras à la kundalini, sans rien promettre de magique. Ils distinguent ce que disent les traditions de ce que mesure la science. Tu y trouveras aussi des exercices simples à essayer chez toi."),
  'psy': dict(slug='emotions-et-vie-interieure',
    seo="Vie intérieure et émotions : des pratiques douces",
    desc="Vie intérieure et émotions : le travail de l'ombre, l'enfant intérieur et les peurs, avec des exercices courts pour accueillir ce que tu ressens.",
    h1="Émotions et vie intérieure",
    intro="La méditation ne fait pas taire ta vie intérieure : elle t'aide à mieux la lire. Ces articles explorent l'ombre, l'enfant intérieur et la peur, un exercice à la fois. Ils s'appuient sur des repères de psychologie, sans jargon. Et quand c'est utile, ils t'invitent clairement à te faire accompagner."),
  'transe': dict(slug='transe-et-etats-de-conscience',
    seo="États modifiés de conscience : les comprendre sans drogue",
    desc="Transe, hypnose, flow : les états modifiés de conscience sans substance. Ce que la science en mesure, et comment y entrer puis en revenir en sécurité.",
    h1="États modifiés de conscience, de l'hypnose au flow",
    intro="Les états modifiés de conscience ne demandent ni drogue ni don particulier. Le flow d'un sportif ou une danse qui t'emporte en sont déjà des formes légères. Ces articles expliquent ce que la science en mesure, comment y entrer et comment en revenir en sécurité. Ils t'aident aussi à garder une trace de tes expériences."),
  'vie': dict(slug='meditation-au-quotidien',
    seo="Méditation au quotidien : travail, sport, études",
    desc="La méditation au quotidien : gérer le stress au travail, préparer un examen, mieux écouter en couple. Des exercices courts, sans promesse miracle.",
    h1="Vivre la méditation au quotidien",
    intro="La méditation au quotidien commence quand tu quittes le coussin. Ces articles montrent comment elle s'invite au travail, en couple ou pendant les études. Tu y trouveras des exercices de quelques minutes et ce que la recherche permet vraiment d'en attendre."),
  'lieux': dict(slug='lieux-sacres-et-sagesses',
    seo="Lieux de pèlerinage, mythes et sagesses du monde",
    desc="Pèlerinages et sagesses du monde : le chemin de Compostelle, les montagnes sacrées, le mythe de l'Atlantide. Leur histoire vraie, et ce qu'ils t'apprennent.",
    h1="Pèlerinages, mythes et sagesses",
    intro="Certains lieux sacrés et chemins de pèlerinage traversent les siècles, car ils parlent à quelque chose de profond en nous. Ces articles racontent leur histoire réelle, de Compostelle au jardin zen de Ryōan-ji. Ils explorent aussi des mythes, comme l'Atlantide, et des idées anciennes comme le memento mori. À chaque fois, tu vois ce qu'ils peuvent apporter à ta pratique aujourd'hui."),
  'chamanisme': dict(slug='chamanisme',
    seo="Chamanisme : définition, origines et traditions vivantes",
    desc="Chamanisme : définition, origine sibérienne du mot et traditions du monde, de la Corée à l'Amazonie. Et comment pratiquer sans t'approprier une culture.",
    h1="Chamanisme : définition et pratiques",
    intro="Chamanisme, définition simple : les pratiques du chamane, qui entre en transe pour communiquer avec les esprits. Le mot « chamane » vient de Sibérie, puis a voyagé jusqu'à désigner des traditions du monde entier. Ces articles décrivent les gestes transmis, du tambour aux offrandes, sans inventer de règles universelles. Et ils posent une question essentielle : comment respecter les cultures d'où viennent ces gestes ?"),
  'astral': dict(slug='voyage-astral-et-signes',
    seo="Signes spirituels, synchronicités et voyage astral",
    desc="Signes spirituels, sortie de corps et voyage astral : ce que l'on sait, ce que l'on ignore et comment explorer ces expériences avec prudence.",
    h1="Signes spirituels et voyage astral",
    intro="Sorties de corps, voyage astral, synchronicités : ces expériences fascinent autant qu'elles intriguent. Ce thème présente les techniques de projection astrale décrites par les pratiquants, et ce que la science a observé. Il t'aide aussi à lire les signes, comme une plume ou un papillon, sans perdre ton esprit critique."),
 },
 'en': {
  'bases': dict(slug='meditation-practice',
    seo="Beginners' Guide to Meditation: Breath, Posture and Focus",
    desc="A beginners' guide to meditation in short, clear lessons: posture, breathing and wandering thoughts. Learn how to meditate on your own, for free.",
    h1="A beginners' guide to meditation practice",
    intro="This beginners' guide to meditation keeps things simple: all you need is a seat, your breath and a few minutes. The articles walk you through the essentials, from posture to breathing to wandering thoughts. Most come with clear diagrams and an exercise you can try at home."),
  'sommeil': dict(slug='sleep-and-dreams',
    seo="How to Sleep Better: Calmer Evenings, Deeper Rest",
    desc="How to sleep better without forcing it: wind down with yoga nidra, make sense of sleep paralysis and explore lucid dreaming. Clear, honest guides.",
    h1="Sleep and dreams: how to sleep better",
    intro="Learning how to sleep better often starts long before your head touches the pillow. These guides begin with simple tools: a bedtime routine, yoga nidra and NSDR. Then they turn to the night itself, from sleep paralysis to dreams you can remember and even steer."),
  'energie': dict(slug='chakras-and-energy',
    seo="Life Energy: How to Feel It and What Science Says",
    desc="Life energy, put to the test: qigong moves, grounding exercises and chakra practices to try today, plus what research really says about them.",
    h1="Life energy, from chi to kundalini",
    intro="Life energy is one of humanity's oldest ideas, and it still feels real to many people who meditate. Here you can test it for yourself, with qigong moves, grounding exercises and a guided chakra practice. Along the way, you get an honest look at what research has and hasn't found."),
  'psy': dict(slug='emotions-and-inner-life',
    seo="How to Process Emotions and Calm Your Mind Gently",
    desc="How to process emotions gently: shadow work, your inner critic and the fears that hold you back, with short practices and honest guidance.",
    h1="How to process emotions and care for your inner life",
    intro="Mindfulness for emotions starts with a small shift: you notice a feeling instead of fighting it. These articles apply it to shadow work, your inner critic and facing your fears. You will find short exercises and ideas drawn from psychology. Where it matters, they also point you clearly toward professional support."),
  'transe': dict(slug='trance-and-altered-states',
    seo="Altered States of Consciousness: Trance, Hypnosis and Flow",
    desc="Altered states of consciousness, explained simply: meditation and trance, hypnosis and flow, plus how to come back grounded after the experience.",
    h1="Trance and altered states of consciousness",
    intro="Altered states of consciousness are less exotic than they sound: getting lost in a good novel is one of them. This topic explores meditation and trance, hypnosis and flow, and what research can actually measure. You will also learn how to enter these states, come back safely and keep a record of the journey."),
  'vie': dict(slug='meditation-in-daily-life',
    seo="Meditation at Work and Beyond: Small Practices for Real Life",
    desc="Meditation at work in a few calm breaths, plus short practices for work stress, exam nerves and busy commutes that fit the day you already have.",
    h1="Meditation at work, at home and on the go",
    intro="Meditation at work can be as small as three conscious breaths before a meeting. The same idea carries into studying, sport and the daily commute. This is mindfulness in everyday life: short moments that fit your real schedule. If you are dealing with work stress and anxiety, start with one practice and keep it small."),
  'lieux': dict(slug='sacred-places-and-wisdom',
    seo="Spiritual Pilgrimage: Sacred Roads, Mountains and Gardens",
    desc="Spiritual pilgrimage without religion, from the Camino de Santiago to Shikoku, and the sacred mountains and Zen gardens that still shape how we think.",
    h1="Spiritual pilgrimage and sacred geography",
    intro="A spiritual pilgrimage needs no religion, only a road and a reason to walk it. These articles tell the real history behind sacred mountains, Zen gardens and myths like Atlantis. They also revisit old ideas, such as memento mori or the power of silence. Along the way, you see what they can bring to your practice today."),
  'chamanisme': dict(slug='shamanism',
    seo="History of Shamanism: From Siberia to the Amazon",
    desc="The history of shamanism, from the Siberian word “shaman” to Korean mudang and Celtic druids, and how to explore it with respect for living cultures.",
    h1="A history of shamanism, tradition by tradition",
    intro="The history of shamanism begins with a single word, “shaman”, from the Evenki language of Siberia. From there, its story runs through Celtic druids, Korean mudang and Michael Harner's modern core shamanism. Our articles explain practices passed down through generations, like the drum, the rattle and the medicine wheel. They also ask a vital question: how do you honor the cultures these practices come from?"),
  'astral': dict(slug='astral-projection-and-signs',
    seo="Astral Projection Techniques for Curious Beginners",
    desc="Astral projection techniques explained calmly, step by step: deep relaxation, first micro-detachments, then the rope and roll-out exit methods.",
    h1="Astral projection techniques, one rung at a time",
    intro="Astral projection techniques start with a paradox: a body that falls asleep while the mind stays awake. These guides move step by step, from deep relaxation to the first micro-detachments. Then come the exit techniques practitioners describe, such as the rope and the roll-out. Explore them with curiosity, and keep a critical mind about what you feel."),
 },
 'es': {
  'bases': dict(slug='practica-de-la-meditacion',
    seo="Guía para meditar: prácticas paso a paso para principiantes",
    desc="Guía para meditar en casa, paso a paso: de la respiración al escaneo corporal y la meditación caminando. Aprende cómo meditar sin tecnicismos y gratis.",
    h1="Guía para meditar en casa, a tu ritmo",
    intro="Esta guía para meditar está pensada para quien empieza desde cero, sin tecnicismos ni prisas. Los artículos repasan lo esencial, de la postura a los pensamientos, para practicar unos minutos al día. Si te preguntas cómo meditar sin complicarte, aquí tienes esquemas claros y ejercicios concretos."),
  'sommeil': dict(slug='sueno-y-suenos',
    seo="Cómo dormir mejor con meditación: sueño y sueños",
    desc="Cómo dormir mejor: higiene del sueño, yoga nidra y sueños lúcidos, explicados sin rodeos. Entiende tus noches y recupera un descanso tranquilo.",
    h1="Cómo dormir mejor y entender tus sueños",
    intro="¿Buscas cómo dormir mejor? A veces ayuda más dejar de pelearte con la noche que sumar trucos. Aquí encontrarás rutinas sencillas, el yoga nidra y el descanso profundo sin dormir (NSDR). También te explicamos qué pasa al quedarte dormido y cómo recordar tus sueños, o incluso volverte lúcido."),
  'energie': dict(slug='chakras-y-energia',
    seo="Energía vital: qué es y cómo sentirla al meditar",
    desc="La energía vital y los 7 chakras explicados con sencillez: un mapa simbólico del cuerpo para guiar la atención al meditar, con ejercicios prácticos.",
    h1="La energía vital y sus mapas del cuerpo",
    intro="Chakras, chi y kundalini comparten una misma idea: la energía vital que recorre el cuerpo. Te presentamos estos mapas del cuerpo tal como son: herramientas simbólicas para guiar la atención. Y te proponemos ejercicios sencillos, como el chi kung, para sentirla en tu cuerpo."),
  'psy': dict(slug='emociones-y-vida-interior',
    seo="Cómo calmar la mente: emociones y vida interior",
    desc="Cómo calmar la mente con meditación suave: el trabajo de sombra, los miedos y el diálogo interno negativo, para vivir mejor contigo mismo.",
    h1="Emociones, sombra y vida interior",
    intro="Meditar no consiste en dejar de sentir: te ayuda a acoger lo que aparece sin ahogarte en ello. Estos artículos abordan la sombra, los miedos y la autocrítica con ejercicios breves y referencias de la psicología. Si te preguntas cómo dejar de tener pensamientos negativos sobre ti, aprenderás a bajar el volumen de tu crítico interior. Y cuando hace falta, te invitan a pedir ayuda profesional."),
  'transe': dict(slug='trance-y-estados-de-conciencia',
    seo="Estados alterados de conciencia, sin sustancias",
    desc="Estados alterados de conciencia: del trance a la hipnosis y la danza extática, con sus mitos, sus peligros reales y cómo vivirlos con seguridad.",
    h1="El trance y otros estados alterados de conciencia",
    intro="Los estados alterados de conciencia empiezan en lo cotidiano, con una simple ensoñación. Estos artículos explican el trance, la hipnosis y la danza extática, y lo que la ciencia puede medir. También te enseñan a explorarlos con seguridad, sin miedo pero con los pies en la tierra."),
  'vie': dict(slug='meditacion-en-el-dia-a-dia',
    seo="Meditación diaria: crear un hábito que dure",
    desc="Meditación diaria que dura: cómo crear el hábito en pocos minutos, con atención plena en la vida cotidiana, en el trabajo, en pareja o antes de un examen.",
    h1="Meditación diaria: meditar en el día a día",
    intro="La atención plena en la vida cotidiana se entrena en lo pequeño: un café, una espera, una conversación. Estos artículos te acompañan en el trabajo, en pareja y en época de exámenes, cuando aprieta el estrés académico. Encontrarás ejercicios de pocos minutos y expectativas realistas, sin promesas milagrosas. Si te cuesta empezar, una meditación diaria guiada de cinco minutos puede ayudarte a crear el hábito."),
  'lieux': dict(slug='simbolos-y-sabiduria',
    seo="Símbolos, arquetipos y sabiduría del mundo",
    desc="Símbolos espirituales y arquetipos, el Camino de Santiago como viaje espiritual y el arte de ser feliz: la sabiduría del mundo, explicada con sencillez.",
    h1="Sabiduría del mundo: símbolos y caminos",
    intro="Templos, bosques, montañas: las meditaciones guiadas hablan con imágenes por una razón. Estos artículos explican el papel de los símbolos espirituales y de los arquetipos en tu práctica. También recorren caminos reales, como la peregrinación a Santiago, y otros viajes espirituales por el mundo. Y se preguntan, con calma, si la felicidad se puede aprender."),
  'chamanisme': dict(slug='chamanismo',
    seo="Tipos de chamanismo: tradiciones, prácticas y respeto",
    desc="Tipos de chamanismo y tradiciones chamánicas del mundo, el tambor y el animal de poder: comprende su historia y practica con respeto.",
    h1="Tipos de chamanismo y tradiciones del mundo",
    intro="El chamanismo reúne tradiciones muy distintas, de Siberia a la Amazonía, pasando por los druidas celtas. Nuestros artículos explican qué es un chamán y el sentido del axis mundi, el eje que une los tres mundos. También describen prácticas chamánicas como el tambor o la búsqueda de tu animal de poder. Y plantean una pregunta esencial: cómo respetar las culturas de las que proceden."),
  'astral': dict(slug='viaje-astral',
    seo="Viaje astral paso a paso, sin sensacionalismo",
    desc="Un viaje astral se prepara poco a poco: relajación profunda, microdesprendimientos y, al final, cómo salir del cuerpo con prudencia y espíritu crítico.",
    h1="El viaje astral, sin prisas",
    intro="El viaje astral se explora por etapas, sin forzar nada. Aquí encontrarás una progresión clara, de la relajación profunda a los microdesprendimientos. Después verás cómo salir del cuerpo con las técnicas que describen los practicantes. Explóralas con curiosidad y sin perder el espíritu crítico."),
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
        alt = bb.HERO_ALTS.get((a.get('image'), lang), a['title'][lang]) if img else ''
        by[g].append((a['published'], '', dict(slug=a['slug'][lang], title=a['title'][lang], desc=a['desc'][lang], img=img, alt=alt)))
    if lang in ('fr', 'en', 'es'):
        for a0 in blog_fr.published(blog_fr.load(), lang):
            a = blog_fr.V(a0, lang)
            by[a0['group']].append((a['published'], a0.get('publish_at', ''),
                                    dict(slug=a['slug'], title=a['seo_title'], desc=a['desc'], img=a['photo']['src_s'],
                                         alt=a['photo'].get('alt', ''))))
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
    first = next((x for _, _, x in arts if x['img']), None)
    img = f'/assets/blog/{first["img"]}' if first else '/assets/brand/og-image.jpg'
    og_alt = (H['h1'] + (' : ' if lang == 'fr' else ': ') + first['alt']) if first and first.get('alt') else H['h1']
    h = bb.head(lang, H['seo'], H['desc'], path_of, path_of(lang), img, ld_tag, img_alt=og_alt, og_type='website',
                langs=langs if langs != ['fr', 'en', 'es'] else None)
    h += bb.header_html(lang, lambda x: f'../../{x}/blog/{HUBS[x][g]["slug"]}.html' if x in langs else f'../../{x}/blog/')
    h += (f'<main class="wrap"><nav class="crumbs"><a href="../">MeditaDream</a><span>›</span>'
          f'<a href="./">{E(L["blog"])}</a></nav><h1>{E(H["h1"])}</h1>'
          f'<p class="lead">{E(H["intro"])}</p><p class="meta">{len(arts)} {E(L["n"])}</p><ul class="alist">')
    for _, _, x in arts:
        th = (f'<span class="th"><img src="../../assets/blog/{x["img"]}" alt="{E(x.get("alt", ""))}" loading="lazy" width="88" height="88"></span>'
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
