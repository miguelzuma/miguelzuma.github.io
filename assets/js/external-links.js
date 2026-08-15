/* Send off-site links to a new tab, so a visitor reading a page is never
   navigated away from it.

   Done here rather than in the templates because the links are spread across
   nine pages and half a dozen data files, and one rule cannot be forgotten the
   way two hundred attributes can. Without JavaScript the links still work;
   they just open in place.

   rel="noopener" is set alongside: a new tab opened this way can otherwise
   reach back at this page through window.opener. */
(function () {
	'use strict';

	var here = location.host;

	Array.prototype.forEach.call(
		document.querySelectorAll('a[href]'),
		function (a) {
			// Only http(s) links that point somewhere else. Leaves mailto:,
			// in-page fragments and same-site links alone.
			if (a.protocol !== 'http:' && a.protocol !== 'https:') return;
			if (!a.host || a.host === here) return;
			if (a.hasAttribute('target')) return;

			a.target = '_blank';
			var rel = (a.getAttribute('rel') || '').split(/\s+/).filter(Boolean);
			if (rel.indexOf('noopener') === -1) rel.push('noopener');
			a.setAttribute('rel', rel.join(' '));
		}
	);
})();
