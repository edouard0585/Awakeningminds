#!/usr/bin/env python3
"""Reporte sur le site les modifications faites dans l'espace privé (https://espace.meditadream.com/admin/).

Lit /am/edits.json : {"items": {"fr:<num>": {...}, "en:<num>": {...}, "q:<id>:<lang>": {...}}}
  fr/en : title, seo_title, desc, body (HTML), et pour fr : publish_at, hold
  q     : title, desc d'un article de la série trilingue du lundi
Idempotent : réappliquer les mêmes valeurs ne change rien. Reconstruit le blog si quelque chose a changé.
"""
import json, os, re, sys, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = 'https://espace.meditadream.com/edits.json'
try:
    req = urllib.request.Request(URL, headers={'User-Agent': 'MeditaDream-blog-sync/1.0 (+https://meditadream.com)', 'Accept': 'application/json'})
    E = json.load(urllib.request.urlopen(req, timeout=20)).get('items') or {}
    if not isinstance(E, dict): E = {}
except Exception as e:
    print(f'Espace privé injoignable ({e}) : rien à appliquer.'); sys.exit(0)
FRQ = f'{ROOT}/_queue/articles_fr.json'; Q3 = f'{ROOT}/_queue/articles.json'
fr = json.load(open(FRQ, encoding='utf-8')); q3 = json.load(open(Q3, encoding='utf-8'))
by = {str(a['num']): a for a in fr}; byq = {a['id']: a for a in q3}
changed = []
MEDIA = 'https://espace.meditadream.com/media/'
UP = f'{ROOT}/assets/blog/up'
def fetch_media(url):
    """Copie dans assets/blog/up/ une photo ou vidéo envoyée depuis l'éditeur ; renvoie son chemin relatif."""
    name = os.path.basename(url.split('?')[0])
    if not re.fullmatch(r'[A-Za-z0-9._-]{3,80}', name): return None
    os.makedirs(UP, exist_ok=True)
    dst = f'{UP}/{name}'
    if not os.path.exists(dst):
        req = urllib.request.Request(MEDIA + name, headers={'User-Agent': 'MeditaDream-blog-sync/1.0'})
        data = urllib.request.urlopen(req, timeout=120).read()
        open(dst, 'wb').write(data); changed.append(f'média {name}')
    return f'up/{name}'
def localize(body):
    def sub(m):
        rel = fetch_media(m.group(1))
        return f'../../assets/blog/{rel}' if rel else m.group(0)
    body = re.sub(re.escape(MEDIA) + r'([A-Za-z0-9._-]+)', lambda m: sub(m), body)
    return body.replace('https://meditadream.com/assets/blog/', '../../assets/blog/')
def put(obj, k, v, label):
    if obj.get(k) != v: obj[k] = v; changed.append(label)
for key, e in E.items():
    p = key.split(':')
    if p[0] in ('fr', 'en') and p[1] in by:
        a = by[p[1]]; t = a if p[0] == 'fr' else a.get('en')
        if t is None: continue
        for k in ('title', 'seo_title', 'desc'):
            if isinstance(e.get(k), str) and e[k].strip(): put(t, k, e[k].strip(), f'{key} {k}')
        if p[0] == 'fr' and not a.get('published'):
            if isinstance(e.get('publish_at'), str) and len(e['publish_at']) == 16: put(a, 'publish_at', e['publish_at'], f'{key} date')
            if 'hold' in e: put(a, 'hold', bool(e['hold']), f'{key} suspension')
        if isinstance(e.get('body'), str) and e['body'].strip():
            f = f'{ROOT}/_queue/sections/{p[0]}-blog/{p[1]}.html'
            body = localize(e['body'])
            if open(f, encoding='utf-8').read() != body:
                open(f, 'w', encoding='utf-8').write(body); changed.append(f'{key} texte')
        if e.get('media_inline'): put(t, 'media_inline', True, f'{key} mise en page')
        if isinstance(e.get('photo'), str) and e['photo'].startswith(MEDIA):
            rel = fetch_media(e['photo'])
            if rel and t['photo'].get('src') != rel:
                sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
                from blog_build import webp_size
                w, h = webp_size(f'{ROOT}/assets/blog/{rel}') or (1200, 675)
                t['photo'] = dict(t['photo'], src=rel, src_s=rel, w=w, h=h); changed.append(f'{key} photo principale')
        if a.get('published') and any(c.startswith(key) for c in changed):
            from datetime import date
            t['modified'] = date.today().isoformat()
    elif p[0] == 'q' and len(p) == 3 and p[1] in byq and p[2] in ('fr', 'en', 'es'):
        a = byq[p[1]]
        for k in ('title', 'desc'):
            if isinstance(e.get(k), str) and e[k].strip() and a[k].get(p[2]) != e[k].strip():
                a[k][p[2]] = e[k].strip(); changed.append(f'{key} {k}')
if not changed:
    print('Aucune modification nouvelle.'); sys.exit(0)
fr.sort(key=lambda a: a['publish_at'])
json.dump(fr, open(FRQ, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(q3, open(Q3, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blog_build
blog_build.build()
print('✓ appliqué :', ', '.join(changed))
