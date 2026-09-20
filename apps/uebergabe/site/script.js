// Progressive enhancement only. No cookies, storage, analytics or network requests.
for (const button of document.querySelectorAll('[data-print]')) {
  button.hidden = false;
  button.addEventListener('click', () => window.print());
}

const tocLinks = [...document.querySelectorAll('.toc a[href^="#"]')];
if ('IntersectionObserver' in window && tocLinks.length) {
  const observer = new IntersectionObserver((entries) => {
    const visible = entries.filter(entry => entry.isIntersecting);
    if (!visible.length) return;
    const id = visible[0].target.id;
    for (const link of tocLinks) {
      if (link.hash === `#${id}`) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    }
  }, { rootMargin: '-12% 0px -60% 0px' });
  for (const link of tocLinks) {
    const section = document.getElementById(link.hash.slice(1));
    if (section) observer.observe(section);
  }
}
