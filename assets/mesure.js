/* Mesure d'audience Google Analytics 4 avec consentement (Consent Mode v2) — bandeau, choix gardé 13 mois,
   lien « Cookies » ajouté au pied de page, événements tel / e-mail / magasins d'applications (liens directs et liens
   internes /app-store/, /google-play/, /app/). Aucune dépendance.
   Réglages sur la balise <script> : data-ads="1" (consentement publicitaire aussi), data-politique (lien « En savoir plus »),
   data-fond, data-texte, data-accent, data-accent-texte (couleurs du site). */
(function () {
  var s = document.currentScript || {getAttribute: function () { return null; }};
  var A = function (k, d) { return s.getAttribute('data-' + k) || d; };
  /* 14-11 : data-ga (identifiant GA4), data-type (type de page), data-cf (jeton Cloudflare Web Analytics : sans cookie, tous
     les visiteurs, chargé sans bandeau), data-clarity (projet Microsoft Clarity : chargé SEULEMENT après « Accepter »). */
  var GA_ID = A('ga', ''), TYPE = A('type', ''), CF = A('cf', ''), CLARITY = A('clarity', '');
  var ADS = A('ads', '0') === '1', DUREE = 395 * 864e5;
  /* Avec Clarity, le choix est redemandé une fois à ceux qui avaient accepté Google Analytics seul ; un refus déjà donné reste valable. */
  var KEY = CLARITY ? 'consent_mesure_v2' : 'consent_mesure_v1', ANCIEN = 'consent_mesure_v1';
  var lang = (document.documentElement.lang || 'fr').slice(0, 2).toLowerCase();
  var TXT = {
    fr: {t: 'Mesure d’audience', p: ADS ? 'Avec ton accord, nous utilisons Google Analytics et Google Ads pour savoir quelles pages t’intéressent et mesurer l’efficacité de nos campagnes. Aucune revente de données.' : CLARITY ? 'Avec ton accord, nous utilisons Google Analytics pour savoir quelles pages sont lues, et Microsoft Clarity pour voir où l’on clique et jusqu’où l’on lit (ce que tu écris reste masqué). Le but : améliorer le site. Aucune publicité, aucune revente de données.' : 'Avec ton accord, nous utilisons Google Analytics pour savoir quelles pages sont lues et améliorer le site. Aucune publicité, aucune revente de données.',
         d: 'Ton choix est gardé 13 mois et modifiable à tout moment via « Cookies » en bas de page.', plus: 'En savoir plus sur les cookies', non: 'Refuser', oui: 'Accepter', lien: 'Cookies',
         moi: 'Tes visites ne sont plus comptées sur cet appareil.', toi: 'Tes visites sont de nouveau comptées sur cet appareil.'},
    en: {t: 'Audience measurement', p: ADS ? 'With your consent, we use Google Analytics and Google Ads to learn which pages interest you and measure our campaigns. Your data is never sold.' : CLARITY ? 'With your consent, we use Google Analytics to learn which pages are read, and Microsoft Clarity to see where people click and how far they read (anything you type stays hidden). The goal: a better site. No ads, your data is never sold.' : 'With your consent, we use Google Analytics to learn which pages are read and improve the site. No ads, your data is never sold.',
         d: 'Your choice is kept for 13 months and can be changed anytime via “Cookies” at the bottom of the page.', plus: 'Learn more about cookies', non: 'Decline', oui: 'Accept', lien: 'Cookies',
         moi: 'Your visits are no longer counted on this device.', toi: 'Your visits are counted again on this device.'},
    es: {t: 'Medición de audiencia', p: ADS ? 'Con tu permiso, usamos Google Analytics y Google Ads para saber qué páginas te interesan y medir nuestras campañas. Nunca vendemos tus datos.' : CLARITY ? 'Con tu permiso, usamos Google Analytics para saber qué páginas se leen, y Microsoft Clarity para ver dónde se hace clic y hasta dónde se lee (lo que escribes queda oculto). El objetivo: mejorar el sitio. Sin publicidad, nunca vendemos tus datos.' : 'Con tu permiso, usamos Google Analytics para saber qué páginas se leen y mejorar el sitio. Sin publicidad, nunca vendemos tus datos.',
         d: 'Tu elección se guarda 13 meses y puedes cambiarla cuando quieras en «Cookies», al pie de la página.', plus: 'Saber más sobre las cookies', non: 'Rechazar', oui: 'Aceptar', lien: 'Cookies',
         moi: 'Tus visitas ya no se cuentan en este dispositivo.', toi: 'Tus visitas vuelven a contarse en este dispositivo.'}
  };
  var T = TXT[lang] || TXT.en;
  /* Visites d'Edouard : ouvrir une page du site avec #ne-pas-compter les exclut sur cet appareil (Google Analytics,
     Cloudflare, Clarity), même si son adresse IP change ; #compter annule. */
  var MOI = false, BASCULE = '';
  try {
    if (location.hash === '#ne-pas-compter') { localStorage.setItem('md_ne_pas_compter', '1'); BASCULE = T.moi; }
    else if (location.hash === '#compter') { localStorage.removeItem('md_ne_pas_compter'); BASCULE = T.toi; }
    MOI = localStorage.getItem('md_ne_pas_compter') === '1';
  } catch (e) {}
  if (MOI && GA_ID) window['ga-disable-' + GA_ID] = true;
  function g() { if (window.gtag) window.gtag.apply(null, arguments); }
  function cl() { if (window.clarity) window.clarity.apply(null, arguments); }
  /* Un événement part vers Google Analytics et, si le visiteur a accepté, vers Clarity (filtre des enregistrements). */
  function ev(nom, params) { g('event', nom, params); cl('event', nom); }
  function lire() {
    try { var c = JSON.parse(localStorage.getItem(KEY)); if (c && Date.now() - c.t < DUREE) return c.v; } catch (e) {}
    try { var o = JSON.parse(localStorage.getItem(ANCIEN)); if (KEY !== ANCIEN && o && o.v === 'non' && Date.now() - o.t < DUREE) return 'non'; } catch (e) {}
    return null;
  }
  function clarityCharger() {
    if (!CLARITY || MOI || window.clarity) return;
    (function (c, l, a, r, i, t, y) { c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); };
      t = l.createElement(r); t.async = 1; t.src = 'https://www.clarity.ms/tag/' + i;
      y = l.getElementsByTagName(r)[0]; y.parentNode.insertBefore(t, y); })(window, document, 'clarity', 'script', CLARITY);
    cl('consentv2', {ad_Storage: 'denied', analytics_Storage: 'granted'});
    cl('set', 'langue', lang); if (TYPE) cl('set', 'type_page', TYPE);
  }
  function cfCharger() {
    if (!CF || MOI || document.querySelector('script[data-cf-beacon]')) return;
    var t = document.createElement('script'); t.type = 'module'; t.src = 'https://static.cloudflareinsights.com/beacon.min.js';
    t.setAttribute('data-cf-beacon', JSON.stringify({token: CF})); document.head.appendChild(t);
  }
  function effacerCookies() {
    document.cookie.split(';').forEach(function (c) {
      var n = c.split('=')[0].trim(); if (!/^(_ga|_gid|_gat|_gcl|_clck|_clsk)/.test(n)) return;
      var h = location.hostname.split('.'), dom = h.slice(-2).join('.');
      ['', '; domain=' + location.hostname, '; domain=.' + dom].forEach(function (d) { document.cookie = n + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/' + d; });
    });
  }
  var box = null;
  function fermer() { if (box) { box.remove(); box = null; } }
  function choisir(v) {
    try { localStorage.setItem(KEY, JSON.stringify({v: v, t: Date.now()})); } catch (e) {}
    var on = v === 'oui' ? 'granted' : 'denied', u = {analytics_storage: on};
    if (ADS) { u.ad_storage = on; u.ad_user_data = on; u.ad_personalization = on; }
    g('consent', 'update', u);
    if (v === 'oui') clarityCharger();
    else { cl('consentv2', {ad_Storage: 'denied', analytics_Storage: 'denied'}); effacerCookies(); }
    fermer();
  }
  function ouvrir() {
    if (box) return;
    var fond = A('fond', '#1d1d1f'), texte = A('texte', '#ffffff'), acc = A('accent', '#ffe047'), acct = A('accent-texte', '#111111');
    box = document.createElement('div');
    box.setAttribute('role', 'dialog'); box.setAttribute('aria-label', T.t);
    box.style.cssText = 'position:fixed;left:16px;right:16px;bottom:16px;z-index:2147483000;max-width:560px;margin:0 auto;padding:18px 20px;border-radius:14px;' +
      'background:' + fond + ';color:' + texte + ';box-shadow:0 10px 40px rgba(0,0,0,.35);font:14px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;text-align:left';
    var b = 'flex:1 1 0;min-width:120px;padding:11px 16px;border-radius:10px;font:600 15px system-ui,sans-serif;cursor:pointer;border:2px solid ' + acc + ';background:' + acc + ';color:' + acct;
    var pol = A('politique', '');
    box.innerHTML = '<p style="margin:0 0 6px;font-weight:700;font-size:15px">' + T.t + '</p><p style="margin:0 0 6px">' + T.p + '</p>' +
      '<p style="margin:0 0 14px;opacity:.8;font-size:13px">' + T.d + (pol ? ' <a href="' + pol + '" style="color:inherit;text-decoration:underline">' + T.plus + '</a>' : '') + '</p>' +
      '<div style="display:flex;gap:10px;flex-wrap:wrap"><button type="button" data-v="non" style="' + b + '">' + T.non + '</button><button type="button" data-v="oui" style="' + b + '">' + T.oui + '</button></div>';
    box.addEventListener('click', function (e) { var v = e.target.getAttribute && e.target.getAttribute('data-v'); if (v) choisir(v); });
    document.body.appendChild(box);
  }
  window.gererCookies = ouvrir;
  function lienPied() {
    var f = document.querySelector('footer'); if (!f || f.querySelector('[data-consent]')) return;
    var a = document.createElement('a'); a.href = '#'; a.setAttribute('data-consent', ''); a.textContent = T.lien;
    a.style.cssText = 'display:inline-block;margin:8px 0;color:inherit;opacity:.92;font-size:13px';
    var p = document.createElement('p'); p.style.cssText = 'margin:0;text-align:center'; p.appendChild(a);
    f.appendChild(p);
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a,[data-consent]'); if (!a) return;
    if (a.hasAttribute('data-consent')) { e.preventDefault(); ouvrir(); return; }
    var h = a.getAttribute('href') || '';
    var store = null;
    if (/^tel:/i.test(h)) ev('contact_tel', {link_url: h});
    else if (/^mailto:/i.test(h)) ev('contact_email', {link_url: h.split('?')[0]});
    else if (/(apps|itunes)\.apple\.com/.test(h)) store = 'app_store';
    else if (/play\.google\.com/.test(h)) store = 'google_play';
    else {
      var m = h.match(/^(?:https?:\/\/(?:www\.)?meditadream\.com)?\/(app-store|google-play|app)\/?(?:[?#].*)?$/i);
      if (m) store = {'app-store': 'app_store', 'google-play': 'google_play', app: 'auto'}[m[1].toLowerCase()];
      if (store === 'auto') {   // 26-11 : /app envoie l'iPhone/iPad vers l'App Store et Android vers Google Play (même test que la page /app,
        var ua = navigator.userAgent || '';   // qui ne recompte plus le clic venu du site) ; ordinateur = 'auto' (page aux deux boutons)
        if (/iPhone|iPad|iPod/.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1)) store = 'app_store';
        else if (/Android/.test(ua)) store = 'google_play';
      }
    }
    var txt = (a.textContent || '').trim();
    if (/^(FR|EN|ES)$/.test(txt) && !a.classList.contains('on') && a.closest('header,nav,.langs,.lang,.lg')) {
      ev('lang_switch', {langue_choisie: txt.toLowerCase(), link_url: h});   // 26-11 : changement de langue
    } else if (/\bap-prat-p\b/.test(a.className || '')) {
      ev('clic_programme', {link_url: h});   // 26-11 : « Voir les séances » / programme depuis l'encadré d'un article
    }
    if (store) {
      var e2 = emplacement(a);
      ev('store_click', {store: store, link_url: h, emplacement: e2});
      cl('set', 'magasin', store); cl('set', 'emplacement', e2); cl('upgrade', 'store_click');
    }
  }, true);
  /* 14-11 (demande d'Edouard : tout le comportement des visiteurs) — quel bouton de téléchargement, profondeur de lecture,
     vidéo de présentation, questions de la FAQ ouvertes. Noms d'événements de Google (scroll, video_*) pour ses dimensions. */
  function emplacement(a) {
    if (a.closest('footer')) return 'pied_de_page';
    if (a.closest('aside.mdb')) return 'bandeau_haut';
    if (a.closest('#download')) return 'section_telecharger';
    if (a.closest('.cta')) return 'encadre_pratiquer';
    if (a.closest('.ap-prat') || /\bap-prat-/.test(a.className || '')) return 'encadre_haut_article';
    if (a.closest('header,.hero')) return 'haut_de_page';
    if (a.closest('article,main,section')) return 'contenu';
    return 'autre';
  }
  /* 26-11 (Edouard : statistiques utiles en plus du clic) — view_download : un bouton App Store / Google Play est apparu
     à l'écran (moitié visible), une fois par emplacement et par page ; store_click ÷ view_download = taux de clic. */
  /* 27-11 — extraits audio des méditations : extrait_audio quand un visiteur lance un extrait (une fois par extrait et par page),
     extrait_audio_fin quand il l'écoute jusqu'au bout. */
  var ecoutes = {};
  document.addEventListener('play', function (e) {
    var a = e.target; if (!a || a.tagName !== 'AUDIO' || !a.getAttribute('data-extrait')) return;
    var id = a.getAttribute('data-extrait'); if (ecoutes[id]) return; ecoutes[id] = 1; ev('extrait_audio', {extrait: id});
  }, true);
  document.addEventListener('ended', function (e) {
    var a = e.target; if (a && a.tagName === 'AUDIO' && a.getAttribute('data-extrait')) ev('extrait_audio_fin', {extrait: a.getAttribute('data-extrait')});
  }, true);
  function boutonsVus() {
    if (!('IntersectionObserver' in window)) return;
    var vus = {}, rx = /(apps|itunes)\.apple\.com|play\.google\.com|^(?:https?:\/\/(?:www\.)?meditadream\.com)?\/(app-store|google-play|app)\/?(?:[?#].*)?$/i;
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (en) {
        if (!en.isIntersecting) return;
        var e3 = emplacement(en.target); io.unobserve(en.target);
        if (vus[e3]) return; vus[e3] = 1; g('event', 'view_download', {emplacement: e3});
      });
    }, {threshold: 0.5});
    [].forEach.call(document.querySelectorAll('a[href]'), function (a) { if (rx.test(a.getAttribute('href') || '')) io.observe(a); });
  }
  var paliers = {};
  function defil() {
    var d = document.documentElement, haut = d.scrollHeight - window.innerHeight;
    if (haut < 300) return;
    var p = (window.pageYOffset || d.scrollTop) / haut * 100;
    [25, 50, 75].forEach(function (x) { if (p >= x && !paliers[x]) { paliers[x] = 1; g('event', 'scroll', {percent_scrolled: x}); } });
  }
  window.addEventListener('scroll', defil, {passive: true});
  function videos() {
    [].forEach.call(document.querySelectorAll('video'), function (v) {
      if (v.getAttribute('data-mesure')) return; v.setAttribute('data-mesure', '1');
      var sec = v.closest('section'), h2 = sec && sec.querySelector('h2'), fait = {};
      var titre = v.getAttribute('title') || (h2 && h2.textContent.trim()) || v.id || 'video';
      var p = function (x) { var o = {video_title: titre, video_provider: 'meditadream', video_url: v.currentSrc || ''}; if (x) o.video_percent = x; return o; };
      v.addEventListener('play', function () { if (!fait.debut) { fait.debut = 1; ev('video_start', p()); } });
      v.addEventListener('timeupdate', function () {
        if (!v.duration) return; var q = v.currentTime / v.duration * 100;
        [10, 25, 50, 75].forEach(function (x) { if (q >= x && !fait[x]) { fait[x] = 1; g('event', 'video_progress', p(x)); } });
      });
      v.addEventListener('ended', function () { if (!fait.fin) { fait.fin = 1; ev('video_complete', p(100)); } });
    });
  }
  document.addEventListener('toggle', function (e) {
    var d = e.target; if (!d || d.tagName !== 'DETAILS' || !d.open || d.className) return;
    var s = d.querySelector('summary'); if (s) ev('faq_open', {question: s.textContent.trim().slice(0, 100)});
  }, true);
  function avis(txt) {
    var d = document.createElement('div'); d.setAttribute('role', 'status'); d.textContent = txt;
    d.style.cssText = 'position:fixed;left:16px;right:16px;top:16px;z-index:2147483001;max-width:480px;margin:0 auto;padding:12px 16px;border-radius:12px;' +
      'background:' + A('fond', '#1d1d1f') + ';color:' + A('texte', '#ffffff') + ';border:1px solid ' + A('accent', '#ffe047') + ';font:600 14px/1.4 system-ui,sans-serif;text-align:center';
    document.body.appendChild(d); setTimeout(function () { d.remove(); }, 5000);
  }
  function init() {
    boutonsVus();
    lienPied(); videos();
    if (BASCULE) avis(BASCULE);
    var c = lire();
    if (c === 'oui') clarityCharger(); else if (!c) ouvrir();
    if (document.readyState === 'complete') cfCharger(); else window.addEventListener('load', cfCharger);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
