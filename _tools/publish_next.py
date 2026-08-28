#!/usr/bin/env python3
"""Publie le prochain article de la file (appelé chaque lundi par GitHub Actions)."""
import json, os, sys
from datetime import date, timezone, timedelta
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = f'{ROOT}/_queue/articles.json'
arts = json.load(open(P, encoding='utf-8'))
nxt = next((a for a in arts if not a.get('published')), None)
if not nxt:
    print('File vide : tous les articles sont publiés.')
    sys.exit(0)
# date de Paris (UTC+1/+2 ; le cron tourne le matin, UTC+2 suffit à viser le bon jour)
nxt['published'] = (date.today() if os.environ.get('CI') is None
                    else __import__('datetime').datetime.now(timezone(timedelta(hours=2))).date()).isoformat()
json.dump(arts, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blog_build
blog_build.build()
print(f"✓ publié : {nxt['id']} — « {nxt['title']['fr']} » ({nxt['published']})")
