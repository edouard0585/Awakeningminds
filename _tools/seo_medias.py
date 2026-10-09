#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Passe finale « médias » de tout le site (stdlib seule : tourne aussi dans les actions GitHub du blog).

1. Chaque <img> a un texte alternatif ET un titre dans la langue de la page :
   - texte manquant ou vide → le texte déjà écrit ailleurs sur le site pour la même image dans la même langue
     (ex. le schéma d'un article repris en vignette), sinon « Illustration : <titre de la carte> » ;
   - titre manquant → le titre de la carte qui contient l'image, sinon le texte alternatif.
2. decoding="async" partout ; loading="lazy" sur toute image qui n'est pas l'image principale de la page.
3. sitemap-images.xml : chaque page indexable et toutes ses images ; sitemap-videos.xml : chaque vidéo décrite
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


def corrige(s, l, alts):
    out, last, n = [], 0, 0
    premiere = True
    for m in IMG.finditer(s):
        t = m.group(0); t0 = t
        src = (ATTR('src').search(t) or [None, ''])[1]
        a = ATTR('alt').search(t)
        carte = titre_carte(s, m.start())
        if not a or not a.group(1).strip():
            alt = alts.get((l, cle(src))) or (html.escape(PREFIXE[l] + carte, quote=True) if carte else '')
            if alt:
                t = ATTR('alt').sub(lambda _: f' alt="{alt}"', t, 1) if a else t.replace('<img', f'<img alt="{alt}"', 1)
        if not ATTR('title').search(t):
            ti = carte or html.unescape((ATTR('alt').search(t) or [None, ''])[1])
            if ti: t = t[:-1].rstrip('/').rstrip() + f' title="{html.escape(ti[:110], quote=True)}">'
        if 'decoding=' not in t: t = t[:-1].rstrip('/').rstrip() + ' decoding="async">'
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


def main():
    alts = index_alts()
    total = 0
    imgs, vids = [], []
    for f, r in pages():
        s = open(f, encoding='utf-8').read(); l = langue(r, s)
        s2, n = corrige(s, l, alts)
        if n: open(f, 'w', encoding='utf-8').write(s2); total += n
        loc = canonique(s2)
        if not loc or not indexable(s2): continue
        vus = []
        for m in IMG.finditer(s2):
            src = ATTR('src').search(m.group(0))
            if not src or src.group(1).startswith('data:'): continue
            u = absolu(src.group(1), r)
            if u not in vus: vus.append(u)
        if vus:
            imgs.append(f'<url><loc>{x(loc)}</loc>' + ''.join(f'<image:image><image:loc>{x(u)}</image:loc></image:image>' for u in vus[:1000]) + '</url>')
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
