#!/usr/bin/env python3
"""Build the public multi-app website with no third-party dependencies.

Only allowlisted website files enter build/site. Draft apps expose one truthful
holding page. Full legal/support pages require an explicitly published manifest
and validated public operator details. --preview is local-only and noindex.
"""
import argparse
from datetime import date
import html
from html.parser import HTMLParser
import ipaddress
import json
from pathlib import Path
import re
import shutil
import tempfile
from urllib.parse import unquote, urljoin, urlparse

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://schobebro.github.io/"
PAGES = ("index.html", "support.html", "privacy.html", "terms.html", "imprint.html")
APP_FILES = ("styles.css", "script.js", "favicon.svg", ".nojekyll", "assets/app-comparison.png")
PORTAL_FILES = ("styles.css", "script.js", "favicon.svg")
PLACEHOLDER = re.compile(r"\[\[[A-Z_]+\]\]")
FIELDS = {
    "PUBLISHER_NAME": "publisherName",
    "COPYRIGHT_HOLDER": "copyrightHolder",
    "PUBLISHER_POSTAL_ADDRESS": "publisherPostalAddress",
    "PUBLIC_SUPPORT_EMAIL": "supportEmail",
    "PUBLIC_LEGAL_DETAILS": "publicLegalDetails",
    "LAST_UPDATED": "lastUpdated",
    "SUPPORT_MAIL_PROVIDER": "supportMailProvider",
    "SUPPORT_RETENTION_POLICY": "supportRetentionPolicy",
    "SUPPORT_PRIVACY_DETAILS": "supportPrivacyDetails",
    "WEBSITE_PRIVACY_BASIS": "websitePrivacyBasis",
    "APPLICABLE_PRIVACY_RIGHTS_AND_SUPERVISORY_AUTHORITY": "applicablePrivacyRightsAndSupervisoryAuthority",
}
OPTIONAL = {"publicLegalDetails"}
DRAFT = '<p class="draft">Vorschau · Anbieter- und Kontaktangaben sind noch nicht vollständig. Diese Fassung ist nicht veröffentlicht.</p>'
FIELD_LABELS = {
    "publisherName": "Name des Anbieters",
    "copyrightHolder": "Name des Anbieters",
    "publisherPostalAddress": "Anschrift",
    "supportEmail": "Kontakt-E-Mail",
    "supportMailProvider": "E-Mail-Dienst",
    "supportRetentionPolicy": "Aufbewahrung und Löschung",
    "supportPrivacyDetails": "Datenschutzhinweise zum Support",
    "websitePrivacyBasis": "Zweck und Rechtsgrundlage der Website",
    "applicablePrivacyRightsAndSupervisoryAuthority": "Datenschutzrechte und Aufsichtsbehörde",
}


def effective_config(config):
    if not isinstance(config, dict):
        raise ValueError("Konfiguration muss ein JSON-Objekt sein")
    allowed = set(FIELDS.values()) | {"appStoreURL"}
    unknown = set(config) - allowed
    if unknown:
        raise ValueError("Unbekannte Konfigurationsfelder: " + ", ".join(sorted(unknown)))
    result = dict(config)
    for key in allowed:
        if result.get(key) is not None and not isinstance(result[key], str):
            raise ValueError(f"{key}: Text oder null erwartet")
    if not result.get("copyrightHolder"):
        result["copyrightHolder"] = result.get("publisherName")
    return result

def is_placeholder(value):
    if not isinstance(value, str) or not value.strip():
        return True
    folded = value.strip().casefold()
    return bool(PLACEHOLDER.search(value) or re.search(r"\b(todo|tbd|placeholder|platzhalter|eintragen|ergänzen|changeme)\b", folded) or folded in {"null", "none", "unknown", "unbekannt", "xxx"})


