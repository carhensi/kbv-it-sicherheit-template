# AGENTS.md – Hinweise für KI-Agenten

Leitfaden für automatisierte Agenten, die an diesem Repository arbeiten. Ziel: schnell
produktiv werden, ohne die (teils nicht offensichtlichen) Fallstricke neu zu entdecken.

## Worum es geht

Öffentliches **Muster-/Template** einer IT-Sicherheitsdokumentation für Arztpraxen nach
**§ 390 SGB V** (KBV-IT-Sicherheitsrichtlinie). Reines LaTeX-Projekt, Lizenz CC BY-SA 4.0.
Es ist **kein** Software-Projekt – das Artefakt ist ein PDF.

## Build

Gebaut wird containerisiert (Docker + Make, `lualatex` aus `maxkratz/texlive:2026-python`).
Es gibt **drei Varianten**:

| Target | Variante | Standard |
|---|---|---|
| `make build-standard` | kompakt (`scrartcl`) | PDF/A-3u |
| `make build-accessible` | getaggt (`article` + `\DocumentMetadata`) | PDF/A-3u + PDF/UA-1 |
| `make build-printable` | Druck (`pdfx`) | PDF/X-1a |
| `make all` | alle drei + Versionsstempel + Mermaid | |

Output: `tex/main-{standard,accessible,printable}.pdf`. Der Build läuft `lualatex` **3×**
(Referenzen/TOC). Weitere Targets: `make test` (pytest), `make mermaid`, `make clean`,
`make version`, `make use-sample` / `make use-real`.

## Struktur

- `tex/main.tex` – Master, bindet alle Kapitel via `\input` ein; enthält die
  Varianten-Weichen.
- `tex/content/*.tex` – Kapitel & Anhänge (numerisch sortiert) + Arbeitsvorlagen (`9xx`).
- `tex/config/` – `packages.tex` (Pakete/Weichen), `metadata.tex` (Praxisdaten),
  `columntypes.tex`.
- `tex/style/` – `theme.sty`, `macros.sty`, `signatures.sty`.
- `scripts/` – Build-/Versions-Helfer + `test_build.py` (Unit-Tests).
- `.github/workflows/build.yml` – CI (siehe unten).

## Daten / Datenschutz

- **Niemals echte Praxisdaten committen.** `tex/config/metadata.tex`,
  `tex/assets/geraeteliste.csv`, `tex/assets/netzplan.mmd` sind praxisspezifisch; es gibt
  jeweils `*-sample`-Varianten. CI baut mit Sample-Daten (`make use-sample`).

## CI-Gates (build.yml)

- Baut **standard** + **accessible** (mit Sample-Daten).
- Validiert mit **verapdf**: `--flavour 3u` (beide) und `--flavour ua1` (accessible).
  Grün = `failedChecks="0"`.
- `make test` (5 pytest-Tests).
- **Kein** chktex/aspell-Gate. `.aspell.de.pws`/`.chktexrc` sind nur lokale Editor-Configs.
- **printable wird in CI nicht gebaut** – nach Änderungen an gemeinsamen Dateien lokal
  `make build-printable` gegenprüfen.
- CI läuft auf `ubuntu-latest` mit Docker-in-Docker; das Build-Image kommt aus
  `TEXLIVE_IMAGE` im Makefile (kein `container:`). `vars.USE_SAMPLE_DATA=true` → Build mit
  `metadata-sample.tex` (`metadata.tex` ist gitignored).
- Release-Assets: nur **Standard + Accessible** PDF (kein printable).
- Repo erlaubt nur **Squash-Merge**.

## Fallstricke (wichtig!)

1. **enumitem & Accessible-Build:** Im Accessible-Build darf `enumitem` **nicht** geladen
   werden (zerstört PDF/UA-Tagging). Sowohl `config/packages.tex` als auch `style/theme.sty`
   klammern das mit `\ifaccessible\else…\fi`. Wer Listen-Setup anfasst: beide Stellen prüfen.
