#!/usr/bin/env python3
"""Balise Google Analytics 4 (G-CFLRM9XKV2) avec consentement, injectée dans toutes les pages HTML du site.
Idempotent : le bloc entre <!--mesure:debut--> et <!--mesure:fin--> est remplacé à chaque passage.
Appelé après chaque générateur (build_site.py, publications du blog dans les actions GitHub).
Usage : python3 _tools/mesure.py            (toutes les pages)
        python3 _tools/mesure.py --verifier (liste les pages sans balise, code de sortie 1 s'il en manque)"""
import hashlib, os, re, sys
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GA = 'G-CFLRM9XKV2'
JS = os.path.join(RACINE, 'assets', 'mesure.js')
BLOC = re.compile(r'\n?<!--mesure:debut-->.*?<!--mesure:fin-->', re.S)
POLITIQUE = {'fr': '/fr/privacy.html#site-web', 'en': '/en/privacy.html#website', 'es': '/es/privacy.html#sitio-web'}

def type_page(rel):
    p = rel.replace(os.sep, '/')
    if p in ('index.html', '404.html'): return 'accueil_langues' if p == 'index.html' else 'erreur_404'
    if '/blog/' in p: return 'blog_index' if p.endswith('/blog/index.html') else ('blog_theme' if '/theme' in p or '/themes/' in p else 'blog_article')
    if '/formation-meditation/' in p: return 'formation'
    if '/meditations/' in p or '/meditaciones/' in p: return 'categorie_meditation'
    if re.search(r'(entreprise|empresas|teams)\.html$', p): return 'entreprise'
    if '/mondes/' in p or '/worlds/' in p or '/mundos/' in p: return 'monde'
    if re.search(r'(privacy|terms|support)\.html$', p): return 'legal'
    if re.match(r'^(fr|en|es)/index\.html$', p): return 'accueil'
    return 'page'

def bloc(rel, html):
    m = re.search(r'<html[^>]*\blang="([a-z]{2})', html)
    lang = m.group(1) if m else 'en'
    v = hashlib.md5(open(JS, 'rb').read()).hexdigest()[:8]
    return ('\n<!--mesure:debut--><script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}'
            "gtag('consent','default',{analytics_storage:'denied',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied',wait_for_update:500});"
            "try{var c=JSON.parse(localStorage.getItem('consent_mesure_v1'));if(c&&c.v==='oui'&&Date.now()-c.t<395*864e5)gtag('consent','update',{analytics_storage:'granted'})}catch(e){}"
            "gtag('js',new Date());gtag('config','%s',{content_language:'%s',page_type:'%s',content_group:'%s'})</script>"
            '<script async src="https://www.googletagmanager.com/gtag/js?id=%s"></script>'
            '<script src="/assets/mesure.js?v=%s" defer data-politique="%s" data-fond="#14142a" data-texte="#F5E6C8" data-accent="#D4AF6A" data-accent-texte="#0A0A14"></script>'
            '<!--mesure:fin-->') % (GA, lang, type_page(rel), type_page(rel), GA, v, POLITIQUE.get(lang, POLITIQUE['en']))

def pages():
    for d, sous, fich in os.walk(RACINE):
        sous[:] = [s for s in sous if not s.startswith(('.', '_')) and s != 'node_modules']
        for f in fich:
            if f.endswith('.html'): yield os.path.relpath(os.path.join(d, f), RACINE)

def main(verif=None):
    if verif is None: verif = '--verifier' in sys.argv
    manque, modifiees = [], 0
    for rel in pages():
        chemin = os.path.join(RACINE, rel)
        html = open(chemin, encoding='utf-8').read()
        if 'http-equiv="refresh"' in html and '<!--mesure:debut-->' not in html: continue  # pages de redirection : rien à mesurer
        if '</head>' not in html: continue
        if verif:
            if '<!--mesure:debut-->' not in html: manque.append(rel)
            continue
        neuf = BLOC.sub('', html).replace('</head>', bloc(rel, html) + '</head>', 1)
        if neuf != html:
            open(chemin, 'w', encoding='utf-8').write(neuf); modifiees += 1
    if verif:
        print('\n'.join(manque) or 'toutes les pages ont la balise'); sys.exit(1 if manque else 0)
    print('mesure : %d page(s) mises à jour' % modifiees)

if __name__ == '__main__':
    main()
