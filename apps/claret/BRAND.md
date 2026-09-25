# Claret · Gestaltung und Bildherkunft

Stand: 25. September 2026. Die Website übernimmt die öffentlichen Seiten aus dem
privaten App-Repository `Schobebro/WineTrainer` (`marketing/`). Seitentexte sind
Englisch (britische Schreibweise), wie die App.

Gestaltung nach `design/STYLE.md` (style-v0.3) im App-Repository: helle
Porzellanfläche `#FCFBF8`, Karten `#FFFEFE`, Haarlinie `#E4E1DF`, Tinte
`#28272A`, gedämpfte Tinte `#6E6B70`, Weinrot `#6B1E2E` für Links, Titel und
Tasten, Salbei `#4F6B4C`; dunkle Darstellung mit den dunklen App-Werten.
`--band` (`#F5F2EE`) ist eine reine Seitentönung zwischen Fläche und Haarlinie.
Schrift: Systemserife (New York, `ui-serif`) für Überschriften, Systemschrift
(SF Pro, `system-ui`) für Text. Keine Webfonts, kein JavaScript, keine externen
Ressourcen. `marketing/check` prüft den Kontrast aller Textpaare in hell und dunkel.

## Übernommene Dateien

Icons sind mit `sips` verkleinerte Kopien des gewählten App-Icon-Masters
`design/icon/masters/icon-claret-rim-1024.png` („Der Rand“, SHA-256
`6eed0cecdb391f8b92c653b35d13af5b9444d24944e7569e9bb5918ecd7e1218`), anschließend
verlustfrei mit `oxipng` optimiert. Die fünf Bildschirmaufnahmen sind die
unveränderten Marketingbilder aus `marketing/img/` (abgeleitet von den
Store-Aufnahmen der UI/UX-Runde vom 22. September 2026).

| Website-Datei unter `site/` | Quelle im App-Repository | SHA-256 |
| --- | --- | --- |
| `favicon.png` (64 px) | `marketing/favicon.png` | `0ef8572b95c748ce60c48b746b8d5fb98708cff90c5b265b248c11f00e4244b5` |
| `apple-touch-icon.png` (180 px) | `marketing/apple-touch-icon.png` | `b1320e1f7d3eda2a133f6d4ebd0bb08eac95dae0d21d9ae5ce9fc134bd1caa1b` |
| `img/icon-256.png` | `marketing/img/icon-256.png` | `707b0f6cfb15e318045bf13446da284e79ba38e8fb29b87bb119d86950f85a47` |
| `img/screen-today.webp` | `marketing/img/screen-today.webp` | `592f94edceff934a9fded42c3ea27e3e2d9cc92785f828faa57bf16a00a7eac5` |
| `img/screen-lesson.webp` | `marketing/img/screen-lesson.webp` | `bc8cb6ea42e4a9311d65d5ed4c04fb3ca7c5d6a23b59f592796bd5a1aca44f50` |
| `img/screen-exam.webp` | `marketing/img/screen-exam.webp` | `0d722f802ce29c143817421ca6ab59f2db4d54603847e3b365465fb0d42d36ef` |
| `img/screen-tasting.webp` | `marketing/img/screen-tasting.webp` | `4e118295b434b29f4002885cd10989962dbcd35cbce8e80011f1719b5750ff23` |
| `img/screen-map.webp` | `marketing/img/screen-map.webp` | `91390aaedca12e6075b778fba7f724d3d54b08acac9a6a866b11d811b5b54fc8` |

## Abgleich mit dem App-Repository

Quelle der Seiten sind die Vorlagen `marketing/templates/*.html` und
`marketing/style.css` im App-Repository. Nach `tools/configure-release` schreibt
`marketing/sync-website <dieser Ordner>/site` die fünf Seiten, das Stylesheet und
die Bilder hierher; HTML-Kommentare (interne Gründerhinweise) entfallen dabei.
`marketing/check --website <dieser Ordner>/site` bestätigt die Gleichheit.
Betreiberangaben stehen dort nur als `[[TOKENS]]` und werden ausschließlich hier
aus `config.json` eingesetzt. Die öffentlichen Dateien stehen in `app.json` unter `files`.
