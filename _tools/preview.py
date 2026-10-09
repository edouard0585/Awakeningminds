#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aperçu exact d'un article (publié ou non), rendu par le générateur du site, pour l'espace privé.

    python3 _tools/preview.py <clé> [edits.json]
      clé : fr:<num> | en:<num>   (articles du mercredi/samedi)  ·  q:<id>:<lang> (série du lundi)
      edits.json : modifications en attente de l'espace privé (appliquées seulement à l'aperçu)
Écrit la page HTML sur la sortie standard, avec <base> vers le site pour que photos et liens s'affichent.
Rien n'est écrit dans le dépôt.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blog_build as bb
import blog_fr

key = sys.argv[1]
E = {}
if len(sys.argv) > 2 and os.path.exists(sys.argv[2]):
    E = json.load(open(sys.argv[2], encoding='utf-8')).get('items') or {}
    if not isinstance(E, dict): E = {}
p = key.split(':')
bb.SCHEMA_FILES = {int(k): v for k, v in bb._load_schema_files().items()}
bb._scan_hero_alts()
MEDIA = 'https://espace.awakeningminds.app/media/'

if p[0] in ('fr', 'en'):
    arts = blog_fr.load()
    a = next((x for x in arts if str(x['num']) == p[1]), None)
    if a is None or (p[0] == 'en' and not a.get('en')): sys.exit('Article introuvable')
    for lang in ('fr', 'en'):           # modifications en attente, dans les deux langues
        e = E.get(f'{lang}:{p[1]}', {}); t = a if lang == 'fr' else a.get('en')
        if not t or not e: continue
        for k in ('title', 'seo_title', 'desc'):
            if isinstance(e.get(k), str) and e[k].strip(): t[k] = e[k].strip()
        if e.get('media_inline'): t['media_inline'] = True
        if isinstance(e.get('photo'), str) and e['photo'].startswith(MEDIA):
            t['photo'] = dict(t['photo'], src=e['photo'], src_s=e['photo'])
        if lang == 'fr' and isinstance(e.get('publish_at'), str): a['publish_at'] = e['publish_at']
        if isinstance(e.get('body'), str) and e['body'].strip(): t['_body'] = e['body']
    if not a.get('published'): a['published'] = a['publish_at'][:10]
    orig_body = blog_fr.body_html
    def body_html(x, lang='fr'):
        t = x if lang == 'fr' else x.get('en', {})
        return t.get('_body') or orig_body(x, lang)
    blog_fr.body_html = body_html
    html = blog_fr.render_article(bb, a, arts, p[0])
    lang = p[0]
else:
    arts = bb.load()
    lang = p[2]
    a = next((x for x in arts if x['id'] == p[1]), None)
    if a is None: sys.exit('Article introuvable')
    e = E.get(key, {})
    for k in ('title', 'desc'):
        if isinstance(e.get(k), str) and e[k].strip(): a[k][lang] = e[k].strip()
    if not a.get('published'):
        from datetime import date
        a['published'] = date.today().isoformat()
    html = bb.render_article(a, lang, arts)

# les chemins relatifs (../../assets, ../, article.html) doivent viser le site en ligne
html = html.replace('<head>', f'<head><base href="https://meditadream.com/{lang}/blog/">', 1)
html = html.replace('../../assets/blog/' + MEDIA, MEDIA)  # médias envoyés depuis l'espace privé
sys.stdout.write(html)
