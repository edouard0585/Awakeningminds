/* Exercice de respiration guidé de meditadream.com (27-11-2026). Aucune dépendance, aucun fichier audio.
   La page fournit le balisage (#outil) et les réglages (#resp-donnees, JSON : techniques, ordre, libellés), tous deux
   écrits par _tools/outils.py. Ce script s'occupe du minutage, du cercle, du son et de l'accessibilité.

   Minutage : tout se déduit de l'horloge (heure courante − heure de départ). Aucun compteur de tics : un onglet passé à
     l'arrière-plan, un téléphone verrouillé ou une page ralentie retrouvent la bonne phase et le bon temps restant.
     L'horloge suivie est l'horloge monotone du navigateur (performance.now) : un réglage de l'heure du système pendant
     l'exercice ne le décale pas. Comme elle s'arrête quand l'appareil dort, l'heure du système sert à rattraper la veille.
   Cercle : il grandit à l'inspiration, reste pendant la rétention, rétrécit à l'expiration (requestAnimationFrame).
     Avec « mouvement réduit » (prefers-reduced-motion), il ne change plus de taille : restent le mot, le décompte et
     une barre qui avance par paliers d'une seconde.
   Son (facultatif, coupé au départ) : une note très douce à chaque changement de phase, fabriquée par WebAudio et
     programmée sur l'horloge audio. Plus aiguë pour inspirer, plus grave pour expirer.
   Écran : gardé allumé pendant l'exercice quand navigator.wakeLock existe (sinon rien, sans erreur).
   Mesure : gtag('event', 'outil_respiration', {technique, etape: 'debut' | 'fin', duree}) au départ et à la fin. Rien d'autre.
   Mémoire : la dernière technique choisie (localStorage, clé md_resp_technique). Ni cookie ni autre stockage. */
