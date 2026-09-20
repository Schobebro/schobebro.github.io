#!/usr/bin/env python3
"""Build independent app websites with no third-party dependencies.

Only allowlisted website files enter build/site. Every app has its own complete
website. Draft legal/support pages identify incomplete information; all draft
pages stay noindex. Published apps require validated public operator details.
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
PLACEHOLDER = re.compile(r"\[\[[A-Z_]+\]\]")
FIELDS = {
    "PUBLISHER_NAME": "publisherName",
    "COPYRIGHT_HOLDER": "copyrightHolder",
    "PUBLISHER_POSTAL_ADDRESS": "publisherPostalAddress",
    "PUBLIC_SUPPORT_EMAIL": "supportEmail",
    "SECONDARY_SUPPORT_EMAIL": "secondarySupportEmail",
    "PUBLIC_LEGAL_DETAILS": "publicLegalDetails",
    "LAST_UPDATED": "lastUpdated",
    "SUPPORT_MAIL_PROVIDER": "supportMailProvider",
    "SUPPORT_RETENTION_POLICY": "supportRetentionPolicy",
    "SUPPORT_PRIVACY_DETAILS": "supportPrivacyDetails",
    "WEBSITE_PRIVACY_BASIS": "websitePrivacyBasis",
    "APPLICABLE_PRIVACY_RIGHTS_AND_SUPERVISORY_AUTHORITY": "applicablePrivacyRightsAndSupervisoryAuthority",
}
OPTIONAL = {"publicLegalDetails", "secondarySupportEmail"}
DRAFT = '<p class="draft">Entwurf · Diese Informationen werden noch vervollständigt. Offene Angaben sind gekennzeichnet.</p>'
PREVIEW = '<p class="draft">Vorschau · Diese Ansicht dient zur Prüfung. Offene Angaben sind gekennzeichnet.</p>'
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
    for field in ("supportEmail", "secondarySupportEmail"):
        if field == "secondarySupportEmail" and not config.get(field):
            continue
        email = config[field].strip()
        if not re.fullmatch(r'[^\s@<>:?&#"]+@[^\s@<>]+\.[^\s@<>]+', email):
            raise ValueError(f"{field}: gültige öffentliche Kontakt-E-Mail fehlt")
        public_https("https://" + email.split("@", 1)[1], field)
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


def render_page(content, config, *, preview=False, draft=False, page_name="index.html"):
    for key in OPTIONAL:
        if not config.get(key):
            content = re.sub(r'<section\b[^>]*data-optional="' + re.escape(key) + r'"[^>]*>.*?</section>', "", content, flags=re.S)
    # A missing contact address must never become a clickable fake email,
    # including on publicly accessible draft pages.
    if is_placeholder(config.get("supportEmail")):
        content = re.sub(r'<a\b([^>]*?)href="mailto:\[\[PUBLIC_SUPPORT_EMAIL\]\]"([^>]*)>(.*?)</a>',
                         r'<span\1 aria-disabled="true"\2>\3</span>', content, flags=re.S)
    if is_placeholder(config.get("copyrightHolder")):
        content = re.sub(r'<p>©\s+\d{4}\s+<span class="placeholder">\[\[COPYRIGHT_HOLDER\]\]</span></p>', "", content)
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
        content = content.replace("<main", PREVIEW + "\n<main", 1)
    elif draft and page_name != "index.html":
        content = content.replace("<main", DRAFT + "\n<main", 1)
    if preview or draft:
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
    urls = []
    with tempfile.TemporaryDirectory(prefix="site-", dir=output.parent) as temp:
        staging = Path(temp) / "site"
        staging.mkdir()
        copy_public_file(root / "root/index.html", staging / "index.html")
        if preview:
            content = (staging / "index.html").read_text(encoding="utf-8")
            content = re.sub(r'<meta name="robots" content="[^"]*">', "", content)
            content = content.replace("</head>", '<meta name="robots" content="noindex,nofollow"></head>')
            (staging / "index.html").write_text(content, encoding="utf-8")
        for directory, manifest in apps:
            slug = manifest["slug"]
            destination = staging / slug
            destination.mkdir()
            source = directory / "site"
            if source.is_symlink():
                raise ValueError(f"{slug}: Website darf kein symbolischer Link sein")
            draft = manifest["status"] == "draft"
            config = effective_config(read_json(directory / "config.json"))
            if not preview and not draft:
                validate_config(config)
            for name in APP_FILES:
                copy_public_file(source / name, destination / name)
            for name in PAGES:
                page = source / name
                if page.is_symlink():
                    raise ValueError(f"{slug}/{name}: symbolische Links sind nicht erlaubt")
                content = render_page(page.read_text(encoding="utf-8"), config, preview=preview, draft=draft, page_name=name)
                if not preview:
                    if not draft and any(marker in content for marker in ('class="draft"', "noindex", 'class="placeholder"', "Noch offen:")):
                        raise ValueError(f"{slug}/{name}: Entwurf oder Platzhalter darf nicht veröffentlicht werden")
                    canonical = urljoin(BASE_URL, slug + "/" + ("" if name == "index.html" else name))
                    content = content.replace("</head>", f'<link rel="canonical" href="{html.escape(canonical, quote=True)}"></head>')
                    if not draft:
                        urls.append(canonical)
                (destination / name).write_text(content, encoding="utf-8")
        (staging / ".nojekyll").touch()
        robots = "User-agent: *\nDisallow: /\n" if preview else "User-agent: *\nAllow: /\n"
        if not preview and urls:
            robots += f"Sitemap: {BASE_URL}sitemap.xml\n"
        (staging / "robots.txt").write_text(robots, encoding="utf-8")
        if not preview and urls:
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
