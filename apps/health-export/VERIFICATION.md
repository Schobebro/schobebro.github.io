# Health Export · Prüfnachweis

Stand: 08.10.2026. Nur `apps/health-export/**` geändert. Kein Commit, Push, Merge oder Upload durch den Paket-Worker.

## Vorhandene Tests

Befehl: `python3 -m unittest discover -s scripts/tests -v`

Wörtliches Ergebnis:

```text
Ran 17 tests in 0.376s

OK
```

## Builds

Befehle: `python3 scripts/build.py` und `python3 scripts/build.py --preview`. Beide Exit-Code 0. Wörtliche Ausgabe:

```text
Website gebaut: /private/tmp/health-export-company-web-20261008/build/site
Vorschau gebaut: /private/tmp/health-export-company-web-20261008/build/preview
```

## Zusätzliche Paketprüfung

Per Python-Standardbibliothek wurden beide tatsächlichen Build-Verzeichnisse gegen die Manifest-Dateiliste, relative Links, Entwurfsmarkierungen und `noindex` geprüft. Die öffentliche Konfiguration wurde mit Übergabe verglichen und zusätzlich durch `validate_config` validiert. Alle öffentlichen Dateien wurden über einen kurzzeitig gestarteten lokalen HTTP-Server auf `127.0.0.1` abgerufen und byteweise verglichen. Der Server wurde anschließend beendet. Der erste HTTP-Versuch wurde durch die Sandbox blockiert; der erlaubte Wiederholungslauf war erfolgreich.

Wörtliches Ergebnis des erfolgreichen Laufs:

```text
PASS: Öffentliche Betreiberkonfiguration entspricht Übergabe; nur Standdatum aktualisiert, appStoreURL null, Status draft.
PASS: site: exakt 8 öffentliche Dateien; 70 relative Links bleiben unter /health-export/; Entwurfs-/noindex-Grenze geprüft.
PASS: site: alle 8 Dateien lokal per HTTP mit Status 200 und identischen Bytes ausgeliefert.
PASS: preview: exakt 8 öffentliche Dateien; 70 relative Links bleiben unter /health-export/; Entwurfs-/noindex-Grenze geprüft.
PASS: preview: alle 8 Dateien lokal per HTTP mit Status 200 und identischen Bytes ausgeliefert.
PASS: App-Icon bytegleich zum originalen 1024×1024-Asset; kein Health-Screenshot.
PASS: Keine App-Quelldateien, Symlinks, Secrets-Marker oder privaten Life-OS-Pfade im Paket; personenbezogene Betreiberangaben ausschließlich aus öffentlicher Company-Konfiguration.
```

Die acht Dateien sind `index.html`, `support.html`, `privacy.html`, `terms.html`, `imprint.html`, `styles.css`, `assets/app-icon.png` und `.nojekyll`. App-Konfiguration, App-Manifest und Dokumentation gelangen nicht in die Build-Ausgabe. Health Export ist nicht im Sitemap enthalten. Die fünf Seiten sind in beiden Builds `noindex`; Vorschau und vier Kontakt-/Rechtsseiten tragen den Builder-Hinweis. Die Startseite zeigt zusätzlich ausdrücklich den Vorbereitungsstatus.

`git diff --check` lieferte Exit-Code 0 ohne Ausgabe.

## Grenzen und offene Punkte

Lokale Build-/Link-/HTTP-Prüfung ist erfolgt; keine visuelle Abnahme auf echtem iPhone, keine Apple- oder rechtliche Freigabe. Vor Veröffentlichung/Verkauf bleiben Store-Anbieter-/Vertragsabgleich, iCloud-Exportentscheidung nach 5.1.3, finaler Preis und finale Store-Angaben offen. Der App-Status bleibt `draft`; es gibt keine Store-URL oder Verfügbarkeitszusage.

## Ergänzende Hauptsession-Prüfung

08.10.2026: 17 Tests und regulären/Vorschau-Build selbst erneut erfolgreich ausgeführt.
Lokale Vorschau in Brave sichtbar kontrolliert: Startseite in Desktopbreite und 390×844,
Datenschutzseite in 390×844. Navigation/Text/Icon passen in die Breite, keine abgeschnittenen
Controls beobachtet; Entwurf-/Vorschauhinweise sichtbar. Das ist Browser-Emulation,
keine reale iPhone-Browser-Abnahme und keine Veröffentlichungsfreigabe.


## Erneute Paketabnahme · 08.10.2026

Geprüfter Seitenstand: `e4688153bb41cc3e74d3ddfbab98aeaf1a033d8d`.
17 Tests erneut bestanden (`Ran 17 tests in 0.351s`, `OK`), regulärer und
Vorschau-Build erfolgreich. Beide enthalten genau die acht oben aufgeführten
Dateien; keine unaufgelösten Platzhalter, auf allen fünf Seiten `lang="de"`,
je ein H1 und `noindex`. Betreiberkonfiguration nochmals mit der bestehenden
öffentlichen Übergabe-Konfiguration verglichen: ausschließlich das Standdatum
weicht ab. Die GitHub-Prüfung des Seitenstands ist erfolgreich:
[Workflow 37779509840](https://github.com/Schobebro/schobebro.github.io/actions/runs/37779509840).

Quellabgleich: Zeitraum 1–365 Tage, Kurzbefehle 1–7 Tage/Standard 2,
HealthKit nur lesend, zehn Datentypen, temporäres Staging mit vollständigem
Dateischutz, Ordner-Bookmark/Exportstatus, Tages-JSON/CSV und Dateierhalt sind
mit dem aktuellen Produktverhalten vereinbar. Keine behauptete medizinische
Bewertung oder automatische Cloud-Zulassung.

Eigener lokaler HTTP-Server, nach Prüfung beendet: Start, Datenschutz und
Support lieferten HTTP 200. Browser-Abnahme in Brave bei 320 × 844 CSS-Pixeln:
`innerWidth = scrollWidth = 320` auf allen drei Seiten, keine horizontalen
Überläufe. Start und Datenschutz sichtbar kontrolliert. Tastaturfokus auf dem
Markenlink zeigte `rgb(160, 71, 14) solid 3px`; die erste Support-Antwort ließ
sich per Enter öffnen und war im DOM sichtbar. Semantische Überschriften,
Navigation, Skip-Link und Bildalternativen vorhanden. Das ist keine reale
VoiceOver-/iPhone-Abnahme und kein umfassendes WCAG-Konformitätszertifikat.

Berechnete Kontraste der Textfarben zum jeweiligen CSS-Hintergrund:
Fließtext 11,02:1, Links 6,30:1, Untertitel 5,73:1, Datum 5,12:1,
Rubrik 5,76:1, Footer 5,56:1, Hinweis 8,35:1, Button 10,91:1.
Fokuskontur zum Seitenhintergrund 5,72:1.

Die geplante öffentliche Datenschutzadresse lieferte bei der erneuten
lesenden Prüfung HTTP 404. Eine lokale HTTP-200-Antwort belegt keine
Veröffentlichung. [Konkrete Freigabe und Live-Abnahme](PUBLISHING.md).
