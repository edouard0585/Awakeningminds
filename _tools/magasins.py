"""Badges officiels App Store et Google Play avec lien de téléchargement (demande d'Edouard du 06-11-2026 : « sur chaque
page et au sein de chaque blog post, au meilleur endroit, pour toutes les pages et posts publiés et programmés »).
Appelé par seo_medias.py (passe finale de build_site.py et de blog_build.build(), donc aussi à chaque publication
programmée du blog) :
1. dans chaque encadré « cta » (articles du blog, piliers, méditations, mondes, formations…), sous le texte et avant le
   bouton : c'est l'endroit où le lecteur décide de pratiquer ;
2. accueils : les badges à la place des deux boutons texte de la section « Télécharge MeditaDream » (#download) ;
3. tout en haut du pied de page de chaque page (sauf la page de choix de langue et les pages de redirection /app,
   /app-store, /google-play) : « Télécharge MeditaDream » + les badges + la mention des marques.
Badges officiels, non modifiés, servis par Apple (Apple Marketing Tools) et Google (générateur de badges Google Play),
dans la langue de la page ; même hauteur visible (le PNG Google a une marge transparente, différente en anglais)."""
import re

APPLE = 'https://apps.apple.com/app/meditadream/id6808918209'
GOOGLE = 'https://play.google.com/store/apps/details?id=com.edouardrichemond.mindexploreroffline'
BADGE_APPLE = 'https://toolbox.marketingtools.apple.com/api/v2/badges/download-on-the-app-store/black/{}'
BADGE_GOOGLE = 'https://play.google.com/intl/en_us/badges/static/images/badges/{}_badge_web_generic.png'
LOCALE_APPLE = {'fr': ('fr-fr', 126.50751), 'en': ('en-us', 119.66407), 'es': ('es-es', 119.66407)}
# partie visible du PNG Google (646 × 250) : en = 564 × 168 à 41 px du bord ; fr et es = 646 × 192 à 29 px du haut
VISIBLE_GOOGLE = {'en': (41, 41, 168), 'fr': (0, 29, 192), 'es': (0, 29, 192)}
ALT = {
    'fr': ("Télécharger MeditaDream dans l'App Store", 'Disponible sur Google Play'),
    'en': ('Download MeditaDream on the App Store', 'Get MeditaDream on Google Play'),
    'es': ('Descargar MeditaDream en el App Store', 'Disponible en Google Play'),
}
TITRE = {'fr': 'Télécharge MeditaDream, gratuitement', 'en': 'Download MeditaDream for free', 'es': 'Descarga MeditaDream gratis'}
MARQUES = {
    'fr': "App Store est une marque de service d'Apple Inc. Google Play et le logo Google Play sont des marques de Google LLC.",
    'en': 'App Store is a service mark of Apple Inc. Google Play and the Google Play logo are trademarks of Google LLC.',
    'es': 'App Store es una marca de servicio de Apple Inc. Google Play y el logotipo de Google Play son marcas de Google LLC.',
}
NEUTRE = 'background:none!important;padding:0!important;margin:0!important;border:0!important;box-shadow:none!important;'
BLOC = re.compile(r'<!--mag-->.*?<!--/mag-->', re.S)
CTA = re.compile(r'(<div class="cta">.*?</p>)', re.S)
STORES = re.compile(r'(<div class="stores">)(.*?)(</div>)', re.S)
EXCLUS = ('index.html', '404.html', 'app/', 'app-store/', 'google-play/')


