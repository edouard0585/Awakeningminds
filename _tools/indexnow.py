#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Signale aux moteurs IndexNow (Bing, Yandex, Seznam, Naver…) les pages nouvelles ou modifiées.

   python3 _tools/indexnow.py                 → pages dont le lastmod des sitemaps est aujourd'hui
   python3 _tools/indexnow.py --depuis 2026-09-01
   python3 _tools/indexnow.py --tout          → toutes les pages des sitemaps
   … --liste                                   → affiche sans envoyer
La clé est le fichier <clé>.txt à la racine du site (vérifiée par les moteurs). Stdlib seulement.
"""
import glob, json, os, re, sys, urllib.request
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = 'awakeningminds.app'
BASE = f'https://{HOST}'
ENDPOINTS = ['https://api.indexnow.org/indexnow', 'https://www.bing.com/indexnow', 'https://yandex.com/indexnow']


def cle():
    for f in glob.glob(os.path.join(ROOT, '*.txt')):
        n = os.path.basename(f)[:-4]
        if re.fullmatch(r'[0-9a-f]{32}', n) and open(f).read().strip() == n: return n
    sys.exit('clé IndexNow introuvable')


def urls(depuis=None):
    out = []
    for sm in ('sitemap.xml', 'sitemap-blog.xml'):
        x = open(os.path.join(ROOT, sm), encoding='utf-8').read()
        for m in re.finditer(r'<url>(.*?)</url>', x, re.S):
            loc = re.search(r'<loc>(.*?)</loc>', m.group(1)).group(1)
            lm = re.search(r'<lastmod>(.*?)</lastmod>', m.group(1))
            if depuis is None or (lm and lm.group(1) >= depuis): out.append(loc)
    return out


if __name__ == '__main__':
    a = sys.argv[1:]
    depuis = None if '--tout' in a else (a[a.index('--depuis') + 1] if '--depuis' in a else date.today().isoformat())
    liste = urls(depuis)
    if not liste: print('IndexNow : rien de nouveau'); sys.exit(0)
    k = cle()
    if '--liste' in a:
        print(f'{len(liste)} URL (clé {k[:6]}…) :'); print('\n'.join(liste)); sys.exit(0)
    corps = json.dumps({'host': HOST, 'key': k, 'keyLocation': f'{BASE}/{k}.txt', 'urlList': liste}).encode()
    for ep in ENDPOINTS:
        try:
            r = urllib.request.urlopen(urllib.request.Request(ep, data=corps, headers={'Content-Type': 'application/json; charset=utf-8'}), timeout=30)
            print(f'IndexNow {ep} → {r.status} ({len(liste)} URL)')
        except urllib.error.HTTPError as e:
            print(f'IndexNow {ep} → {e.code} {e.read()[:200]!r}')
        except Exception as e:
            print(f'IndexNow {ep} → erreur {e}')
