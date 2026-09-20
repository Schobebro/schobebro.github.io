# Schobebro · App-Websites

Öffentliche Websites, Hilfe und rechtliche Informationen für die Apps von Schobebro. Eine gemeinsame GitHub-Pages-Website, ein Verzeichnis pro App. **Dieses Repository enthält ausschließlich Website-Dateien; App-Quellcode bleibt in den jeweiligen privaten Repositories.**

- **Startseite:** https://schobebro.github.io/
- **Übergabe:** https://schobebro.github.io/uebergabe/

## Aufbau

```text
portal/                    Gemeinsame Startseite, Styles und Icon
apps/
  uebergabe/
    app.json               Name, Beschreibung, URL-Pfad und Veröffentlichungsstatus
    config.json            Ausschließlich öffentliche Betreiberangaben
    config.example.json    Vorlage der erforderlichen Angaben
    site/                  HTML, CSS, JS und öffentlich freigegebene Bilder
scripts/
  build.py                 Gemeinsamer Builder, nur Python-Standardbibliothek
  tests/                   Prüfungen der Veröffentlichung und Dateiauswahl
.github/workflows/pages.yml
```

Die Website benötigt keinen Webserver mit eigener Anwendungslogik, kein Framework, keine Node-Abhängigkeiten und keine Zugangsdaten. Der Browser lädt keine externen Schriften oder Analyse-Skripte. Das Hosting selbst unterliegt den [Datenschutzhinweisen von GitHub](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement).

## Lokal ansehen

Voraussetzung: Python 3.10 oder neuer.

```sh
python3 -m unittest discover -s scripts/tests -v
python3 scripts/build.py
python3 -m http.server 4180 --bind 127.0.0.1 --directory build/site
```

Unter http://127.0.0.1:4180/ siehst du genau die Dateien, die veröffentlicht werden. Für die vollständigen Entwürfe:

```sh
python3 scripts/build.py --preview
python3 -m http.server 4181 --bind 127.0.0.1 --directory build/preview
```

Die Vorschau unter http://127.0.0.1:4181/ enthält auch unfertige Rechtsseiten. Diese sind sichtbar als Entwurf und mit `noindex` markiert. Die Vorschau ist ein lokales/CI-Prüfartefakt und wird **nicht** auf GitHub Pages veröffentlicht.

## Aktueller Stand: Übergabe

`apps/uebergabe/app.json` steht auf `"status": "draft"`. Der öffentliche Build enthält dort eine kurze Vorbereitungsseite. Die vollständigen fünf Seiten — Start, Support, Datenschutz, Nutzungsbedingungen und Impressum — sind im Quellverzeichnis und in der Vorschau vorbereitet.

Für die Veröffentlichung der vollständigen Website fehlen die tatsächlichen Betreiber- und Datenschutzangaben in `apps/uebergabe/config.json`:

| Feld | Öffentlich angezeigter Inhalt |
| --- | --- |
| `publisherName` | Rechtlich verantwortlicher Anbieter |
| `publisherPostalAddress` | Vollständige öffentliche Anschrift |
| `supportEmail` | Öffentliche Kontakt-E-Mail |
| `supportMailProvider` | Tatsächlich verwendeter E-Mail-Dienst |
| `supportRetentionPolicy` | Aufbewahrung und Löschung von Support-Anfragen |
| `supportPrivacyDetails` | Anwendbare Rechtsgrundlage, Empfänger und Übermittlungen beim Support |
| `websitePrivacyBasis` | Zweck und anwendbare Rechtsgrundlage der Website-Verarbeitung |
| `applicablePrivacyRightsAndSupervisoryAuthority` | Anwendbare Datenschutzrechte und zuständige Aufsicht |
| `publicLegalDetails` | Weitere erforderliche Register-/Vertretungs-/Steuerangaben, sonst `null` |
| `copyrightHolder` | Optional abweichender Rechteinhaber, sonst Anbietername |
| `lastUpdated` | Datum der aktuellen Texte, `JJJJ-MM-TT` |
| `appStoreURL` | Optional für spätere App-Store-Verlinkung; aktuell kein Download-Button |

