/* Hover/focus highlighting for the Einstein-predictions rosette on the
   Research page. Each legend link carries data-lights="lensing waves ...";
   while it is hovered or focused, those sets brighten on the hero SVG.
   The links are plain anchors, so without this script — and on touch
   devices, where there is no hover — they simply navigate. */
(function () {
  var hero = document.querySelector('.venn-hero');
  if (!hero) return;
  var svg = hero.querySelector('svg.venn');
  if (!svg) return;

  var active = [];

  function light(sets) {
    unlight();
    active = sets.split(/\s+/).filter(Boolean).map(function (s) {
      return 'lit-' + s;
    });
    if (!active.length) return;
    svg.classList.add('venn-focus');
    active.forEach(function (c) { svg.classList.add(c); });
  }

  function unlight() {
    svg.classList.remove('venn-focus');
    active.forEach(function (c) { svg.classList.remove(c); });
    active = [];
  }

  hero.querySelectorAll('.venn-legend a[data-lights]').forEach(function (a) {
    var sets = a.getAttribute('data-lights');
    a.addEventListener('mouseenter', function () { light(sets); });
    a.addEventListener('focus', function () { light(sets); });
    a.addEventListener('mouseleave', unlight);
    a.addEventListener('blur', unlight);
  });
})();
