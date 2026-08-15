"""
AstroLotto Score – Experimentelles Scoring-System (v2)
=====================================================
- Präzisere Positionen via skyfield (JPL-Ephemeriden)
- Erweiterte Städteliste mit Koordinaten
- AstroWeather-Score für die nächste Di- und Sa-Ziehung

WICHTIGER HINWEIS:
Dies ist ein Unterhaltungs- und Experimentier-Tool.
Astrologie ist keine wissenschaftlich belegte Methode zur Vorhersage
von Zufallsereignissen wie Lottoziehungen. Lotterien sind (pseudo-)zufällig.
Kein Score erhöht die mathematische Gewinnwahrscheinlichkeit.
"""

import streamlit as st
from datetime import date, datetime, timedelta, timezone
import math
import hashlib

from skyfield.api import load

ts = load.timescale()
eph = load("de421.bsp")

planets = {
    "sun": eph["sun"],
    "moon": eph["moon"],
    "mercury": eph["mercury"],
    "venus": eph["venus"],
    "earth": eph["earth"],
    "mars": eph["mars"],
    "jupiter": eph["jupiter barycenter"],
    "saturn": eph["saturn barycenter"],
    "uranus": eph["uranus barycenter"],
    "neptune": eph["neptune barycenter"],
    "pluto": eph["pluto barycenter"],
}

st.set_page_config(
    page_title="AstroLotto Score",
    page_icon="🍀",
    layout="centered",
    initial_sidebar_state="expanded",
)

CITY_COORDS = {
    "Berlin": (52.5200, 13.4050),
    "Hamburg": (53.5511, 9.9937),
    "München": (48.1351, 11.5820),
    "Köln": (50.9375, 6.9603),
    "Frankfurt am Main": (50.1109, 8.6821),
    "Stuttgart": (48.7758, 9.1829),
    "Düsseldorf": (51.2277, 6.7735),
    "Leipzig": (51.3397, 12.3731),
    "Dortmund": (51.5136, 7.4653),
    "Essen": (51.4556, 7.0116),
    "Bremen": (53.0793, 8.8017),
    "Dresden": (51.0504, 13.7373),
    "Hannover": (52.3759, 9.7320),
    "Nürnberg": (49.4521, 11.0767),
    "Duisburg": (51.4344, 6.7623),
    "Bochum": (51.4818, 7.2162),
    "Wuppertal": (51.2562, 7.1508),
    "Bielefeld": (52.0302, 8.5325),
    "Bonn": (50.7374, 7.0982),
    "Münster": (51.9607, 7.6261),
    "Karlsruhe": (49.0069, 8.4037),
    "Mannheim": (49.4875, 8.4660),
    "Augsburg": (48.3705, 10.8978),
    "Wiesbaden": (50.0782, 8.2398),
    "Mönchengladbach": (51.1805, 6.4428),
    "Gelsenkirchen": (51.5177, 7.0857),
    "Braunschweig": (52.2689, 10.5268),
    "Kiel": (54.3233, 10.1228),
    "Aachen": (50.7753, 6.0839),
    "Magdeburg": (52.1205, 11.6276),
    "Freiburg": (47.9990, 7.8421),
    "Krefeld": (51.3388, 6.5853),
    "Lübeck": (53.8655, 10.6866),
    "Oberhausen": (51.4963, 6.8515),
    "Erfurt": (50.9848, 11.0299),
    "Rostock": (54.0924, 12.0991),
    "Mainz": (49.9929, 8.2473),
    "Kassel": (51.3127, 9.4797),
    "Hagen": (51.3671, 7.4633),
    "Hamm": (51.6739, 7.8159),
    "Saarbrücken": (49.2402, 6.9969),
    "Potsdam": (52.3906, 13.0645),
    "Wien": (48.2082, 16.3738),
    "Graz": (47.0707, 15.4395),
    "Linz": (48.3069, 14.2858),
    "Salzburg": (47.8095, 13.0550),
    "Innsbruck": (47.2692, 11.4041),
    "Zürich": (47.3769, 8.5417),
    "Genf": (46.2044, 6.1432),
    "Basel": (47.5596, 7.5886),
    "Bern": (46.9480, 7.4474),
    "Lausanne": (46.5197, 6.6323),
    "Luxemburg": (49.6116, 6.1319),
    "Amsterdam": (52.3676, 4.9041),
    "Brüssel": (50.8503, 4.3517),
    "Paris": (48.8566, 2.3522),
    "London": (51.5074, -0.1278),
    "Madrid": (40.4168, -3.7038),
    "Barcelona": (41.3874, 2.1686),
    "Rom": (41.9028, 12.4964),
    "Mailand": (45.4642, 9.1900),
    "Lissabon": (38.7223, -9.1393),
    "Prag": (50.0755, 14.4378),
    "Warschau": (52.2297, 21.0122),
    "Budapest": (47.4979, 19.0402),
    "Kopenhagen": (55.6761, 12.5683),
    "Stockholm": (59.3293, 18.0686),
    "Oslo": (59.9139, 10.7522),
    "Helsinki": (60.1699, 24.9384),
    "Dublin": (53.3498, -6.2603),
    "Athen": (37.9838, 23.7275),
    "Istanbul": (41.0082, 28.9784),
    "New York": (40.7128, -74.0060),
    "Los Angeles": (34.0522, -118.2437),
    "Toronto": (43.6532, -79.3832),
    "Dubai": (25.2048, 55.2708),
    "Bangkok": (13.7563, 100.5018),
    "Singapur": (1.3521, 103.8198),
    "Sydney": (-33.8688, 151.2093),
    "Melbourne": (-37.8136, 144.9631),
    "Kapstadt": (-33.9249, 18.4241),
    "Andere / Unbekannt": (50.0, 10.0),
}


