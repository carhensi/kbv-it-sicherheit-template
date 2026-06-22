# Changelog

All notable changes to the IT-Sicherheitsdokumentation will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to date-based versioning (YYYY.MM.DD).

## [Unreleased]

### Hinzugefügt
- Druckversion (PDF/X-1a) wird in CI gebaut und ans Release angehängt

### Geändert
- Release-Assets versionslos benannt → stabile `latest/download`-Links in der README (keine Pflege pro Release)
- CI baut nicht mehr bei jedem main-Push (Validierung via PR, Release via Tag)
- metadata-sample auf 2026.06.22 aktualisiert; `*.diff` in .gitignore

## [2026.06.22] - 2026-06-22

NIS2-/Cybersicherheits-Hinweis, KBV-Präzisierungen (§390, Compliance-Mapping, Anlagen), Tabellen-/Build-Fixes, Auto-Changelog, TeXLive 2026 und tag-getriebenes Release.

### Hinzugefügt
- Hinweis zu NIS2 / Cybersicherheitsrecht (NIS2-Umsetzungsgesetz, Stand Juni 2026) in Einleitung, Glossar und README
- Genereller Stand-/Aktualitätshinweis zu Rechts- und Fristenangaben mit Verweis auf die jeweils aktuelle KBV-Fassung

### Geändert
- Rechtsgrundlage präzisiert: §390 SGB V in Kraft seit 01.04.2025, neue Anforderungen ab 01.10.2025 (statt "Version 1.1")
- KBV-Compliance-Mapping: Zählungen entwirrt (Anlage 1 = 50 Anforderungen, 41 anwendbar; Anlage 2 = 8/9 anwendbare), n.a.-Symbol vereinheitlicht
- Fehlerhafte "(Anlage 3)"-Bezüge korrigiert (Anlage 3 = Großpraxen, für ≤5-Praxen nicht zutreffend)

### Behoben
- "Misplaced \omit" in Vorlagen-Tabellen (Header-Makro auf expandierbares \newcommand umgestellt)
- Fehlende PVS-Support-Nummer auf der IT-Notfallkarte (\PVSSupport → \PVSSupportTel)
- pgfkeys-Fehler im Standard-Build: TikZ-alt-Key nur noch im Accessible-Build
- enumitem im Accessible-Build deaktiviert (schützt PDF/UA-1-Tagging)
- "Option clash for package hyperref" in der Druckversion (PDF/X-1a)

### Entfernt / CI
- Veralteten, defekten Workflow validate.yml entfernt (build.yml deckt Validierung ab)
- Makefile: .PHONY um build-printable/build-all/build-sample-* ergänzt
- Build-Umgebung auf TeXLive 2026 aktualisiert (alle Varianten + PDF/A-3u/PDF/UA-1 verifiziert)
- GitHub-Actions aktualisiert (checkout@v7, upload-/download-artifact@v7/@v8, gh-release@v3 – Node 24)
- Release tag-getrieben (Version aus signiertem Git-Tag) statt initial_release-Flag

## [2025.09.01] - 2025-09-01

Initial Release der vollständigen IT-Sicherheitsdokumentation nach §390 SGB V.

### Initial Release
- Complete IT security documentation according to §390 SGB V (KBV IT-Sicherheitsrichtlinie)
- KBV compliance: Anlage 1 (100%), Anlage 2 (80%), Anlage 5 (100%)
- PDF/A-3u and PDF/UA-1 (100%) compliance
- Modular LaTeX structure with Docker-based builds
- GitHub Actions CI/CD with parallel builds
- Templates: Emergency card, training plan, VVT, TOMs, and more
