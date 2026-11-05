// Search over search.json, which build.py writes. Runs entirely in the browser: nothing is sent
// anywhere, and the site needs no search server.
(function () {
  var box = document.getElementById("q");
  var out = document.getElementById("results");
  if (!box || !out) return;
  var records = null;

  function esc(text) {
    var el = document.createElement("span");
    el.textContent = text;
    return el.innerHTML;
  }

  function show(query) {
    var words = query.toLowerCase().split(/\s+/).filter(Boolean);
    if (!words.length) { out.innerHTML = ""; return; }
    var hits = records.map(function (r) {
      var title = r.t.toLowerCase(), text = r.x.toLowerCase(), score = 0;
      for (var i = 0; i < words.length; i++) {
        var inTitle = title.indexOf(words[i]) >= 0, inText = text.indexOf(words[i]) >= 0;
        if (!inTitle && !inText) return null;
        score += (inTitle ? 5 : 0) + (inText ? 1 : 0);
      }
      return { r: r, score: score };
    }).filter(Boolean).sort(function (a, b) { return b.score - a.score; }).slice(0, 40);
    out.innerHTML = hits.length ? hits.map(function (h) {
      return '<div class="search-result"><a href="' + esc(h.r.u) + '">' + esc(h.r.t) + "</a><p>" + esc(h.r.d) + "</p></div>";
    }).join("") : '<p class="muted">Nothing found.</p>';
  }

  fetch("/search.json").then(function (r) { return r.json(); }).then(function (data) {
    records = data;
    var start = new URLSearchParams(location.search).get("q");
    if (start) { box.value = start; show(start); }
    box.addEventListener("input", function () { show(box.value); });
  });
})();