def ecliptic_longitude(body_name: str, dt: datetime) -> float:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    t = ts.from_datetime(dt)
    earth = planets["earth"]
    body = planets[body_name]
    astrometric = earth.at(t).observe(body)
    lat, lon, _ = astrometric.ecliptic_latlon()
    return lon.degrees % 360.0


def norm_deg(deg: float) -> float:
    return deg % 360.0


def angle_diff(a: float, b: float) -> float:
    d = abs(norm_deg(a - b))
    return min(d, 360.0 - d)


def is_aspect(lon1: float, lon2: float, aspect_angle: float, orb: float = 8.0) -> bool:
    return abs(angle_diff(lon1, lon2) - aspect_angle) <= orb


def moon_phase_fraction(dt: datetime) -> float:
    sun = ecliptic_longitude("sun", dt)
    moon = ecliptic_longitude("moon", dt)
    return norm_deg(moon - sun) / 360.0


def mercury_retrograde(dt: datetime) -> bool:
    lon0 = ecliptic_longitude("mercury", dt)
    lon1 = ecliptic_longitude("mercury", dt + timedelta(days=1))
    delta = (lon1 - lon0 + 180) % 360 - 180
    return delta < 0


def part_of_fortune(asc: float, sun: float, moon: float, is_day: bool) -> float:
    if is_day:
        return norm_deg(asc + moon - sun)
    return norm_deg(asc + sun - moon)


def approx_ascendant(dt: datetime, lat: float, lon: float) -> float:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    t = ts.from_datetime(dt)
    gast = t.gast * 15.0
    lst = norm_deg(gast + lon)
    eps = 23.439
    asc = math.degrees(
        math.atan2(
            math.cos(math.radians(lst)),
            -(
                math.sin(math.radians(lst)) * math.cos(math.radians(eps))
                + math.tan(math.radians(lat)) * math.sin(math.radians(eps))
            ),
        )
    )
    return norm_deg(asc)