def badges(l, h=44, campagne='encadre'):
    l = l if l in ALT else 'en'
    loc, w = LOCALE_APPLE[l]
    gx, gy, gh = VISIBLE_GOOGLE[l]
    ih = h * 250 / gh                       # hauteur du PNG pour que la partie visible fasse h
    iw = ih * 646 / 250
    mv, mh = gy / 250 * ih, gx / 646 * iw
    a = (f'<a href="{APPLE}" target="_blank" rel="noopener" style="display:inline-block!important;line-height:0;{NEUTRE}">'
         f'<img src="{BADGE_APPLE.format(loc)}" alt="{ALT[l][0]}" title="{ALT[l][0]}" width="{round(w * h / 40)}" height="{h}" '
         f'loading="lazy" decoding="async" data-nosm="1" style="display:block!important;height:{h}px!important;width:auto!important;max-width:none!important;margin:0!important"></a>')
    vw = (646 - 2 * gx) / gh * h            # largeur visible du badge Google
    # le PNG Google a une marge à peine teintée : on ne garde que le badge (cadre à la taille visible, coins arrondis)
    lien_g = f'{GOOGLE}&amp;referrer=utm_source%3Dmeditadream.com%26utm_medium%3Dbadge-site%26utm_campaign%3D{campagne}'  # source dans la Play Console
    g = (f'<a href="{lien_g}" target="_blank" rel="noopener" style="display:inline-block!important;line-height:0;overflow:hidden!important;'
         f'width:{vw:.2f}px!important;height:{h}px!important;border-radius:{0.12 * h:.1f}px!important;{NEUTRE}">'
         f'<img src="{BADGE_GOOGLE.format(l)}" alt="{ALT[l][1]}" title="{ALT[l][1]}" width="{round(iw)}" height="{round(ih)}" '
         f'loading="lazy" decoding="async" data-nosm="1" style="display:block!important;height:{ih:.2f}px!important;width:auto!important;max-width:none!important;margin:-{mv:.2f}px 0 0 -{mh:.2f}px!important"></a>')
    return a + g


def rangee(l, h=44, marge='6px 0 18px', campagne='encadre'):
    return (f'<div class="badges" style="display:flex;flex-wrap:wrap;gap:12px;justify-content:center;align-items:center;margin:{marge}">'
            f'{badges(l, h, campagne)}</div>')


def pied(l):
    l = l if l in ALT else 'en'
    return (f'<!--mag--><div class="wrap" style="display:flex;flex-direction:column;align-items:center;gap:8px;padding-top:6px;padding-bottom:14px;'
            f'margin-bottom:14px;border-bottom:1px solid rgba(255,255,255,.08);text-align:center">'
            f'<span style="font-size:14px;color:inherit">{TITRE[l]}</span>{rangee(l, 40, "0", "pied-de-page")}'
            f'<small style="font-size:11px;opacity:.6;max-width:640px;line-height:1.4">{MARQUES[l]}</small></div><!--/mag-->')


def ajoute(s, l, r):
    """Pose (ou repose) les badges ; ne fait rien sur les pages exclues. Idempotent (balises <!--mag-->)."""
    s = BLOC.sub('', s)
    if r in EXCLUS or r.startswith(EXCLUS[2:]):
        return s
    # 1. encadrés « cta » : sous le texte, avant le bouton (jamais hors de l'encadré : bornes vérifiées)
    morceaux, pos = [], 0
    for m in re.finditer(r'<div class="cta">', s):
        if m.start() < pos:
            continue
        fin = s.find('</div>', m.end())
        if fin < 0:
            continue
        p = s.find('</p>', m.end(), fin)
        coupe = p + len('</p>') if p >= 0 else fin
        morceaux.append(s[pos:coupe] + '<!--mag-->' + rangee(l) + '<!--/mag-->')
        pos = coupe
    s = ''.join(morceaux) + s[pos:]
    # 2. accueils : section #download
    if 'id="download"' in s:
        s = STORES.sub(lambda m: m.group(1) + '<!--mag-->' + badges(l, 48, 'accueil') + '<!--/mag-->' + m.group(3), s, count=1)
    # 3. haut du pied de page
    i = s.rfind('<footer')
    if i >= 0:
        j = s.index('>', i) + 1
        s = s[:j] + pied(l) + s[j:]
    return s
