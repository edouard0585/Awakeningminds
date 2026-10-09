/* Mesure d'audience Google Analytics 4 avec consentement (Consent Mode v2) — bandeau, choix gardé 13 mois,
   lien « Cookies » ajouté au pied de page, événements tel / e-mail / magasins d'applications. Aucune dépendance.
   Réglages sur la balise <script> : data-ads="1" (consentement publicitaire aussi), data-politique (lien « En savoir plus »),
   data-fond, data-texte, data-accent, data-accent-texte (couleurs du site). */
(function () {
  var s = document.currentScript || {getAttribute: function () { return null; }};
  var A = function (k, d) { return s.getAttribute('data-' + k) || d; };
  var ADS = A('ads', '0') === '1', KEY = 'consent_mesure_v1', DUREE = 395 * 864e5;
  var lang = (document.documentElement.lang || 'fr').slice(0, 2).toLowerCase();
  var TXT = {
    fr: {t: 'Mesure d’audience', p: ADS ? 'Avec ton accord, nous utilisons Google Analytics et Google Ads pour savoir quelles pages t’intéressent et mesurer l’efficacité de nos campagnes. Aucune revente de données.' : 'Avec ton accord, nous utilisons Google Analytics pour savoir quelles pages sont lues et améliorer le site. Aucune publicité, aucune revente de données.',
         d: 'Ton choix est gardé 13 mois et modifiable à tout moment via « Cookies » en bas de page.', plus: 'En savoir plus sur les cookies', non: 'Refuser', oui: 'Accepter', lien: 'Cookies'},
    en: {t: 'Audience measurement', p: ADS ? 'With your consent, we use Google Analytics and Google Ads to learn which pages interest you and measure our campaigns. Your data is never sold.' : 'With your consent, we use Google Analytics to learn which pages are read and improve the site. No ads, your data is never sold.',
         d: 'Your choice is kept for 13 months and can be changed anytime via “Cookies” at the bottom of the page.', plus: 'Learn more about cookies', non: 'Decline', oui: 'Accept', lien: 'Cookies'},
    es: {t: 'Medición de audiencia', p: ADS ? 'Con tu permiso, usamos Google Analytics y Google Ads para saber qué páginas te interesan y medir nuestras campañas. Nunca vendemos tus datos.' : 'Con tu permiso, usamos Google Analytics para saber qué páginas se leen y mejorar el sitio. Sin publicidad, nunca vendemos tus datos.',
         d: 'Tu elección se guarda 13 meses y puedes cambiarla cuando quieras en «Cookies», al pie de la página.', plus: 'Saber más sobre las cookies', non: 'Rechazar', oui: 'Aceptar', lien: 'Cookies'}
  };
  var T = TXT[lang] || TXT.en;
  function g() { if (window.gtag) window.gtag.apply(null, arguments); }
  function lire() { try { var c = JSON.parse(localStorage.getItem(KEY)); if (c && Date.now() - c.t < DUREE) return c.v; } catch (e) {} return null; }
  function effacerCookies() {
    document.cookie.split(';').forEach(function (c) {
      var n = c.split('=')[0].trim(); if (!/^(_ga|_gid|_gat|_gcl)/.test(n)) return;
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
    if (v !== 'oui') effacerCookies();
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
    a.style.cssText = 'display:inline-block;margin:8px 0;color:inherit;opacity:.75;font-size:13px';
    var p = document.createElement('p'); p.style.cssText = 'margin:0;text-align:center'; p.appendChild(a);
    f.appendChild(p);
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a,[data-consent]'); if (!a) return;
    if (a.hasAttribute('data-consent')) { e.preventDefault(); ouvrir(); return; }
    var h = a.getAttribute('href') || '';
    if (/^tel:/i.test(h)) g('event', 'contact_tel', {link_url: h});
    else if (/^mailto:/i.test(h)) g('event', 'contact_email', {link_url: h.split('?')[0]});
    else if (/(apps|itunes)\.apple\.com/.test(h)) g('event', 'store_click', {store: 'app_store', link_url: h});
    else if (/play\.google\.com/.test(h)) g('event', 'store_click', {store: 'google_play', link_url: h});
  }, true);
  function init() { lienPied(); if (!lire()) ouvrir(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
