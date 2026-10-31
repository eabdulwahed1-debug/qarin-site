/* Qarin Kids buying assistant: category → budget → use → tailored Amazon.sa results */
(function () {
  var root = document.getElementById('finder');
  if (!root || !window.QARIN_FINDER) return;
  var data = window.QARIN_FINDER;
  var tag = window.QARIN_TAG || '';
  var lang = document.documentElement.lang === 'en' ? 'en' : 'ar';
  var langRoot = root.getAttribute('data-root') || '';
  var T = {
    ar: {
      q1: 'وش تحتاج لطفلك؟', q2: 'كم ميزانيتك؟', q3: 'حدّد أكثر',
      step: 'الخطوة', of: 'من', back: 'رجوع', restart: 'ابدأ من جديد',
      resultTitle: 'جاهز! هذي أنسب الخيارات لك',
      cta: 'اعرض أنسب الخيارات في أمازون', all: 'كل الخيارات بنفس الميزانية', guide: 'نصائح القسم',
      note: 'النتائج مرتبة حسب تقييم المشترين، وفي حدود ميزانيتك.',
      under: function (a) { return 'أقل من ' + a + ' ريال'; },
      over: function (a) { return 'أكثر من ' + a + ' ريال'; },
      range: function (a, b) { return a + ' – ' + b + ' ريال'; }
    },
    en: {
      q1: 'What do you need?', q2: "What's your budget?", q3: 'Narrow it down',
      step: 'Step', of: 'of', back: 'Back', restart: 'Start over',
      resultTitle: 'Done! Here are your best matches',
      cta: 'Show my best matches on Amazon', all: 'All options in this budget', guide: 'Section tips',
      note: 'Results are sorted by buyer reviews and stay within your budget.',
      under: function (a) { return 'Under SAR ' + a; },
      over: function (a) { return 'Over SAR ' + a; },
      range: function (a, b) { return 'SAR ' + a + '–' + b; }
    }
  }[lang];

  function fmt(n) { return Number(n).toLocaleString('en-US'); }
  function budgetLabel(b) {
    if (!b[0]) return T.under(fmt(b[1]));
    if (!b[1]) return T.over(fmt(b[0]));
    return T.range(fmt(b[0]), fmt(b[1]));
  }
  function amz(keywords, b) {
    var url = 'https://www.amazon.sa/s?k=' + encodeURIComponent(keywords).replace(/%20/g, '+');
    if (b) url += '&rh=' + encodeURIComponent('p_36:' + (b[0] ? b[0] * 100 : '') + '-' + (b[1] ? b[1] * 100 : ''));
    url += '&s=review-rank';
    if (tag) url += '&tag=' + encodeURIComponent(tag);
    return url;
  }
  function track(name) {
    try { if (window.goatcounter && window.goatcounter.count) window.goatcounter.count({ path: 'finder:' + name, event: true }); } catch (e) {}
  }
  function el(tagName, cls, html) { var e = document.createElement(tagName); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  var state = { cat: null, budget: null };

  function head(n, q) {
    var h = el('div', 'f-head');
    h.appendChild(el('span', 'f-step', T.step + ' ' + n + ' ' + T.of + ' 3'));
    h.appendChild(el('h2', 'f-q', esc(q)));
    return h;
  }
  function backBtn(fn) { var b = el('button', 'f-back', '← ' + T.back); if (lang === 'ar') b.textContent = T.back + ' →'; b.type = 'button'; b.onclick = fn; return b; }

  function step1() {
    root.innerHTML = '';
    root.appendChild(head(1, T.q1));
    var g = el('div', 'f-grid');
    data.categories.forEach(function (c) {
      var b = el('button', 'f-opt f-cat', '<span class="f-ic" style="--c:' + c.color + '">' + c.icon + '</span><b>' + esc(c[lang]) + '</b>');
      b.type = 'button';
      b.onclick = function () { state.cat = c; track(c.id); step2(); };
      g.appendChild(b);
    });
    root.appendChild(g);
  }
  function step2() {
    var c = state.cat;
    root.innerHTML = '';
    root.appendChild(head(2, T.q2));
    var g = el('div', 'f-chips');
    c.budgets.forEach(function (b) {
      var x = el('button', 'f-opt f-chip', esc(budgetLabel(b)));
      x.type = 'button';
      x.onclick = function () { state.budget = b; step3(); };
      g.appendChild(x);
    });
    root.appendChild(g);
    root.appendChild(backBtn(step1));
  }
  function step3() {
    var c = state.cat;
    root.innerHTML = '';
    root.appendChild(head(3, T.q3));
    var g = el('div', 'f-chips');
    c.uses.forEach(function (u) {
      var x = el('button', 'f-opt f-chip', esc(u[lang]));
      x.type = 'button';
      x.onclick = function () { result(u); };
      g.appendChild(x);
    });
    root.appendChild(g);
    root.appendChild(backBtn(step2));
  }
  function result(u) {
    var c = state.cat, b = state.budget;
    var kw = lang === 'ar' ? u.kw_ar : u.kw_en;
    var base = lang === 'ar' ? c.kw_ar : c.kw_en;
    root.innerHTML = '';
    var box = el('div', 'f-result');
    box.appendChild(el('span', 'f-step', '✓ ' + esc(c[lang]) + ' · ' + esc(budgetLabel(b)) + ' · ' + esc(u[lang])));
    box.appendChild(el('h2', 'f-q', esc(T.resultTitle)));
    box.appendChild(el('p', 'f-tip', '💡 ' + esc(lang === 'ar' ? u.tip_ar : u.tip_en)));
    var main = el('a', 'f-cta', esc(T.cta) + ' ' + (lang === 'ar' ? '←' : '→'));
    main.href = amz(kw, b); main.target = '_blank'; main.rel = 'sponsored nofollow noopener';
    main.onclick = function () { track('go:' + c.id + ':' + kw); };
    box.appendChild(main);
    var row = el('div', 'f-links');
    var all = el('a', '', esc(T.all)); all.href = amz(base, b); all.target = '_blank'; all.rel = 'sponsored nofollow noopener';
    all.onclick = function () { track('all:' + c.id); };
    row.appendChild(all);
    if (c.guide) { var gd = el('a', '', esc(T.guide)); gd.href = langRoot + c.guide + '/'; row.appendChild(gd); }
    box.appendChild(row);
    box.appendChild(el('p', 'f-note', esc(T.note)));
    var again = el('button', 'f-back', '↺ ' + T.restart); again.type = 'button'; again.onclick = function () { state = { cat: null, budget: null }; step1(); };
    box.appendChild(again);
    root.appendChild(box);
  }
  step1();
})();
