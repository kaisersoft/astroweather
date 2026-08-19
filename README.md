# AstroLotto Score

Experimentelles Streamlit-Tool, das astrologische Faktoren (Ephemeriden via skyfield / JPL DE421) zu einem Unterhaltungs-Score für Lotto-Ziehungstage verdichtet.

**Nur zur Unterhaltung – keine Gewinngarantie.**

---

## Features (v5)

| Bereich | Inhalt |
|--------|--------|
| **Ephemeriden** | skyfield + JPL DE421 |
| **Zeitzonen** | Echte Ortszeiten via `zoneinfo` (80+ Städte) |
| **Häuser** | Porphyry (Quadranten-Teilung, näher an Placidus als Whole Sign) + verbesserter ASC/MC |
| **Mond** | Phase, Void of Course, genaue Aspekte (anwendend/scheidend) |
| **Merkur** | Rückläufig, stationär, Verbrennung, Haus 3, Aspekte zu Jupiter/Uranus |
| **Aspekte** | Anwendend vs. scheidend; Orben je nach Planet |
| **Aspektmuster** | Großes Trigon, T-Quadrat, Yod (Finger Gottes) |
| **Lose** | Part of Fortune, Lot of Spirit |
| **Zusatzkörper** | Mittlerer Nordknoten, Chiron-Näherung |
| **Zeitqualität** | Tagesherrscher, Planetenstunden |
| **Persönlich** | Transite, Ruler der 5./8./11. Häuser |
| **Progressionen** | Sekundärprogressiver Mond + progressiver Aszendent |
| **Solar Return** | Vereinfachte Sonnenrückkehr (Jupiter/Uranus in Glückshäusern) |
| **Lotterien** | Eurojackpot (Di/Fr, 20:00) und LOTTO 6aus49 (Mi/Sa, 18:25) |
| **AstroWeather** | Nächste 3 Ziehungen mit Score + Jackpot-Hinweis |
| **Verlauf** | 14-Tage-Score-Trend |
| **Hochscore** | Alle Ziehungstage bis Jahresende mit Score > 75 % |
| **Kalender** | Ausgewählte Hochscore-Tage als `.ics` (Google Kalender, Erinnerung 09:00) |
| **UI** | Clean-Fortune-Dashboard (hell, Sidebar, Metric-Cards, Status-Pills) |

---

## Changelog (Übersicht der Umbauten)

### v3 → Ausgangspunkt
- skyfield-Ephemeriden, Ganz-Zeichen-Häuser, grober Aszendent
- Allgemeiner + persönlicher Score, Mondphase, Merkur Rx
- AstroWeather, 14-Tage-Verlauf, Hochscore-Tabelle > 75 %
- Profil-Historie, Text-Export, Jackpot-Abruf (lotto.de / Fallback)

### v4 – Präzision innerhalb des Systems
- **Echte Zeitzonen** (`zoneinfo`) statt UTC-Approximation
- **Verbesserter Aszendent + MC** (RAMC / schräge Aufsteigung)
- **Void of Course Moon** (−12 bei VoC)
- **Merkur feiner:** stationär, Verbrennung, Haus 3, harmonische Aspekte
- **Anwendende vs. scheidende Aspekte** (anwendend stärker)
- **Tagesherrscher & Planetenstunden** (Jupiter/Venus-Bonus, Saturn/Mars-Abzug)
- **Ruler der 5./8./11. Häuser** aktiv mitbewertet
- **Lot of Spirit** zusätzlich zum Part of Fortune
- **Exakte Ziehungszeiten** (EJ 20:00, 6aus49 18:25)
- **Score-Dämpfung** sehr hoher Werte (weniger Inflation > 80 %)

### v5 – Höherer Aufwand + Interface
- **Porphyry-Häuser** statt Whole Sign
- **Aspektmuster:** Großes Trigon, T-Quadrat, Yod
- **Sekundärprogression** (progressiver Mond + ASC)
- **Solar Return** (Näherung; Jupiter/Uranus in Glückshäusern)
- **Nordknoten** (mittlerer Knoten) und **Chiron**-Näherung
- **Google-Kalender-Export:** Multiselect / „Alle auswählen“ für Hochscore-Tage → `.ics` mit Erinnerung 09:00 Ortszeit
- **UI „Clean Fortune“:**
  - Helles Dashboard (`layout="wide"`)
  - Sidebar: Logo, Geburtsdaten, Lotto-Modus, primärer Button
  - Metric-Tiles (Kombiniert / Allgemein / Persönlich) mit farbigem Top-Border
  - Status-Pills (Mond, Merkur, VoC, Tagesherrscher, Planetenstunde)
  - AstroWeather-Karten, 14-Tage-Chart, Hochscore-Tabelle + ICS-Export
  - Custom CSS (Inter, Off-White, weiße Karten, dezente Schatten)

---

## Installation & Start

```bash
# Python 3.10+ empfohlen
pip install streamlit skyfield pandas

# Optional: Ephemeris wird beim ersten Lauf geladen (de421.bsp)
streamlit run app.py
```

Abhängigkeiten:
- `streamlit`
- `skyfield` (lädt `de421.bsp`)
- `pandas` (Charts / Tabellen)
- Standardbibliothek: `zoneinfo`, `datetime`, `math`, …

---

## Nutzung

1. In der **Sidebar** Geburtsdatum, -zeit und -ort wählen.
2. Lotterie-Modus (Eurojackpot oder 6aus49) und Abfrage-Datum setzen.
3. **Score berechnen** klicken.
4. Scores, AstroWeather und 14-Tage-Trend prüfen.
5. Bei Hochscore-Tagen (> 75 %) Tage auswählen → **Google Kalender (.ics)** herunterladen und in [Google Kalender](https://calendar.google.com) importieren (Einstellungen → Importieren & exportieren).

---

## Google-Kalender-Import

1. `.ics`-Datei speichern.
2. Google Kalender → Zahnrad → **Einstellungen**.
3. Links: **Importieren & exportieren** → Datei wählen → Kalender wählen → **Importieren**.

Jeder Termin:
- Start **09:00** Ortszeit (Zeitzone des Geburtsorts)
- Erinnerung zum Start + 1 Stunde vorher
- Beschreibung mit Score und Ziehungszeit

---

## Architektur (kurz)

```
app.py
├── Ephemeriden-Hilfen (ecliptic_longitude, speeds, aspects, VoC, …)
├── Häuser (approx_ascendant_mc, porphyry_houses)
├── Aspektmuster (detect_aspect_patterns)
├── Progressionen / Solar Return
├── score_general / score_personal
├── Lotterie-Config, Jackpots, Hochscore-Suche
├── build_google_calendar_ics
└── UI (Clean Fortune: Sidebar + Dashboard)
```

Scoring: **50 % allgemein + 50 % persönlich**, danach Dämpfung sehr hoher Rohwerte.

---

## Grenzen / Hinweise

- Astrologie ist **keine** wissenschaftlich belegte Vorhersagemethode für Zufallsziehungen.
- Porphyry ≠ echtes Placidus (dafür z. B. Swiss Ephemeris).
- Nordknoten = *mittlerer* Knoten; Chiron = polynomiale Näherung.
- Solar Return und Progressionen sind bewusst vereinfacht (Unterhaltung).
- Jackpot-Zahlen: Versuch live von lotto.de, sonst Fallback.

---

## Lizenz / Disclaimer

Nur zur Unterhaltung. Keine Gewinngarantie. Nutzung auf eigene Verantwortung.
**Nicht** als Anlage- oder Spielberatung geeignet.
