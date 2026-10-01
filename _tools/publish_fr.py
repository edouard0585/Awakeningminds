#!/usr/bin/env python3
"""Publie les articles français seuls dont l'heure est venue (mercredi 16 h et samedi 11 h, heure de Paris).

Appelé plusieurs fois le mercredi et le samedi par GitHub Actions (publish-fr.yml) : publie tout article
dont `publish_at` est passé et qui n'est pas encore publié, puis reconstruit le blog.
  python3 _tools/publish_fr.py            → publie ce qui est dû
  python3 _tools/publish_fr.py --liste    → affiche le calendrier sans rien changer
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blog_fr
arts = blog_fr.load()
now = blog_fr.paris_now()
if '--liste' in sys.argv:
    for a in arts:
        print(a['publish_at'].replace('T', ' '), '✓' if a.get('published') else ('⏸' if a.get('hold') else ' '), f"#{a['num']:<3}",
              f"{len(a['schemas'])} schéma(s)", '+EN' if a.get('en') else '   ', a['seo_title'])
    sys.exit(0)
dus = [a for a in arts if not a.get('published') and not a.get('hold') and a['publish_at'] <= now.strftime('%Y-%m-%dT%H:%M')]
if not dus:
    print(f'Rien à publier ({now:%Y-%m-%d %H:%M} à Paris).'); sys.exit(0)
for a in dus:
    a['published'] = now.date().isoformat()
    if not a.get('schemas'):
        print(f"⚠ #{a['num']} publié sans schéma")
json.dump(arts, open(blog_fr.QUEUE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
import blog_build
blog_build.build()
for a in dus: print(f"✓ publié : #{a['num']} — « {a['seo_title']} » → /fr/blog/{a['slug']}.html" + (f" + /en/blog/{a['en']['slug']}.html" if a.get('en') else ''))
