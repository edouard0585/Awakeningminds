"""06-11 — vitesse (Core Web Vitals) : police de secours calée sur Cormorant Garamond pour supprimer le décalage (CLS)
quand la police du site arrive après le premier affichage (mesuré le 06-11 : CLS 0,125 sur les articles, cause = la police).
Mesures faites dans le navigateur (largeur d'une même phrase à 100 px) : Cormorant 500 = 88,4 % de Georgia, Cormorant 600 =
76 % de Georgia Bold, Cormorant italique 500 = 78,5 % de Georgia Italic ; hauteurs de Cormorant : 0,924 au-dessus,
0,287 en dessous (les « override » sont divisés par size-adjust, comme le font fontaine et next/font).
Appelé par seo_medias.py (passe finale de chaque construction). Idempotent (balises <!--vitesse-->)."""
import re

POLICE = ('<!--vitesse--><style>'
          "@font-face{font-family:'Cormorant Fallback';font-style:normal;font-weight:100 500;src:local('Georgia');"
          'size-adjust:88.4%;ascent-override:104.5%;descent-override:32.5%;line-gap-override:0%}'
          "@font-face{font-family:'Cormorant Fallback';font-style:normal;font-weight:501 900;src:local('Georgia Bold'),local('Georgia-Bold');"
          'size-adjust:76%;ascent-override:121.6%;descent-override:37.8%;line-gap-override:0%}'
          "@font-face{font-family:'Cormorant Fallback';font-style:italic;font-weight:100 900;src:local('Georgia Italic'),local('Georgia-Italic');"
          'size-adjust:78.5%;ascent-override:117.7%;descent-override:36.6%;line-gap-override:0%}'
          '</style><!--/vitesse-->')
BLOC = re.compile(r'<!--vitesse-->.*?<!--/vitesse-->', re.S)
PILE = re.compile(r"""(['"])Cormorant Garamond\1,(?!\1?Cormorant Fallback)""")


def ajoute(s, l=None, r=None):
    s = BLOC.sub('', s)
    if 'Cormorant Garamond' not in s or '</head>' not in s:
        return s
    s = PILE.sub(lambda m: f"{m.group(1)}Cormorant Garamond{m.group(1)},{m.group(1)}Cormorant Fallback{m.group(1)},", s)
    return s.replace('</head>', POLICE + '</head>', 1)
