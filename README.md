# AstroLotto Score (Streamlit)

Experimentelles Scoring-System auf Basis öffentlicher astrologischer Traditionen zu Glück, plötzlichen Gewinnen und Spekulation (Jupiter, Uranus, 5./8./11. Haus, Part of Fortune usw.).

## Wichtiger Hinweis

Dies ist ein **Unterhaltungs- und Experimentier-Tool**.  
Astrologie ist keine wissenschaftlich belegte Methode zur Vorhersage von Lottoziehungen.  
Die mathematische Gewinnwahrscheinlichkeit bleibt unverändert extrem niedrig.

## Features

- **Allgemeiner Score** (Tages-Transite)
- **Persönlicher Score** (Transite zum Radix / Part of Fortune)
- **Kombinierter Score** (50/50) – prominent und fett dargestellt
- Anzeige als Prozent + Glückssymbol
- Platzhalter für Jackpot-Höhe und geschätzte Tippzahlen (Di & Sa)

## Lokal starten

```bash
cd astro_lotto_app
pip install -r requirements.txt
streamlit run app.py
```

## Deploy auf Streamlit Cloud

1. Repo auf GitHub pushen
2. Bei [share.streamlit.io](https://share.streamlit.io) neues App-Deployment anlegen
3. Main-File: `app.py`
4. Python-Version nach Bedarf wählen

## Technische Hinweise

- Planetenpositionen sind **Näherungswerte** (mittlere Bewegungen).  
  Für Produktionsgenauigkeit Swiss Ephemeris (`pyswisseph`) oder `skyfield` einbinden.
- Jackpot- und Teilnehmerzahlen sind **deterministische Platzhalter**.  
  Für echte Daten offizielle Lotto-Quellen / APIs anbinden.
- Aszendent und Part of Fortune sind stark vereinfacht berechnet.

## Erweitertes Regelwerk (Kurz)

Siehe Sidebar in der App sowie die Kommentare im Quellcode.  
Gewichtung orientiert sich an häufig genannten öffentlichen Quellen (westlich + vedisch) zu Sudden Wealth / Lottery / Gambling.