2. **`\multicolumn` in Tabellen-Zellen via Makro:** Ein Header-Makro, das `\multicolumn`
   als erstes Zellen-Token ausgibt, muss klassisch mit `\newcommand` definiert sein – **nicht**
   mit `\NewDocumentCommand` (xparse macht es `\protected`; beim Zellstart wird es dann nicht
   expandiert → Fehler „Misplaced \omit"). Siehe `\AccessibleTableHeader` in `macros.sty`.
3. **printable + hyperref:** `pdfx` (x-1a) lädt `hyperref` bereits. `hyperref` darf im
   printable-Zweig nicht erneut mit Optionen geladen werden (`Option clash`) – stattdessen
   `\hypersetup`. Geregelt über `\ifprintable` in `packages.tex`.
4. **TikZ `alt=`-Key:** Nur im Accessible-Build (Tagging) definiert. Im Standard/printable
   führt er zu `/tikz/alt`-pgfkeys-Fehler → mit `\ifaccessible` klammern (siehe
   `910_anhang-netzplan.tex`).
5. **Varianten-Weichen:** `\ifaccessible` und `\ifprintable` werden vom Makefile per
   `\def\accessible{}` / `\def\printable{}` gesetzt. Neue variantenabhängige Logik immer
   über diese Booleans.

## Konventionen

- Deutschsprachiger Inhalt; Anführungszeichen via `\enquote{…}` (csquotes), Querverweise
  via `\cref`/`\Cref` (cleveref), Hinweise via `\Hinweis`.
- Rechtsbezug ist **§ 390 SGB V** (ersetzt § 75b). KBV-Anlagen: 1 (Praxen, 50 Anf.),
  2 (mittlere Praxen), 3 (Großpraxen), 4 (Medizingeräte), 5 (TI).

## Aktualität von Rechtsangaben

Gesetzes-/Fristen-/Schwellenwert-Angaben (z. B. § 390, NIS2) sind zeitpunktbezogen. In der
Einleitung steht ein **Stand-/Prüf-Hinweis** mit Verweis auf die jeweils aktuelle KBV-Fassung.
Bei Änderungen dieser Angaben Stand-Datum und Quelle (KBV/BSI) mitpflegen.

## Verifikation nach Änderungen

1. `make build-standard` **und** `make build-accessible` (bei Style/Tabellen/Paket-Änderungen
   zusätzlich `make build-printable`).
2. Log auf `! ` (Fehler) und `Misplaced` prüfen → muss 0 sein.
3. Broken Refs: PDF-Text extrahieren, auf `??` prüfen. **`pdftotext` ist NICHT im
   TeXLive-Image** → poppler-Container nutzen:
   `docker run --rm -v "$PWD/tex":/data debian:stable-slim sh -c 'apt-get update -qq && apt-get install -y -qq poppler-utils && pdftotext /data/main-standard.pdf - | grep -c "??"'`
   ⚠️ Fehlt das Tool, ist die Pipe leer → `grep -c`=0 = **falscher** Pass. Tool-Existenz prüfen!
4. PDF/A & PDF/UA: verapdf (`--flavour 3u` / `--flavour ua1`) → `failedChecks="0"`.
5. `make test` grün.

**Signatur lokal:** `git log/tag -v` zeigt „N" ohne `gpg.ssh.allowedSignersFile` — die
Signatur ist trotzdem da. Mit ephemerer allowed_signers-Datei (`<email> <ssh-key>`) verifizieren.
**CI-Status:** `gh run watch` bricht unzuverlässig vorzeitig ab → besser
`gh run view <id> --json status --jq .status` pollen.

## Release (tag-getrieben)

1. Summary-Zeile (+ Bullets) unter neuem `## [vYYYY.MM.DD] - YYYY-MM-DD` in `CHANGELOG.md`.
2. PR → **Squash-Merge** nach `main`.
3. Signierten Tag setzen + pushen:
   `git tag -s vYYYY.MM.DD -m "Release …" && git push origin vYYYY.MM.DD`
4. Der Tag-Push triggert `build.yml` (`push: tags`); der `release`-Job baut + erstellt das
   GitHub-Release (Version aus dem Tag-Namen) via softprops auf dem vorhandenen signierten Tag.

Kein `gh workflow run`/`initial_release`-Flag mehr. Der `release`-Job läuft **nur** beim
Tag-Push (im PR übersprungen) — also erstmalig „echt" beim Release; Lauf beobachten.
README-Download-Links sind versions-hartkodiert → pro Release anpassen (offener TODO:
versionslose Asset-Namen).

## Git

Nicht ungefragt committen/pushen. Default-Branch ist `main`; für Änderungen Branch anlegen.