(function () {
  'use strict';
  var racine = document.getElementById('outil'), brut = document.getElementById('resp-donnees');
  if (!racine || !brut) return;
  var C;
  try { C = JSON.parse(brut.textContent); } catch (e) { return; }
  var TECH = C.techniques, T = C.t;
  var q = function (s) { return racine.querySelector(s); };
  var el = {
    tech: q('.resp-tech'), duree: q('.resp-duree'), rythme: q('.resp-rythme'), scene: q('.resp-scene'), disque: q('.resp-disque'),
    mot: q('.resp-mot'), compte: q('.resp-compte'), phase: q('.resp-phase i'), restant: q('.resp-restant'), cycle: q('.resp-cycle'),
    total: q('.resp-total i'), go: q('.resp-go'), re: q('.resp-re'), son: q('.resp-son'), fin: q('.resp-fin'), dire: q('.resp-dire')
  };
  for (var k0 in el) { if (!el[k0]) return; }

  var CLE = 'md_resp_technique';
  var PETIT = 0.56, GRAND = 1;                 // taille du cercle, poumons vides et poumons pleins
  var NOTES = {inspire: 440, retiens: 554.37, expire: 329.63, pause: 277.18};   // la, do dièse, mi, do dièse grave
  var tech = C.ordre[0], choix = TECH[tech].defaut;
  var etat = 'repos';                          // repos | cours | pause | fin
  var acquis = 0;                              // temps écoulé (ms), gardé pendant une pause
  var base = 0, mono0 = 0, mur0 = 0, sommeil = 0;  // écoulé avant ce départ ; départ sur chaque horloge ; sommeil de l'appareil rattrapé
  var SOMMEIL = 2000;                          // écart entre les deux horloges (ms) qui signe une mise en veille de l'appareil
  var phases = [], cycleMs = 0, totalMs = 0, nCycles = 0;
  var vu = {};                                 // dernier texte écrit, pour ne toucher à la page que quand il change
  var image = 0, reveil = 0;                   // requestAnimationFrame et minuterie de secours en attente
  var son = false, audio = null, sortie = null, notes = [], sonPrevu = -1;
  var verrou = null, verrouDemande = false;
  var mq = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : null;
  var calme = function () { return !!(mq && mq.matches); };

  /* ---------- le rythme ---------- */
  function preparer() {
    var t = TECH[tech], niveau = 0, debut = 0;
    phases = t.phases.map(function (p) {
      var de = niveau;
      if (p[0] === 'inspire') niveau = 1; else if (p[0] === 'expire') niveau = 0;
      var x = {nom: p[0], ms: p[1] * 1000, debut: debut, de: de, a: niveau};
      debut += x.ms;
      return x;
    });
    cycleMs = debut;
    nCycles = t.choix[choix].c;
    totalMs = cycleMs * nCycles;
  }
  /* Temps écoulé depuis le départ, pauses déduites. Deux horloges :
     - l'horloge monotone (performance.now) donne le rythme : elle avance toujours à la même allure, même si l'heure du
       système est réglée pendant l'exercice (synchronisation automatique, changement à la main) ;
     - l'heure du système (Date.now) sert de témoin : sur un téléphone verrouillé ou un ordinateur en veille, l'horloge
       monotone s'arrête alors que l'heure continue. Plus de 2 s d'écart entre les deux = l'appareil a dormi : l'écart est
       rattrapé, l'exercice a continué pendant ce temps (comme pour un onglet resté à l'arrière-plan). */
  function tic() { return window.performance && performance.now ? performance.now() : Date.now(); }
  function caler() { base = acquis; mono0 = tic(); mur0 = Date.now(); sommeil = 0; }
  function ecoule() {
    if (etat !== 'cours') return acquis;
    var m = tic() - mono0, mur = Date.now() - mur0;
    if (mur - (m + sommeil) > SOMMEIL) sommeil = mur - m;
    var e = base + m + sommeil;
    if (e > acquis) acquis = e;
    return acquis;
  }
  function position(e) {
    if (e > totalMs - 1) e = totalMs - 1;
    if (e < 0) e = 0;
    var c = Math.floor(e / cycleMs), dans = e - c * cycleMs, i = 0;
    while (i < phases.length - 1 && dans >= phases[i].debut + phases[i].ms) i++;
    return {c: c, i: i, dans: dans - phases[i].debut};
  }
  function horloge(ms) {
    var s = Math.max(0, Math.ceil(ms / 1000)), r = s % 60;
    return Math.floor(s / 60) + ':' + (r < 10 ? '0' : '') + r;
  }
  function doux(f) { return 0.5 - 0.5 * Math.cos(Math.PI * Math.min(1, Math.max(0, f))); }

  /* ---------- l'affichage ---------- */
  function ecrire(cle, noeud, texte) { if (vu[cle] !== texte) { vu[cle] = texte; noeud.textContent = texte; } }
  function style(cle, noeud, prop, valeur) { if (vu[cle] !== valeur) { vu[cle] = valeur; noeud.style[prop] = valeur; } }
  function dire(texte) { ecrire('dire', el.dire, texte); }
  function afficher() {
    var e = ecoule();
    if (etat === 'cours' && e >= totalMs) { finir(); return; }
    var p = position(e), ph = phases[p.i], sec = Math.ceil((ph.ms - p.dans) / 1000);
    var actif = etat === 'cours' || etat === 'pause';
    // le cercle
    if (calme()) style('taille', el.disque, 'transform', '');
    else style('taille', el.disque, 'transform', 'scale(' + (actif ? PETIT + (GRAND - PETIT) * (ph.de + (ph.a - ph.de) * doux(p.dans / ph.ms)) : PETIT).toFixed(4) + ')');
    // le mot et le décompte
    if (etat === 'cours') {
      ecrire('mot', el.mot, T.phases[ph.nom]);
      dire(T.phases[ph.nom]);
    } else if (etat === 'pause') ecrire('mot', el.mot, T.en_pause);
    else ecrire('mot', el.mot, etat === 'fin' ? '✦' : T.pret);
    ecrire('compte', el.compte, actif ? String(sec) : '');
    // barre de la phase (mouvement réduit) : un palier par seconde
    style('phase', el.phase, 'width', actif ? Math.round(100 * Math.min(1, (Math.floor(p.dans / 1000) + 1) / (ph.ms / 1000))) + '%' : '0');
    // temps restant, cycle, avancement de la séance (une fois par seconde)
    var reste = etat === 'fin' ? 0 : totalMs - e;
    ecrire('restant', el.restant, horloge(reste));
    ecrire('cycle', el.cycle, T.cycle.replace('{i}', String(p.c + 1)).replace('{n}', String(nCycles)));
    style('total', el.total, 'width', (etat === 'fin' ? 100 : Math.floor(e / 1000) * 1000 / totalMs * 100).toFixed(2) + '%');
    if (etat === 'cours') programmerSon(p, ph);
  }
  function boutons() {
    racine.setAttribute('data-etat', etat);
    el.go.textContent = etat === 'cours' ? T.pause : etat === 'pause' ? T.reprendre : T.demarrer;
    el.go.hidden = etat === 'fin';
    el.re.hidden = etat === 'repos';
    el.son.hidden = etat === 'fin';
    el.fin.hidden = etat !== 'fin';
  }
  /* Deux réveils pendant l'exercice : l'image suivante (cercle fluide) et, en secours, une minuterie vers la prochaine
     seconde (un onglet à l'arrière-plan n'a plus d'images). Les deux ne font que relire l'horloge. */
  function tourner() {
    image = 0;
    if (etat !== 'cours') return;
    afficher();
    if (etat === 'cours' && !document.hidden) image = requestAnimationFrame(tourner);
  }
  function veiller() {
    reveil = 0;
    if (etat !== 'cours') return;
    afficher();
    if (etat === 'cours') reveil = setTimeout(veiller, 1000 - (ecoule() % 1000) + 3);
  }
  function lancer() {
    if (!image && !document.hidden) image = requestAnimationFrame(tourner);
    if (!reveil) reveil = setTimeout(veiller, 1000 - (ecoule() % 1000) + 3);
  }
  function arreter() {
    if (image) cancelAnimationFrame(image);
    if (reveil) clearTimeout(reveil);
    image = 0; reveil = 0;
  }

  /* ---------- les états ---------- */
  function mesurer(etape) {
    try {
      if (window.gtag) window.gtag('event', 'outil_respiration', {technique: tech, etape: etape, duree: Math.round(totalMs / 1000)});
    } catch (e) {}
  }
  function demarrer() {
    arreter(); taire();
    preparer();
    vu = {};
    acquis = 0; caler(); etat = 'cours'; sonPrevu = 0;
    boutons();
    mesurer('debut');
    if (son) { reveillerSon(); note(NOTES[phases[0].nom], 0); }
    verrouiller();
    afficher();
    lancer();
    montrer();
  }
  function pause() {
    if (etat !== 'cours') return;
    ecoule();
    etat = 'pause';
    arreter(); taire(); liberer();
    boutons(); afficher();
    dire(T.dire_pause);
  }
  function reprendre() {
    if (etat !== 'pause') return;
    caler(); etat = 'cours';
    var p = position(acquis);
    sonPrevu = p.c * phases.length + p.i;
    if (son) { reveillerSon(); note(NOTES[phases[p.i].nom], 0); }
    boutons();
    verrouiller();
    afficher();
    lancer();
  }
  function finir() {
    var dedans = racine.contains(document.activeElement);
    etat = 'fin'; acquis = totalMs;
    arreter(); liberer();
    boutons(); afficher();
    dire(T.dire_fin);
    mesurer('fin');
    // le message de fin : il reçoit le focus si l'on était dans l'outil, et il est amené à l'écran si l'outil s'y trouve
    if (dedans) { try { el.fin.focus({preventScroll: true}); } catch (e) { el.fin.focus(); } }
    try {
      var r = racine.getBoundingClientRect(), h = window.innerHeight || document.documentElement.clientHeight;
      if (r.bottom > 0 && r.top < h) el.fin.scrollIntoView({behavior: calme() ? 'auto' : 'smooth', block: 'nearest'});
    } catch (e) {}
  }
  function repos() {
    arreter(); taire(); liberer();
    etat = 'repos'; acquis = 0;
    preparer();
    vu = {};
    boutons(); afficher();
    dire('');
  }
  /* Au départ, tout ce qui sert pendant l'exercice doit être à l'écran, sous l'en-tête collant du site : les boutons, le
     cercle, le temps restant et le son. Le bloc est centré s'il tient dans la fenêtre, sinon calé sous l'en-tête. */
  function montrer() {
    try {
      var h = window.innerHeight || document.documentElement.clientHeight, entete = 68;
      var a = el.scene.getBoundingClientRect(), b = el.go.getBoundingClientRect(), c = el.son.getBoundingClientRect();
      var haut = Math.min(a.top, b.top), bas = Math.max(a.bottom, c.bottom), libre = h - entete;
      if (haut >= entete && bas <= h) return;
      var cible = bas - haut <= libre ? entete + (libre - (bas - haut)) / 2 : entete + 6;
      if ('scrollBehavior' in document.documentElement.style) window.scrollBy({top: haut - cible, behavior: calme() ? 'auto' : 'smooth'});
      else window.scrollBy(0, haut - cible);
    } catch (e) {}
  }

  /* ---------- technique et durée ---------- */
  function dessinerChoix() {
    var h = '';
    TECH[tech].choix.forEach(function (c, i) {
      h += '<input type="radio" name="resp-duree" id="resp-d-' + i + '" value="' + i + '"' + (i === choix ? ' checked' : '') + '><label for="resp-d-' + i + '"></label>';
    });
    el.duree.innerHTML = h;
    var l = el.duree.querySelectorAll('label');
    TECH[tech].choix.forEach(function (c, i) { l[i].textContent = c.t; });
  }
  function choisir(nom, retenir) {
    if (!TECH[nom]) return;
    tech = nom; choix = TECH[nom].defaut;
    var r = document.getElementById('resp-t-' + nom);
    if (r) r.checked = true;
    dessinerChoix();
    el.rythme.textContent = '';                // le rythme en mots : « Inspire 5 s », « Expire 5 s »
    TECH[nom].phases.forEach(function (p) {
      var s = document.createElement('span');
      s.textContent = T.phases[p[0]] + '\u00a0' + p[1] + '\u00a0s';
      el.rythme.appendChild(s);
    });
    repos();
    if (retenir) { try { localStorage.setItem(CLE, nom); } catch (e) {} }
  }

  /* ---------- le son ---------- */
  function reveillerSon() {
    if (!audio) {
      var A = window.AudioContext || window.webkitAudioContext;
      if (!A) return null;
      try {
        audio = new A();
        sortie = audio.createGain();
        sortie.gain.value = 0.9;
        sortie.connect(audio.destination);
      } catch (e) { audio = null; return null; }
    }
    try { if (audio.state === 'suspended') audio.resume(); } catch (e) {}
    return audio;
  }
  /* Une note de bol, très douce : une sinusoïde et son octave, attaque de 40 ms, extinction lente. « dans » en ms. */
  function note(hz, dans, force, duree) {
    var a = reveillerSon();
    if (!a) return;
    try {
      var t = a.currentTime + Math.max(0, dans) / 1000 + 0.02, d = duree || 1.7, f = force || 0.075;
      var g = a.createGain();
      g.gain.setValueAtTime(0.0001, t);
      g.gain.linearRampToValueAtTime(f, t + 0.04);
      g.gain.exponentialRampToValueAtTime(0.0001, t + d);
      g.connect(sortie);
      var sources = [[hz, 1], [hz * 2, 0.22]].map(function (h) {
        var o = a.createOscillator(), v = a.createGain();
        o.type = 'sine'; o.frequency.value = h[0]; v.gain.value = h[1];
        o.connect(v); v.connect(g);
        o.start(t); o.stop(t + d + 0.05);
        return o;
      });
      var n = {t: t, fin: t + d + 0.05, g: g, sources: sources};
      notes.push(n);
      notes = notes.filter(function (x) { return x.fin > a.currentTime; });
    } catch (e) {}
  }
  /* Les notes programmées mais pas encore jouées sont retirées (pause, arrêt, son coupé) ; une note en cours s'éteint seule. */
  function taire() {
    if (!audio) return;
    var m = audio.currentTime;
    notes.forEach(function (n) {
      if (n.t > m) { try { n.g.disconnect(); n.sources.forEach(function (o) { o.stop(); }); } catch (e) {} }
    });
    notes = notes.filter(function (n) { return n.t <= m && n.fin > m; });
  }
  /* La note du prochain changement est programmée jusqu'à 1,5 s d'avance sur l'horloge audio : elle tombe juste même si
     l'affichage ralentit (onglet à l'arrière-plan : les minuteries n'y passent plus qu'une fois par seconde). */
  function programmerSon(p, ph) {
    if (!son) return;
    var numero = p.c * phases.length + p.i + 1, dans = ph.ms - p.dans;
    if (numero === sonPrevu || dans > 1500) return;
    sonPrevu = numero;
    if (p.c === nCycles - 1 && p.i === phases.length - 1) {          // la fin : un accord qui s'éteint lentement
      note(329.63, dans, 0.05, 3); note(440, dans, 0.05, 3); note(659.25, dans + 180, 0.035, 3);
    } else note(NOTES[phases[(p.i + 1) % phases.length].nom], dans);
  }

  /* ---------- l'écran reste allumé ---------- */
  function verrouiller() {
    if (!('wakeLock' in navigator) || verrou || verrouDemande || document.visibilityState !== 'visible') return;
    try {
      verrouDemande = true;
      navigator.wakeLock.request('screen').then(function (v) {
        verrouDemande = false;
        if (etat !== 'cours') { v.release().catch(function () {}); return; }
        verrou = v;
        v.addEventListener('release', function () { if (verrou === v) verrou = null; });
      }).catch(function () { verrouDemande = false; });
    } catch (e) { verrouDemande = false; }
  }
  function liberer() {
    var v = verrou;
    verrou = null;
    if (v) { try { v.release().catch(function () {}); } catch (e) {} }
  }

  /* ---------- les gestes ---------- */
  el.go.addEventListener('click', function () {
    if (etat === 'cours') pause(); else if (etat === 'pause') reprendre(); else demarrer();
  });
  el.re.addEventListener('click', function () { demarrer(); });
  el.son.addEventListener('click', function () {
    son = !son;
    el.son.setAttribute('aria-checked', son ? 'true' : 'false');
    if (!son) { taire(); return; }
    reveillerSon();
    var p = position(ecoule());
    sonPrevu = p.c * phases.length + p.i;
    note(NOTES[etat === 'cours' ? phases[p.i].nom : 'inspire'], 0);   // la note s'entend tout de suite : on sait à quoi s'attendre
  });
  el.tech.addEventListener('change', function (ev) {
    if (ev.target && ev.target.name === 'resp-tech') choisir(ev.target.value, true);
  });
  el.duree.addEventListener('change', function (ev) {
    if (!ev.target || ev.target.name !== 'resp-duree') return;
    var i = parseInt(ev.target.value, 10);
    if (!TECH[tech].choix[i]) return;
    choix = i;
    repos();
  });
  /* Boutons « Lancer … » du texte de la page : ils règlent l'outil sur la technique et y ramènent. */
  document.addEventListener('click', function (ev) {
    var a = ev.target && ev.target.closest ? ev.target.closest('[data-resp]') : null;
    if (!a) return;
    var nom = a.getAttribute('data-resp');
    if (!TECH[nom]) return;
    ev.preventDefault();
    if (nom !== tech || etat === 'fin') choisir(nom, true);
    try { racine.scrollIntoView({behavior: calme() ? 'auto' : 'smooth', block: 'start'}); } catch (e) { racine.scrollIntoView(); }
    try { el.go.focus({preventScroll: true}); } catch (e) {}
  });
  /* Retour au premier plan : l'affichage rattrape l'horloge d'un coup, l'écran est de nouveau gardé allumé. */
  document.addEventListener('visibilitychange', function () {
    if (document.hidden || etat !== 'cours') return;
    afficher();
    if (etat !== 'cours') return;
    if (son) reveillerSon();
    verrouiller();
    lancer();
  });
  if (mq) {
    var change = function () { vu = {}; afficher(); };
    if (mq.addEventListener) mq.addEventListener('change', change); else if (mq.addListener) mq.addListener(change);
  }

  /* ---------- départ ---------- */
  try { var m = localStorage.getItem(CLE); if (m && TECH[m]) tech = m; } catch (e) {}
  choisir(tech, false);
})();
