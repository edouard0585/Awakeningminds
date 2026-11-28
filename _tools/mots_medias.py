# -*- coding: utf-8 -*-
"""28-11 — mots-clés dans les MÉDIAS de chaque page (chantier SEO, demande d'Edouard : « y compris dans les titres, descriptions…
des médias »). Pour chaque page de _tools/mots_pages.json ({adresse: {"p": principal, "s": second}}), après seo_medias :
  · image principale (première image du contenu) : le mot principal ouvre son texte alternatif (« Mot principal : description »)
    et son titre, s'ils ne le contiennent pas déjà ;
  · image de partage : og:image:alt et twitter:image:alt, même règle ; ImageObject « #image-principale » : légende (caption) ;
  · extrait audio : description de l'AudioObject (« Mot principal : extrait de la méditation guidée … ») ;
  · sitemap-images.xml : titre et légende de la première image de la page.
Idempotent (rien n'est ajouté deux fois) ; une page absente de la liste n'est pas touchée. Les noms de fichiers des images ne
changent pas (images déjà indexées)."""
import html, json, os, re, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(ROOT, '_tools')
SEP = {'fr': ' : ', 'en': ': ', 'es': ': '}


def _norm(s):
    s = unicodedata.normalize('NFKD', html.unescape(s or '').lower().replace('’', "'").replace('-', ' '))
    return re.sub(r'\s+', ' ', re.sub(r"[^a-z0-9ñ ]", ' ', ''.join(c for c in s if not unicodedata.combining(c)))).strip()


def _contient(t, m):
    t, m = _norm(t), _norm(m)
    if not m or f' {m} ' in f' {t} ':
        return True
    mots = [re.escape(w) + r'(?:s|es|x)?' for w in m.split()]
    return re.search(r'\b' + r'\W+(?:\w+\W+){0,2}'.join(mots) + r'\b', t) is not None


def _cap(m):
    return m[:1].upper() + m[1:] if m and m[:1].islower() else m


ARTICLES = re.compile(r"^(Un|Une|Le|La|Les|L’|L'|Des|Deux|Trois|Quatre|A|An|The|Two|Three|Four|El|Los|Las|Unos|Unas|Dos|Tres)\b")


def _avec(lang, mot, texte):
    """« Mot principal : description » : les libellés courts déjà posés en tête (« Catégorie : », « Titre : ») sont remplacés par le
    mot principal ; rien ne change si le texte contient déjà le mot principal."""
    if not texte or _contient(texte, mot):
        return texte
    reste = texte
    for _ in range(2):
        m = re.match(r'^([^.:!?]{2,70}?)\s*:\s+(.{20,})$', reste, re.S)
        if not m: break
        reste = m.group(2)
    if ARTICLES.match(reste):
        reste = reste[:1].lower() + reste[1:]
    return _cap(mot) + SEP.get(lang, ': ') + reste


def _titre(lang, mot, v):
    """titre d'image : 70 signes au plus (règle de l'audit) ; sinon le mot principal seul."""
    nv = _avec(lang, mot, v)
    return nv if len(nv) <= 70 else (_cap(mot) if len(mot) <= 70 else v)


def _attr(balise, nom, f):
    """applique f à la valeur (déséchappée) de l'attribut nom de la balise ; renvoie la balise."""
    m = re.search(r'\b' + nom + r'="([^"]*)"', balise)
    if not m:
        return balise
    v = html.unescape(m.group(1)); nv = f(v)
    return balise if nv == v else balise[:m.start(1)] + html.escape(nv, quote=True) + balise[m.end(1):]


def page(h, lang, mot):
    # image principale : première <img> du contenu (après le début de <main>)
    i = h.find('<main')
    if i >= 0:
        m = re.compile(r'<img\b[^>]*>').search(h, i)
        if m:
            b = _attr(_attr(m.group(0), 'alt', lambda v: _avec(lang, mot, v)), 'title', lambda v: _titre(lang, mot, v))
            h = h[:m.start()] + b + h[m.end():]
    # partage
    for prop in (r'property="og:image:alt"', r'name="twitter:image:alt"'):
        m = re.search(r'<meta ' + prop + r' content="[^"]*"', h)
        if m:
            h = h[:m.start()] + _attr(m.group(0), 'content', lambda v: _avec(lang, mot, v)) + h[m.end():]
    # données structurées : AudioObject (description), ImageObject principal (légende)
    def ld(mm):
        try:
            o = json.loads(mm.group(1))
        except Exception:
            return mm.group(0)
        chg = [False]
        def marche(x):
            if isinstance(x, dict):
                t = x.get('@type')
                if t == 'AudioObject' and isinstance(x.get('description'), str):
                    d = x['description']
                    nv = d if _contient(d, mot) else _cap(mot) + SEP.get(lang, ': ') + d[:1].lower() + d[1:]
                    if nv != x['description']: x['description'] = nv; chg[0] = True
                if t == 'ImageObject' and str(x.get('@id', '')).endswith('#image-principale'):
                    c = x.get('caption')
                    nv = _avec(lang, mot, c) if isinstance(c, str) and c else _cap(mot)
                    if nv != c: x['caption'] = nv; chg[0] = True
                for v in x.values(): marche(v)
            elif isinstance(x, list):
                for v in x: marche(v)
        marche(o)
        return ('<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False).replace('<', '\\u003c') + '</script>') if chg[0] else mm.group(0)
    h = re.sub(r'<script type="application/ld\+json">(.*?)</script>', ld, h, flags=re.S)
    return h


def main():
    f = os.path.join(T, 'mots_pages.json')
    if not os.path.exists(f):
        return
    M = {u: v for u, v in json.load(open(f, encoding='utf-8')).items() if not u.startswith('_')}
    n = 0
    for u, v in M.items():
        p = os.path.join(ROOT, u.lstrip('/') + ('index.html' if u.endswith('/') else ''))
        if not os.path.exists(p) or not v.get('p'):
            continue
        lang = u.strip('/').split('/')[0]
        h = open(p, encoding='utf-8').read(); nh = page(h, lang, v['p'])
        if nh != h:
            open(p, 'w', encoding='utf-8').write(nh); n += 1
    # sitemap des images : titre et légende de la première image de chaque page
    sm = os.path.join(ROOT, 'sitemap-images.xml')
    if os.path.exists(sm):
        s = open(sm, encoding='utf-8').read()
        def url(mm):
            bloc = mm.group(0); loc = re.search(r'<loc>https://meditadream\.com([^<]+)</loc>', bloc)
            v = M.get(loc.group(1)) if loc else None
            if not v or not v.get('p'): return bloc
            lang = loc.group(1).strip('/').split('/')[0]
            im = re.search(r'<image:image>.*?</image:image>', bloc, re.S)
            if not im: return bloc
            def champ(x):
                return '<' + x.group(1) + '>' + html.escape(_avec(lang, v['p'], html.unescape(x.group(2))), quote=False) + '</' + x.group(1) + '>'
            ni = re.sub(r'<(image:title|image:caption)>(.*?)</\1>', champ, im.group(0), flags=re.S)
            return bloc[:im.start()] + ni + bloc[im.end():]
        ns = re.sub(r'<url>.*?</url>', url, s, flags=re.S)
        if ns != s:
            open(sm, 'w', encoding='utf-8').write(ns)
    print(f'✓ mots-clés dans les médias : {n} page(s) complétée(s)')


if __name__ == '__main__':
    main()
