"""Bandeau fin de téléchargement en haut de chaque page (demande d'Edouard du 06-11-2026 : « met en haut de chaque page
un petit header fin mais beau avec lien de téléchargement »).
Posé par seo_medias.py (passe finale de build_site.py et de blog_build.build(), donc aussi à chaque publication
programmée du blog), juste après <body>, AVANT l'en-tête collant du site : il se voit à l'ouverture et part au défilement,
l'en-tête du site reste collé en haut. Hauteur fixe (34 px), image avec largeur et hauteur, styles en ligne : aucun
décalage de mise en page (CLS). Tout le bandeau est un seul lien vers /app/ (le bon magasin selon le téléphone, les deux
boutons sur ordinateur ; les clics sont comptés par assets/mesure.js). Texte propre à chaque langue (jamais traduit mot
à mot) : fr « en français, gratuites, sans pub ni abonnement », en « no subscription, no ads, no account », es « en
español, gratis, sin conexión ». Idempotent (balises <!--bandeau-->)."""
import re

TEXTES = {
    'fr': ('Méditations guidées en français, 100 % gratuites, sans pub ni abonnement', '100 % gratuite', 'Télécharger', "Télécharger l'application MeditaDream"),
    'en': ('Free guided meditation app, no subscription, no ads, no account', '100% free', 'Get the app', 'Download the MeditaDream app'),
    'es': ('Meditaciones guiadas en español, gratis y sin conexión', '100 % gratis', 'Descargar', 'Descargar la app MeditaDream'),
}
STYLE = ('<style>.mdb{display:block;height:34px;margin:0;background:linear-gradient(90deg,#100d20,#1c1736 50%,#100d20);'
         'border-bottom:1px solid rgba(212,175,106,.32);font:13px/34px system-ui,-apple-system,"Segoe UI",sans-serif;position:relative;z-index:60}'
         '.mdb a{display:flex;align-items:center;justify-content:center;gap:9px;height:34px;padding:0 12px;color:#F5E6C8;text-decoration:none;white-space:nowrap;overflow:hidden}'
         '.mdb i{display:block;width:20px;height:20px;border-radius:50%;flex:none;background:url(/assets/brand/favicon-rond-48.png) center/cover}'
         '.mdb b{color:#E9CF94;font-weight:600;letter-spacing:.2px}'
         '.mdb .mdb-l{opacity:.9;overflow:hidden;text-overflow:ellipsis}.mdb .mdb-s{display:none;opacity:.9}'
         '.mdb .mdb-b{flex:none;background:#D4AF6A;color:#0A0A14;border-radius:999px;padding:0 12px;line-height:22px;height:22px;font-weight:600;font-size:12px}'
         '.mdb a:hover .mdb-b,.mdb a:focus-visible .mdb-b{background:#E9CF94}.mdb a:focus-visible{outline:2px solid #E9CF94;outline-offset:-3px}'
         '@media(max-width:560px){.mdb .mdb-l{display:none}.mdb .mdb-s{display:inline}}</style>')
BLOC = re.compile(r'<!--bandeau-->.*?<!--/bandeau-->', re.S)
EXCLUS = ('index.html', '404.html')
PREFIXES_EXCLUS = ('app/', 'app-store/', 'google-play/')


def html_bandeau(l):
    l = l if l in TEXTES else 'en'
    long_, court, bouton, aria = TEXTES[l]
    return ('<!--bandeau--><aside class="mdb" aria-label="MeditaDream">' + STYLE
            + f'<a href="/app/" title="{aria}"><i aria-hidden="true"></i>'
            + f'<span><b>MeditaDream</b><span class="mdb-l"> · {long_}</span><span class="mdb-s"> · {court}</span></span>'
            + f'<span class="mdb-b">{bouton}</span></a></aside><!--/bandeau-->')


def ajoute(s, l, r):
    """Pose (ou repose) le bandeau juste après <body>. Ne fait rien sur les pages exclues."""
    s = BLOC.sub('', s)
    if r in EXCLUS or r.startswith(PREFIXES_EXCLUS):
        return s
    m = re.search(r'<body[^>]*>', s)
    if not m:
        return s
    return s[:m.end()] + html_bandeau(l) + s[m.end():]
