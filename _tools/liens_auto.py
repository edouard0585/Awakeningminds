# -*- coding: utf-8 -*-
"""07-11 — liens internes automatiques dans les articles du blog (carte des mots-clés de meditadream.com).

Chaque page du site a un mot-clé principal (_tools/liens_cles.json, exporté par la carte des mots-clés). Quand un
article publié contient, dans un paragraphe ou une liste, le mot principal d'une AUTRE page déjà en ligne, ce mot
devient un lien vers elle. Au plus 3 liens par article, un seul par page visée, jamais dans un titre, une légende,
la FAQ, l'encadré « À pratiquer » ou un lien existant, jamais vers l'article lui-même.

Les pages pas encore en ligne (articles programmés, catégorie cachée par a_venir.json) n'ont pas de fichier : elles
ne reçoivent aucun lien. Dès leur publication, la construction suivante (action GitHub comprise) les relie toute seule.
Idempotent : les liens ajoutés portent la classe « lien-cle » et sont refaits à chaque construction.
"""
import json, os, re, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX = 3
ACC = {'a': 'aàâäáã', 'e': 'eéèêë', 'i': 'iîïí', 'o': 'oôöóõ', 'u': 'uùûüú', 'c': 'cç', 'n': 'nñ', 'y': 'yÿ'}
VIDES = {'br', 'img', 'hr', 'input', 'meta', 'link', 'source', 'wbr', 'col', 'area', 'base', 'embed', 'track'}
INTERDITS = {'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'figcaption', 'summary', 'button', 'script', 'style', 'details',
             'nav', 'header', 'footer', 'label', 'code', 'pre'}
TAG = re.compile(r'(<[^>]+>)')
AUTO = re.compile(r'<a href="[^"]*" class="lien-cle">(.*?)</a>', re.S)


def _sans_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))


def motif(mot):
    """expression qui retrouve le mot dans un texte : accents, majuscules et pluriel simple ignorés."""
    mots = [w for w in re.split(r"[\s'’\-]+", _sans_accents(mot.lower())) if w]
    if not mots: return None
    parts = [''.join(f'[{ACC[c]}{ACC[c].upper()}]' if c in ACC else re.escape(c) for c in w) + r'(?:s|x|es)?' for w in mots]
    return re.compile(r'(?<![\w])' + r"[\s'’\-]+".join(parts) + r'(?![\w])', re.I)


def _fichier(url):
    p = url.split('#')[0]
    return os.path.join(ROOT, p.lstrip('/') + ('index.html' if p.endswith('/') else ''))


def cibles(lang):
    """[(expression, adresse)] des pages EN LIGNE, du mot le plus long au plus court (2 mots au moins)."""
    try:
        d = json.load(open(os.path.join(ROOT, '_tools', 'liens_cles.json'), encoding='utf-8')).get(lang, [])
    except Exception:
        return []
    out = []
    for mot, url in d:
        if len(mot.split()) < 2 or not os.path.exists(_fichier(url)): continue
        rx = motif(mot)
        if rx: out.append((len(mot), rx, url))
    return [(rx, url) for _, rx, url in sorted(out, key=lambda x: -x[0])]


def _deja(url, hrefs):
    bout = url.split('#')[0].rstrip('/').split('/')[-1]
    return any(bout and bout in h for h in hrefs)


def lier(page, lang, url_page, cib):
    """ajoute au plus MAX liens dans le corps de l'article (entre <article class="post"> et la FAQ)."""
    i = page.find('<article class="post">')
    if i < 0: return page, 0
    j = page.find('<section class="afaq">', i)
    j = page.find('</article>', i) if j < 0 else j
    corps = AUTO.sub(r'\1', page[i:j])
    hrefs = re.findall(r'href="([^"]+)"', corps)
    parts = TAG.split(corps)
    pile, n, faits = [], 0, set()
    for k, p in enumerate(parts):
        if p.startswith('<'):
            m = re.match(r'<\s*(/)?\s*([a-zA-Z0-9]+)([^>]*)>', p)
            if not m: continue
            tag = m.group(2).lower()
            if tag in VIDES or p.endswith('/>'): continue
            if m.group(1):
                while pile and pile.pop()[0] != tag: pass
            else:
                pile.append((tag, m.group(3)))
            continue
        if n >= MAX: break
        if not p.strip(): continue
        tags = {t for t, _ in pile}
        if not tags & {'p', 'li'} or tags & INTERDITS: continue
        if any('ap-prat' in a or 'afaq' in a or 'crumbs' in a for _, a in pile): continue
        for rx, url in cib:
            if url == url_page or url in faits or _deja(url, hrefs): continue
            m = rx.search(p)
            if m:
                parts[k] = p[:m.start()] + f'<a href="{url}" class="lien-cle">' + p[m.start():m.end()] + '</a>' + p[m.end():]
                faits.add(url); n += 1
                break
    return page[:i] + ''.join(parts) + page[j:], n


def main():
    total = 0
    for lang in ('fr', 'en', 'es'):
        cib = cibles(lang)
        if not cib: continue
        d = os.path.join(ROOT, lang, 'blog')
        for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if not f.endswith('.html') or f == 'index.html': continue
            ch = os.path.join(d, f)
            s = open(ch, encoding='utf-8').read()
            if '<article class="post">' not in s: continue
            neuf, n = lier(s, lang, f'/{lang}/blog/{f}', cib)
            if neuf != s:
                open(ch, 'w', encoding='utf-8').write(neuf)
            total += n
    print(f'✓ liens internes automatiques (mots-clés) : {total}')


if __name__ == '__main__':
    main()
