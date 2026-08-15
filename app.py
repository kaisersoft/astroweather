"""
AstroLotto Score – Experimentelles Scoring-System
=================================================
Basierend auf öffentlich zugänglichen astrologischen Traditionen
(Jupiter, Uranus, 5./8./11. Haus, Part of Fortune etc.).

WICHTIGER HINWEIS:
Dies ist ein Unterhaltungs- und Experimentier-Tool.
Astrologie ist keine wissenschaftlich belegte Methode zur Vorhersage
von Zufallsereignissen wie Lottoziehungen. Lotterien sind (pseudo-)zufällig.
Kein Score erhöht die mathematische Gewinnwahrscheinlichkeit.
"""

import streamlit as st
from datetime import date, datetime, timedelta
import math
import hashlib

# -------------------------------------------------
# Seiten-Konfiguration
# -------------------------------------------------
st.set_page_config(
    page_title="AstroLotto Score",
    page_icon="🍀",
    layout="centered",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------
# Hilfsfunktionen – vereinfachte Ephemeriden-Näherung
# (Für ein echtes Produktionssystem sollte Swiss Ephemeris / skyfield genutzt werden)
# -------------------------------------------------

def julian_day(dt: datetime) -> float:
    """Einfache Julian-Day-Berechnung."""
    a = (14 - dt.month) // 12
    y = dt.year + 4800 - a
    m = dt.month + 12 * a - 3
    jdn = dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    frac = (dt.hour - 12) / 24 + dt.minute / 1440 + dt.second / 86400
    return jdn + frac


def norm_deg(deg: float) -> float:
    return deg % 360.0


def approx_planet_longitude(planet: str, jd: float) -> float:
    """
    Grobe Näherung der ekliptikalen Länge (für Demo-Zwecke).
    Basiert auf mittleren Bewegungen – nicht ephemeris-genau.
    """
    # Epoche J2000 ≈ JD 2451545.0
    T = (jd - 2451545.0) / 36525.0

    # Mittlere Längen (vereinfacht)
    if planet == "sun":
        return norm_deg(280.460 + 36000.770 * T)
    elif planet == "moon":
        return norm_deg(218.316 + 481267.881 * T)
    elif planet == "mercury":
        return norm_deg(252.251 + 149472.674 * T)
    elif planet == "venus":
        return norm_deg(181.980 + 58517.815 * T)
    elif planet == "mars":
        return norm_deg(355.433 + 19140.299 * T)
    elif planet == "jupiter":
        return norm_deg(34.351 + 3034.906 * T)
    elif planet == "saturn":
        return norm_deg(50.077 + 1222.114 * T)
    elif planet == "uranus":
        return norm_deg(314.055 + 428.495 * T)
    elif planet == "neptune":
        return norm_deg(304.880 + 218.459 * T)
    elif planet == "pluto":
        return norm_deg(238.929 + 145.208 * T)
    return 0.0


def angle_diff(a: float, b: float) -> float:
    """Kleinste Winkeldifferenz (0–180)."""
    d = abs(norm_deg(a - b))
    return min(d, 360 - d)


def is_aspect(lon1: float, lon2: float, aspect_angle: float, orb: float = 8.0) -> bool:
    return abs(angle_diff(lon1, lon2) - aspect_angle) <= orb


def moon_phase_fraction(jd: float) -> float:
    """0 = Neumond, 0.5 = Vollmond."""
    sun = approx_planet_longitude("sun", jd)
    moon = approx_planet_longitude("moon", jd)
    return norm_deg(moon - sun) / 360.0


# -------------------------------------------------
# Part of Fortune (vereinfacht)
# -------------------------------------------------
def part_of_fortune(asc: float, sun: float, moon: float, is_day: bool) -> float:
    """
    Klassische Formel:
    Tag:  ASC + Mond - Sonne
    Nacht: ASC + Sonne - Mond
    """
    if is_day:
        return norm_deg(asc + moon - sun)
    return norm_deg(asc + sun - moon)


# -------------------------------------------------
# Scoring-Logik (erweitertes Regelwerk)
# -------------------------------------------------

def score_general(dt: datetime) -> tuple[float, list[str]]:
    """
    Allgemeiner Tages-Score (0–100) auf Basis öffentlicher Traditionen.
    """
    jd = julian_day(dt)
    reasons = []
    points = 50.0  # Basis

    sun = approx_planet_longitude("sun", jd)
    moon = approx_planet_longitude("moon", jd)
    mercury = approx_planet_longitude("mercury", jd)
    venus = approx_planet_longitude("venus", jd)
    jupiter = approx_planet_longitude("jupiter", jd)
    saturn = approx_planet_longitude("saturn", jd)
    uranus = approx_planet_longitude("uranus", jd)

    # --- Jupiter-Aspekte (sehr stark gewichtet) ---
    if is_aspect(jupiter, sun, 120, 8) or is_aspect(jupiter, sun, 60, 6):
        points += 12
        reasons.append("Jupiter harmonisch zur Sonne (+)")
    if is_aspect(jupiter, moon, 120, 8) or is_aspect(jupiter, moon, 60, 6):
        points += 10
        reasons.append("Jupiter harmonisch zum Mond (+)")
    if is_aspect(jupiter, venus, 120, 8) or is_aspect(jupiter, venus, 0, 6):
        points += 11
        reasons.append("Jupiter–Venus Glücksaspekt (+)")
    if is_aspect(jupiter, sun, 90, 7) or is_aspect(jupiter, sun, 180, 7):
        points -= 8
        reasons.append("Jupiter hart zur Sonne (−)")

    # --- Uranus (plötzliche Ereignisse) ---
    if is_aspect(uranus, mercury, 0, 6) or is_aspect(uranus, mercury, 120, 7):
        points += 14
        reasons.append("Uranus aktiviert Merkur (Zahlen/Tickets) (+)")
    if is_aspect(uranus, jupiter, 0, 6) or is_aspect(uranus, jupiter, 120, 7):
        points += 13
        reasons.append("Uranus–Jupiter (plötzliches Glück) (+)")
    if is_aspect(uranus, venus, 0, 6):
        points += 9
        reasons.append("Uranus–Venus (unerwarteter Geldfluss) (+)")

    # --- Mondphase ---
    phase = moon_phase_fraction(jd)
    if 0.1 < phase < 0.45:  # zunehmend
        points += 7
        reasons.append("Zunehmender Mond (+)")
    elif 0.55 < phase < 0.9:  # abnehmend
        points -= 4
        reasons.append("Abnehmender Mond (−)")
    if abs(phase - 0.5) < 0.04:  # nahe Vollmond
        points += 5
        reasons.append("Nahe Vollmond (+)")

    # --- Merkur rückläufig (grobe Näherung über relative Bewegung) ---
    # Vereinfachte Heuristik: wenn Merkur „langsam“ erscheint
    merc_speed_proxy = abs((approx_planet_longitude("mercury", jd + 1) - mercury + 180) % 360 - 180)
    if merc_speed_proxy < 0.3:
        points -= 7
        reasons.append("Merkur wirkt rückläufig/langsam (−)")

    # --- Saturn-Belastung ---
    if is_aspect(saturn, jupiter, 90, 6) or is_aspect(saturn, jupiter, 180, 6):
        points -= 9
        reasons.append("Saturn belastet Jupiter (−)")
    if is_aspect(saturn, venus, 90, 6):
        points -= 6
        reasons.append("Saturn–Venus Spannung (−)")

    # --- Venus–Jupiter klassischer Glücksaspekt ---
    if is_aspect(venus, jupiter, 120, 7) or is_aspect(venus, jupiter, 60, 5):
        points += 8
        reasons.append("Venus–Jupiter Trigon/Sextil (+)")

    # Clamp
    points = max(0.0, min(100.0, points))
    return points, reasons


def score_personal(birth_dt: datetime, query_dt: datetime, lat: float, lon: float) -> tuple[float, list[str]]:
    """
    Persönlicher Score (0–100).
    Nutzt genäherte Radix-Positionen + aktuelle Transite.
    """
    reasons = []
    points = 48.0

    # Radix (Geburt)
    jd_birth = julian_day(birth_dt)
    sun_n = approx_planet_longitude("sun", jd_birth)
    moon_n = approx_planet_longitude("moon", jd_birth)
    mercury_n = approx_planet_longitude("mercury", jd_birth)
    venus_n = approx_planet_longitude("venus", jd_birth)
    jupiter_n = approx_planet_longitude("jupiter", jd_birth)
    uranus_n = approx_planet_longitude("uranus", jd_birth)

    # Sehr grobe Aszendenten-Näherung (Local Sidereal Time proxy)
    # Für Demo: aus Länge und Uhrzeit abgeleitet
    jd_q = julian_day(query_dt)
    lst_proxy = norm_deg(approx_planet_longitude("sun", jd_q) + (query_dt.hour + query_dt.minute / 60) * 15 + lon)
    asc_proxy = lst_proxy  # stark vereinfacht

    is_day_birth = 6 <= birth_dt.hour < 18
    pof = part_of_fortune(asc_proxy, sun_n, moon_n, is_day_birth)

    # Aktuelle Transite
    sun_t = approx_planet_longitude("sun", jd_q)
    moon_t = approx_planet_longitude("moon", jd_q)
    jupiter_t = approx_planet_longitude("jupiter", jd_q)
    uranus_t = approx_planet_longitude("uranus", jd_q)
    venus_t = approx_planet_longitude("venus", jd_q)
    saturn_t = approx_planet_longitude("saturn", jd_q)

    # --- Jupiter-Transit über persönliche Punkte ---
    if is_aspect(jupiter_t, sun_n, 0, 6) or is_aspect(jupiter_t, sun_n, 120, 7):
        points += 14
        reasons.append("Jupiter-Transit zur radix Sonne (+)")
    if is_aspect(jupiter_t, moon_n, 0, 6) or is_aspect(jupiter_t, moon_n, 120, 7):
        points += 12
        reasons.append("Jupiter-Transit zum radix Mond (+)")
    if is_aspect(jupiter_t, venus_n, 0, 6) or is_aspect(jupiter_t, venus_n, 120, 7):
        points += 11
        reasons.append("Jupiter-Transit zur radix Venus (+)")
    if is_aspect(jupiter_t, jupiter_n, 0, 5):  # Jupiter-Return Nähe
        points += 15
        reasons.append("Jupiter-Return / Rückkehr-Nähe (+)")

    # --- Part of Fortune Aktivierung ---
    if is_aspect(jupiter_t, pof, 0, 6) or is_aspect(jupiter_t, pof, 120, 7):
        points += 13
        reasons.append("Jupiter aktiviert Part of Fortune (+)")
    if is_aspect(uranus_t, pof, 0, 5) or is_aspect(uranus_t, pof, 120, 6):
        points += 12
        reasons.append("Uranus aktiviert Part of Fortune (+)")
    if is_aspect(moon_t, pof, 0, 5):
        points += 7
        reasons.append("Mond über Part of Fortune (+)")

    # --- Uranus auf persönliche Planeten ---
    if is_aspect(uranus_t, mercury_n, 0, 5) or is_aspect(uranus_t, mercury_n, 120, 6):
        points += 13
        reasons.append("Uranus auf radix Merkur (Tickets/Zahlen) (+)")
    if is_aspect(uranus_t, jupiter_n, 0, 5) or is_aspect(uranus_t, jupiter_n, 120, 6):
        points += 12
        reasons.append("Uranus auf radix Jupiter (+)")
    if is_aspect(uranus_t, venus_n, 0, 5):
        points += 9
        reasons.append("Uranus auf radix Venus (+)")

    # --- Saturn-Belastungen ---
    if is_aspect(saturn_t, jupiter_n, 90, 6) or is_aspect(saturn_t, jupiter_n, 180, 6):
        points -= 10
        reasons.append("Saturn belastet radix Jupiter (−)")
    if is_aspect(saturn_t, pof, 90, 5) or is_aspect(saturn_t, pof, 180, 5):
        points -= 8
        reasons.append("Saturn belastet Part of Fortune (−)")

    # --- Venus-Transit ---
    if is_aspect(venus_t, jupiter_n, 120, 6) or is_aspect(venus_t, jupiter_n, 0, 5):
        points += 8
        reasons.append("Venus-Transit zu radix Jupiter (+)")

    # --- Mond-Transit über persönliche Glücksfaktoren ---
    if is_aspect(moon_t, jupiter_n, 0, 5) or is_aspect(moon_t, jupiter_n, 120, 6):
        points += 6
        reasons.append("Mond–Jupiter persönlich (+)")

    points = max(0.0, min(100.0, points))
    return points, reasons


def luck_symbol(score: float) -> str:
    if score >= 80:
        return "🍀🍀🍀"
    if score >= 65:
        return "🍀🍀"
    if score >= 50:
        return "🍀"
    if score >= 35:
        return "🌱"
    return "🌑"


def score_color(score: float) -> str:
    if score >= 70:
        return "#2e7d32"  # grün
    if score >= 50:
        return "#f9a825"  # gelb
    return "#c62828"  # rot


# -------------------------------------------------
# Mock-Daten für Jackpot / Teilnehmer (Platzhalter)
# -------------------------------------------------
def mock_jackpot_info(d: date) -> dict:
    """
    Platzhalter – in einer echten App würden hier offizielle Lotto-APIs
    oder Scraping-Ergebnisse eingespeist.
    """
    # Deterministische „Zufalls“-Werte aus dem Datum
    seed = int(d.strftime("%Y%m%d"))
    h = hashlib.md5(str(seed).encode()).hexdigest()
    base = int(h[:6], 16) % 40 + 5  # 5–45 Mio

    # Dienstag / Samstag relativ zum Abfrage-Tag
    weekday = d.weekday()  # 0=Mo … 6=So
    days_to_tue = (1 - weekday) % 7
    days_to_sat = (5 - weekday) % 7
    if days_to_tue == 0:
        days_to_tue = 7
    if days_to_sat == 0:
        days_to_sat = 7

    tue = d + timedelta(days=days_to_tue)
    sat = d + timedelta(days=days_to_sat)

    return {
        "tuesday": {
            "date": tue,
            "jackpot_mio": round(base + (int(h[6:8], 16) % 10), 1),
            "tips_mio": round(18 + (int(h[8:10], 16) % 15), 1),
        },
        "saturday": {
            "date": sat,
            "jackpot_mio": round(base + 8 + (int(h[10:12], 16) % 12), 1),
            "tips_mio": round(28 + (int(h[12:14], 16) % 20), 1),
        },
    }


# -------------------------------------------------
# Streamlit UI
# -------------------------------------------------
st.title("🍀 AstroLotto Score")
st.caption("Experimentelles Scoring auf Basis öffentlicher astrologischer Traditionen")

with st.expander("⚠️ Wichtiger Hinweis – bitte lesen", expanded=False):
    st.markdown(
        """
        Dieses Tool ist **rein experimentell und zur Unterhaltung** gedacht.  
        Astrologie ist **keine wissenschaftlich belegte Methode**, um Zufallsereignisse 
        wie Lottoziehungen vorherzusagen. Die Gewinnwahrscheinlichkeit bleibt 
        mathematisch unverändert extrem niedrig.  

        Das Scoring orientiert sich an öffentlich diskutierten Traditionen 
        (Jupiter, Uranus, 5./8./11. Haus, Part of Fortune usw.) und stellt 
        **kein Prognoseinstrument** dar.
        """
    )

st.markdown("---")

# --- Eingaben ---
st.subheader("Persönliche Daten (für Personal Score)")
col1, col2, col3 = st.columns(3)

with col1:
    birth_date = st.date_input("Geburtsdatum", value=date(1990, 5, 15))
with col2:
    birth_time = st.time_input("Geburtsuhrzeit", value=datetime.strptime("12:00", "%H:%M").time())
with col3:
    query_date = st.date_input("Abfrage-Datum (Score für diesen Tag)", value=date.today())

col4, col5 = st.columns(2)
with col4:
    birth_city = st.text_input("Geburtsort (Stadt)", value="Berlin")
with col5:
    # Grobe Koordinaten-Auswahl über bekannte Städte (Demo)
    city_coords = {
        "Berlin": (52.52, 13.41),
        "München": (48.14, 11.58),
        "Hamburg": (53.55, 9.99),
        "Köln": (50.94, 6.96),
        "Frankfurt": (50.11, 8.68),
        "Wien": (48.21, 16.37),
        "Zürich": (47.37, 8.54),
        "Andere / Unbekannt": (50.0, 10.0),
    }
    city_choice = st.selectbox("Koordinaten-Vorlage", list(city_coords.keys()), index=0)
    lat, lon = city_coords[city_choice]

st.markdown("---")

if st.button("Score berechnen", type="primary", use_container_width=True):
    birth_dt = datetime.combine(birth_date, birth_time)
    query_dt = datetime.combine(query_date, datetime.strptime("12:00", "%H:%M").time())

    gen_score, gen_reasons = score_general(query_dt)
    per_score, per_reasons = score_personal(birth_dt, query_dt, lat, lon)
    comb_score = (gen_score + per_score) / 2.0

    jack = mock_jackpot_info(query_date)

    # ---------- Ergebnis-Anzeige ----------
    st.markdown("## Ergebnis")

    # Kombinierter Score – prominent, fett, oben
    comb_symbol = luck_symbol(comb_score)
    comb_col = score_color(comb_score)
    st.markdown(
        f"""
        <div style="text-align:center; padding:1.2rem; border-radius:12px; 
                    background:linear-gradient(135deg,#f5f5f5,#e8f5e9); 
                    border:2px solid {comb_col}; margin-bottom:1.5rem;">
            <div style="font-size:1.1rem; color:#555;">Kombinierter AstroScore</div>
            <div style="font-size:3rem; font-weight:800; color:{comb_col}; line-height:1.1;">
                {comb_score:.1f} %
            </div>
            <div style="font-size:1.8rem; margin-top:0.3rem;">{comb_symbol}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Die beiden Einzel-Scores
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"""
            <div style="text-align:center; padding:1rem; border-radius:10px; background:#fafafa; border:1px solid #ddd;">
                <div style="font-size:0.95rem; color:#666;">Allgemeiner Score</div>
                <div style="font-size:2rem; font-weight:700; color:{score_color(gen_score)};">
                    {gen_score:.1f} %
                </div>
                <div style="font-size:1.4rem;">{luck_symbol(gen_score)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div style="text-align:center; padding:1rem; border-radius:10px; background:#fafafa; border:1px solid #ddd;">
                <div style="font-size:0.95rem; color:#666;">Persönlicher Score</div>
                <div style="font-size:2rem; font-weight:700; color:{score_color(per_score)};">
                    {per_score:.1f} %
                </div>
                <div style="font-size:1.4rem;">{luck_symbol(per_score)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("")

    # Jackpot-Infos
    st.subheader("Nächste Ziehungen (Platzhalter-Daten)")
    j1, j2 = st.columns(2)
    with j1:
        st.metric(
            label=f"Dienstag ({jack['tuesday']['date'].strftime('%d.%m.%Y')})",
            value=f"{jack['tuesday']['jackpot_mio']} Mio. €",
            delta=f"≈ {jack['tuesday']['tips_mio']} Mio. Tipps",
        )
    with j2:
        st.metric(
            label=f"Samstag ({jack['saturday']['date'].strftime('%d.%m.%Y')})",
            value=f"{jack['saturday']['jackpot_mio']} Mio. €",
            delta=f"≈ {jack['saturday']['tips_mio']} Mio. Tipps",
        )

    # Begründungen
    with st.expander("Allgemeine Faktoren (Transite des Tages)"):
        if gen_reasons:
            for r in gen_reasons:
                st.write("• " + r)
        else:
            st.write("Keine besonders starken allgemeinen Faktoren.")

    with st.expander("Persönliche Faktoren (Transite zum Radix)"):
        if per_reasons:
            for r in per_reasons:
                st.write("• " + r)
        else:
            st.write("Keine besonders starken persönlichen Faktoren.")

    st.markdown("---")
    st.caption(
        "Hinweis: Planetenpositionen sind Näherungswerte (Demo). "
        "Für höhere Genauigkeit Swiss Ephemeris / skyfield einbinden. "
        "Jackpot- und Teilnehmerzahlen sind Platzhalter."
    )

else:
    st.info("Geburtsdaten eingeben und auf **Score berechnen** klicken.")

# Sidebar – kurzes Regelwerk
with st.sidebar:
    st.header("Regelwerk (Kurz)")
    st.markdown(
        """
        **50 % Allgemein + 50 % Persönlich**

        **Allgemein u. a.:**
        - Jupiter-Aspekte (Sonne, Mond, Venus)
        - Uranus an Merkur / Jupiter / Venus
        - Mondphase
        - Merkur-Status
        - Saturn-Belastungen

        **Persönlich u. a.:**
        - Jupiter-Transit zu Sonne, Mond, Venus, Jupiter
        - Aktivierung des Part of Fortune
        - Uranus auf radix Merkur / Jupiter / Venus
        - Saturn-Belastungen am Glückspunkt

        **Häuser-Bezug (Tradition):**  
        5. (Spekulation), 8. (plötzliche Gewinne),  
        11. (große Zugewinne), 2. (Vermögen)
        """
    )
    st.markdown("---")
    st.caption("Nur zur Unterhaltung. Keine Gewinngarantie.")
