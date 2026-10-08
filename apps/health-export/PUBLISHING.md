# Health Export · Veröffentlichungspaket

Stand: 08.10.2026. Bestehender [PR #1](https://github.com/Schobebro/schobebro.github.io/pull/1),
Branch `feat/health-export-pages-20261008`. Die finale Website-Abnahme
ist im Prüfnachweis dokumentiert; maßgeblich für die Freigabe ist der
aktuelle vollständige PR-Head. Vor einer Freigabe aktuellen vollständigen PR-Head und
seinen grünen CI-Lauf zusammen prüfen. Keine Veröffentlichung ohne Freigabe.

## Umfang einer Freigabe

Ein Merge nach `main` veröffentlicht über den vorhandenen Pages-Workflow
sofort die komplette Website-Ausgabe. Der freigabefähige Stand verwendet `status: published`. Der PR selbst
veröffentlicht nichts.

Dieser Stand ist als fertige öffentliche Informationswebsite freigabefähig.
`status: published` entfernt die Builder-Entwurfshinweise; alle fünf Seiten
sind indexierbar. Die Startseite sagt wahrheitsgemäß, dass die App noch nicht
im App Store verfügbar ist. Gemeinsame Website-/Support-Betreiber stehen im
Impressum und Datenschutz; eine rechtliche Store-Verkäuferrolle wird daraus
nicht abgeleitet. Apple- und Store-Entscheidungen bleiben separate
Voraussetzungen für App-Einreichung/Verkauf, dokumentiert in
[LEGAL-NOTES.md](LEGAL-NOTES.md). Empfehlung: Den geprüften PR-Head als
Informationswebsite freigeben und mergen, dann Deploy und Live-URLs abnehmen.

Die Website ist vollständig Deutsch. DE/EN-App und DE/EN-Storetexte bedeuten
keine vorhandenen englischen Webseiten. Vor zusätzlichem englischem Vertrieb
Support-/Datenschutzverständlichkeit bewerten; eine englische Fassung ist
noch nicht Bestandteil dieses PR. Es gibt keine Store-Adresse und keinen
Download-Button. Der geplante Preis 0,99 € ist als Plan für Deutschland
gekennzeichnet.

## Dateien und Nachweise

Veröffentlicht werden ausschließlich `index.html`, `support.html`,
`privacy.html`, `terms.html`, `imprint.html`, `styles.css`,
`assets/app-icon.png` und `.nojekyll` unter `/health-export/`.
Konfiguration und Arbeitsdokumentation sind im öffentlichen Repository
sichtbar, gelangen jedoch nicht in die Pages-Ausgabe. Alle Betreiberangaben
stammen aus dem vorhandenen öffentlichen Company-Setup.

[Erneute Tests, Builds, Produktabgleich und Browser-/Accessibility-Prüfung](VERIFICATION.md).
Vor Merge erneut die CI des tatsächlichen PR-Heads prüfen. Anschließend den
Deploy-Lauf auf `main` bis zu erfolgreichem `Publish GitHub Pages` verfolgen.
Ein erfolgreicher PR-Build enthält keinen Deploy-Nachweis.

## Live-Abnahme nach Freigabe und Deploy

Die fünf direkten Zieladressen:

- https://schobebro.github.io/health-export/
- https://schobebro.github.io/health-export/support.html
- https://schobebro.github.io/health-export/privacy.html
- https://schobebro.github.io/health-export/terms.html
- https://schobebro.github.io/health-export/imprint.html

Status und ausgelieferten Inhalt nach erfolgreichem Deploy prüfen:

```sh
curl --fail --show-error --silent https://schobebro.github.io/health-export/ -o /tmp/health-export-live-index.html
curl --fail --show-error --silent https://schobebro.github.io/health-export/support.html -o /tmp/health-export-live-support.html
curl --fail --show-error --silent https://schobebro.github.io/health-export/privacy.html -o /tmp/health-export-live-privacy.html
curl --fail --show-error --silent https://schobebro.github.io/health-export/terms.html -o /tmp/health-export-live-terms.html
curl --fail --show-error --silent https://schobebro.github.io/health-export/imprint.html -o /tmp/health-export-live-imprint.html
```

Alle fünf HTTP-200-Antworten und Health-Export-Inhalte verlangen; keine
GitHub-404-Seite oder bloße Root-Weiterleitung akzeptieren. Live im Browser
Navigation, CSS/Icon, Support-Maillinks und Datenschutzanker prüfen.
Es dürfen keine Entwurfshinweise oder offenen
Anbieterbehauptungen mehr stehen. `noindex` allein verhindert nicht die
öffentliche Abrufbarkeit.

Erst nach belegter Live-Abnahme diese Datenschutz-/Support-Adressen in
App und Store-Paket übernehmen und den In-App-Aufruf in beiden Sprachen
prüfen. Website-Freigabe erteilt keine Apple-Einreichungsfreigabe.