def score_general(dt: datetime) -> tuple[float, list[str]]:
    reasons = []
    points = 50.0

    sun = ecliptic_longitude("sun", dt)
    moon = ecliptic_longitude("moon", dt)
    mercury = ecliptic_longitude("mercury", dt)
    venus = ecliptic_longitude("venus", dt)
    jupiter = ecliptic_longitude("jupiter", dt)
    saturn = ecliptic_longitude("saturn", dt)
    uranus = ecliptic_longitude("uranus", dt)

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

    if is_aspect(uranus, mercury, 0, 6) or is_aspect(uranus, mercury, 120, 7):
        points += 14
        reasons.append("Uranus aktiviert Merkur (Zahlen/Tickets) (+)")
    if is_aspect(uranus, jupiter, 0, 6) or is_aspect(uranus, jupiter, 120, 7):
        points += 13
        reasons.append("Uranus–Jupiter (plötzliches Glück) (+)")
    if is_aspect(uranus, venus, 0, 6):
        points += 9
        reasons.append("Uranus–Venus (unerwarteter Geldfluss) (+)")

    phase = moon_phase_fraction(dt)
    if 0.1 < phase < 0.45:
        points += 7
        reasons.append("Zunehmender Mond (+)")
    elif 0.55 < phase < 0.9:
        points -= 4
        reasons.append("Abnehmender Mond (−)")
    if abs(phase - 0.5) < 0.04:
        points += 5
        reasons.append("Nahe Vollmond (+)")

    if mercury_retrograde(dt):
        points -= 7
        reasons.append("Merkur rückläufig (−)")

    if is_aspect(saturn, jupiter, 90, 6) or is_aspect(saturn, jupiter, 180, 6):
        points -= 9
        reasons.append("Saturn belastet Jupiter (−)")
    if is_aspect(saturn, venus, 90, 6):
        points -= 6
        reasons.append("Saturn–Venus Spannung (−)")

    if is_aspect(venus, jupiter, 120, 7) or is_aspect(venus, jupiter, 60, 5):
        points += 8
        reasons.append("Venus–Jupiter Trigon/Sextil (+)")

    points = max(0.0, min(100.0, points))
    return points, reasons


def score_personal(birth_dt: datetime, query_dt: datetime, lat: float, lon: float) -> tuple[float, list[str]]:
    reasons = []
    points = 48.0

    sun_n = ecliptic_longitude("sun", birth_dt)
    moon_n = ecliptic_longitude("moon", birth_dt)
    mercury_n = ecliptic_longitude("mercury", birth_dt)
    venus_n = ecliptic_longitude("venus", birth_dt)
    jupiter_n = ecliptic_longitude("jupiter", birth_dt)

    asc_n = approx_ascendant(birth_dt, lat, lon)
    is_day_birth = 6 <= birth_dt.hour < 18
    pof = part_of_fortune(asc_n, sun_n, moon_n, is_day_birth)

    jupiter_t = ecliptic_longitude("jupiter", query_dt)
    uranus_t = ecliptic_longitude("uranus", query_dt)
    venus_t = ecliptic_longitude("venus", query_dt)
    saturn_t = ecliptic_longitude("saturn", query_dt)
    moon_t = ecliptic_longitude("moon", query_dt)

    if is_aspect(jupiter_t, sun_n, 0, 6) or is_aspect(jupiter_t, sun_n, 120, 7):
        points += 14
        reasons.append("Jupiter-Transit zur radix Sonne (+)")
    if is_aspect(jupiter_t, moon_n, 0, 6) or is_aspect(jupiter_t, moon_n, 120, 7):
        points += 12
        reasons.append("Jupiter-Transit zum radix Mond (+)")
    if is_aspect(jupiter_t, venus_n, 0, 6) or is_aspect(jupiter_t, venus_n, 120, 7):
        points += 11
        reasons.append("Jupiter-Transit zur radix Venus (+)")
    if is_aspect(jupiter_t, jupiter_n, 0, 5):
        points += 15
        reasons.append("Jupiter-Return / Rückkehr-Nähe (+)")

    if is_aspect(jupiter_t, pof, 0, 6) or is_aspect(jupiter_t, pof, 120, 7):
        points += 13
        reasons.append("Jupiter aktiviert Part of Fortune (+)")
    if is_aspect(uranus_t, pof, 0, 5) or is_aspect(uranus_t, pof, 120, 6):
        points += 12
        reasons.append("Uranus aktiviert Part of Fortune (+)")
    if is_aspect(moon_t, pof, 0, 5):
        points += 7
        reasons.append("Mond über Part of Fortune (+)")

    if is_aspect(uranus_t, mercury_n, 0, 5) or is_aspect(uranus_t, mercury_n, 120, 6):
        points += 13
        reasons.append("Uranus auf radix Merkur (Tickets/Zahlen) (+)")
    if is_aspect(uranus_t, jupiter_n, 0, 5) or is_aspect(uranus_t, jupiter_n, 120, 6):
        points += 12
        reasons.append("Uranus auf radix Jupiter (+)")
    if is_aspect(uranus_t, venus_n, 0, 5):
        points += 9
        reasons.append("Uranus auf radix Venus (+)")

    if is_aspect(saturn_t, jupiter_n, 90, 6) or is_aspect(saturn_t, jupiter_n, 180, 6):
        points -= 10
        reasons.append("Saturn belastet radix Jupiter (−)")
    if is_aspect(saturn_t, pof, 90, 5) or is_aspect(saturn_t, pof, 180, 5):
        points -= 8
        reasons.append("Saturn belastet Part of Fortune (−)")

    if is_aspect(venus_t, jupiter_n, 120, 6) or is_aspect(venus_t, jupiter_n, 0, 5):
        points += 8
        reasons.append("Venus-Transit zu radix Jupiter (+)")

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
        return "#2e7d32"
    if score >= 50:
        return "#f9a825"
    return "#c62828"