def public_https(value, field):
    if is_placeholder(value):
        raise ValueError(f"{field}: echte öffentliche HTTPS-Adresse fehlt")
    if any(character.isspace() for character in value):
        raise ValueError(f"{field}: Leerzeichen sind in der Adresse nicht zulässig")
    parsed = urlparse(value)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not host or parsed.username or parsed.password or parsed.fragment or parsed.query:
        raise ValueError(f"{field}: öffentliche HTTPS-Adresse ohne Zugangsdaten, Query oder Fragment erwartet")
    if host in {"localhost", "example.com", "example.org", "example.net"} or host.endswith((".localhost", ".local", ".test", ".invalid", ".example", ".example.com", ".example.org", ".example.net")):
        raise ValueError(f"{field}: Platzhalter oder lokale Adresse ist nicht veröffentlichbar")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        labels = host.rstrip(".").split(".")
        if len(labels) < 2 or all(label.isdigit() for label in labels) or any(not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", label) for label in labels):
            raise ValueError(f"{field}: gültige öffentliche Domain erwartet")
    else:
        if not address.is_global:
            raise ValueError(f"{field}: private IP-Adresse ist nicht öffentlich")
    return value


def validate_config(config):
    config = effective_config(config)
    required = set(FIELDS.values()) - OPTIONAL
    missing = sorted(key for key in required if is_placeholder(config.get(key)))
    if missing:
        raise ValueError("Herausgeber-/Datenschutzangaben fehlen: " + ", ".join(missing))
    email = config["supportEmail"].strip()
    if not re.fullmatch(r'[^\s@<>:?&#"]+@[^\s@<>]+\.[^\s@<>]+', email):
        raise ValueError("supportEmail: gültige öffentliche Kontakt-E-Mail fehlt")
    public_https("https://" + email.split("@", 1)[1], "supportEmail")
    for key in OPTIONAL:
        extra = config.get(key)
        if extra is not None and is_placeholder(extra):
            raise ValueError(f"{key}: echte Angaben oder null verwenden")
    try:
        date.fromisoformat(config["lastUpdated"])
    except (ValueError, TypeError):
        raise ValueError("lastUpdated: Datum im Format JJJJ-MM-TT erwartet")
    if config.get("appStoreURL"):
        store_url = public_https(config["appStoreURL"], "appStoreURL")
        if urlparse(store_url).hostname != "apps.apple.com":
            raise ValueError("appStoreURL muss auf apps.apple.com zeigen")
    return config


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.identifiers = set()

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in {"href", "src"} and value:
                self.links.append(value)
            if key == "id" and value:
                self.identifiers.add(value)


def render_page(content, config, preview):
    for key in OPTIONAL:
        if not config.get(key):
            content = re.sub(r'<section\b[^>]*data-optional="' + re.escape(key) + r'"[^>]*>.*?</section>', "", content, flags=re.S)
    if preview:
        # A missing contact address must never become a clickable fake email.
        if is_placeholder(config.get("supportEmail")):
            content = re.sub(r'<a\b([^>]*?)href="mailto:\[\[PUBLIC_SUPPORT_EMAIL\]\]"([^>]*)>(.*?)</a>',
                             r'<span\1 aria-disabled="true"\2>\3</span>', content, flags=re.S)
    for token, key in FIELDS.items():
        value = config.get(key)
        if key in OPTIONAL:
            value = value or ""
        elif is_placeholder(value):
            value = "Noch offen: " + FIELD_LABELS.get(key, key)
        elif key == "lastUpdated":
            parsed_date = date.fromisoformat(value)
            value = parsed_date.strftime("%d.%m.%Y")
        content = content.replace(f"[[{token}]]", html.escape(value, quote=True))
    content = re.sub(r'<p class="draft">.*?</p>', "", content, flags=re.S)
    if preview:
        content = content.replace("<main", DRAFT + "\n<main", 1)
        content = re.sub(r'<meta name="robots" content="[^"]*">', '<meta name="robots" content="noindex,nofollow">', content)
        if '<meta name="robots"' not in content:
            content = content.replace("</head>", '<meta name="robots" content="noindex,nofollow"></head>')
    else:
        content = content.replace('<meta name="robots" content="noindex,nofollow">', '<meta name="robots" content="index,follow">')
        content = content.replace('class="placeholder"', 'class="configured"')
    return content


def read_json(path):
    if path.is_symlink():
        raise ValueError(f"Symbolische Links sind nicht erlaubt: {path.name}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"{path.name}: ungültiges JSON") from error


def load_apps(root):
    apps = []
    for directory in sorted((root / "apps").iterdir()):
        if directory.name.startswith("."):
            continue
        if directory.is_symlink() or not directory.is_dir():
            raise ValueError(f"App muss ein echtes Verzeichnis sein: {directory.name}")
        manifest = read_json(directory / "app.json")
        if not isinstance(manifest, dict) or set(manifest) != {"slug", "name", "description", "status"}:
            raise ValueError(f"{directory.name}: Manifest benötigt slug, name, description und status")
        slug = manifest["slug"]
        if not isinstance(slug, str) or not re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", slug) or slug != directory.name:
            raise ValueError(f"{directory.name}: slug muss ein sicherer Pfad sein und dem Ordnernamen entsprechen")
        if slug in {"assets", "build", "scripts", "apps", "portal"}:
            raise ValueError(f"{slug}: reservierter Pfad")
        if manifest["status"] not in {"draft", "published"}:
            raise ValueError(f"{slug}: status muss draft oder published sein")
        for field in ("name", "description"):
            if not isinstance(manifest[field], str) or not manifest[field].strip():
                raise ValueError(f"{slug}: {field} muss Text enthalten")
        apps.append((directory, manifest))
    return apps


def copy_public_file(source, destination):
    if source.is_symlink() or not source.is_file() or any(parent.is_symlink() for parent in source.parents):
        raise ValueError(f"Öffentliche Quelldatei fehlt oder ist ein Link: {source.name}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def cards_html(apps, preview):
    cards = []
    for _, manifest in apps:
        name = html.escape(manifest["name"])
        description = html.escape(manifest["description"])
        status = "Vorschau" if preview else ("Veröffentlicht" if manifest["status"] == "published" else "In Vorbereitung")
        cards.append(f'<a class="app-card" href="{manifest["slug"]}/"><span class="app-status">{status}</span>'
                     f'<h2>{name}</h2><p>{description}</p><span class="app-link">Website ansehen →</span></a>')
    return "\n".join(cards)


def holding_page(manifest):
    name = html.escape(manifest["name"])
    description = html.escape(manifest["description"])
    return f'''<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,follow"><meta name="theme-color" content="#153e32">
<title>{name} · Website in Vorbereitung</title><link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="styles.css"></head><body><div class="shell">
<header class="site-header"><a class="wordmark" href="../">Schobebro<span>.</span></a></header>
<main id="inhalt"><section class="document-heading"><p class="eyebrow">Website in Vorbereitung</p>
<h1>{name}</h1><p class="lede">{description}</p><p>Die öffentlichen Informationen zu dieser App werden noch vorbereitet.</p>
<a class="back-link" href="../">← Alle Apps</a></section></main></div></body></html>
'''


def validate_tree(directory, preview=False):
    """Catch unresolved tokens and broken local links across all deployed pages."""
    pages = {}
    for page in directory.rglob("*.html"):
        content = page.read_text(encoding="utf-8")
        if PLACEHOLDER.search(content):
            raise ValueError(f"{page.name}: ungelöste Template-Tokens")
        if preview and "noindex" not in content:
            raise ValueError(f"{page.name}: Vorschau muss noindex enthalten")
        parser = Links()
        parser.feed(content)
        pages[page.resolve()] = parser
    for page, parser in pages.items():
        for link in parser.links:
            if link.startswith("https://"):
                parsed = urlparse(link)
                public_https(parsed._replace(fragment="", query="").geturl(), f"{page.name} Link")
                continue
            if link.startswith(("mailto:", "tel:")):
                if not link.split(":", 1)[1].strip():
                    raise ValueError(f"{page.name}: leerer Kontaktlink")
                continue
            parsed = urlparse(link)
            if parsed.scheme or parsed.netloc or parsed.path.startswith("/"):
                raise ValueError(f"{page.name}: nur HTTPS- oder relative Links erlaubt: {link}")
            target = (page.parent / unquote(parsed.path)).resolve() if parsed.path else page.resolve()
            if target.is_dir():
                target = target / "index.html"
            if not target.is_relative_to(directory.resolve()) or not target.is_file():
                raise ValueError(f"{page.name}: fehlender oder unsicherer lokaler Link {link}")
            if parsed.fragment and target.suffix == ".html":
                target_parser = pages.get(target)
                if target_parser is None or unquote(parsed.fragment) not in target_parser.identifiers:
                    raise ValueError(f"{page.name}: unbekannter Seitenanker {link}")


def build(root=ROOT, preview=False):
    root = Path(root).resolve()
    apps = load_apps(root)
    output = root / "build" / ("preview" if preview else "site")
    if output.is_symlink() or output.parent.is_symlink():
        raise ValueError("Ausgabeziel darf kein symbolischer Link sein")
    output.parent.mkdir(parents=True, exist_ok=True)
    urls = [BASE_URL]
    with tempfile.TemporaryDirectory(prefix="site-", dir=output.parent) as temp:
        staging = Path(temp) / "site"
        staging.mkdir()
        portal = root / "portal"
        portal_index = portal / "index.html"
        if portal_index.is_symlink():
            raise ValueError("Portal darf kein symbolischer Link sein")
        content = portal_index.read_text(encoding="utf-8")
        if content.count("[[APP_CARDS]]") != 1:
            raise ValueError("portal/index.html muss genau ein [[APP_CARDS]] enthalten")
        content = content.replace("[[APP_CARDS]]", cards_html(apps, preview))
        if preview:
            content = re.sub(r'<meta name="robots" content="[^"]*">', "", content)
            content = content.replace("</head>", '<meta name="robots" content="noindex,nofollow"></head>')
        (staging / "index.html").write_text(content, encoding="utf-8")
        for name in PORTAL_FILES:
            if (portal / name).exists():
                copy_public_file(portal / name, staging / name)
        for directory, manifest in apps:
            slug = manifest["slug"]
            destination = staging / slug
            destination.mkdir()
            source = directory / "site"
            if source.is_symlink():
                raise ValueError(f"{slug}: Website darf kein symbolischer Link sein")
            if not preview and manifest["status"] == "draft":
                (destination / "index.html").write_text(holding_page(manifest), encoding="utf-8")
                for name in ("styles.css", "favicon.svg"):
                    copy_public_file(source / name, destination / name)
                continue
            config = effective_config(read_json(directory / "config.json"))
            if not preview:
                validate_config(config)
            for name in APP_FILES:
                copy_public_file(source / name, destination / name)
            for name in PAGES:
                page = source / name
                if page.is_symlink():
                    raise ValueError(f"{slug}/{name}: symbolische Links sind nicht erlaubt")
                content = render_page(page.read_text(encoding="utf-8"), config, preview)
                if not preview:
                    if any(marker in content for marker in ('class="draft"', "noindex", 'class="placeholder"', "Noch offen:")):
                        raise ValueError(f"{slug}/{name}: Entwurf oder Platzhalter darf nicht veröffentlicht werden")
                    canonical = urljoin(BASE_URL, slug + "/" + ("" if name == "index.html" else name))
                    content = content.replace("</head>", f'<link rel="canonical" href="{html.escape(canonical, quote=True)}"></head>')
                    urls.append(canonical)
                (destination / name).write_text(content, encoding="utf-8")
        (staging / ".nojekyll").touch()
        robots = "User-agent: *\nDisallow: /\n" if preview else f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}sitemap.xml\n"
        (staging / "robots.txt").write_text(robots, encoding="utf-8")
        if not preview:
            entries = "".join(f"<url><loc>{html.escape(url)}</loc></url>" for url in urls)
            (staging / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + entries + "</urlset>\n", encoding="utf-8")
        validate_tree(staging, preview)
        if output.exists():
            shutil.rmtree(output)
        shutil.move(str(staging), str(output))
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", action="store_true", help="Alle Seiten als lokale noindex-Vorschau bauen")
    args = parser.parse_args()
    try:
        output = build(preview=args.preview)
    except (ValueError, OSError) as error:
        parser.exit(1, f"Build abgebrochen: {error}\n")
    print(f"{'Vorschau' if args.preview else 'Website'} gebaut: {output}")


if __name__ == "__main__":
    main()
