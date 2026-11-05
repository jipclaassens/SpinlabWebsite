// The filter on the theses page. Without javascript the whole list simply stays visible.
(function () {
  var box = document.getElementById("thesis-filter");
  if (!box) return;
  box.hidden = false;
  var none = document.getElementById("thesis-none");
  var groups = document.querySelectorAll(".thesis-group");

  box.addEventListener("input", function () {
    var words = box.value.toLowerCase().split(/\s+/).filter(Boolean);
    var shown = 0;
    groups.forEach(function (group) {
      var inGroup = 0;
      var heading = group.querySelector("h2").textContent.toLowerCase();
      group.querySelectorAll(".thesis").forEach(function (row) {
        var text = heading + " " + row.textContent.toLowerCase();
        var match = words.every(function (word) { return text.indexOf(word) >= 0; });
        row.hidden = !match;
        if (match) inGroup++;
      });
      group.hidden = inGroup === 0;
      shown += inGroup;
    });
    none.hidden = shown > 0;
  });
})();
