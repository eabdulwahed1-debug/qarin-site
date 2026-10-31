/* Khutwa shopping assistant ("مساعد خطوة") + instant search.
   Runs entirely in the browser on our own catalog (assets/catalog.json): understands need, child's age and
   budget in Arabic or English, then recommends subsections with review-sorted, tagged store links.
   No personal data is stored or sent anywhere. */
(function () {
  var AR = document.documentElement.lang !== 'en';
  var ROOT = window.KH_ROOT || '';
  var TAG = window.KH_TAG || '';
  var CAT = null, loading = null;

  var T = AR ? {
    title: 'مساعد خطوة', sub: 'يختار لك الأنسب خلال ثوانٍ', open: 'اسأل مساعد خطوة',
    hello: 'هلا! 👋 قل لي وش يحتاج طفلك، وكم عمره، وكم ميزانيتك تقريباً — وأنا أختار لك الأنسب.',
    example: 'مثال: «طفلي عمره 3 سنوات وتأخر في الكلام، ميزانيتي تحت 100 ريال»',
    ph: 'اكتب سؤالك…', send: 'إرسال', understood: 'فهمت', age: 'العمر', budget: 'الميزانية',
    under: 'حتى', sar: 'ريال', years: 'سنة', months: 'شهر', need: 'الاحتياج',
    picks: 'هذي أنسب الاقتراحات لك:', none: 'ما فهمت الاحتياج بالضبط 🙏 اختر واحداً من هذي الأقسام:',
    amz: 'الأفضل تقييماً في أمازون', cmp: 'قارن السعر', section: 'كل القسم',
    tip: 'الروابط مرتبة حسب تقييم المشترين' , budgetTip: 'وفي حدود ميزانيتك',
    more: 'تبي شي ثاني؟ اكتب لي أو اختر:', care: 'ℹ️ هذه أدوات مساعدة وليست علاجاً؛ لأي قلق استشر الأخصائي.',
    chips: ['تأخر الكلام', 'التركيز والتشتت', 'السفر مع طفل', 'الرضاعة والرضيع', 'هدية تعليمية', 'سلامة البيت'],
    sugAsk: 'اسأل المساعد عن', sugAmz: 'ابحث في أمازون عن', sugCmp: 'قارن أسعار'
  } : {
    title: 'Khutwa assistant', sub: 'Finds the right pick in seconds', open: 'Ask the Khutwa assistant',
    hello: "Hi! 👋 Tell me what your child needs, their age and roughly your budget — I'll pick the best options.",
    example: 'e.g. “My son is 3 and his speech is delayed, budget under 100 SAR”',
    ph: 'Type your question…', send: 'Send', understood: 'Got it', age: 'Age', budget: 'Budget',
    under: 'up to', sar: 'SAR', years: 'yrs', months: 'months', need: 'Need',
    picks: 'Here are the best matches:', none: "I didn't quite get the need 🙏 Pick one of these:",
    amz: 'Top-rated on Amazon', cmp: 'Compare price', section: 'Whole section',
    tip: 'Links are sorted by buyer reviews', budgetTip: 'and within your budget',
    more: 'Anything else? Type or pick:', care: 'ℹ️ These are practice aids, not treatment — see a specialist if worried.',
    chips: ['Speech delay', 'Focus & attention', 'Travelling with a baby', 'Feeding & newborn', 'Learning gift', 'Home safety'],
    sugAsk: 'Ask the assistant about', sugAmz: 'Search Amazon for', sugCmp: 'Compare prices for'
  };

  function load() {
    if (CAT) return Promise.resolve(CAT);
    if (!loading) loading = fetch(ROOT + 'assets/catalog.json').then(function (r) { return r.json(); }).then(function (j) { CAT = j; return j; });
    return loading;
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function norm(s) {
    return (s || '').toLowerCase()
      .replace(/[ً-ْـ]/g, '')
      .replace(/[٠-٩]/g, function (d) { return '٠١٢٣٤٥٦٧٨٩'.indexOf(d); })
      .replace(/[أإآ]/g, 'ا').replace(/ة/g, 'ه').replace(/ى/g, 'ي').replace(/ؤ/g, 'و').replace(/ئ/g, 'ي');
  }
  function tokens(s) {
    return norm(s).split(/[^a-z0-9؀-ۿ]+/).filter(Boolean).map(function (w) {
      if (/^[؀-ۿ]/.test(w)) { w = w.replace(/^(وال|بال|فال|كال|لل|ال)/, ''); }
      return w;
    }).filter(function (w) { return w.length > 1; });
  }
  function track(p) { try { window.goatcounter && window.goatcounter.count({ path: p, event: true }); } catch (e) {} }

  /* --- understanding --- */
  function parse(q) {
    var n = norm(q), out = { age: null, budget: null };
    var m = n.match(/(\d+(?:\.\d+)?)\s*(سنه|سنوات|سنين|سنتين|عام|اعوام|years?|yrs?|yo)(?![a-z])/);
    if (m) out.age = parseFloat(m[1]);
    else if (/سنتين|عمره سنتين/.test(n)) out.age = 2;
    if (out.age == null) {
      var en = n.match(/(son|daughter|child|kid|boy|girl|toddler|he|she|baby)\s+(?:is\s+|turned\s+|aged\s+)?(\d{1,2})(?!\d)(?!\s*(sar|riyal|ريال|%))/);
      if (en) out.age = parseInt(en[2], 10);
    }
    var mo = n.match(/(\d+)\s*(شهر|شهور|اشهر|months?)/);
    if (out.age == null && mo) out.age = parseInt(mo[1], 10) / 12;
    if (out.age == null && /(رضيع|مولود|حديث الولاده|newborn|infant)/.test(n)) out.age = 0.3;
    var b = n.match(/(تحت|اقل من|ما يزيد عن|حدود|بحدود|لين|الى|under|below|max|up to|budget)\s*(\d+)/) ||
            n.match(/(\d+)\s*(ريال|ر\.?س|sar|riyal)/);
    if (b) out.budget = parseInt(b[2] && /\d/.test(b[2]) ? b[2] : b[1], 10);
    return out;
  }
  var STOP = /^(طفل|طفلي|طفلتي|ولد|ولدي|بنت|بنتي|ابني|بنيتي|عمر|عمره|عمرها|ميزانيه|ميزانيتي|ريال|سنه|سنوات|سنين|شهر|شهور|اشهر|تحت|اقل|حدود|ابي|ابغى|ابغي|اريد|احتاج|عندي|كيف|وش|ايش|شي|اللي|عشان|my|son|daughter|kid|child|baby's|years?|old|months?|budget|under|sar|want|need|for|the|and|with)$/;
  function score(q) {
    var qt = tokens(q.replace(/\d+/g, ' ')).filter(function (w) { return !STOP.test(w); });
    var res = [];
    CAT.groups.forEach(function (g) {
      var gt = tokens(g.tags + ' ' + g.ar + ' ' + g.en);
      var gs = 0;
      qt.forEach(function (w) { if (gt.some(function (t) { return w.length > 2 && (t === w || (t.length > 3 && (t.indexOf(w) === 0 || w.indexOf(t) === 0))); })) gs += (g.id === 'travel' ? 3 : 2); });
      g.items.forEach(function (it, i) {
        var itT = tokens(it.tags + ' ' + it.ar + ' ' + it.en), s = gs;
        qt.forEach(function (w) { if (itT.some(function (t) { return w.length > 2 && (t === w || (t.length > 3 && (t.indexOf(w) === 0 || w.indexOf(t) === 0))); })) s += 5; });
        res.push({ g: g, it: it, i: i, s: s });
      });
    });
    return res;
  }
  function ageFits(it, age) {
    var m = (it.en || '').match(/\((\d+)[–-](\d+)\)/);
    if (!m || age == null) return 0;
    var a = +m[1], b = +m[2];
    return age >= a && age <= b ? 6 : (Math.abs(age - (age < a ? a : b)) <= 1 ? 1 : -4);
  }
  function amzUrl(kw, budget) {
    var u = 'https://www.amazon.sa/s?k=' + encodeURIComponent(kw).replace(/%20/g, '+');
    if (budget) u += '&rh=' + encodeURIComponent('p_36:-' + budget * 100);
    return u + '&s=review-rank' + (TAG ? '&tag=' + encodeURIComponent(TAG) : '');
  }
  function recommend(q) {
    var p = parse(q);
    var list = score(q).map(function (r) { if (r.s > 0) r.s += ageFits(r.it, p.age); return r; })
      .filter(function (r) { return r.s > 0; })
      .sort(function (a, b) { return b.s - a.s; });
    // keep the best section dominant but allow a second one
    var top = list.slice(0, 3);
    return { p: p, top: top };
  }

  /* --- UI --- */
  var fab, panel, log, input;
  function build() {
    fab = document.createElement('button');
    fab.className = 'kh-fab'; fab.type = 'button';
    fab.innerHTML = '<span class="kh-fab-dot"></span>✨ <b>' + esc(T.open) + '</b>';
    fab.onclick = function () { toggle(true); };
    panel = document.createElement('section');
    panel.className = 'kh-panel'; panel.hidden = true; panel.setAttribute('aria-label', T.title);
    panel.innerHTML = '<header class="kh-head"><div class="kh-avatar">خ</div><div><b>' + esc(T.title) + '</b><small>' + esc(T.sub) +
      '</small></div><button type="button" class="kh-x" aria-label="close">×</button></header><div class="kh-log" aria-live="polite"></div>' +
      '<form class="kh-form"><input type="text" autocomplete="off" placeholder="' + esc(T.ph) + '" aria-label="' + esc(T.ph) + '"><button type="submit">' + esc(T.send) + '</button></form>';
    document.body.appendChild(fab); document.body.appendChild(panel);
    log = panel.querySelector('.kh-log'); input = panel.querySelector('input');
    panel.querySelector('.kh-x').onclick = function () { toggle(false); };
    panel.querySelector('form').onsubmit = function (e) { e.preventDefault(); var v = input.value.trim(); if (v) { input.value = ''; ask(v); } };
    bot('<p>' + esc(T.hello) + '</p><p class="kh-ex">' + esc(T.example) + '</p>' + chips());
  }
  function toggle(on) {
    panel.hidden = !on; fab.hidden = on;
    if (on) { load(); setTimeout(function () { input.focus(); }, 50); track('agent:open'); }
  }
  function chips() {
    return '<div class="kh-chips">' + T.chips.map(function (c) { return '<button type="button" class="kh-chip">' + esc(c) + '</button>'; }).join('') + '</div>';
  }
  function bind(el) {
    el.querySelectorAll('.kh-chip').forEach(function (b) { b.onclick = function () { ask(b.textContent); }; });
    el.querySelectorAll('a[data-ev]').forEach(function (a) { a.addEventListener('click', function () { track(a.dataset.ev); }); });
  }
  function bot(html) { var d = document.createElement('div'); d.className = 'kh-msg kh-bot'; d.innerHTML = html; log.appendChild(d); bind(d); log.scrollTop = log.scrollHeight; }
  function me(text) { var d = document.createElement('div'); d.className = 'kh-msg kh-me'; d.textContent = text; log.appendChild(d); log.scrollTop = log.scrollHeight; }
  function typing() { var d = document.createElement('div'); d.className = 'kh-msg kh-bot kh-typing'; d.innerHTML = '<i></i><i></i><i></i>'; log.appendChild(d); log.scrollTop = log.scrollHeight; return d; }

  function ask(q) {
    toggle(true); me(q); track('agent:q:' + q.slice(0, 60));
    var t = typing();
    load().then(function () {
      setTimeout(function () {
        t.remove();
        var r = recommend(q), p = r.p;
        if (!r.top.length) { bot('<p>' + esc(T.none) + '</p>' + chips()); return; }
        var facts = [];
        facts.push(T.need + ': <b>' + esc(r.top[0].g[AR ? 'ar' : 'en']) + '</b>');
        if (p.age != null) facts.push(T.age + ': <b>' + (p.age < 1 ? Math.round(p.age * 12) + ' ' + T.months : p.age + ' ' + T.years) + '</b>');
        if (p.budget) facts.push(T.budget + ': <b>' + T.under + ' ' + p.budget + ' ' + T.sar + '</b>');
        var html = '<p>✅ ' + T.understood + ' — ' + facts.join(' · ') + '</p><p>' + esc(T.picks) + '</p><div class="kh-cards">';
        r.top.forEach(function (x) {
          var kw = AR ? x.it.kw_ar : x.it.kw_en;
          html += '<div class="kh-card">' + (x.it.img ? '<img src="' + esc(x.it.img) + '" alt="" loading="lazy">' : '') +
            '<div><b>' + esc(x.it[AR ? 'ar' : 'en']) + '</b><small>' + esc(x.g[AR ? 'ar' : 'en']) + '</small>' +
            '<a class="kh-buy" href="' + esc(amzUrl(kw, p.budget)) + '" target="_blank" rel="sponsored nofollow noopener" data-ev="agent:amz:' + esc(x.g.id) + ':' + x.i + '">' + esc(T.amz) + '</a>' +
            '<span class="kh-links"><a href="' + esc(ROOT + (AR ? '' : 'en/') + 'compare/?q=' + encodeURIComponent(kw)) + '" data-ev="agent:cmp">' + esc(T.cmp) + '</a> · ' +
            '<a href="' + esc(ROOT + (AR ? '' : 'en/') + 'need/' + x.g.id + '/') + '">' + esc(T.section) + '</a></span></div></div>';
        });
        html += '</div><p class="kh-note">' + esc(T.tip) + (p.budget ? ' ' + esc(T.budgetTip) : '') + '.</p>';
        if (r.top.some(function (x) { return x.g.id === 'speech' || x.g.id === 'focus'; })) html += '<p class="kh-note">' + esc(T.care) + '</p>';
        html += '<p>' + esc(T.more) + '</p>' + chips();
        bot(html);
      }, 450);
    });
  }

  /* --- instant search in the header --- */
  function instant() {
    var form = document.querySelector('.top-search'); if (!form) return;
    var inp = form.querySelector('input[type=search]');
    var box = document.createElement('div'); box.className = 'kh-sug'; box.hidden = true; form.appendChild(box);
    form.addEventListener('submit', function (e) { e.preventDefault(); var v = inp.value.trim(); if (v) { box.hidden = true; ask(v); } });
    inp.addEventListener('input', function () {
      var v = inp.value.trim(); if (v.length < 2) { box.hidden = true; return; }
      load().then(function () {
        var hits = score(v).filter(function (r) { return r.s >= 5; }).sort(function (a, b) { return b.s - a.s; }).slice(0, 5);
        var h = hits.map(function (x) {
          var kw = AR ? x.it.kw_ar : x.it.kw_en;
          return '<a class="kh-s-item" href="' + esc(amzUrl(kw)) + '" target="_blank" rel="sponsored nofollow noopener" data-ev="search:amz:' + x.g.id + ':' + x.i + '">' +
            (x.it.img ? '<img src="' + esc(x.it.img) + '" alt="">' : '') + '<span><b>' + esc(x.it[AR ? 'ar' : 'en']) + '</b><small>' + esc(x.g[AR ? 'ar' : 'en']) + '</small></span></a>';
        }).join('');
        h += '<button type="button" class="kh-s-act kh-s-ask">✨ ' + esc(T.sugAsk) + ' «' + esc(v) + '»</button>' +
          '<a class="kh-s-act" href="' + esc(amzUrl(v)) + '" target="_blank" rel="sponsored nofollow noopener" data-ev="search:amz-free">🔎 ' + esc(T.sugAmz) + ' «' + esc(v) + '»</a>' +
          '<a class="kh-s-act" href="' + esc(ROOT + (AR ? '' : 'en/') + 'compare/?q=' + encodeURIComponent(v)) + '" data-ev="search:cmp">⚖️ ' + esc(T.sugCmp) + ' «' + esc(v) + '»</a>';
        box.innerHTML = h; box.hidden = false; bind(box);
        box.querySelector('.kh-s-ask').onclick = function () { box.hidden = true; ask(v); };
      });
    });
    document.addEventListener('click', function (e) { if (!form.contains(e.target)) box.hidden = true; });
  }

  build(); instant();
  document.querySelectorAll('[data-open-agent]').forEach(function (b) { b.addEventListener('click', function (e) { e.preventDefault(); toggle(true); }); });
  window.khAsk = ask;
})();
