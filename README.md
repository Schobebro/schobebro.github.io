# Schobebro · App-Websites

Ein gemeinsames Repository für eigenständige App-Websites. Jede App hat ihre eigene Startseite, Gestaltung, Navigation, Hilfe und Rechtstexte unter einem eigenen URL-Pfad. Es gibt keine gemeinsame App-Übersicht. **Dieses Repository enthält ausschließlich Website-Dateien; App-Quellcode bleibt in den jeweiligen privaten Repositories.**

- **Übergabe-Website:** https://schobebro.github.io/uebergabe/
- **Doppelpfad-Website:** https://schobebro.github.io/doppelpfad/
- `https://schobebro.github.io/` leitet direkt zu Übergabe weiter.
- Weitere Websites werden unabhängig unter `/app-name/` ergänzt.

## Aufbau

```text
root/index.html            Weiterleitung zu Übergabe, keine gemeinsame Website
apps/
  doppelpfad/              Eigenständige Website für das Offline-Rätselspiel
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

Unter http://127.0.0.1:4180/uebergabe/ und http://127.0.0.1:4180/doppelpfad/ siehst du die eigenständigen App-Websites. Für die ausdrücklich markierte lokale Vorschau:

```sh
python3 scripts/build.py --preview
python3 -m http.server 4181 --bind 127.0.0.1 --directory build/preview
```

Die lokale Vorschau unter http://127.0.0.1:4181/uebergabe/ markiert alle Seiten als Vorschau. Der reguläre Build enthält ebenfalls alle fünf Seiten. Solange die Betreiberangaben noch unvollständig sind, bleiben Kontakt- und Rechtsseiten sichtbar als Entwurf gekennzeichnet und die gesamte App-Website trägt `noindex`. Die lokale Vorschau ist ein separates CI-Prüfartefakt.

## Aktueller Stand: Übergabe

`apps/uebergabe/app.json` steht auf `"status": "published"`. Die vollständige Website mit Start, Support, Datenschutz, Nutzungsbedingungen und Impressum enthält die angegebenen Betreiberanschriften und beide Kontaktadressen. Gemeinsame Verantwortung, Gmail, GitHub Pages, lokale Speicherung und Apple-Systemdienste sind beschrieben. [Grundlage und Betriebshinweise](apps/uebergabe/LEGAL-NOTES.md). Links und Assets bleiben innerhalb von `/uebergabe/`.

Das freigegebene Logo zeigt zwei Menschen bei einer Übergabe, deren Körper ein gemeinsamer U-Bogen verbindet. Die Bildmarke steht neben dem Namen im Kopf aller fünf Seiten und wird für Favicon und Apple-Touch-Icon verwendet. [Herkunft und übernommene Dateien](apps/uebergabe/BRAND.md).

Die öffentlichen Betreiber- und Datenschutzangaben werden in `apps/uebergabe/config.json` gepflegt:

| Feld | Öffentlich angezeigter Inhalt |
| --- | --- |
| `publisherName` | Rechtlich verantwortlicher Anbieter |
| `publisherPostalAddress` | Vollständige öffentliche Anschrift |
| `supportEmail` | Öffentliche Kontakt-E-Mail |
| `secondarySupportEmail` | Optional zweite öffentliche Kontakt-E-Mail |
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

Die Seiten haben jeweils eigene direkte Adressen:

- Support: https://schobebro.github.io/uebergabe/support.html
- Datenschutz: https://schobebro.github.io/uebergabe/privacy.html
- Nutzungsbedingungen: https://schobebro.github.io/uebergabe/terms.html
- Impressum: https://schobebro.github.io/uebergabe/imprint.html

Solange der Status `draft` ist, zeigen Kontakt- und Rechtsseiten einen Entwurfshinweis. Fehlende E-Mail-Adressen sind keine anklickbaren Kontaktlinks. Die Texte müssen vor der Verwendung im App-Store-Release fertiggestellt werden.

## Aktueller Stand: Doppelpfad

`apps/doppelpfad/app.json` steht auf `"status": "published"`. Die Website
verwendet Doppelpfads Papierfarben, sein App-Icon und eine native Aufnahme aus
Version 1.0.0 (13). Sie enthält eine Produktseite, Spielhilfe mit aufklappbaren
Antworten, Support, Datenschutz, Nutzungsbedingungen und Impressum.

Die öffentlichen Betreiber- und Supportangaben entsprechen dem bestehenden
Company-Setup mit Leo und Felix. Die Datenschutztexte beschreiben Doppelpfads
lokale Spielstände, Wiederherstellungskopien und mögliche Betriebssystem-Sicherungen.
Eine App-Store-Verfügbarkeit oder ein Preis wird noch nicht angekündigt.
`published` bezieht sich auf die Website. Eine spätere App-Store-Verlinkung
wird nach Bestätigung der echten Store-Adresse ergänzt.

- Produkt: https://schobebro.github.io/doppelpfad/
- Support: https://schobebro.github.io/doppelpfad/support.html
- Datenschutz: https://schobebro.github.io/doppelpfad/privacy.html
- Nutzungsbedingungen: https://schobebro.github.io/doppelpfad/terms.html
- Impressum: https://schobebro.github.io/doppelpfad/imprint.html

[Gestaltung und Bildherkunft](apps/doppelpfad/BRAND.md) ·
[Grundlage der öffentlichen Texte](apps/doppelpfad/LEGAL-NOTES.md) ·
[Prüfnachweis](apps/doppelpfad/VERIFICATION.md)

## Weitere App hinzufügen

1. `apps/uebergabe/` als Ausgangspunkt nach `apps/meine-app/` kopieren.
2. In `app.json` `slug` auf `meine-app` setzen und Name/Beschreibung anpassen. `status` zunächst `draft` lassen. Der Slug muss dem Ordnernamen entsprechen; nur Kleinbuchstaben, Ziffern und Bindestriche sind erlaubt.
3. In `config.json` die öffentlichen Angaben passend zur App ergänzen. Die URLs leitet der Builder automatisch aus dem Slug ab.
4. Alle fünf HTML-Seiten, Bilder, Favicon und Rechtstexte tatsächlich auf die neue App anpassen. Insbesondere sind Angaben zu Datenspeicherung, Berechtigungen und Drittanbietern app-spezifisch.
5. Beide Builds prüfen und die Vorschau auf Desktop und Mobilgerät ansehen. Für zusätzliche Assets die explizite Dateiliste `APP_FILES` in `scripts/build.py` erweitern.
6. Auf `main` committen: die vollständige eigenständige Website liegt unter `/meine-app/`. Sobald alle Angaben und Texte fertig sind, `status` auf `published` setzen; die Entwurfshinweise entfallen nach erfolgreicher Validierung.

Es werden keine App-Kacheln, gemeinsame Navigation oder Querverlinkungen erzeugt. Alle relativen Links innerhalb einer App funktionieren unter ihrem Unterverzeichnis. Die Root-Weiterleitung bleibt ausdrücklich auf Übergabe gerichtet und ändert sich nicht automatisch, wenn eine weitere App hinzukommt.

## GitHub Pages

Repository: **Schobebro/schobebro.github.io**. In **Settings → Pages** ist **GitHub Actions** die Veröffentlichungsquelle. Die eigenständigen Websites teilen sich ausschließlich das Hosting unter `https://schobebro.github.io/`. `root/index.html` ist lediglich eine Weiterleitung.

Der Workflow **Websites · GitHub Pages**:

- prüft Tests und beide Builds bei jedem Push und Pull Request;
- stellt eine vollständige Vorschau für sieben Tage als Actions-Artefakt bereit;
- veröffentlicht bei Änderungen auf `main` oder manuellem Start auf `main` ausschließlich `build/site`;
- stoppt die Veröffentlichung, wenn eine als `published` markierte App unvollständige Angaben oder kaputte interne Links hat;
- kopiert nur ausdrücklich freigegebene Dateien, keine Konfigurationen, Skripte oder Quell-Dokumentation in den Website-Build;
- verwendet offizielle GitHub-Actions mit festgelegten Commit-SHAs und benötigt keine eigenen Secrets.

Pull Requests veröffentlichen nichts. Der Deploy-Job hat nur die zusätzlichen Rechte `pages: write` und `id-token: write`; der übrige Workflow liest lediglich Repository-Inhalte. Fehlgeschlagene Builds ersetzen die bisher veröffentlichte Website nicht.

[GitHub Pages: Websites für Organisationen](https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages) · [Eigene Pages-Workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
