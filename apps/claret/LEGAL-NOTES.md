# Claret · Grundlage der öffentlichen Texte

Stand: 25. September 2026. Board-Entscheidung vom 25. September 2026: Claret
erhält die Website `https://schobebro.github.io/claret/`; die frühere Domain
`winetrainer.app` entfällt. Status `draft`, bis Uwe nach Sichtprüfung freigibt.

## Übernommen aus Übergabe

Aus `apps/uebergabe/config.json` unverändert übernommen: `publisherPostalAddress`,
`supportEmail` (Leo), `secondarySupportEmail` (Felix). In `publisherName` und
`copyrightHolder` ist nur die Konjunktion für die englischen Seiten übersetzt.
Die Texte `supportMailProvider`, `supportRetentionPolicy`, `supportPrivacyDetails`,
`websitePrivacyBasis` und `applicablePrivacyRightsAndSupervisoryAuthority` sind
inhaltsgleiche englische Übersetzungen. Ebenso übernommen: gemeinsame
Verantwortung nach Art. 26 DSGVO mit gemeinsamer Aufgabenregelung, Gmail als
Support-Postfach, GitHub-Pages-Protokolle, Widerspruchshinweis und die
Aufsichtsbehörden Berlin und Baden-Württemberg. Es wird keine Rechtsform,
Gesellschaft, Registereintragung oder USt-ID behauptet; `publicLegalDetails` bleibt `null`.

## App-spezifisch geprüft

Quellstand `Schobebro/WineTrainer` vom 25. September 2026, `store/metadata/app-privacy.txt`
und Code: offline, kein Konto, keine Analyse-, Werbe- oder Tracking-SDKs, kein
Netzwerkzugriff im App-Code; Lernstände lokal (können in Gerätesicherungen
enthalten sein); Erinnerungen als lokale Mitteilungen erst nach Einschalten;
„Reset progress“ in den Einstellungen; Einmalkauf „Full Course“
(`app.winetrainer.fullcourse`, nicht verbrauchbar) über StoreKit, Wiederherstellung
unter Settings → About → Restore purchase; Apple kann Absturzberichte nach
Nutzerfreigabe bereitstellen. Nutzungsbedingungen: Apple-Standard-EULA,
keine Bestehensgarantie, Unabhängigkeitshinweis aus `independenceNotice` und
`wsetDescriptor` (`release/configuration.json`), OpenStreetMap-Lizenzhinweis.

Die Website nennt keinen Preis, keinen Download-Link und kein Veröffentlichungsdatum
(`appStoreURL` bleibt `null`).

## Offen vor `published` bzw. vor dem Store-Release

- Verkäufer im App Store (Leos Konto, Einzelperson oder Organisation) und damit
  Lizenzgeber sowie DSA-Händlerstatus im App Store Connect sind nicht geklärt.
  Die Seiten verweisen deshalb auf den „im Store-Eintrag ausgewiesenen App-Anbieter“.
- Copyright-Inhaber: App-Konfiguration nennt eine vorläufige Angabe; die Website
  verwendet `copyrightHolder` wie bei Übergabe.
- Entgeltlicher Vertrieb: Mit dem Verkauf des Full Course können steuerliche und
  gewerbliche Anbieterangaben nötig werden; nicht geprüft.
- Wie bei Übergabe wurden keine Auftragsverarbeitungs- oder Dienstleisterverträge
  mit Google oder GitHub geprüft oder abgeschlossen.
- Beide Postfächer müssen betreut werden; Löschregeln sind im Betrieb umzusetzen.
- Die Nennung von WSET als beschreibende Angabe (`wsetDescriptor`) ist eine
  Gründerentscheidung ohne rechtliche Prüfung.

## Primärquellen

- [§ 5 DDG](https://www.gesetze-im-internet.de/ddg/__5.html) und [§ 18 MStV](https://www.gesetze-bayern.de/Content/Document/MStV-18)
- [DSGVO, insbesondere Art. 6, 13, 15–21, 26 und 77](https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng)
- [Apple Standard-EULA](https://www.apple.com/legal/internet-services/itunes/dev/stdeula/)
- [GitHub Pages und IP-Protokollierung](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages#data-collection)
- [Google-Datenschutzerklärung](https://policies.google.com/privacy?hl=en-GB)
- [Apple App Store & Privacy](https://www.apple.com/legal/privacy/data/en/app-store/) und [App Analytics & Privacy](https://www.apple.com/legal/privacy/data/en/app-analytics/)

Diese Arbeitsnotiz gehört nicht in den Website-Build. `published` bezeichnet
nur den Website-Status, keine rechtliche Prüfung.