**Alle committed Dateien, einschließlich der Konfiguration, sind öffentlich.** Keine Zugangsdaten, Apple-Schlüssel, internen Review-Kontakte, Kundendaten oder privaten App-Sammlungen eintragen.

Erst wenn die Angaben und Texte zu Anbieter, App und Betrieb passen, `status` auf `published` setzen. `python3 scripts/build.py` prüft Vollständigkeit, Platzhalter, öffentliche Adressen, interne Dateien und Anker. HTML-Werte werden sicher escaped. Diese technische Prüfung ersetzt keine Prüfung der tatsächlichen Angaben und anwendbaren rechtlichen Anforderungen.

Danach entstehen die App-Store-Adressen:

- Support: https://schobebro.github.io/uebergabe/support.html
- Datenschutz: https://schobebro.github.io/uebergabe/privacy.html
- Nutzungsbedingungen: https://schobebro.github.io/uebergabe/terms.html
- Impressum: https://schobebro.github.io/uebergabe/imprint.html

Solange der Status `draft` ist, werden diese vier Seiten absichtlich nicht ausgeliefert. Sie sind noch keine verwendbaren App-Store-URLs.

## Weitere App hinzufügen

1. `apps/uebergabe/` als Ausgangspunkt nach `apps/meine-app/` kopieren.
2. In `app.json` `slug` auf `meine-app` setzen und Name/Beschreibung anpassen. `status` zunächst `draft` lassen. Der Slug muss dem Ordnernamen entsprechen; nur Kleinbuchstaben, Ziffern und Bindestriche sind erlaubt.
3. In `config.json` die öffentlichen Angaben passend zur App ergänzen. Die URLs leitet der Builder automatisch aus dem Slug ab.
4. Alle fünf HTML-Seiten, Bilder, Favicon und Rechtstexte tatsächlich auf die neue App anpassen. Insbesondere sind Angaben zu Datenspeicherung, Berechtigungen und Drittanbietern app-spezifisch.
5. Beide Builds prüfen und die Vorschau auf Desktop und Mobilgerät ansehen. Für zusätzliche Assets die explizite Dateiliste `APP_FILES` in `scripts/build.py` erweitern.
6. Sobald die vollständige Website bereit ist, `status` auf `published` setzen und auf `main` committen. Die Startseite erhält die App-Kachel automatisch; die Website liegt unter `/meine-app/`.

Es gibt bewusst keine zweite Liste von App-Links, die parallel gepflegt werden müsste. Alle relativen Links innerhalb einer App funktionieren unter ihrem Unterverzeichnis.

## GitHub Pages

Repository: **Schobebro/schobebro.github.io**. In **Settings → Pages** ist **GitHub Actions** die Veröffentlichungsquelle. Weil das Repository nach der Organisation benannt ist, liegt die gemeinsame Startseite direkt unter `https://schobebro.github.io/`.

Der Workflow **Websites · GitHub Pages**:

- prüft Tests und beide Builds bei jedem Push und Pull Request;
- stellt eine vollständige Vorschau für sieben Tage als Actions-Artefakt bereit;
- veröffentlicht bei Änderungen auf `main` oder manuellem Start auf `main` ausschließlich `build/site`;
- stoppt die Veröffentlichung, wenn eine als `published` markierte App unvollständige Angaben oder kaputte interne Links hat;
- kopiert nur ausdrücklich freigegebene Dateien, keine Konfigurationen, Skripte oder Quell-Dokumentation in den Website-Build;
- verwendet offizielle GitHub-Actions mit festgelegten Commit-SHAs und benötigt keine eigenen Secrets.

Pull Requests veröffentlichen nichts. Der Deploy-Job hat nur die zusätzlichen Rechte `pages: write` und `id-token: write`; der übrige Workflow liest lediglich Repository-Inhalte. Fehlgeschlagene Builds ersetzen die bisher veröffentlichte Website nicht.

[GitHub Pages: Websites für Organisationen](https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages) · [Eigene Pages-Workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