def next_weekday(d: date, weekday: int) -> date:
    days_ahead = (weekday - d.weekday()) % 7
    return d + timedelta(days=days_ahead)


def mock_jackpot_info(d: date) -> dict:
    seed = int(d.strftime("%Y%m%d"))
    h = hashlib.md5(str(seed).encode()).hexdigest()
    base = int(h[:6], 16) % 40 + 5
    tue = next_weekday(d, 1)
    sat = next_weekday(d, 5)
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


st.title("🍀 AstroLotto Score")
st.caption("Präzisere Ephemeriden (skyfield) · Erweiterte Städte · AstroWeather für Di & Sa")

with st.expander("⚠️ Wichtiger Hinweis – bitte lesen", expanded=False):
    st.markdown(
        """
        Dieses Tool ist **rein experimentell und zur Unterhaltung** gedacht.  
        Astrologie ist **keine wissenschaftlich belegte Methode**, um Zufallsereignisse 
        wie Lottoziehungen vorherzusagen. Die Gewinnwahrscheinlichkeit bleibt 
        mathematisch unverändert extrem niedrig.  

        Planetenpositionen werden mit **skyfield** (JPL DE421) berechnet.  
        Aszendent und Part of Fortune sind weiterhin Näherungen.  
        Jackpot- und Teilnehmerzahlen sind Platzhalter.
        """
    )

st.markdown("---")
st.subheader("Persönliche Daten")

col1, col2, col3 = st.columns(3)
with col1:
    birth_date = st.date_input("Geburtsdatum", value=date(1990, 5, 15))
with col2:
    birth_time = st.time_input("Geburtsuhrzeit", value=datetime.strptime("12:00", "%H:%M").time())
with col3:
    query_date = st.date_input("Abfrage-Datum", value=date.today())

city_names = sorted(CITY_COORDS.keys())
default_idx = city_names.index("Berlin") if "Berlin" in city_names else 0
city_choice = st.selectbox(
    "Geburtsort (Koordinaten)",
    city_names,
    index=default_idx,
    help="Nächstgelegene Stadt wählen. Sonst „Andere / Unbekannt“.",
)
lat, lon = CITY_COORDS[city_choice]
st.caption(f"Koordinaten: {lat:.4f}°, {lon:.4f}° · {len(CITY_COORDS)} Städte verfügbar")

st.markdown("---")

