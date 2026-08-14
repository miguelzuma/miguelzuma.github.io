/* Fragment aliases for deep links made against the previous version of this
   site, whose anchors were <a name="..."> targets that no longer exist. Each
   entry points an old fragment at the section that now holds the same
   material; a value containing "#" is a page that has moved elsewhere.

   Without this, an old link lands silently at the top of a long page. */
(function () {
  var ALIASES = {
    'research.html': {
      pbh: 'main-program',
      gws: 'tests-of-gravity',
      tests: 'cosmology',
      theory: 'scalar-tensor',
      future: 'leadership'
    },
    'outreach.html': {
      popular_advice: 'talks.html#careers',
      popular_en: 'archive-en',
      popular_de: 'archive-de',
      popular_es: 'archive-es',
      teaching: 'talks.html#teaching'
    }
  };

  function resolve() {
    var hash = window.location.hash.slice(1);
    if (!hash) return;

    var old;
    try {
      old = decodeURIComponent(hash);
    } catch (e) {
      return;
    }
    if (document.getElementById(old)) return; // a real section: nothing to do

    var page = window.location.pathname.split('/').pop() || 'index.html';
    var target = (ALIASES[page] || {})[old];
    if (!target) return;

    if (target.indexOf('#') > -1) {
      // The material lives on another page now. replace() rather than
      // assignment, so the dead anchor does not sit in the back button.
      window.location.replace(target);
      return;
    }

    var el = document.getElementById(target);
    if (!el) return;

    // Rewriting the hash alone does not make Chrome scroll, so do it by hand.
    // replaceState leaves the back button pointing where it did, and fires no
    // hashchange, so this cannot loop. The jump is instant, overriding the
    // page's smooth scroll-behavior: this stands in for a fragment the browser
    // should have resolved on load, not for a click.
    history.replaceState(null, '', '#' + target);
    jump(el);

    // Images above the target settle after this runs and shift it; re-anchor
    // once, unless the reader has already scrolled away.
    var landed = Math.round(window.pageYOffset);
    window.addEventListener('load', function () {
      if (Math.round(window.pageYOffset) === landed) jump(el);
    }, { once: true });
  }

  function jump(el) {
    el.scrollIntoView({ behavior: 'instant', block: 'start' });
  }

  resolve();
  window.addEventListener('hashchange', resolve);
})();
