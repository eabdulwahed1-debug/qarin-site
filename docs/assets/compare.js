/* Alam Tifli price-compare launcher: opens the same product search on several stores side by side.
   Live prices need official APIs (Amazon PA-API, AliExpress API) — added once accounts are approved. */
(function () {
  var box = document.getElementById('cmp-results');
  if (!box) return;
  var cfg = window.KH_CMP || {};
  var ar = document.documentElement.lang !== 'en';
  var q = new URLSearchParams(location.search).get('q');
  var input = document.querySelector('.cmp-form input[name=q]');
  if (!q) return;
  if (input) input.value = q;
  var e = encodeURIComponent(q);
  var stores = [
    { id: 'amazon', name: ar ? 'أمازون السعودية' : 'Amazon.sa', color: '#ff9900', icon: '🟠',
      url: 'https://www.amazon.sa/s?k=' + e + '&s=review-rank' + (cfg.amazon ? '&tag=' + encodeURIComponent(cfg.amazon) : ''),
      note: ar ? 'شحن سريع داخل السعودية وإرجاع سهل' : 'Fast delivery in Saudi Arabia, easy returns' },
    { id: 'aliexpress', name: ar ? 'علي إكسبريس' : 'AliExpress', color: '#e43225', icon: '🔴',
      url: 'https://ar.aliexpress.com/wholesale?SearchText=' + e + '&SortType=total_tranpro_desc',
      note: ar ? 'غالباً الأرخص، لكن الشحن أبطأ' : 'Often cheapest, slower shipping' }
  ];
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  var h = '<h2 class="cmp-title">' + (ar ? 'نتائج «' : 'Results for “') + esc(q) + (ar ? '» في كل متجر' : '” in each store') + '</h2><div class="cmp-grid">';
  stores.forEach(function (s) {
    h += '<a class="cmp-card" style="--s:' + s.color + '" href="' + esc(s.url) + '" target="_blank" rel="sponsored nofollow noopener" data-store="' + s.id + '">' +
      '<span class="cmp-ic">' + s.icon + '</span><b>' + esc(s.name) + '</b><small>' + esc(s.note) + '</small>' +
      '<span class="cmp-go">' + (ar ? 'شوف الأسعار ←' : 'See prices →') + '</span></a>';
  });
  h += '</div><p class="cmp-tip">💡 ' + (ar
    ? 'افتح المتاجر وقارن: السعر شامل الشحن، مدة التوصيل، وتقييم البائع. الأرخص مو دايم الأفضل.'
    : 'Open the stores and compare: price including shipping, delivery time and seller rating. Cheapest isn\'t always best.') + '</p>';
  box.innerHTML = h;
  box.querySelectorAll('.cmp-card').forEach(function (a) {
    a.addEventListener('click', function () {
      try { window.goatcounter && window.goatcounter.count({ path: 'compare:' + a.dataset.store + ':' + q, event: true }); } catch (x) {}
    });
  });
})();
