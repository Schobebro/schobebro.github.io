// Optionale Ergänzungen: kein Tracking, kein Browserspeicher und keine Netzwerkanfragen.
for (const button of document.querySelectorAll('[data-print]')) {
  button.hidden = false;
  button.addEventListener('click', () => window.print());
}
const tocLinks = [...document.querySelectorAll('.toc a[href^="#"]')];
if ('IntersectionObserver' in window && tocLinks.length) {
  const observer = new IntersectionObserver(entries => {
    const visible = entries.find(entry => entry.isIntersecting);
    if (!visible) return;
    for (const link of tocLinks) {
      if (link.hash === `#${visible.target.id}`) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    }
  }, { rootMargin: '-12% 0px -60% 0px' });
  for (const link of tocLinks) {
    const section = document.getElementById(link.hash.slice(1));
    if (section) observer.observe(section);
  }
}
