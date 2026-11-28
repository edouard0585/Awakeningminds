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
    # 27-11 : cinq articles sur les sujets demandés par Edouard (voyage astral, rêve lucide, guides spirituels)
    'astral-signes': 'astral', 'astral-dangers': 'astral', 'lucide-risques': 'sommeil', 'guide-trouver': 'astral', 'guide-signes': 'astral',
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
    seo="Comment pratiquer la méditation : 7 étapes pour débutants",
    desc="Comment pratiquer la méditation chez toi : 7 étapes simples pour commencer et méditer facilement, de la posture au souffle, puis des guides gratuits.",
    h1="Comment pratiquer la méditation, pas à pas",
    h2="Commencer la méditation : les guides à lire",
    intro="Comment pratiquer la méditation quand tu débutes ? Avec une technique simple, à la portée de tout débutant : tu t'assois, tu reviens au souffle et tu recommences. Pour commencer la méditation, pas besoin de matériel ni de silence parfait : méditer chez soi, quelques minutes, suffit. Si tu te demandes comment faire de la méditation, suis d'abord les sept étapes ci-dessous. Ces guides reprennent ensuite les bases une à une, de la posture aux pensées, pour méditer facilement et à ton rythme. Tu y trouveras des schémas clairs et des exercices de quelques minutes, de quoi installer peu à peu une pratique méditative régulière."),
  'sommeil': dict(slug='sommeil-et-reves',
    seo="Sommeil et rêves : comprendre tes rêves, apaiser tes nuits",
    desc="Sommeil et rêves : un rituel du soir pour t'endormir, le yoga nidra pour te reposer, le rêve lucide pour explorer. Des guides clairs, sans promesse magique.",
    h1="Sommeil et rêves, du coucher au réveil",
    h2="Sommeil et rêves : tous les articles",
    intro="Entre sommeil et rêves, la nuit occupe un tiers de ta vie : c'est souvent là que le stress se montre. Que faire avant de dormir pour que la nuit se passe mieux ? Ces articles t'aident d'abord à te préparer : rituel du soir, méditation guidée ou repos profond. Ils éclairent aussi ce qui se passe à l'endormissement, de l'hypnagogie à la paralysie du sommeil. On rêve surtout pendant le sommeil paradoxal, et personne ne sait encore tout à fait pourquoi. Ces articles t'invitent enfin à explorer tes rêves : t'en souvenir, les comprendre, peut-être devenir lucide."),
  'energie': dict(slug='chakras-et-energie',
    seo="Énergie vitale : qi, kundalini et aura, ce qu'on en sait",
    desc="L'énergie vitale, c'est quoi ? Qi, prana, kundalini, chakras : ce qu'en disent les traditions et la science, et des exercices pour la sentir dans ton corps.",
    h1="L'énergie vitale, entre tradition et science",
    h2="Énergie vitale : chakras, qi gong et troisième œil",
    intro="L'énergie vitale, c'est quoi ? Un souffle qui anime le corps, selon de nombreuses traditions : on l'appelle le qi (ou chi) en Chine, le prana en Inde. Ces articles explorent ses cartes les plus connues, des chakras à l'énergie kundalini, sans rien promettre de magique. Ils expliquent ce que les traditions entendent par « ouvrir ses chakras », du chakra racine au chakra du cœur, et distinguent ce qu'elles disent de ce que mesure la science. Tu y trouveras aussi des exercices simples à essayer chez toi pour ressentir l'énergie dans ton corps, du qi gong à la méditation."),
  'psy': dict(slug='emotions-et-vie-interieure',
    seo="Vie intérieure et émotions : pratiques de méditation douces",
    desc="Vie intérieure et émotions en méditation : le travail de l'ombre, l'enfant intérieur et les peurs, avec des exercices courts pour accueillir tes émotions.",
    h1="Émotions et vie intérieure",
    h2="Vie intérieure : émotions, larmes et part d’ombre",
    intro="La vie intérieure, c'est tout ce qui se passe en toi sans se voir : émotions, pensées, souvenirs, images. La méditation ne la fait pas taire : elle t'aide à mieux la lire et à comprendre tes émotions. Avoir une vie intérieure riche, ce n'est pas tout comprendre, c'est savoir écouter. Ces articles explorent l'ombre, l'enfant intérieur et la peur, un exercice à la fois, pour apprendre à accueillir tes émotions plutôt qu'à les combattre. Ils s'appuient sur des repères de psychologie, sans jargon. Et quand c'est utile, ils t'invitent clairement à te faire accompagner."),
  'transe': dict(slug='transe-et-etats-de-conscience',
    seo="États modifiés de conscience sans drogue : transe et hypnose",
    desc="Transe, hypnose, flow : les états modifiés de conscience sans substance. Ce que la science en mesure, et comment y entrer puis en revenir en sécurité.",
    h1="États modifiés de conscience, de l'hypnose au flow",
    h2="États modifiés de conscience : transe et hypnose",
    intro="Un état modifié de conscience, c’est un moment où l’attention, la perception du temps et les sensations changent par rapport à l’état de veille ordinaire. Les états modifiés de conscience ne demandent ni drogue ni don particulier : le chamanisme, l’hypnose et la méditation y mènent par des techniques différentes. Le flow d’un sportif ou une danse qui t’emporte en sont déjà des formes légères. Qu’est-ce que la transe ? L’hypnose, c’est quoi ? Ces articles y répondent, puis expliquent ce que la science mesure de ces états, comment entrer en transe et en revenir en sécurité. Ils t’aident aussi à garder une trace de tes expériences."),
  'vie': dict(slug='meditation-au-quotidien',
    seo="Vivre la méditation au quotidien : travail, sport, études",
    desc="Méditation et pleine conscience au quotidien : gérer le stress au travail, préparer un examen, mieux écouter en couple. Des exercices courts, sans promesse.",
    h1="Vivre la méditation au quotidien",
    h2="La méditation au quotidien, article par article",
    intro="La méditation au quotidien commence quand tu quittes le coussin. Comment la pratiquer sans y passer des heures ? Par petites touches : marcher, manger, écouter en étant vraiment là. C'est la pleine conscience au quotidien, qu'on appelle aussi méditation informelle. Ces articles montrent comment elle s'invite au travail, en couple ou pendant les études, et comment méditer tous les jours sans te forcer. Tu y trouveras des exercices de méditation de quelques minutes, au bureau comme à la maison, et ce que la recherche permet vraiment d'en attendre."),
  'lieux': dict(slug='lieux-sacres-et-sagesses',
    seo="Lieux et chemins de pèlerinage, mythes et sagesses du monde",
    desc="Lieux et chemins de pèlerinage, de Compostelle aux 88 temples de Shikoku, mythes et sagesses du monde : leur histoire vraie, et ce qu'ils t'apprennent.",
    h1="Lieux de pèlerinage, mythes et sagesses",
    h2="Chemins de pèlerinage et sagesses du monde : les articles",
    intro="Certains lieux sacrés et chemins de pèlerinage traversent les siècles, car ils parlent à quelque chose de profond en nous. Pourquoi faire un pèlerinage aujourd'hui, même sans religion ? Souvent pour marcher, ralentir et faire le point : c'est le pèlerinage spirituel, ou laïque. Ces articles racontent leur histoire réelle : celle de grands lieux de pèlerinage, du chemin de Compostelle aux 88 temples de Shikoku, et celle du jardin zen de Ryōan-ji. Ils explorent aussi des mythes, comme l'Atlantide, des idées anciennes comme le memento mori, et ce que la psychologie positive dit du bonheur. À chaque fois, tu vois ce qu'ils peuvent apporter à ta pratique aujourd'hui."),
  'chamanisme': dict(slug='chamanisme',
    seo="Chamanisme : définition simple, origines et traditions",
    desc="Chamanisme : définition simple, origine du mot et traditions du monde. Qu'est-ce que le chamanisme, et comment le pratiquer sans t'approprier une culture ?",
    h1="Chamanisme : définition et pratiques",
    h2="Chamanisme : définition et récits du monde",
    intro="Chamanisme, définition simple : les pratiques du chamane, qui entre en transe pour communiquer avec les esprits. Qu'est-ce que le chamanisme, au juste ? Ni une religion unique ni une doctrine : un ensemble de traditions, différentes d'un peuple à l'autre. Le mot « chamane » vient de Sibérie, puis a voyagé jusqu'à désigner des traditions du monde entier, du chamanisme sibérien à celui de l'Amazonie. Ces articles décrivent les pratiques chamaniques et les gestes transmis, du tambour aux offrandes, avec des repères comme l'arbre du monde ou l'animal de pouvoir, sans inventer de règles universelles. Et ils posent une question essentielle : comment respecter les cultures d'où viennent ces gestes ?"),
  'astral': dict(slug='voyage-astral-et-signes',
    seo="Signes spirituels, synchronicités et voyage astral",
    desc="Signes spirituels, sortie de corps et voyage astral : ce que l'on sait, ce que l'on ignore et comment explorer ces expériences avec prudence.",
    h1="Signes spirituels et voyage astral",
    h2="Voyage astral et signes spirituels : les articles",
    intro="Sorties de corps, voyage astral, synchronicités : ces expériences fascinent autant qu'elles intriguent. Ce thème présente les techniques de projection astrale décrites par les pratiquants, et ce que la science a observé. Il t'aide aussi à lire les signes, comme une plume ou un papillon, sans perdre ton esprit critique."),
 },
 'en': {
  'bases': dict(slug='meditation-practice',
    seo="How to Do Meditation Correctly: Beginners' Guide in 7 Steps",
    desc="How to do meditation correctly in 7 simple steps: posture, breath and focus when thoughts wander. Then a beginners' guide to meditation, lesson by lesson.",
    h1="How to meditate correctly: a beginners' guide to meditation practice",
    h2="Beginners guide to meditation: every article",
    intro="This beginners' guide to meditation keeps things simple: all you need is a seat, your breath and a few minutes. Wondering how to meditate properly? Start with the seven steps below, which show how to meditate step by step. Then the articles walk you through the basic meditation practices, from posture to breathing to wandering thoughts, and show how to use meditation in daily life. Most come with clear diagrams and an exercise you can try at home, so you can learn how to practice meditation at your own pace."),
  'sommeil': dict(slug='sleep-and-dreams',
    seo="How to Sleep Better at Night: Calmer Evenings, Deeper Rest",
    desc="How to sleep better, and what to do when you can't sleep: wind down with yoga nidra, make sense of sleep paralysis and explore lucid dreaming.",
    h1="Sleep and dreams: how to sleep better",
    h2="How to sleep better: articles for calmer nights",
    intro="Learning how to sleep better at night, naturally, often starts long before your head touches the pillow. These guides begin with how to relax before bed: a bedtime routine to wind down, yoga nidra and NSDR. They also cover what to do when you can't sleep: stop chasing sleep, slow your breathing and let rest come first. Then they turn to the night itself, from what sleep paralysis is to dreams you can remember and even steer."),
  'energie': dict(slug='chakras-and-energy',
    seo="Life Force Energy (Chi): How to Feel It, What Science Says",
    desc="Life force energy, put to the test: what chi energy is, plus qigong moves, grounding exercises and chakra practices to try, and what research says.",
    h1="Life energy, from chi to kundalini",
    h2="Life energy in practice: chakras, qigong, third eye",
    intro="Life energy is one of humanity's oldest ideas, and it still feels real to many people who meditate. So what is chi energy, exactly? It is the Chinese name, also written qi, for a vital energy, or life force energy, said to flow through every living body. In India, a similar idea is called prana. Some yoga traditions add kundalini energy, said to rest coiled at the base of the spine, and map it all with the chakras. Here you can test life energy for yourself, with qigong moves, grounding exercises and a guided chakra practice. Along the way, you get an honest look at whether chi energy is real: what research has and hasn't found."),
  'psy': dict(slug='emotions-and-inner-life',
    seo="How to Process Difficult Emotions and Calm Your Mind Gently",
    desc="How to process emotions and calm the mind gently: shadow work, your inner critic and the fears that hold you back, with short, honest practices.",
    h1="How to process emotions and care for your inner life",
    h2="How to deal with difficult emotions: the articles",
    intro="How do you process emotions in a healthy way, when a difficult one takes over? Mindfulness for emotions starts with a small shift: you notice a feeling instead of fighting it. That emotional awareness is what lets you calm the mind without pushing anything down. These articles apply it to shadow work, your inner critic and facing your fears. You will find short exercises and ideas drawn from psychology. Where it matters, they also point you clearly toward professional support."),
  'transe': dict(slug='trance-and-altered-states',
    seo="Altered States of Consciousness: Trance, Hypnosis and Flow",
    desc="Altered states of consciousness without drugs, explained simply: meditation and trance, hypnosis and flow, plus how to come back grounded afterward.",
    h1="Trance and altered states of consciousness",
    h2="Altered states of consciousness, from trance to hypnosis",
    intro="Altered states of consciousness are less exotic than they sound: getting lost in a good novel is one of them. What is an altered state of consciousness? Any moment when attention, the sense of time or the sense of self shifts away from ordinary waking awareness. Everyday examples of altered states of consciousness include daydreaming, the flow state and deep meditation. This topic explores meditation and trance, hypnosis and flow, and what research can actually measure. You will also learn how to enter a trance state in meditation, come back safely and keep a record of the journey."),
  'vie': dict(slug='meditation-in-daily-life',
    seo="Meditation at Work and Beyond: Small Practices for Real Life",
    desc="Meditation at work in a few calm breaths, plus short practices for work stress, exam nerves and busy commutes that fit the day you already have.",
    h1="Meditation at work, at home and on the go",
    h2="Meditation at work and at home: the articles",
    intro="Meditation at work can be as small as three conscious breaths before a meeting. The same idea carries into studying, sport and the daily commute. This is mindfulness in everyday life: short moments that fit your real schedule. If you are dealing with work stress and anxiety, start with one practice and keep it small."),
  'lieux': dict(slug='sacred-places-and-wisdom',
    seo="Spiritual Pilgrimage: Sacred Roads, Mountains and Gardens",
    desc="Spiritual pilgrimage without religion, from the Camino de Santiago to Shikoku, plus sacred geography: sacred sites, mountains and Zen gardens.",
    h1="Spiritual pilgrimage and sacred geography",
    h2="Spiritual pilgrimage and sacred places: the articles",
    intro="A spiritual pilgrimage needs no religion, only a road and a reason to walk it. Its meaning is simple: a journey made for inner reasons. It can be a long walking pilgrimage like the Camino de Santiago or Shikoku, or a one-day spiritual walk near home. Sacred geography is the map these journeys follow: the sacred sites, mountains and springs that cultures around the world have honored for centuries. These articles tell the real history behind sacred mountains, Zen gardens and myths like Atlantis. They also revisit old ideas, such as memento mori or the power of silence. Along the way, you see what they can bring to your practice today."),
  'chamanisme': dict(slug='shamanism',
    seo="History of Shamanism: From Siberia to Korea and the Amazon",
    desc="The history of shamanism, from the Siberian word “shaman” to Korean shamans and Celtic druids, and how to approach shamanic traditions with respect.",
    h1="A history of shamanism, tradition by tradition",
    h2="Shamanic traditions and their history, article by article",
    intro="The history of shamanism begins with a single word, “shaman”, from the Evenki language of Siberia. That is where the word comes from; the origin of shamanism itself is older and still debated. It is not one religion: there are many types of shamanism, each a shamanic tradition rooted in its own culture and often still practiced today. From Siberian shamans, the story runs through Celtic druids, Korean shamans called mudang and Michael Harner's modern core shamanism. Our articles explain shamanic practices passed down through generations, like the drum, the rattle and the medicine wheel. They also ask a vital question: how do you honor the cultures these practices come from?"),
  'astral': dict(slug='astral-projection-and-signs',
    seo="Astral Projection Techniques for Curious Beginners",
    desc="Astral projection techniques explained calmly, step by step: deep relaxation, first micro-detachments, then the rope and roll-out exit methods.",
    h1="Astral projection techniques, one rung at a time",
    h2="Astral projection techniques: all the articles",
    intro="Astral projection techniques start with a paradox: a body that falls asleep while the mind stays awake. These guides move step by step, from deep relaxation to the first micro-detachments. Then come the exit techniques practitioners describe, such as the rope and the roll-out. Explore them with curiosity, and keep a critical mind about what you feel."),
 },
 'es': {
  'bases': dict(slug='practica-de-la-meditacion',
    seo="Guía para meditar: cómo meditar correctamente en 7 pasos",
    desc="Guía para meditar desde cero: cómo meditar correctamente en 7 pasos, con la postura, la respiración y qué hacer con los pensamientos. Gratis.",
    h1="Guía para meditar en casa, paso a paso y a tu ritmo",
    h2="Guía de meditación para principiantes: todos los artículos",
    intro="Esta guía para meditar está pensada para quien empieza desde cero, sin tecnicismos ni prisas. Los artículos repasan lo esencial, de la postura a los pensamientos, con prácticas de meditación sencillas para unos minutos al día. Si eres principiante y te preguntas cómo meditar en casa, o cómo meditar por primera vez sin complicarte, empieza por los siete pasos para meditar que tienes aquí abajo. Después encontrarás esquemas claros y ejercicios de meditación para principiantes."),
  'sommeil': dict(slug='sueno-y-suenos',
    seo="Cómo dormir mejor: rutina para dormir, meditación y sueños",
    desc="Cómo dormir mejor por la noche: rutina para dormir, higiene del sueño, yoga nidra y sueños lúcidos, explicados sin rodeos. Guías gratis para tus noches.",
    h1="Cómo dormir mejor y entender tus sueños",
    h2="Cómo dormir mejor y rápido: artículos para tus noches",
    intro="¿Buscas cómo dormir mejor? A veces ayuda más dejar de pelearte con la noche que sumar trucos. ¿Qué hacer antes de dormir? Una rutina para dormir mejor empieza quince minutos antes: poca luz, el teléfono lejos y un ejercicio de respiración para dormir. Aquí encontrarás rutinas sencillas, ideas para dormir con meditación, el yoga nidra y el descanso profundo sin dormir (NSDR). También te explicamos qué pasa al quedarte dormido y cómo recordar tus sueños, o incluso volverte lúcido."),
  'energie': dict(slug='chakras-y-energia',
    seo="Energía vital del cuerpo: qué es y cómo sentirla al meditar",
    desc="Qué es la energía vital y qué significa tener los chakras bloqueados: los 7 chakras como mapa simbólico del cuerpo, con ejercicios para sentirla al meditar.",
    h1="La energía vital y sus mapas del cuerpo",
    h2="Energía vital: chakras, qi gong y tercer ojo",
    intro="¿Qué es la energía vital? Es la idea, común a muchas tradiciones, de un aliento que recorre el cuerpo: el prana del yoga, la energía chi (o qi) de China, la energía kundalini. Los chakras son uno de sus mapas del cuerpo, y te los presentamos tal como son: herramientas simbólicas para guiar la atención. Aquí verás qué hay detrás de la idea de los chakras bloqueados, empezando por el chakra raíz y el del corazón. Y te proponemos ejercicios sencillos, de la meditación al chi kung, para sentir la energía vital en tu cuerpo."),
  'psy': dict(slug='emociones-y-vida-interior',
    seo="Cómo calmar la mente: emociones y pensamientos negativos",
    desc="Cómo calmar la mente y cómo dejar de tener pensamientos negativos con meditación suave: emociones, miedos y trabajo de sombra, paso a paso.",
    h1="Calmar la mente: emociones, sombra y vida interior",
    h2="Meditación para calmar la mente y liberar emociones: los artículos",
    intro="¿Cómo calmar la mente cuando no para? Meditar no consiste en dejar de sentir: te ayuda a acoger lo que aparece sin ahogarte en ello. Estos artículos abordan la sombra, los miedos y la autocrítica con ejercicios breves y referencias de la psicología, pensando en tu bienestar emocional. Si te preguntas cómo dejar de sobrepensar o cómo dejar de tener pensamientos negativos sobre ti, aprenderás a bajar el volumen de tu crítico interior. Y cuando hace falta, te invitan a pedir ayuda profesional."),
  'transe': dict(slug='trance-y-estados-de-conciencia',
    seo="Estados alterados de conciencia sin drogas: trance, hipnosis",
    desc="Qué es un estado alterado de conciencia, con ejemplos: trance, hipnosis y meditación profunda, sus mitos y cómo explorarlos sin drogas y con seguridad.",
    h1="El trance y otros estados alterados de conciencia",
    h2="Estados alterados de conciencia: ejemplos, del trance a la hipnosis",
    intro="¿Qué es un estado alterado de conciencia? En psicología, es un cambio pasajero en tu forma de percibir el tiempo, el cuerpo o los pensamientos. Los estados alterados de conciencia empiezan en lo cotidiano, con una ensoñación o una novela que te absorbe. Estos artículos explican el trance, si la hipnosis es real y qué lugar ocupan la meditación y la danza extática entre los estados de conciencia, según lo que la ciencia puede medir. También te enseñan a explorarlos sin drogas y con seguridad, sin miedo pero con los pies en la tierra."),
  'vie': dict(slug='meditacion-en-el-dia-a-dia',
    seo="Meditación diaria guiada: cómo crear un hábito que dure",
    desc="Meditación diaria que dura: cómo crear el hábito de meditar con atención plena en la vida cotidiana, en el trabajo, en pareja o antes de un examen.",
    h1="Meditación diaria: meditar en el día a día",
    h2="Meditación diaria: artículos para el día a día",
    intro="La atención plena en la vida cotidiana se entrena en lo pequeño: un café, una espera, una conversación. Meditar todos los días no exige una hora de silencio: es llevar el mindfulness al día a día. Estos artículos te acompañan con la meditación en el trabajo, en pareja y antes de un examen, cuando aprieta el estrés académico. Encontrarás ejercicios de atención plena de pocos minutos y expectativas realistas, sin promesas milagrosas. Si te cuesta empezar, una meditación diaria guiada de cinco minutos puede ayudarte a crear el hábito de meditar."),
  'lieux': dict(slug='simbolos-y-sabiduria',
    seo="Caminos de peregrinación, símbolos y arquetipos del mundo",
    desc="Caminos de peregrinación como el Camino de Santiago, símbolos y arquetipos, y el arte de ser feliz: la sabiduría del mundo, explicada con sencillez.",
    h1="Sabiduría del mundo: símbolos y caminos de peregrinación",
    h2="Símbolos y sabiduría del mundo: los artículos",
    intro="Templos, bosques, montañas: las meditaciones guiadas hablan con imágenes por una razón. Estos artículos explican el papel de los símbolos espirituales y de los arquetipos en tu práctica, y por qué usamos símbolos para meditar. También recorren caminos de peregrinación reales, como el Camino de Santiago o la ruta de los 88 templos de Shikoku, y otros viajes espirituales por el mundo. Y se preguntan, con calma, si la felicidad se puede aprender."),
  'chamanisme': dict(slug='chamanismo',
    seo="Tipos de chamanismo y de chamanes: tradiciones y prácticas",
    desc="Qué es el chamanismo y qué tipos de chamanismo existen: tradiciones chamánicas del mundo, el tambor y el animal de poder, con su historia y con respeto.",
    h1="Tipos de chamanismo y tradiciones del mundo",
    h2="Tipos de chamanismo: los artículos",
    intro="¿Qué es el chamanismo? No es una religión única, y su significado cambia de un pueblo a otro: reúne tradiciones muy distintas, del chamanismo siberiano al de la Amazonía, pasando por los druidas celtas. Por eso se habla de tipos de chamanismo, y de tipos de chamanes distintos en cada cultura. Nuestros artículos explican qué es un chamán y el sentido del axis mundi, el eje que une los tres mundos. También describen prácticas chamánicas como el tambor o la búsqueda de tu animal de poder. Y plantean una pregunta esencial: cómo respetar las culturas de las que proceden."),
  'astral': dict(slug='viaje-astral',
    seo="Guías de viaje astral paso a paso, sin sensacionalismo",
    desc="Un viaje astral se prepara poco a poco: relajación profunda, microdesprendimientos y, al final, cómo salir del cuerpo con prudencia y espíritu crítico.",
    h1="El viaje astral, sin prisas",
    h2="Viaje astral: todos los artículos",
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


def _blocs():
    """27-11 : HTML ajouté en tête de certaines pages de thème : {langue: {groupe: html}} (_tools/hubs_blocs.json)."""
    f = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hubs_blocs.json')
    try:
        return json.load(open(f, encoding='utf-8'))
    except Exception:
        return {}


def render(bb, lang, g, act, by):
    H = dict(HUBS[lang][g], bloc=_blocs().get(lang, {}).get(g)); L = LBL[lang]; BASE = bb.BASE
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
          f'<p class="lead">{E(H["intro"])}</p>'
          + (H.get('bloc') or '')   # 27-11 : bloc de réponse directe en tête (ex. EN « How to meditate correctly » en 7 étapes), HTML de _tools/hubs_blocs.json
          + (f'<h2>{E(H["h2"])}</h2>' if H.get('h2') else '')   # 20-11 : intertitre avec le mot principal (audit SEOptimer)
          + f'<p class="meta">{len(arts)} {E(L["n"])}</p><ul class="alist">')
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
