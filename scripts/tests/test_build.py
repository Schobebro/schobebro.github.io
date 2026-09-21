"""Release-boundary tests: drafts, legal config, escaping and public allowlist."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from urllib.parse import urlparse

SPEC = importlib.util.spec_from_file_location("site_build", Path(__file__).parents[1] / "build.py")
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class SiteBuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.app = self.root / "apps/uebergabe"
        shutil.copytree(builder.ROOT / "apps/uebergabe", self.app)
        shutil.copyfile(self.app / "config.example.json", self.app / "config.json")
        self.manifest(status="draft")
        shutil.copytree(builder.ROOT / "root", self.root / "root")

    def manifest(self, **changes):
        path = self.app / "app.json"
        value = json.loads(path.read_text())
        value.update(changes)
        path.write_text(json.dumps(value))

    def valid_config(self):
        config = {field: "Vollständige öffentliche Angabe" for field in builder.FIELDS.values()}
        config.update({
            "publisherName": 'Muster & Partner <Büro> "Nord"',
            "copyrightHolder": "Muster & Partner",
            "publisherPostalAddress": "Musterstraße 5, 10115 Berlin",
            "supportEmail": "support@schobebro.de",
            "secondarySupportEmail": "team@schobebro.de",
            "lastUpdated": "2026-09-20",
            "publicLegalDetails": None,
            "appStoreURL": None,
        })
        (self.app / "config.json").write_text(json.dumps(config))
        return config

    def test_draft_mounts_full_website_and_marks_unfinished_legal_pages(self):
        output = builder.build(self.root)
        files = {str(path.relative_to(output / "uebergabe")) for path in (output / "uebergabe").rglob("*") if path.is_file()}
        self.assertEqual(files, set(builder.PAGES + builder.APP_FILES))
        for name in builder.PAGES:
            page = (output / "uebergabe" / name).read_text()
            self.assertIn('content="noindex,nofollow"', page)
            self.assertNotIn("nicht veröffentlicht", page)
            self.assertNotIn("[[", page)
            self.assertNotIn('href="mailto:', page)
            canonical = "https://schobebro.github.io/uebergabe/" + ("" if name == "index.html" else name)
            self.assertIn(f'rel="canonical" href="{canonical}"', page)
            if name != "index.html":
                self.assertIn('class="draft">Entwurf', page)
        landing = (output / "uebergabe/index.html").read_text()
        self.assertIn("Ausgeben.", landing)
        self.assertIn('src="assets/app-comparison.png"', landing)
        self.assertIn('href="privacy.html"', landing)
        self.assertNotIn('class="draft"', landing)
        self.assertNotIn("Noch offen:", landing)
        self.assertNotIn("Website in Vorbereitung", landing)
        self.assertFalse((output / "sitemap.xml").exists())
        self.assertNotIn("Sitemap:", (output / "robots.txt").read_text())
        self.assertIn("Noch offen: Anschrift", (output / "uebergabe/imprint.html").read_text())

    def test_root_is_only_redirect_without_shared_portal(self):
        unused_portal = self.root / "portal"
        unused_portal.mkdir()
        (unused_portal / "index.html").write_text("OLD SHARED PORTAL [[APP_CARDS]]")
        (self.root / "root/private.txt").write_text("NOT A PUBLIC FILE")
        output = builder.build(self.root)
        root_page = (output / "index.html").read_text()
        self.assertEqual(root_page, (self.root / "root/index.html").read_text())
        self.assertIn('http-equiv="refresh"', root_page)
        self.assertIn('href="uebergabe/"', root_page)
        self.assertNotIn("OLD SHARED PORTAL", root_page)
        self.assertNotIn("app-card", root_page)
        self.assertFalse((output / "styles.css").exists())
        self.assertFalse((output / "private.txt").exists())

    def test_partial_published_config_is_rejected_without_replacing_output(self):
        output = builder.build(self.root)
        previous = {path.relative_to(output): path.read_bytes() for path in output.rglob("*") if path.is_file()}
        self.manifest(status="published")
        with self.assertRaisesRegex(ValueError, "angaben fehlen"):
            builder.build(self.root)
        self.assertEqual({path.relative_to(output): path.read_bytes() for path in output.rglob("*") if path.is_file()}, previous)

    def test_published_config_renders_five_escaped_pages(self):
        self.manifest(status="published")
        self.valid_config()
        output = builder.build(self.root)
        for name in builder.PAGES:
            text = (output / "uebergabe" / name).read_text()
            self.assertNotIn("[[", text)
            self.assertNotIn("Noch offen:", text)
            self.assertNotIn("noindex", text)
            self.assertNotIn('class="draft"', text)
            canonical = "https://schobebro.github.io/uebergabe/" + ("" if name == "index.html" else name)
            self.assertIn(f'rel="canonical" href="{canonical}"', text)
        terms = (output / "uebergabe/terms.html").read_text()
        self.assertIn("Muster &amp; Partner &lt;Büro&gt; &quot;Nord&quot;", terms)
        self.assertNotIn("<Büro>", terms)
        self.assertIn("© 2026", terms)
        contact = (output / "uebergabe/imprint.html").read_text()
        self.assertIn('href="mailto:team@schobebro.de"', contact)
        self.assertEqual((output / "sitemap.xml").read_text().count("<url>"), 5)
        self.assertNotIn("<loc>https://schobebro.github.io/</loc>", (output / "sitemap.xml").read_text())

    def test_optional_second_contact_can_be_omitted_and_rejects_invalid_email(self):
        self.manifest(status="published")
        config = self.valid_config()
        config["secondarySupportEmail"] = None
        (self.app / "config.json").write_text(json.dumps(config))
        output = builder.build(self.root)
        self.assertNotIn('mailto:team@schobebro.de', (output / "uebergabe/imprint.html").read_text())
        config["secondarySupportEmail"] = "not-an-email"
        (self.app / "config.json").write_text(json.dumps(config))
        with self.assertRaisesRegex(ValueError, "secondarySupportEmail"):
            builder.build(self.root)

    def test_multiple_apps_keep_pages_assets_and_indexing_independent(self):
        second = self.root / "apps/zweite-app"
        shutil.copytree(self.app, second)
        manifest = json.loads((second / "app.json").read_text())
        (second / "app.json").write_text(json.dumps(manifest | {"slug": "zweite-app", "name": "Zweite App"}))
        self.manifest(status="published")
        self.valid_config()
        output = builder.build(self.root)
        for slug, indexed in (("uebergabe", True), ("zweite-app", False)):
            for name in builder.PAGES:
                page_path = output / slug / name
                page = page_path.read_text()
                canonical = f"{builder.BASE_URL}{slug}/" + ("" if name == "index.html" else name)
                self.assertIn(f'rel="canonical" href="{canonical}"', page)
                self.assertEqual("noindex,nofollow" in page, not indexed)
                links = builder.Links()
                links.feed(page)
                for link in links.links:
                    parsed = urlparse(link)
                    if not parsed.scheme:
                        target = (page_path.parent / parsed.path).resolve()
                        self.assertTrue(target.is_relative_to(output / slug), link)
            for name in builder.APP_FILES:
                self.assertTrue((output / slug / name).is_file())
        sitemap = (output / "sitemap.xml").read_text()
        self.assertNotIn("zweite-app", sitemap)
        self.assertEqual(sitemap.count("<url>"), 5)
        self.assertIn("Sitemap: https://schobebro.github.io/sitemap.xml", (output / "robots.txt").read_text())

    def test_preview_includes_full_draft_with_disabled_missing_email(self):
        output = builder.build(self.root, preview=True)
        for name in builder.PAGES:
            text = (output / "uebergabe" / name).read_text()
            self.assertIn("noindex,nofollow", text)
            self.assertIn('class="draft"', text)
            self.assertNotIn("nicht veröffentlicht", text)
            self.assertNotIn('href="mailto:Noch offen', text)
        self.assertIn("noindex", (output / "index.html").read_text())
        self.assertEqual((output / "robots.txt").read_text(), "User-agent: *\nDisallow: /\n")

    def test_path_traversal_slug_is_rejected(self):
        for slug in ("../outside", "uebergabe/../../outside", "/absolute", "different-folder"):
            with self.subTest(slug=slug):
                self.manifest(slug=slug)
                with self.assertRaisesRegex(ValueError, "slug"):
                    builder.build(self.root)

    def test_only_allowlisted_public_files_are_copied(self):
        self.manifest(status="published")
        self.valid_config()
        for file in (self.app / "private-user.json", self.app / "site/.env", self.app / "site/README.md", self.app / "site/assets/device-backup.json"):
            file.write_text("private source marker")
        output = builder.build(self.root)
        contents = {str(path.relative_to(output)) for path in output.rglob("*") if path.is_file()}
        allowed = {"index.html", ".nojekyll", "robots.txt", "sitemap.xml"}
        allowed.update("uebergabe/" + name for name in builder.PAGES + builder.APP_FILES)
        self.assertEqual(contents, allowed)

    def test_source_symlink_is_rejected(self):
        target = self.app / "site/favicon.png"
        target.unlink()
        target.symlink_to(self.app / "config.json")
        with self.assertRaisesRegex(ValueError, "Link"):
            builder.build(self.root)

    def test_unexpected_config_and_placeholder_email_are_rejected(self):
        config = self.valid_config()
        for change in ({"websiteURL": "https://wrong.de/"}, {"supportEmail": "support@example.com"}):
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    builder.validate_config(config | change)


if __name__ == "__main__":
    unittest.main()
