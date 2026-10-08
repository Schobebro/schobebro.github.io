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
Lokale Vorschau in Brave sichtbar kontrolliert: Startseite in Desktopbreite und390×844,
Datenschutzseite in390×844. Navigation/Text/Icon passen in die Breite, keine abgeschnittenen
Controls beobachtet; Entwurf-/Vorschauhinweise sichtbar. Das ist Browser-Emulation,
keine reale iPhone-Browser-Abnahme und keine Veröffentlichungsfreigabe.
