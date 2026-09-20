"""Release-boundary tests: drafts, legal config, escaping and public allowlist."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

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
        portal = self.root / "portal"
        portal.mkdir()
        (portal / "index.html").write_text('<!doctype html><html lang="de"><head><title>Apps</title></head><body><main>[[APP_CARDS]]</main></body></html>')

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
            "lastUpdated": "2026-09-20",
            "publicLegalDetails": None,
            "appStoreURL": None,
        })
        (self.app / "config.json").write_text(json.dumps(config))
        return config

    def test_draft_never_deploys_unfinished_legal_pages(self):
        output = builder.build(self.root)
        files = {str(path.relative_to(output / "uebergabe")) for path in (output / "uebergabe").rglob("*") if path.is_file()}
        self.assertEqual(files, {"index.html", "styles.css", "favicon.svg"})
        landing = (output / "uebergabe/index.html").read_text()
        self.assertIn("Website in Vorbereitung", landing)
        self.assertNotIn("privacy.html", landing)
        self.assertNotIn("privacy.html", (output / "sitemap.xml").read_text())

    def test_partial_published_config_is_rejected_without_replacing_output(self):
        output = builder.build(self.root)
        previous = (output / "uebergabe/index.html").read_text()
        self.manifest(status="published")
        with self.assertRaisesRegex(ValueError, "angaben fehlen"):
            builder.build(self.root)
        self.assertEqual((output / "uebergabe/index.html").read_text(), previous)

    def test_published_config_renders_five_escaped_pages(self):
        self.manifest(status="published")
        self.valid_config()
        output = builder.build(self.root)
        for name in builder.PAGES:
            text = (output / "uebergabe" / name).read_text()
            self.assertNotIn("[[", text)
            self.assertNotIn("Noch offen:", text)
            self.assertNotIn("noindex", text)
            canonical = "https://schobebro.github.io/uebergabe/" + ("" if name == "index.html" else name)
            self.assertIn(f'rel="canonical" href="{canonical}"', text)
        privacy = (output / "uebergabe/privacy.html").read_text()
        self.assertIn("Muster &amp; Partner &lt;Büro&gt; &quot;Nord&quot;", privacy)
        self.assertNotIn("<Büro>", privacy)

    def test_preview_includes_full_draft_with_disabled_missing_email(self):
        output = builder.build(self.root, preview=True)
        for name in builder.PAGES:
            text = (output / "uebergabe" / name).read_text()
            self.assertIn("noindex,nofollow", text)
            self.assertIn('class="draft"', text)
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
        target = self.app / "site/favicon.svg"
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
