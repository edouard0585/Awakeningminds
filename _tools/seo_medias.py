#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Passe finale « médias » de tout le site (stdlib seule : tourne aussi dans les actions GitHub du blog).

1. Chaque <img> a un texte alternatif ET un titre dans la langue de la page :
   - texte manquant ou vide → le texte déjà écrit ailleurs sur le site pour la même image dans la même langue
     (ex. le schéma d'un article repris en vignette), sinon « Illustration : <titre de la carte> » ;
   - titre manquant → le titre de la carte qui contient l'image, sinon le texte alternatif.
   - titre de plus de 70 caractères → raccourci au premier séparateur naturel (titre court, descriptif).
2. decoding="async" partout ; loading="lazy" sur toute image qui n'est pas l'image principale de la page ;
   page sans image principale déclarée → fetchpriority="high" sur la première grande image visible à l'ouverture.
3. JSON-LD : l'image de partage (og:image) décrite par un ImageObject (légende = og:image:alt, crédit MeditaDream)
   quand la page ne la décrit pas déjà.
4. sitemap-images.xml : chaque page indexable, son og:image et toutes ses images, avec <image:title> (titre court)
   et <image:caption> (texte alternatif) dans la langue de la page ; sitemap-videos.xml : chaque vidéo décrite
   par un VideoObject (titre, description, miniature, durée, date).

    python3 _tools/seo_medias.py      (appelé par build_site.py et blog_build.build())
"""
import glob, html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://meditadream.com'
LANGS = ('fr', 'en', 'es')
PREFIXE = {'fr': 'Illustration : ', 'en': 'Illustration: ', 'es': 'Ilustración: '}
IMG = re.compile(r'<img\b[^>]*>', re.S)
ATTR = lambda nom: re.compile(r'\s' + nom + r'="([^"]*)"')


def pages():
    for f in sorted(glob.glob(f'{ROOT}/**/*.html', recursive=True)):
        r = os.path.relpath(f, ROOT)
        if r.startswith(('_queue/', '_tools/', '.git/')): continue
        yield f, r


def langue(r, s):
    m = re.search(r'<html[^>]*\slang="([a-z]{2})', s)
    return m.group(1) if m else (r.split('/')[0] if r.split('/')[0] in LANGS else 'en')


def cle(src):
    """Même image quelle que soit sa copie : nom de fichier sans dossier, sans largeur ni extension."""
    b = os.path.basename(src.split('?')[0])
    return re.sub(r'(-\d{2,4})?\.(webp|png|jpe?g)$', '', b)


def texte(fragment):
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', fragment))).strip()


def titre_carte(s, pos):
    """Titre (h2/h3/b) de la carte <a>…</a> ou <li>…</li> qui contient l'image placée en `pos`."""
    debut = max(s.rfind('<a ', 0, pos), s.rfind('<li', 0, pos))
    fin_a = s.find('</a>', pos); fin_li = s.find('</li>', pos)
    fin = min(x for x in (fin_a, fin_li, pos + 1500) if x > 0)
    if debut < 0 or pos - debut > 800: return ''
    m = re.search(r'<(h[1-4]|b)\b[^>]*>(.*?)</\1>', s[pos:fin], re.S)
    return texte(m.group(2)) if m else ''


def index_alts():
    """Textes alternatifs déjà écrits sur le site : (langue, clé de l'image) → texte le plus fréquent."""
    from collections import Counter, defaultdict
    vu = defaultdict(Counter)
    for f, r in pages():
        s = open(f, encoding='utf-8').read(); l = langue(r, s)
        for m in IMG.finditer(s):
            t = m.group(0); a = ATTR('alt').search(t); src = ATTR('src').search(t)
            if a and src and a.group(1).strip(): vu[(l, cle(src.group(1)))][a.group(1)] += 1
    return {k: c.most_common(1)[0][0] for k, c in vu.items()}


SEPS = (' : ', ': ', ' — ', ' – ', ' - ', ', ', ' (', ' ; ', '. ')


def titre_court(t, maxi=70):
    """Titre d'image court (≤ 70 car.) tiré d'un texte plus long : coupé au premier séparateur naturel
    (deux-points, tiret, virgule…) placé après 15 caractères, sinon au dernier mot qui tient."""
    t = re.sub(r'\s+', ' ', t or '').strip()
    if len(t) <= maxi: return t
    coupes = [i for i in (t.find(x, 15) for x in SEPS) if 15 <= i <= maxi]
    if coupes: return t[:min(coupes)].rstrip(' ,;:—–-(.')
    return t[:maxi].rsplit(' ', 1)[0].rstrip(' ,;:—–-(.')


def largeur(t):
    w = ATTR('width').search(t)
    try: return int(w.group(1)) if w else 0
    except ValueError: return 0


MOTS_AVANT_PLI = 80   # au-delà de ~80 mots de texte avant elle, une image n'est plus visible à l'ouverture (mobile)


def image_principale(s):
    """Position de l'image principale visible à l'ouverture, quand la page n'en déclare aucune (fetchpriority="high") :
    la première image d'au moins 200 px de large, placée au plus ~80 mots après le début du H1. None sinon."""
    if 'fetchpriority="high"' in s: return None
    h1 = s.find('<h1')
    if h1 < 0: return None
    for m in IMG.finditer(s, h1):
        avant = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', s[h1:m.start()], flags=re.S)
        if len(texte(avant).split()) > MOTS_AVANT_PLI: return None
        if largeur(m.group(0)) >= 200: return m.start()
    return None


def corrige(s, l, alts):
    out, last, n = [], 0, 0
    premiere = True
    princ = image_principale(s)
    for m in IMG.finditer(s):
        t = m.group(0); t0 = t
        src = (ATTR('src').search(t) or [None, ''])[1]
        a = ATTR('alt').search(t)
        carte = titre_carte(s, m.start())
        if not a or not a.group(1).strip():
            alt = alts.get((l, cle(src))) or (html.escape(PREFIXE[l] + carte, quote=True) if carte else '')
            if alt:
                t = ATTR('alt').sub(lambda _: f' alt="{alt}"', t, 1) if a else t.replace('<img', f'<img alt="{alt}"', 1)
        ti0 = ATTR('title').search(t)
        if not ti0 or len(html.unescape(ti0.group(1))) > 70:
            ti = titre_court(html.unescape(ti0.group(1)) if ti0 else (carte or html.unescape((ATTR('alt').search(t) or [None, ''])[1])))
            if ti:
                ti = html.escape(ti, quote=True)
                t = ATTR('title').sub(lambda _: f' title="{ti}"', t, 1) if ti0 else t[:-1].rstrip('/').rstrip() + f' title="{ti}">'
        if 'decoding=' not in t: t = t[:-1].rstrip('/').rstrip() + ' decoding="async">'
        if m.start() == princ:
            # image principale visible à l'ouverture : chargée en priorité, jamais différée
            t = re.sub(r'\sloading="lazy"', '', t)
            t = t[:-1].rstrip('/').rstrip() + ' fetchpriority="high">'
        if premiere:
            premiere = False   # la première image d'une page peut être l'image principale : jamais différée d'office
        elif 'loading=' not in t and 'fetchpriority=' not in t:
            t = t[:-1].rstrip('/').rstrip() + ' loading="lazy">'
        if t != t0: n += 1
        out.append(s[last:m.start()]); out.append(t); last = m.end()
    out.append(s[last:])
    return ''.join(out), n


def indexable(s):
    return not re.search(r'<meta name="robots" content="[^"]*noindex', s) and 'http-equiv="refresh"' not in s


def canonique(s):
    m = re.search(r'<link rel="canonical" href="([^"]+)"', s)
    return m.group(1) if m else None


def absolu(src, r):
    if src.startswith('http'): return src
    if src.startswith('/'): return BASE + src
    return BASE + '/' + os.path.normpath(os.path.join(os.path.dirname(r), src)).replace(os.sep, '/')


def secondes(iso):
    m = re.fullmatch(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso or '')
    return (int(m.group(1) or 0) * 3600 + int(m.group(2) or 0) * 60 + int(m.group(3) or 0)) if m else None


def videos_ld(s):
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try: d = json.loads(m.group(1))
        except Exception: continue
        for x in (d.get('@graph') or [d]) if isinstance(d, dict) else d:
            if isinstance(x, dict) and x.get('@type') == 'VideoObject': yield x


def x(v):
    return html.escape(str(v), quote=False)


def meta(s, k):
    m = re.search(r'<meta (?:property|name)="' + re.escape(k) + r'" content="([^"]*)"', s)
    return html.unescape(m.group(1)) if m else ''


def nom_page(s):
    """Nom court de la page : le H1, sinon le titre sans « · MeditaDream »."""
    m = re.search(r'<h1\b[^>]*>(.*?)</h1>', s, re.S)
    t = texte(m.group(1)) if m else texte((re.search(r'<title>(.*?)</title>', s, re.S) or [None, ''])[1])
    return re.sub(r'\s*[·|—-]\s*MeditaDream\s*$', '', t).strip()


IO_BLOC = re.compile(r'<script type="application/ld\+json">\{"@context": "https://schema.org", "@type": "ImageObject", "@id": "[^"]*#image-principale".*?</script>', re.S)


def image_ld(s, l, loc):
    """ImageObject de l'image de partage (og:image) quand aucun JSON-LD de la page ne la décrit déjà comme ImageObject."""
    s = IO_BLOC.sub('', s)
    og = meta(s, 'og:image')
    if not og.startswith(BASE): return s
    for v in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        if '"ImageObject"' in v.group(1) and json.dumps(og)[1:-1] in v.group(1).replace('\\/', '/'):
            try:
                d = json.loads(v.group(1))
            except Exception: continue
            if any(isinstance(o, dict) and o.get('@type') == 'ImageObject' and og in (o.get('url'), o.get('contentUrl')) for o in objets(d)):
                return s
    nom = nom_page(s)
    io = {'@context': 'https://schema.org', '@type': 'ImageObject', '@id': loc + '#image-principale',
          'url': og, 'contentUrl': og, 'name': titre_court(nom) or 'MeditaDream',
          'caption': meta(s, 'og:image:alt') or nom, 'inLanguage': l, 'representativeOfPage': True,
          'creditText': 'MeditaDream', 'copyrightNotice': '© MeditaDream',
          'creator': {'@type': 'Organization', 'name': 'MeditaDream', 'url': BASE + '/'}}
    w, h = meta(s, 'og:image:width'), meta(s, 'og:image:height')
    if w.isdigit() and h.isdigit(): io.update(width=int(w), height=int(h))
    bloc = '<script type="application/ld+json">' + json.dumps(io, ensure_ascii=False).replace('<', '\\u003c') + '</script>'
    return s.replace('</head>', bloc + '</head>', 1) if '</head>' in s else s


def objets(d):
    if isinstance(d, dict):
        yield d
        for v in d.values(): yield from objets(v)
    elif isinstance(d, list):
        for v in d: yield from objets(v)


def entree_image(u, titre, legende):
    return (f'<image:image><image:loc>{x(u)}</image:loc>'
            + (f'<image:title>{x(titre)}</image:title>' if titre else '')
            + (f'<image:caption>{x(legende)}</image:caption>' if legende else '') + '</image:image>')


def main():
    alts = index_alts()
    total = 0
    imgs, vids = [], []
    for f, r in pages():
        s = open(f, encoding='utf-8').read(); l = langue(r, s)
        s2, n = corrige(s, l, alts)
        loc = canonique(s2)
        if loc and indexable(s2): s2 = image_ld(s2, l, loc)
        if s2 != s: open(f, 'w', encoding='utf-8').write(s2); total += n
        if not loc or not indexable(s2): continue
        vus = {}
        og = meta(s2, 'og:image')
        if og.startswith(BASE):   # l'image de partage aussi (pages sans <img>, ou image hors du corps)
            vus[og] = (titre_court(nom_page(s2)), meta(s2, 'og:image:alt'))
        for m in IMG.finditer(s2):
            t = m.group(0); src = ATTR('src').search(t)
            if not src or src.group(1).startswith('data:'): continue
            u = absolu(src.group(1), r)
            alt = html.unescape((ATTR('alt').search(t) or [None, ''])[1]).strip()
            ti = html.unescape((ATTR('title').search(t) or [None, ''])[1]).strip()
            if u not in vus or not vus[u][1]: vus[u] = (ti or titre_court(alt), alt or ti)
        if vus:
            imgs.append(f'<url><loc>{x(loc)}</loc>' + ''.join(entree_image(u, ti, cap) for u, (ti, cap) in list(vus.items())[:1000]) + '</url>')
        for v in videos_ld(s2):
            if not v.get('contentUrl') or not v.get('thumbnailUrl'): continue
            d = secondes(v.get('duration'))
            vids.append(f'<url><loc>{x(loc)}</loc><video:video><video:thumbnail_loc>{x(v["thumbnailUrl"])}</video:thumbnail_loc>'
                        f'<video:title>{x(v.get("name", ""))}</video:title><video:description>{x(v.get("description", ""))}</video:description>'
                        f'<video:content_loc>{x(v["contentUrl"])}</video:content_loc>' + (f'<video:duration>{d}</video:duration>' if d else '')
                        + (f'<video:publication_date>{x(v["uploadDate"])}</video:publication_date>' if v.get('uploadDate') else '')
                        + '<video:family_friendly>yes</video:family_friendly><video:live>no</video:live></video:video></url>')
    open(f'{ROOT}/sitemap-images.xml', 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">' + ''.join(imgs) + '</urlset>\n')
    open(f'{ROOT}/sitemap-videos.xml', 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">' + ''.join(vids) + '</urlset>\n')
    nb = sum(u.count('<image:image>') for u in imgs)
    print(f'✓ médias : {total} image(s) complétée(s) · sitemap-images.xml {len(imgs)} pages / {nb} images · sitemap-videos.xml {len(vids)} vidéo(s)')


if __name__ == '__main__':
    main()
