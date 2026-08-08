/* In-page section navigation: keeps the sticky bar clear of the site header
   and marks the section currently in view. Degrades to a plain list of anchor
   links if this never runs. */
(function () {
	'use strict';

	var nav = document.querySelector('[data-subnav]');
	if (!nav) return;

	var header = document.querySelector('.site-header');
	var root = document.documentElement;

	/* The subnav sticks below the header, so it needs the header's height.
	   Measured rather than hard-coded: it changes with the viewport, and the
	   header stops being sticky on narrow screens. */
	function measure() {
		var h = 0;
		if (header && getComputedStyle(header).position === 'sticky') {
			h = header.getBoundingClientRect().height;
		}
		root.style.setProperty('--header-h', h + 'px');
		root.style.setProperty('--subnav-h', nav.getBoundingClientRect().height + 'px');
	}

	var links = Array.prototype.slice.call(nav.querySelectorAll('a[href^="#"]'));
	var targets = links.map(function (a) {
		try {
			return document.getElementById(decodeURIComponent(a.hash.slice(1)));
		} catch (e) {
			return null;
		}
	});

	var current = null;

	function highlight() {
		/* The active section is the last one whose top has passed under the
		   two sticky bars. */
		/* Slack must cover the sections' scroll-margin-top, or the section you
		   just jumped to sits below the cutoff and the previous one stays lit. */
		var cutoff = nav.getBoundingClientRect().bottom + 20;
		var found = -1;
		for (var i = 0; i < targets.length; i++) {
			if (targets[i] && targets[i].getBoundingClientRect().top <= cutoff) found = i;
		}
		/* Past the end of the page, keep the last section marked. */
		if (found === current) return;
		if (current !== null && links[current]) links[current].removeAttribute('aria-current');
		if (found >= 0) links[found].setAttribute('aria-current', 'true');
		current = found;
	}

	var ticking = false;
	function onScroll() {
		if (ticking) return;
		ticking = true;
		requestAnimationFrame(function () {
			highlight();
			ticking = false;
		});
	}

	measure();
	highlight();
	addEventListener('scroll', onScroll, { passive: true });
	addEventListener('resize', function () {
		measure();
		highlight();
	});
})();