if st.button("Score berechnen", type="primary", use_container_width=True):
    with st.spinner("Berechne Planetenpositionen (skyfield) …"):
        birth_dt = datetime.combine(birth_date, birth_time).replace(tzinfo=timezone.utc)
        query_dt = datetime.combine(query_date, datetime.strptime("12:00", "%H:%M").time()).replace(
            tzinfo=timezone.utc
        )

        gen_score, gen_reasons = score_general(query_dt)
        per_score, per_reasons = score_personal(birth_dt, query_dt, lat, lon)
        comb_score = (gen_score + per_score) / 2.0

        jack = mock_jackpot_info(query_date)

        tue_dt = datetime.combine(jack["tuesday"]["date"], datetime.strptime("18:00", "%H:%M").time()).replace(
            tzinfo=timezone.utc
        )
        sat_dt = datetime.combine(jack["saturday"]["date"], datetime.strptime("18:00", "%H:%M").time()).replace(
            tzinfo=timezone.utc
        )

        gen_tue, _ = score_general(tue_dt)
        per_tue, _ = score_personal(birth_dt, tue_dt, lat, lon)
        comb_tue = (gen_tue + per_tue) / 2.0

        gen_sat, _ = score_general(sat_dt)
        per_sat, _ = score_personal(birth_dt, sat_dt, lat, lon)
        comb_sat = (gen_sat + per_sat) / 2.0

    st.markdown("## Ergebnis für Abfrage-Datum")

    st.markdown(
        f"""
        <div style="text-align:center; padding:1.2rem; border-radius:12px; 
                    background:linear-gradient(135deg,#f5f5f5,#e8f5e9); 
                    border:2px solid {score_color(comb_score)}; margin-bottom:1.5rem;">
            <div style="font-size:1.1rem; color:#555;">Kombinierter AstroScore</div>
            <div style="font-size:3rem; font-weight:800; color:{score_color(comb_score)}; line-height:1.1;">
                {comb_score:.1f} %
            </div>
            <div style="font-size:1.8rem; margin-top:0.3rem;">{luck_symbol(comb_score)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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

    st.markdown("---")
    st.subheader("AstroWeather – Nächste Ziehungen")

    tcol, scol = st.columns(2)
    with tcol:
        st.markdown(
            f"""
            <div style="text-align:center; padding:1rem; border-radius:10px; 
                        background:#fff8e1; border:2px solid {score_color(comb_tue)};">
                <div style="font-size:0.9rem; color:#666;">Dienstag {jack['tuesday']['date'].strftime('%d.%m.%Y')}</div>
                <div style="font-size:1.6rem; font-weight:800; color:{score_color(comb_tue)};">
                    {comb_tue:.1f} %
                </div>
                <div style="font-size:1.3rem;">{luck_symbol(comb_tue)}</div>
                <div style="font-size:0.85rem; color:#555; margin-top:0.4rem;">
                    Jackpot ≈ {jack['tuesday']['jackpot_mio']} Mio. €<br>
                    Tipps ≈ {jack['tuesday']['tips_mio']} Mio.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with scol:
        st.markdown(
            f"""
            <div style="text-align:center; padding:1rem; border-radius:10px; 
                        background:#e3f2fd; border:2px solid {score_color(comb_sat)};">
                <div style="font-size:0.9rem; color:#666;">Samstag {jack['saturday']['date'].strftime('%d.%m.%Y')}</div>
                <div style="font-size:1.6rem; font-weight:800; color:{score_color(comb_sat)};">
                    {comb_sat:.1f} %
                </div>
                <div style="font-size:1.3rem;">{luck_symbol(comb_sat)}</div>
                <div style="font-size:0.85rem; color:#555; margin-top:0.4rem;">
                    Jackpot ≈ {jack['saturday']['jackpot_mio']} Mio. €<br>
                    Tipps ≈ {jack['saturday']['tips_mio']} Mio.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("Allgemeine Faktoren (Abfrage-Datum)"):
        if gen_reasons:
            for r in gen_reasons:
                st.write("• " + r)
        else:
            st.write("Keine besonders starken allgemeinen Faktoren.")

    with st.expander("Persönliche Faktoren (Abfrage-Datum)"):
        if per_reasons:
            for r in per_reasons:
                st.write("• " + r)
        else:
            st.write("Keine besonders starken persönlichen Faktoren.")

    st.markdown("---")
    st.caption(
        "Ephemeriden: skyfield + JPL DE421. "
        "Aszendent/PoF vereinfacht. Jackpot/Tipps = Platzhalter. "
        "Nur zur Unterhaltung – keine Gewinngarantie."
    )

else:
    st.info("Daten eingeben und auf **Score berechnen** klicken.")

with st.sidebar:
    st.header("Regelwerk (Kurz)")
    st.markdown(
        """
        **50 % Allgemein + 50 % Persönlich**

        **Allgemein:**  
        Jupiter-Aspekte, Uranus an Merkur/Jupiter/Venus,  
        Mondphase, Merkur-Rückläufigkeit, Saturn-Belastungen

        **Persönlich:**  
        Jupiter-Transite zu Sonne/Mond/Venus/Jupiter,  
        Part of Fortune, Uranus auf radix Merkur/Jupiter/Venus

        **AstroWeather Di / Sa:**  
        Kombinierter Score für den jeweiligen  
        Ziehungsabend (18:00 UTC).

        **Häuser-Tradition:**  
        5 (Spekulation), 8 (plötzliche Gewinne),  
        11 (große Zugewinne), 2 (Vermögen)
        """
    )
    st.markdown("---")
    st.caption(f"{len(CITY_COORDS)} Städte verfügbar")
    st.caption("Nur zur Unterhaltung.")
