"""
AstroLotto Score v5 – Clean Fortune UI
======================================
- skyfield (JPL DE421) für Planetenpositionen
- 80+ Städte mit echten Zeitzonen (zoneinfo)
- Porphyry-Häuser + verbesserter Aszendent/MC
- Void of Course Mond, genaue Mondaspekte
- Merkur: Stationär, Verbrennung, Aspekte, Hausstellung
- Anwendende vs. scheidende Aspekte + Aspektmuster
  (Großes Trigon, T-Quadrat, Yod)
- Tagesherrscher + Planetenstunden
- Part of Fortune, Lot of Spirit, Nordknoten, Chiron-Näherung
- Sekundärprogressiver Mond + progressiver ASC
- Solar Return (vereinfacht)
- AstroWeather, 14-Tage-Verlauf, Hochscore >75 %
- Sonnen-/Mondfinsternisse (Knotenorb, 3-Tage-Fenster)
- Abgabefrist + Countdown (heutige Tippabgabe)
- Ephemeriden-Cache
- Google-Kalender-Export (.ics, Erinnerung 09:00)
- UI: Clean Fortune Dashboard (Sidebar + Metric-Cards)

NUR ZUR UNTERHALTUNG – keine Gewinngarantie.
"""

import streamlit as st
from datetime import date, datetime, timedelta, timezone, time
from zoneinfo import ZoneInfo
import math
import random
import time as time_module

import streamlit.components.v1 as components
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

DAY_RULERS = {
    0: ("Mond", "moon"),
    1: ("Mars", "mars"),
    2: ("Merkur", "mercury"),
    3: ("Jupiter", "jupiter"),
    4: ("Venus", "venus"),
    5: ("Saturn", "saturn"),
    6: ("Sonne", "sun"),
}

HOUR_SEQUENCE = ["saturn", "jupiter", "mars", "sun", "venus", "mercury", "moon"]

SIGN_RULERS = {
    0: "mars", 1: "venus", 2: "mercury", 3: "moon",
    4: "sun", 5: "mercury", 6: "venus", 7: "mars",
    8: "jupiter", 9: "saturn", 10: "saturn", 11: "jupiter",
}

BODY_NAMES_DE = {
    "sun": "Sonne", "moon": "Mond", "mercury": "Merkur", "venus": "Venus",
    "mars": "Mars", "jupiter": "Jupiter", "saturn": "Saturn",
    "uranus": "Uranus", "neptune": "Neptun", "pluto": "Pluto",
    "north_node": "Nordknoten", "chiron": "Chiron",
}

st.set_page_config(
    page_title="AstroLotto Score",
    page_icon="🍀",
    layout="wide",
    initial_sidebar_state="expanded",
)

CITY_DATA = {
    "Berlin": (52.5200, 13.4050, "Europe/Berlin"),
    "Hamburg": (53.5511, 9.9937, "Europe/Berlin"),
    "München": (48.1351, 11.5820, "Europe/Berlin"),
    "Köln": (50.9375, 6.9603, "Europe/Berlin"),
    "Frankfurt am Main": (50.1109, 8.6821, "Europe/Berlin"),
    "Stuttgart": (48.7758, 9.1829, "Europe/Berlin"),
    "Düsseldorf": (51.2277, 6.7735, "Europe/Berlin"),
    "Leipzig": (51.3397, 12.3731, "Europe/Berlin"),
    "Dortmund": (51.5136, 7.4653, "Europe/Berlin"),
    "Essen": (51.4556, 7.0116, "Europe/Berlin"),
    "Bremen": (53.0793, 8.8017, "Europe/Berlin"),
    "Dresden": (51.0504, 13.7373, "Europe/Berlin"),
    "Hannover": (52.3759, 9.7320, "Europe/Berlin"),
    "Nürnberg": (49.4521, 11.0767, "Europe/Berlin"),
    "Duisburg": (51.4344, 6.7623, "Europe/Berlin"),
    "Bochum": (51.4818, 7.2162, "Europe/Berlin"),
    "Wuppertal": (51.2562, 7.1508, "Europe/Berlin"),
    "Bielefeld": (52.0302, 8.5325, "Europe/Berlin"),
    "Bonn": (50.7374, 7.0982, "Europe/Berlin"),
    "Münster": (51.9607, 7.6261, "Europe/Berlin"),
    "Karlsruhe": (49.0069, 8.4037, "Europe/Berlin"),
    "Mannheim": (49.4875, 8.4660, "Europe/Berlin"),
    "Augsburg": (48.3705, 10.8978, "Europe/Berlin"),
    "Wiesbaden": (50.0782, 8.2398, "Europe/Berlin"),
    "Mönchengladbach": (51.1805, 6.4428, "Europe/Berlin"),
    "Gelsenkirchen": (51.5177, 7.0857, "Europe/Berlin"),
    "Braunschweig": (52.2689, 10.5268, "Europe/Berlin"),
    "Kiel": (54.3233, 10.1228, "Europe/Berlin"),
    "Aachen": (50.7753, 6.0839, "Europe/Berlin"),
    "Magdeburg": (52.1205, 11.6276, "Europe/Berlin"),
    "Freiburg": (47.9990, 7.8421, "Europe/Berlin"),
    "Krefeld": (51.3388, 6.5853, "Europe/Berlin"),
    "Lübeck": (53.8655, 10.6866, "Europe/Berlin"),
    "Oberhausen": (51.4963, 6.8515, "Europe/Berlin"),
    "Erfurt": (50.9848, 11.0299, "Europe/Berlin"),
    "Rostock": (54.0924, 12.0991, "Europe/Berlin"),
    "Mainz": (49.9929, 8.2473, "Europe/Berlin"),
    "Kassel": (51.3127, 9.4797, "Europe/Berlin"),
    "Hagen": (51.3671, 7.4633, "Europe/Berlin"),
    "Hamm": (51.6739, 7.8159, "Europe/Berlin"),
    "Saarbrücken": (49.2402, 6.9969, "Europe/Berlin"),
    "Potsdam": (52.3906, 13.0645, "Europe/Berlin"),
    "Wien": (48.2082, 16.3738, "Europe/Vienna"),
    "Graz": (47.0707, 15.4395, "Europe/Vienna"),
    "Linz": (48.3069, 14.2858, "Europe/Vienna"),
    "Salzburg": (47.8095, 13.0550, "Europe/Vienna"),
    "Innsbruck": (47.2692, 11.4041, "Europe/Vienna"),
    "Zürich": (47.3769, 8.5417, "Europe/Zurich"),
    "Genf": (46.2044, 6.1432, "Europe/Zurich"),
    "Basel": (47.5596, 7.5886, "Europe/Zurich"),
    "Bern": (46.9480, 7.4474, "Europe/Zurich"),
    "Lausanne": (46.5197, 6.6323, "Europe/Zurich"),
    "Luxemburg": (49.6116, 6.1319, "Europe/Luxembourg"),
    "Amsterdam": (52.3676, 4.9041, "Europe/Amsterdam"),
    "Brüssel": (50.8503, 4.3517, "Europe/Brussels"),
    "Paris": (48.8566, 2.3522, "Europe/Paris"),
    "London": (51.5074, -0.1278, "Europe/London"),
    "Madrid": (40.4168, -3.7038, "Europe/Madrid"),
    "Barcelona": (41.3874, 2.1686, "Europe/Madrid"),
    "Rom": (41.9028, 12.4964, "Europe/Rome"),
    "Mailand": (45.4642, 9.1900, "Europe/Rome"),
    "Lissabon": (38.7223, -9.1393, "Europe/Lisbon"),
    "Prag": (50.0755, 14.4378, "Europe/Prague"),
    "Warschau": (52.2297, 21.0122, "Europe/Warsaw"),
    "Budapest": (47.4979, 19.0402, "Europe/Budapest"),
    "Kopenhagen": (55.6761, 12.5683, "Europe/Copenhagen"),
    "Stockholm": (59.3293, 18.0686, "Europe/Stockholm"),
    "Oslo": (59.9139, 10.7522, "Europe/Oslo"),
    "Helsinki": (60.1699, 24.9384, "Europe/Helsinki"),
    "Dublin": (53.3498, -6.2603, "Europe/Dublin"),
    "Athen": (37.9838, 23.7275, "Europe/Athens"),
    "Istanbul": (41.0082, 28.9784, "Europe/Istanbul"),
    "New York": (40.7128, -74.0060, "America/New_York"),
    "Los Angeles": (34.0522, -118.2437, "America/Los_Angeles"),
    "Toronto": (43.6532, -79.3832, "America/Toronto"),
    "Dubai": (25.2048, 55.2708, "Asia/Dubai"),
    "Bangkok": (13.7563, 100.5018, "Asia/Bangkok"),
    "Singapur": (1.3521, 103.8198, "Asia/Singapore"),
    "Sydney": (-33.8688, 151.2093, "Australia/Sydney"),
    "Melbourne": (-37.8136, 144.9631, "Australia/Melbourne"),
    "Kapstadt": (-33.9249, 18.4241, "Africa/Johannesburg"),
    "Andere / Unbekannt": (50.0, 10.0, "UTC"),
}


# ---------------------------------------------------------------------------
# Astronomische Hilfsfunktionen
# ---------------------------------------------------------------------------

_LON_CACHE: dict = {}
_SPEED_CACHE: dict = {}
_VOC_CACHE: dict = {}
_ECLIPSE_CACHE: dict = {}
_CACHE_MAX = 12000


def _utc_bucket(dt: datetime, seconds: int) -> int:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.astimezone(timezone.utc).timestamp() // seconds * seconds)


def _cache_put(store: dict, key, value):
    store[key] = value
    if len(store) > _CACHE_MAX:
        for i, k in enumerate(list(store.keys())):
            if i % 2 == 0:
                del store[k]
    return value


def ecliptic_longitude(body_name: str, dt: datetime) -> float:
    bucket = 300 if body_name == "moon" else 600
    key = (body_name, _utc_bucket(dt, bucket))
    hit = _LON_CACHE.get(key)
    if hit is not None:
        return hit
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    t = ts.from_datetime(dt)
    astrometric = planets["earth"].at(t).observe(planets[body_name])
    _, lon, _ = astrometric.ecliptic_latlon()
    return _cache_put(_LON_CACHE, key, lon.degrees % 360.0)


def planet_speed(body_name: str, dt: datetime, hours: float = 6.0) -> float:
    key = (body_name, _utc_bucket(dt, 600), hours)
    hit = _SPEED_CACHE.get(key)
    if hit is not None:
        return hit
    lon0 = ecliptic_longitude(body_name, dt)
    lon1 = ecliptic_longitude(body_name, dt + timedelta(hours=hours))
    delta = (lon1 - lon0 + 180) % 360 - 180
    return _cache_put(_SPEED_CACHE, key, delta * (24.0 / hours))


def norm_deg(deg: float) -> float:
    return deg % 360.0


def angle_diff(a: float, b: float) -> float:
    d = abs(norm_deg(a - b))
    return min(d, 360.0 - d)


def is_aspect(lon1: float, lon2: float, aspect_angle: float, orb: float = 8.0) -> bool:
    return abs(angle_diff(lon1, lon2) - aspect_angle) <= orb


def is_applying(lon1, speed1, lon2, speed2, aspect_angle) -> bool:
    current_diff = norm_deg(lon1 - lon2)
    targets = [aspect_angle, 360 - aspect_angle]
    best_target = min(targets, key=lambda t: abs((current_diff - t + 180) % 360 - 180))
    rel_speed = speed1 - speed2
    signed = (current_diff - best_target + 180) % 360 - 180
    return (signed * rel_speed) < 0


def moon_phase_fraction(dt: datetime) -> float:
    sun = ecliptic_longitude("sun", dt)
    moon = ecliptic_longitude("moon", dt)
    return norm_deg(moon - sun) / 360.0


def moon_phase_label(frac: float) -> str:
    if frac < 0.03 or frac > 0.97:
        return "Neumond"
    if 0.22 < frac < 0.28:
        return "Zunehmende Sichel / Halbmond"
    if 0.47 < frac < 0.53:
        return "Vollmond"
    if 0.72 < frac < 0.78:
        return "Abnehmender Halbmond"
    if frac < 0.5:
        return "Zunehmender Mond"
    return "Abnehmender Mond"


def mercury_retrograde(dt: datetime) -> bool:
    return planet_speed("mercury", dt) < 0


def mercury_stationary(dt: datetime, threshold: float = 0.15) -> bool:
    return abs(planet_speed("mercury", dt)) < threshold


def mercury_combust(dt: datetime, orb: float = 8.5) -> bool:
    return angle_diff(ecliptic_longitude("sun", dt), ecliptic_longitude("mercury", dt)) <= orb


def part_of_fortune(asc: float, sun: float, moon: float, is_day: bool) -> float:
    if is_day:
        return norm_deg(asc + moon - sun)
    return norm_deg(asc + sun - moon)


def lot_of_spirit(asc: float, sun: float, moon: float, is_day: bool) -> float:
    if is_day:
        return norm_deg(asc + sun - moon)
    return norm_deg(asc + moon - sun)


def mean_north_node(dt: datetime) -> float:
    """
    Mittlerer Mondknoten (Näherung, ausreichend für Unterhaltung).
    Basierend auf bekannter mittlerer Länge ca. 125.04° am J2000 + Drift.
    """
    # J2000.0 = 2000-01-01 12:00 TT
    j2000 = datetime(2000, 1, 1, 12, 0, tzinfo=timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    days = (dt - j2000).total_seconds() / 86400.0
    # Mittlerer Knoten: ~ -0.0529539°/Tag
    node = 125.04455501 - 0.05295376 * days
    return norm_deg(node)


def approx_chiron(dt: datetime) -> float:
    """
    Grobe Chiron-Länge (polynomiale Näherung, ±2–3° typisch).
    Für Unterhaltungszwecke ausreichend.
    """
    j2000 = datetime(2000, 1, 1, 12, 0, tzinfo=timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    years = (dt - j2000).total_seconds() / (86400.0 * 365.25)
    # Chiron ~ 4.5° bei J2000, Umlauf ~50.7 Jahre
    # Sehr vereinfachte sinusoidale Näherung
    mean = 4.5 + (360.0 / 50.7) * years
    # leichte Exzentrizitätskorrektur
    anomaly = math.radians(mean * 0.8)
    lon = mean + 8.0 * math.sin(anomaly)
    return norm_deg(lon)


def approx_ascendant_mc(dt: datetime, lat: float, lon: float) -> tuple[float, float]:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    t = ts.from_datetime(dt)
    gast = t.gast * 15.0
    lst = norm_deg(gast + lon)
    eps = 23.4392911

    mc = math.degrees(
        math.atan2(
            math.sin(math.radians(lst)),
            math.cos(math.radians(lst)) * math.cos(math.radians(eps)),
        )
    )
    mc = norm_deg(mc)

    asc = math.degrees(
        math.atan2(
            math.cos(math.radians(lst)),
            -(
                math.sin(math.radians(lst)) * math.cos(math.radians(eps))
                + math.tan(math.radians(lat)) * math.sin(math.radians(eps))
            ),
        )
    )
    return norm_deg(asc), mc


def porphyry_houses(asc: float, mc: float) -> list[float]:
    """
    Porphyry-Häuser: Quadranten zwischen ASC–MC–DSC–IC werden
    in drei gleiche Teile geteilt. Deutlich näher an Placidus als Whole Sign.
    Gibt Cusps 1–12 zurück (Cusp 1 = ASC, Cusp 10 = MC).
    """
    dsc = norm_deg(asc + 180)
    ic = norm_deg(mc + 180)

    def trisect(start: float, end: float) -> list[float]:
        """Drei gleiche Abschnitte von start nach end (kürzester Bogen vorwärts)."""
        span = norm_deg(end - start)
        step = span / 3.0
        return [norm_deg(start + step), norm_deg(start + 2 * step)]

    # Quadrant ASC → MC (Häuser 12, 11)
    c12, c11 = trisect(asc, mc)
    # Quadrant MC → DSC (Häuser 9, 8)
    c9, c8 = trisect(mc, dsc)
    # Quadrant DSC → IC (Häuser 7, 6) – Cusp 7 = DSC
    c6, c5 = trisect(dsc, ic)
    # Quadrant IC → ASC (Häuser 4, 3) – Cusp 4 = IC
    c3, c2 = trisect(ic, asc)

    # Index 0 ungenutzt, 1=ASC … 12
    cusps = [0.0] * 13
    cusps[1] = asc
    cusps[2] = c2
    cusps[3] = c3
    cusps[4] = ic
    cusps[5] = c5
    cusps[6] = c6
    cusps[7] = dsc
    cusps[8] = c8
    cusps[9] = c9
    cusps[10] = mc
    cusps[11] = c11
    cusps[12] = c12
    return cusps


def house_of_longitude(lon: float, cusps: list[float]) -> int:
    """Welches Haus enthält die gegebene Länge (Porphyry-Cusps)."""
    for h in range(1, 13):
        next_h = h + 1 if h < 12 else 1
        start = cusps[h]
        end = cusps[next_h]
        if start <= end:
            if start <= lon < end:
                return h
        else:  # über 0°
            if lon >= start or lon < end:
                return h
    return 1


def sign_index(lon: float) -> int:
    return int(lon // 30) % 12


def whole_sign_house(planet_lon: float, asc_lon: float) -> int:
    return ((sign_index(planet_lon) - sign_index(asc_lon)) % 12) + 1


def house_ruler_porphyry(house_num: int, cusps: list[float]) -> str:
    """Ruler des Zeichens, in dem der Haus-Cusp steht."""
    sign = sign_index(cusps[house_num])
    return SIGN_RULERS[sign]


def is_void_of_course(dt: datetime, major_orbs: dict | None = None) -> bool:
    voc_key = _utc_bucket(dt, 600)
    if major_orbs is None and voc_key in _VOC_CACHE:
        return _VOC_CACHE[voc_key]
    if major_orbs is None:
        major_orbs = {
            "sun": 8.0, "mercury": 7.0, "venus": 7.0, "mars": 7.0,
            "jupiter": 8.0, "saturn": 8.0, "uranus": 6.0,
            "neptune": 6.0, "pluto": 5.0,
        }
    moon = ecliptic_longitude("moon", dt)
    moon_sign = sign_index(moon)
    moon_speed = planet_speed("moon", dt)
    deg_in_sign = moon % 30
    degrees_left = 30.0 - deg_in_sign
    hours_left = degrees_left / max(abs(moon_speed) / 24.0, 0.01)
    aspects = [0, 60, 90, 120, 180]
    bodies = list(major_orbs.keys())
    steps = max(3, int(hours_left / 2) + 1)
    for i in range(1, steps + 1):
        future = dt + timedelta(hours=(hours_left * i / steps))
        m = ecliptic_longitude("moon", future)
        if sign_index(m) != moon_sign:
            break
        for body in bodies:
            b = ecliptic_longitude(body, future)
            orb = major_orbs[body]
            for asp in aspects:
                if is_aspect(m, b, asp, orb):
                    return _cache_put(_VOC_CACHE, voc_key, False)
    return _cache_put(_VOC_CACHE, voc_key, True)


def get_day_ruler(dt: datetime) -> tuple[str, str]:
    return DAY_RULERS[dt.weekday()]


def get_planetary_hour(dt: datetime, lat: float, lon: float) -> tuple[str, str]:
    day_of_year = dt.timetuple().tm_yday
    decl = 23.44 * math.sin(math.radians((360 / 365) * (day_of_year - 81)))
    lat_r = math.radians(lat)
    decl_r = math.radians(decl)
    try:
        ha = math.acos(-math.tan(lat_r) * math.tan(decl_r))
        daylight_hours = 2 * math.degrees(ha) / 15.0
    except ValueError:
        daylight_hours = 12.0
    daylight_hours = max(6.0, min(18.0, daylight_hours))
    night_hours = 24.0 - daylight_hours
    sunrise_h = 12.0 - daylight_hours / 2.0
    local_hour = dt.hour + dt.minute / 60.0
    if sunrise_h <= local_hour < sunrise_h + daylight_hours:
        hour_idx = int((local_hour - sunrise_h) / (daylight_hours / 12.0))
        hour_idx = max(0, min(11, hour_idx))
    else:
        if local_hour >= sunrise_h + daylight_hours:
            night_start = sunrise_h + daylight_hours
        else:
            night_start = sunrise_h + daylight_hours - 24.0
        hour_idx = int((local_hour - night_start) / (night_hours / 12.0))
        hour_idx = max(0, min(11, hour_idx))
    day_ruler_key = DAY_RULERS[dt.weekday()][1]
    start_idx = HOUR_SEQUENCE.index(day_ruler_key)
    seq_idx = (start_idx + hour_idx) % 7
    body = HOUR_SEQUENCE[seq_idx]
    return BODY_NAMES_DE.get(body, body), body


def dampen_score(raw: float) -> float:
    if raw <= 70:
        return raw
    excess = raw - 70
    return 70 + excess * (0.75 - 0.15 * (excess / 30.0))


# ---------------------------------------------------------------------------
# Finsternisse
# ---------------------------------------------------------------------------

def _node_orb(lon: float, node: float) -> float:
    return min(angle_diff(lon, node), angle_diff(lon, norm_deg(node + 180.0)))


def eclipse_at(dt: datetime) -> dict | None:
    """Solar/Lunar-Eklipse am Zeitpunkt, falls Lunation knotengebunden ist."""
    sun = ecliptic_longitude("sun", dt)
    moon = ecliptic_longitude("moon", dt)
    node = mean_north_node(dt)
    elong = angle_diff(sun, moon)
    sun_node = _node_orb(sun, node)
    moon_node = _node_orb(moon, node)
    if elong <= 1.5 and sun_node <= 18.0:
        return {
            "kind": "solar",
            "label": "Sonnenfinsternis",
            "axis": sun,
            "node_orb": sun_node,
        }
    if abs(elong - 180.0) <= 1.5 and min(sun_node, moon_node) <= 18.0:
        return {
            "kind": "lunar",
            "label": "Mondfinsternis",
            "axis": moon,
            "node_orb": min(sun_node, moon_node),
        }
    return None


def _eclipse_strength(node_orb: float) -> tuple[float, str]:
    if node_orb <= 5.0:
        return 1.0, "stark"
    if node_orb <= 12.0:
        return 0.7, "mittel"
    return 0.4, "schwach"


def _eclipse_decay(hours: float) -> float:
    ah = abs(hours)
    if ah <= 12:
        return 1.0
    if ah <= 24:
        return 0.6
    if ah <= 72:
        return 0.3
    return 0.0


def nearest_eclipse(dt: datetime, max_hours: int = 72) -> dict | None:
    """Nächste Eklipse im ±3-Tage-Fenster (stündlich gerastert, gecacht)."""
    key = _utc_bucket(dt, 3600)
    if key in _ECLIPSE_CACHE:
        return _ECLIPSE_CACHE[key]
    best = None
    best_abs = 10**9
    for hours in range(-max_hours, max_hours + 1, 2):
        info = eclipse_at(dt + timedelta(hours=hours))
        if not info:
            continue
        if abs(hours) < best_abs:
            best_abs = abs(hours)
            strength, strength_label = _eclipse_strength(info["node_orb"])
            decay = _eclipse_decay(hours)
            best = {
                **info,
                "hours": hours,
                "when": dt + timedelta(hours=hours),
                "strength": strength,
                "strength_label": strength_label,
                "decay": decay,
            }
            if hours == 0:
                break
    return _cache_put(_ECLIPSE_CACHE, key, best)


def apply_eclipse_general(dt, positions, speeds, cusps, pof, add) -> dict | None:
    info = nearest_eclipse(dt)
    if not info or info["decay"] <= 0:
        return info
    axis = info["axis"]
    w = info["strength"] * info["decay"]
    luck = False
    for body in ("jupiter", "uranus", "venus"):
        if is_aspect(axis, positions[body], 0, 6) or is_aspect(axis, positions[body], 120, 7):
            luck = True
            break
    if is_aspect(axis, pof, 0, 5) or is_aspect(axis, pof, 120, 6):
        luck = True

    saturn_hard = is_aspect(axis, positions["saturn"], 90, 6) or is_aspect(
        axis, positions["saturn"], 180, 6
    )
    h = house_of_longitude(axis, cusps)
    pts = 0.0
    if info["kind"] == "solar":
        pts = (5.0 if luck else -2.0) * w
    else:
        if luck:
            pts = 4.0 * w
        elif saturn_hard:
            pts = -5.0 * w
        else:
            pts = 0.0
    if h in (5, 8, 11):
        pts += 4.0 * w
    if is_aspect(axis, positions["uranus"], 0, 5) or is_aspect(axis, positions["north_node"], 0, 5):
        applying = is_applying(
            positions["uranus"], speeds.get("uranus", 0), axis, 0.0, 0
        )
        if applying:
            pts += 3.0 * w

    pts = max(-8.0, min(10.0, pts))
    if abs(pts) >= 0.5:
        side = "anwendend" if info["hours"] <= 0 else "scheidend"
        add(
            round(pts),
            f"{info['label']} ({info['strength_label']}, {side}, Knoten {info['node_orb']:.1f}°)",
        )
    return info


def apply_eclipse_personal(query_dt, natal: dict, add) -> dict | None:
    info = nearest_eclipse(query_dt)
    if not info or info["decay"] <= 0:
        return info
    axis = info["axis"]
    w = info["strength"] * info["decay"]

    def hit(lon, orb=5.0):
        return is_aspect(axis, lon, 0, orb) or is_aspect(axis, lon, 180, orb)

    if hit(natal["sun"]) or hit(natal["moon"]) or hit(natal["asc"]):
        add(round(10 * w), f"{info['label']} auf radix Sonne/Mond/ASC")
    if hit(natal["mercury"]):
        add(round(9 * w), f"{info['label']} auf radix Merkur (Tickets/Zahlen)")
    if hit(natal["jupiter"]) or hit(natal["venus"]) or hit(natal["pof"]):
        add(round(12 * w), f"{info['label']} auf radix Jupiter/Venus/PoF")
    if hit(natal["uranus"]) or hit(natal["node"]):
        add(round(8 * w), f"{info['label']} auf radix Uranus/Nordknoten")
    if hit(natal["saturn"]) or (
        is_aspect(axis, natal["pof"], 90, 5) or is_aspect(axis, natal["pof"], 180, 5)
    ):
        if is_aspect(axis, natal["saturn"], 90, 5) or is_aspect(axis, natal["saturn"], 180, 5):
            add(round(-8 * w), f"{info['label']} hart zu radix Saturn")
    return info


# ---------------------------------------------------------------------------
# Aspektmuster
# ---------------------------------------------------------------------------

def detect_aspect_patterns(positions: dict[str, float], speeds: dict[str, float] | None = None) -> list[tuple[str, float]]:
    """
    Sucht nach Großem Trigon, T-Quadrat und Yod unter den Glücksplaneten
    und wichtigen Körpern. Gibt (Beschreibung, Punkte) zurück.
    """
    found = []
    luck = ["jupiter", "venus", "uranus", "sun", "moon"]
    all_bodies = list(positions.keys())

    def has(a, b, angle, orb=7.0):
        return is_aspect(positions[a], positions[b], angle, orb)

    # Großes Trigon (3×120°) mit mind. einem Glücksplaneten
    for i, a in enumerate(all_bodies):
        for j, b in enumerate(all_bodies):
            if j <= i:
                continue
            for k, c in enumerate(all_bodies):
                if k <= j:
                    continue
                if has(a, b, 120, 7) and has(b, c, 120, 7) and has(a, c, 120, 7):
                    names = {a, b, c}
                    if names & set(luck):
                        label = "–".join(BODY_NAMES_DE.get(x, x) for x in sorted(names))
                        bonus = 14 if "jupiter" in names or "uranus" in names else 10
                        found.append((f"Großes Trigon ({label})", bonus))
                        break
            else:
                continue
            break
        else:
            continue
        break  # nur ein Großes Trigon zählen

    # T-Quadrat (Opposition + 2 Quadrate)
    for i, a in enumerate(all_bodies):
        for j, b in enumerate(all_bodies):
            if j <= i:
                continue
            if not has(a, b, 180, 8):
                continue
            for c in all_bodies:
                if c in (a, b):
                    continue
                if has(a, c, 90, 7) and has(b, c, 90, 7):
                    names = {a, b, c}
                    # Aufgelöstes T-Quadrat (wenn Apex harmonisch zu einem Glücksplaneten) = Bonus
                    # Einfaches T-Quadrat eher gemischt
                    if "jupiter" in names or "uranus" in names or "venus" in names:
                        label = "–".join(BODY_NAMES_DE.get(x, x) for x in sorted(names))
                        found.append((f"T-Quadrat mit Glücksplanet ({label})", 6))
                    else:
                        found.append(("T-Quadrat (Spannung)", -5))
                    break
            else:
                continue
            break
        else:
            continue
        break

    # Yod (Finger Gottes): 2×150° + 60° Basis
    for i, a in enumerate(all_bodies):
        for j, b in enumerate(all_bodies):
            if j <= i:
                continue
            if not has(a, b, 60, 5):
                continue
            for c in all_bodies:
                if c in (a, b):
                    continue
                if has(a, c, 150, 6) and has(b, c, 150, 6):
                    names = {a, b, c}
                    if names & {"jupiter", "uranus", "venus", "north_node"}:
                        label = "–".join(BODY_NAMES_DE.get(x, x) for x in sorted(names))
                        found.append((f"Yod / Finger Gottes ({label})", 11))
                    else:
                        found.append(("Yod (Schicksalspunkt)", 5))
                    break
            else:
                continue
            break
        else:
            continue
        break

    return found


# ---------------------------------------------------------------------------
# Progressionen & Solar Return
# ---------------------------------------------------------------------------

def secondary_progressed_date(birth_dt: datetime, query_dt: datetime) -> datetime:
    """
    Sekundärprogression: 1 Tag nach Geburt = 1 Jahr Leben.
    Gibt das progressive Datum zurück.
    """
    if birth_dt.tzinfo is None:
        birth_dt = birth_dt.replace(tzinfo=timezone.utc)
    if query_dt.tzinfo is None:
        query_dt = query_dt.replace(tzinfo=timezone.utc)
    age_years = (query_dt - birth_dt).total_seconds() / (86400.0 * 365.2425)
    return birth_dt + timedelta(days=age_years)


def solar_return_approx(birth_dt: datetime, year: int, lat: float, lon: float) -> datetime:
    """
    Näherung des Solar-Return-Zeitpunkts: Sonne wieder auf nataler Länge.
    Sucht im Geburtsmonat ±15 Tage des Jahres.
    """
    natal_sun = ecliptic_longitude("sun", birth_dt)
    # Start um Geburtstag im Zieljahr
    candidate = datetime(year, birth_dt.month, birth_dt.day, 12, 0, tzinfo=timezone.utc)
    best_dt = candidate
    best_diff = 999.0
    for hours in range(-20 * 24, 20 * 24, 6):  # ±20 Tage in 6h-Schritten
        t = candidate + timedelta(hours=hours)
        sun = ecliptic_longitude("sun", t)
        d = angle_diff(sun, natal_sun)
        if d < best_diff:
            best_diff = d
            best_dt = t
    return best_dt


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_general(dt: datetime, lat: float = 50.0, lon: float = 10.0):
    reasons = []
    points = 50.0

    sun = ecliptic_longitude("sun", dt)
    moon = ecliptic_longitude("moon", dt)
    venus = ecliptic_longitude("venus", dt)
    jupiter = ecliptic_longitude("jupiter", dt)
    saturn = ecliptic_longitude("saturn", dt)
    uranus = ecliptic_longitude("uranus", dt)
    mercury = ecliptic_longitude("mercury", dt)
    mars = ecliptic_longitude("mars", dt)
    neptune = ecliptic_longitude("neptune", dt)
    pluto = ecliptic_longitude("pluto", dt)
    node = mean_north_node(dt)
    chiron = approx_chiron(dt)

    positions = {
        "sun": sun, "moon": moon, "mercury": mercury, "venus": venus,
        "mars": mars, "jupiter": jupiter, "saturn": saturn,
        "uranus": uranus, "neptune": neptune, "pluto": pluto,
        "north_node": node, "chiron": chiron,
    }
    speeds = {k: planet_speed(k, dt) if k in planets else 0.0 for k in positions}

    def add(delta, text):
        nonlocal points
        points += delta
        reasons.append((text, delta))

    # Jupiter
    for asp, orb, bonus, label in [
        (120, 8, 12, "Jupiter Trigon Sonne"),
        (60, 6, 9, "Jupiter Sextil Sonne"),
        (0, 6, 10, "Jupiter Konjunktion Sonne"),
    ]:
        if is_aspect(jupiter, sun, asp, orb):
            mult = 1.25 if is_applying(jupiter, speeds["jupiter"], sun, speeds["sun"], asp) else 0.85
            add(round(bonus * mult), f"{label} ({'anwendend' if mult > 1 else 'scheidend'})")
            break
    if is_aspect(jupiter, moon, 120, 8) or is_aspect(jupiter, moon, 60, 6):
        applying = is_applying(jupiter, speeds["jupiter"], moon, speeds["moon"], 120)
        add(11 if applying else 8, "Jupiter harmonisch zum Mond" + (" (anwendend)" if applying else ""))
    if is_aspect(jupiter, venus, 120, 8) or is_aspect(jupiter, venus, 0, 6):
        add(11, "Jupiter–Venus Glücksaspekt")
    if is_aspect(jupiter, sun, 90, 7) or is_aspect(jupiter, sun, 180, 7):
        add(-8, "Jupiter hart zur Sonne")

    # Uranus
    if is_aspect(uranus, mercury, 0, 6) or is_aspect(uranus, mercury, 120, 7):
        applying = is_applying(uranus, speeds["uranus"], mercury, speeds["mercury"], 0)
        add(15 if applying else 11, "Uranus aktiviert Merkur (Zahlen/Tickets)" + (" ★" if applying else ""))
    if is_aspect(uranus, jupiter, 0, 6) or is_aspect(uranus, jupiter, 120, 7):
        add(13, "Uranus–Jupiter (plötzliches Glück)")
    if is_aspect(uranus, venus, 0, 6):
        add(9, "Uranus–Venus (unerwarteter Geldfluss)")

    # Mondphase (Voll-/Neumond-Bonus entfällt bei Eklipse, keine Doppelzählung)
    eclipse_near = nearest_eclipse(dt)
    phase = moon_phase_fraction(dt)
    if 0.1 < phase < 0.45:
        add(7, "Zunehmender Mond")
    elif 0.55 < phase < 0.9:
        add(-4, "Abnehmender Mond")
    if eclipse_near is None or eclipse_near.get("decay", 0) <= 0:
        if abs(phase - 0.5) < 0.04:
            add(5, "Nahe Vollmond")

    if is_void_of_course(dt):
        add(-12, "Mond Void of Course (ungünstig für neue Unternehmungen)")

    # Mondaspekte
    for body, lon_b, name, spd_key in [
        (jupiter, jupiter, "Jupiter", "jupiter"),
        (uranus, uranus, "Uranus", "uranus"),
        (venus, venus, "Venus", "venus"),
        (node, node, "Nordknoten", "north_node"),
    ]:
        for asp, orb, pts in [(0, 5, 8), (120, 6, 7), (60, 5, 5)]:
            if is_aspect(moon, lon_b, asp, orb):
                applying = is_applying(moon, speeds["moon"], lon_b, speeds.get(spd_key, 0), asp)
                add(pts + (2 if applying else 0), f"Mond {asp}° {name}" + (" (anwendend)" if applying else ""))
                break

    # Merkur
    if mercury_stationary(dt):
        add(-9, "Merkur stationär (kritisch für Tickets/Zahlen)")
    elif mercury_retrograde(dt):
        add(-7, "Merkur rückläufig")
    if mercury_combust(dt):
        add(-6, "Merkur verbrannt / unter den Sonnenstrahlen")
    if is_aspect(mercury, jupiter, 120, 7) or is_aspect(mercury, jupiter, 60, 5):
        add(8, "Merkur harmonisch zu Jupiter")
    if is_aspect(mercury, uranus, 120, 6) or is_aspect(mercury, uranus, 0, 5):
        add(7, "Merkur–Uranus (plötzliche Eingebung)")

    # Saturn
    if is_aspect(saturn, jupiter, 90, 6) or is_aspect(saturn, jupiter, 180, 6):
        add(-9, "Saturn belastet Jupiter")
    if is_aspect(saturn, venus, 90, 6):
        add(-6, "Saturn–Venus Spannung")

    if is_aspect(venus, jupiter, 120, 7) or is_aspect(venus, jupiter, 60, 5):
        add(8, "Venus–Jupiter Trigon/Sextil")

    # Häuser (Porphyry)
    asc, mc = approx_ascendant_mc(dt, lat, lon)
    cusps = porphyry_houses(asc, mc)

    for lon_p, name in [
        (jupiter, "Jupiter"), (uranus, "Uranus"), (venus, "Venus"),
        (mercury, "Merkur"), (node, "Nordknoten"), (chiron, "Chiron"),
    ]:
        h = house_of_longitude(lon_p, cusps)
        if h in (5, 8, 11):
            add(5, f"{name} im {h}. Haus (Spekulation/fremd. Geld/Gewinne)")
        if h == 3 and name == "Merkur":
            add(4, "Merkur im 3. Haus (Kommunikation/Tippschein)")

    for h in (5, 8, 11):
        ruler = house_ruler_porphyry(h, cusps)
        ruler_lon = positions.get(ruler) or ecliptic_longitude(ruler, dt)
        if is_aspect(ruler_lon, jupiter, 120, 7) or is_aspect(ruler_lon, jupiter, 0, 5):
            add(4, f"Ruler des {h}. Hauses harmonisch zu Jupiter")
        if is_aspect(ruler_lon, uranus, 0, 5) or is_aspect(ruler_lon, uranus, 120, 6):
            add(3, f"Ruler des {h}. Hauses aktiviert von Uranus")

    if is_aspect(jupiter, mc, 0, 6) or is_aspect(jupiter, mc, 120, 7):
        add(6, "Jupiter am MC / Trigon MC")
    if is_aspect(uranus, mc, 0, 5):
        add(5, "Uranus am MC (plötzliche Sichtbarkeit)")

    # Tagesherrscher & Planetenstunde
    day_name, day_key = get_day_ruler(dt)
    hour_name, hour_key = get_planetary_hour(dt, lat, lon)
    if day_key in ("jupiter", "venus"):
        add(5, f"Tagesherrscher {day_name} (glücksbringend)")
    elif day_key in ("saturn", "mars"):
        add(-4, f"Tagesherrscher {day_name} (erschwerend)")
    if hour_key in ("jupiter", "venus"):
        add(4, f"Planetenstunde {hour_name}")
    elif hour_key in ("saturn", "mars"):
        add(-3, f"Planetenstunde {hour_name}")

    # Part of Fortune + Spirit
    is_day = 6 <= dt.hour < 18
    pof = part_of_fortune(asc, sun, moon, is_day)
    spirit = lot_of_spirit(asc, sun, moon, is_day)
    if is_aspect(jupiter, pof, 0, 5) or is_aspect(jupiter, pof, 120, 6):
        add(7, "Jupiter aktiviert Part of Fortune")
    if is_aspect(uranus, pof, 0, 4) or is_aspect(uranus, pof, 120, 5):
        add(6, "Uranus aktiviert Part of Fortune")
    if is_aspect(moon, pof, 0, 4):
        add(4, "Mond über Part of Fortune")
    if is_aspect(jupiter, spirit, 0, 5) or is_aspect(jupiter, spirit, 120, 6):
        add(5, "Jupiter aktiviert Lot of Spirit")

    # Nordknoten & Chiron
    if is_aspect(jupiter, node, 0, 5) or is_aspect(jupiter, node, 120, 6):
        add(6, "Jupiter–Nordknoten (Schicksal/Glück)")
    if is_aspect(uranus, node, 0, 4) or is_aspect(uranus, node, 120, 5):
        add(5, "Uranus–Nordknoten (unerwarteter Schicksalsimpuls)")
    if is_aspect(jupiter, chiron, 0, 5) or is_aspect(uranus, chiron, 0, 4):
        add(4, "Glücksplanet–Chiron (unerwartete Wendung)")

    # Aspektmuster
    for desc, pts in detect_aspect_patterns(positions, speeds):
        add(pts, desc)

    apply_eclipse_general(dt, positions, speeds, cusps, pof, add)

    points = dampen_score(max(0.0, min(100.0, points)))
    return points, reasons


def score_personal(birth_dt, query_dt, lat, lon):
    reasons = []
    points = 48.0

    sun_n = ecliptic_longitude("sun", birth_dt)
    moon_n = ecliptic_longitude("moon", birth_dt)
    mercury_n = ecliptic_longitude("mercury", birth_dt)
    venus_n = ecliptic_longitude("venus", birth_dt)
    jupiter_n = ecliptic_longitude("jupiter", birth_dt)
    node_n = mean_north_node(birth_dt)

    asc_n, mc_n = approx_ascendant_mc(birth_dt, lat, lon)
    cusps_n = porphyry_houses(asc_n, mc_n)
    is_day = 6 <= birth_dt.hour < 18
    pof = part_of_fortune(asc_n, sun_n, moon_n, is_day)
    spirit = lot_of_spirit(asc_n, sun_n, moon_n, is_day)

    jupiter_t = ecliptic_longitude("jupiter", query_dt)
    uranus_t = ecliptic_longitude("uranus", query_dt)
    venus_t = ecliptic_longitude("venus", query_dt)
    saturn_t = ecliptic_longitude("saturn", query_dt)
    moon_t = ecliptic_longitude("moon", query_dt)
    mercury_t = ecliptic_longitude("mercury", query_dt)
    node_t = mean_north_node(query_dt)
    chiron_t = approx_chiron(query_dt)

    speeds_t = {
        "jupiter": planet_speed("jupiter", query_dt),
        "uranus": planet_speed("uranus", query_dt),
        "venus": planet_speed("venus", query_dt),
        "moon": planet_speed("moon", query_dt),
        "mercury": planet_speed("mercury", query_dt),
        "saturn": planet_speed("saturn", query_dt),
    }

    def add(delta, text):
        nonlocal points
        points += delta
        reasons.append((text, delta))

    # Jupiter-Transite
    for asp, orb, pts, label in [
        (0, 6, 14, "Jupiter-Transit Konjunktion radix Sonne"),
        (120, 7, 12, "Jupiter-Transit Trigon radix Sonne"),
    ]:
        if is_aspect(jupiter_t, sun_n, asp, orb):
            applying = is_applying(jupiter_t, speeds_t["jupiter"], sun_n, 0.0, asp)
            add(pts + (2 if applying else 0), label + (" ★" if applying else ""))
            break
    if is_aspect(jupiter_t, moon_n, 0, 6) or is_aspect(jupiter_t, moon_n, 120, 7):
        add(12, "Jupiter-Transit zum radix Mond")
    if is_aspect(jupiter_t, venus_n, 0, 6) or is_aspect(jupiter_t, venus_n, 120, 7):
        add(11, "Jupiter-Transit zur radix Venus")
    if is_aspect(jupiter_t, jupiter_n, 0, 5):
        add(15, "Jupiter-Return / Rückkehr-Nähe")
    if is_aspect(jupiter_t, node_n, 0, 5) or is_aspect(jupiter_t, node_n, 120, 6):
        add(8, "Jupiter-Transit zum radix Nordknoten")

    # Part of Fortune + Spirit
    if is_aspect(jupiter_t, pof, 0, 6) or is_aspect(jupiter_t, pof, 120, 7):
        add(13, "Jupiter aktiviert Part of Fortune")
    if is_aspect(uranus_t, pof, 0, 5) or is_aspect(uranus_t, pof, 120, 6):
        add(12, "Uranus aktiviert Part of Fortune")
    if is_aspect(moon_t, pof, 0, 5):
        add(7, "Mond über Part of Fortune")
    if is_aspect(jupiter_t, spirit, 0, 5) or is_aspect(jupiter_t, spirit, 120, 6):
        add(6, "Jupiter aktiviert Lot of Spirit")

    # Uranus
    if is_aspect(uranus_t, mercury_n, 0, 5) or is_aspect(uranus_t, mercury_n, 120, 6):
        applying = is_applying(uranus_t, speeds_t["uranus"], mercury_n, 0.0, 0)
        add(14 if applying else 11, "Uranus auf radix Merkur (Tickets/Zahlen)" + (" ★" if applying else ""))
    if is_aspect(uranus_t, jupiter_n, 0, 5) or is_aspect(uranus_t, jupiter_n, 120, 6):
        add(12, "Uranus auf radix Jupiter")
    if is_aspect(uranus_t, venus_n, 0, 5):
        add(9, "Uranus auf radix Venus")

    # Saturn
    if is_aspect(saturn_t, jupiter_n, 90, 6) or is_aspect(saturn_t, jupiter_n, 180, 6):
        add(-10, "Saturn belastet radix Jupiter")
    if is_aspect(saturn_t, pof, 90, 5) or is_aspect(saturn_t, pof, 180, 5):
        add(-8, "Saturn belastet Part of Fortune")

    if is_aspect(venus_t, jupiter_n, 120, 6) or is_aspect(venus_t, jupiter_n, 0, 5):
        add(8, "Venus-Transit zu radix Jupiter")
    if is_aspect(moon_t, jupiter_n, 0, 5) or is_aspect(moon_t, jupiter_n, 120, 6):
        add(6, "Mond–Jupiter persönlich")

    # Häuser
    for tlon, name in [(jupiter_t, "Jupiter"), (uranus_t, "Uranus"), (mercury_t, "Merkur"), (node_t, "Nordknoten")]:
        h = house_of_longitude(tlon, cusps_n)
        if h in (5, 8, 11):
            add(5, f"Transit-{name} im radix {h}. Haus")
        if name == "Merkur" and h == 3:
            add(3, "Transit-Merkur im radix 3. Haus")

    for h in (5, 8, 11):
        ruler = house_ruler_porphyry(h, cusps_n)
        ruler_t = ecliptic_longitude(ruler, query_dt) if ruler in planets else 0.0
        if is_aspect(ruler_t, jupiter_t, 0, 5) or is_aspect(ruler_t, jupiter_t, 120, 6):
            add(4, f"Ruler des radix {h}. Hauses harmonisch zu Transit-Jupiter")

    # --- Sekundärprogression ---
    prog_dt = secondary_progressed_date(birth_dt, query_dt)
    prog_moon = ecliptic_longitude("moon", prog_dt)
    prog_asc, _ = approx_ascendant_mc(prog_dt, lat, lon)

    if is_aspect(prog_moon, jupiter_t, 0, 5) or is_aspect(prog_moon, jupiter_t, 120, 6):
        add(9, "Progressiver Mond harmonisch zu Transit-Jupiter")
    if is_aspect(prog_moon, uranus_t, 0, 4) or is_aspect(prog_moon, uranus_t, 120, 5):
        add(8, "Progressiver Mond–Uranus (plötzlicher emotionaler Impuls)")
    if is_aspect(prog_moon, pof, 0, 4):
        add(6, "Progressiver Mond über Part of Fortune")
    if is_aspect(prog_asc, jupiter_t, 0, 5) or is_aspect(prog_asc, jupiter_t, 120, 6):
        add(7, "Progressiver Aszendent–Jupiter")

    # --- Solar Return (vereinfacht) ---
    try:
        sr_dt = solar_return_approx(birth_dt, query_dt.year, lat, lon)
        sr_jup = ecliptic_longitude("jupiter", sr_dt)
        sr_ura = ecliptic_longitude("uranus", sr_dt)
        sr_asc, sr_mc = approx_ascendant_mc(sr_dt, lat, lon)
        sr_cusps = porphyry_houses(sr_asc, sr_mc)
        h_j = house_of_longitude(sr_jup, sr_cusps)
        h_u = house_of_longitude(sr_ura, sr_cusps)
        if h_j in (5, 8, 11):
            add(8, f"Solar-Return-Jupiter im {h_j}. Haus")
        if h_u in (5, 8, 11):
            add(7, f"Solar-Return-Uranus im {h_u}. Haus")
        if is_aspect(sr_jup, sun_n, 0, 5) or is_aspect(sr_jup, sun_n, 120, 6):
            add(6, "Solar-Jupiter harmonisch zur radix Sonne")
    except Exception:
        pass

    apply_eclipse_personal(
        query_dt,
        {
            "sun": sun_n,
            "moon": moon_n,
            "asc": asc_n,
            "mercury": mercury_n,
            "jupiter": jupiter_n,
            "venus": venus_n,
            "pof": pof,
            "uranus": ecliptic_longitude("uranus", birth_dt),
            "node": node_n,
            "saturn": ecliptic_longitude("saturn", birth_dt),
        },
        add,
    )

    points = dampen_score(max(0.0, min(100.0, points)))
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
        return "#4ade80"
    if score >= 50:
        return "#fbbf24"
    return "#f87171"


def next_n_draw_dates(from_date: date, weekdays: list[int], n: int = 3) -> list[date]:
    out = []
    d = from_date
    for _ in range(60):
        if d.weekday() in weekdays:
            out.append(d)
            if len(out) >= n:
                break
        d += timedelta(days=1)
    return out


def all_draw_dates_until_year_end(from_date: date, weekdays: list[int]) -> list[date]:
    end = date(from_date.year, 12, 31)
    out = []
    d = from_date
    while d <= end:
        if d.weekday() in weekdays:
            out.append(d)
        d += timedelta(days=1)
    return out


def make_aware(dt_naive: datetime, tz_name: str) -> datetime:
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = timezone.utc
    return dt_naive.replace(tzinfo=tz)


def find_high_score_draws(
    birth_dt: datetime,
    lat: float,
    lon: float,
    lottery_mode: str,
    from_date: date,
    tz_name: str,
    threshold: float = 75.0,
) -> list[dict]:
    cfg = LOTTERY_CONFIG[lottery_mode]
    draw_dates = all_draw_dates_until_year_end(from_date, cfg["weekdays"])
    results = []
    for d in draw_dates:
        dh, dm = lottery_draw_hm(cfg, d)
        local_naive = datetime.combine(d, time(dh, dm))
        dr_dt = make_aware(local_naive, tz_name)
        g, _ = score_general(dr_dt, lat, lon)
        p, _ = score_personal(birth_dt, dr_dt, lat, lon)
        comb = (g + p) / 2.0
        if comb > threshold:
            results.append({
                "date": d,
                "weekday_name": cfg["weekday_names"].get(d.weekday(), d.strftime("%A")),
                "score": round(comb, 1),
                "general": round(g, 1),
                "personal": round(p, 1),
            })
    results.sort(key=lambda x: (-x["score"], x["date"]))
    return results


def fetch_jackpots() -> dict:
    result = {
        "eurojackpot": {"jackpot_mio": 22.0, "source": "fallback"},
        "6aus49": {"jackpot_mio": 50.0, "source": "fallback"},
    }
    try:
        import urllib.request
        import re
        req = urllib.request.Request(
            "https://www.lotto.de/aktuelle-jackpots",
            headers={"User-Agent": "Mozilla/5.0 (compatible; AstroLotto/1.0)"},
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        millions = [int(x) for x in re.findall(r"(\d+)\s*Millionen", html)]
        if len(millions) >= 2:
            for m in millions:
                if m >= 40:
                    result["6aus49"] = {"jackpot_mio": float(m), "source": "lotto.de"}
                elif 10 <= m < 40:
                    result["eurojackpot"] = {"jackpot_mio": float(m), "source": "lotto.de"}
            if result["6aus49"]["source"] == "fallback" and millions:
                result["6aus49"]["jackpot_mio"] = float(max(millions))
        elif len(millions) == 1:
            if millions[0] >= 40:
                result["6aus49"]["jackpot_mio"] = float(millions[0])
                result["6aus49"]["source"] = "lotto.de"
            else:
                result["eurojackpot"]["jackpot_mio"] = float(millions[0])
                result["eurojackpot"]["source"] = "lotto.de"
    except Exception:
        pass
    return result


LOTTERY_CONFIG = {
    "eurojackpot": {
        "label": "Eurojackpot",
        "weekdays": [1, 4],
        "weekday_names": {1: "Dienstag", 4: "Freitag"},
        "draw_hour": 20,
        "draw_minute": 0,
        "draw_by_weekday": {1: (20, 0), 4: (20, 0)},
        # Online-Richtwerte (LOTTO24 u. a.); Annahmestellen/Bundesländer weichen ab
        "close_by_weekday": {1: (18, 35), 4: (18, 35)},
        "tips_base": 25.0,
        "max_jackpot": 120.0,
    },
    "6aus49": {
        "label": "LOTTO 6aus49",
        "weekdays": [2, 5],
        "weekday_names": {2: "Mittwoch", 5: "Samstag"},
        "draw_hour": 18,
        "draw_minute": 25,
        "draw_by_weekday": {2: (18, 25), 5: (19, 25)},
        "close_by_weekday": {2: (17, 45), 5: (18, 45)},
        "tips_base": 22.0,
        "max_jackpot": 50.0,
    },
}


def lottery_close_hm(cfg: dict, d: date) -> tuple[int, int]:
    by = cfg.get("close_by_weekday") or {}
    if d.weekday() in by:
        return by[d.weekday()]
    return int(cfg.get("close_hour", 18)), int(cfg.get("close_minute", 0))


def lottery_draw_hm(cfg: dict, d: date) -> tuple[int, int]:
    by = cfg.get("draw_by_weekday") or {}
    if d.weekday() in by:
        return by[d.weekday()]
    return int(cfg["draw_hour"]), int(cfg.get("draw_minute", 0))


def next_submission_deadline(
    now: datetime, lottery_mode: str, tz_name: str
) -> tuple[datetime, date] | None:
    """Nächste Abgabefrist für eine Tippabgabe ab jetzt."""
    cfg = LOTTERY_CONFIG[lottery_mode]
    d = now.date()
    for _ in range(16):
        if d.weekday() in cfg["weekdays"]:
            h, m = lottery_close_hm(cfg, d)
            deadline = make_aware(datetime.combine(d, time(h, m)), tz_name)
            if deadline > now:
                return deadline, d
        d += timedelta(days=1)
    return None


def render_deadline_timer(lottery_mode: str, tz_name: str, height: int = 118) -> None:
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = timezone.utc
    now = datetime.now(tz)
    nxt = next_submission_deadline(now, lottery_mode, tz_name)
    cfg = LOTTERY_CONFIG[lottery_mode]
    if not nxt:
        st.caption("Keine Abgabefrist ermittelt.")
        return
    deadline, draw_date = nxt
    wd = cfg["weekday_names"].get(draw_date.weekday(), draw_date.strftime("%A"))
    label = cfg["label"]
    ts_ms = int(deadline.timestamp() * 1000)
    html = f"""
    <div style="font-family:Inter,system-ui,sans-serif;color:#f8fafc;
                background:#0b1220;border:1px solid #1e293b;border-radius:12px;
                padding:0.85rem 1rem;">
      <div style="font-size:0.72rem;color:#94a3b8;font-weight:500;">
        Abgabefrist · {label}
      </div>
      <div style="font-size:0.95rem;font-weight:700;margin-top:0.15rem;">
        {wd} {draw_date.strftime('%d.%m.%Y')} · {deadline.strftime('%H:%M')} Uhr
      </div>
      <div id="als-cd" style="font-size:1.35rem;font-weight:800;color:#00e5ff;
           letter-spacing:-0.03em;margin-top:0.2rem;font-variant-numeric:tabular-nums;">
        …
      </div>
      <div style="font-size:0.68rem;color:#64748b;margin-top:0.25rem;">
        Richtwert Online. Bundesland / Annahmestelle kann abweichen.
      </div>
    </div>
    <script>
      const target = {ts_ms};
      const el = document.getElementById("als-cd");
      function pad(n) {{ return String(n).padStart(2, "0"); }}
      function tick() {{
        const ms = target - Date.now();
        if (ms <= 0) {{
          el.textContent = "Abgabe vorbei";
          el.style.color = "#f87171";
          return;
        }}
        const s = Math.floor(ms / 1000);
        const d = Math.floor(s / 86400);
        const h = Math.floor((s % 86400) / 3600);
        const m = Math.floor((s % 3600) / 60);
        const sec = s % 60;
        el.textContent = (d > 0 ? d + "d " : "") + pad(h) + ":" + pad(m) + ":" + pad(sec);
        el.style.color = s < 3600 ? "#f87171" : (s < 6 * 3600 ? "#fbbf24" : "#00e5ff");
      }}
      tick();
      setInterval(tick, 1000);
    </script>
    """
    components.html(html, height=height)


def build_draw_info(game_key: str, from_date: date, jackpots: dict) -> list[dict]:
    cfg = LOTTERY_CONFIG[game_key]
    dates = next_n_draw_dates(from_date, cfg["weekdays"], n=3)
    jp = jackpots.get(game_key, {}).get("jackpot_mio", 20.0)
    source = jackpots.get(game_key, {}).get("source", "fallback")
    draws = []
    for i, d in enumerate(dates):
        seed = int(d.strftime("%Y%m%d")) + hash(game_key) % 1000
        tips = round(cfg["tips_base"] + (seed % 17) * 0.4 + i * 1.2, 1)
        jp_i = min(cfg["max_jackpot"], round(jp + i * (1.5 if game_key == "eurojackpot" else 0), 1))
        dh, dm = lottery_draw_hm(cfg, d)
        ch, cm = lottery_close_hm(cfg, d)
        draws.append({
            "date": d,
            "weekday_name": cfg["weekday_names"].get(d.weekday(), d.strftime("%A")),
            "jackpot_mio": jp_i,
            "tips_mio": tips,
            "source": source,
            "draw_hour": dh,
            "draw_minute": dm,
            "close_hour": ch,
            "close_minute": cm,
        })
    return draws


def format_reasons(reasons) -> str:
    lines = []
    for text, delta in sorted(reasons, key=lambda x: -abs(x[1])):
        sign = f"+{delta:.0f}" if delta > 0 else f"{delta:.0f}"
        lines.append(f"• {text} ({sign})")
    return "\n".join(lines) if lines else "• Keine starken Faktoren"


def build_google_calendar_ics(
    selected_rows: list[dict],
    lottery_label: str,
    draw_hour: int,
    draw_minute: int,
    tz_name: str,
    city: str,
) -> str:
    """
    Erzeugt eine .ics-Datei (iCalendar) mit Terminen für die ausgewählten
    Hochscore-Tage. Erinnerung um 09:00 Ortszeit (VALARM am Event-Start).
    Google Kalender: Datei importieren oder doppelklicken.
    """
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//AstroLotto Score//DE",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:AstroLotto Hochscore-Tage",
        f"X-WR-TIMEZONE:{tz_name}",
    ]
    for r in selected_rows:
        d = r["date"]  # date object
        # Event 09:00–09:30 Ortszeit (Erinnerung zum Tipp-Zeitpunkt)
        dt_start = f"{d.strftime('%Y%m%d')}T090000"
        dt_end = f"{d.strftime('%Y%m%d')}T093000"
        uid = f"astrolotto-{d.isoformat()}-{r['score']}@astrolotto.local"
        summary = f"🍀 AstroLotto {lottery_label} – Score {r['score']:.0f} %"
        desc = (
            f"AstroLotto Hochscore-Tag\\n"
            f"Spiel: {lottery_label}\\n"
            f"Kombinierter Score: {r['score']:.1f} % "
            f"(Allg. {r['general']:.1f} / Pers. {r['personal']:.1f})\\n"
            f"Ziehung ca. {draw_hour:02d}:{draw_minute:02d} Uhr\\n"
            f"Ort/TZ: {city} ({tz_name})\\n"
            f"Nur zur Unterhaltung – keine Gewinngarantie."
        )
        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
            f"DTSTART;TZID={tz_name}:{dt_start}",
            f"DTEND;TZID={tz_name}:{dt_end}",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{desc}",
            "STATUS:CONFIRMED",
            "TRANSP:OPAQUE",
            # Erinnerung zum Event-Start (09:00)
            "BEGIN:VALARM",
            "ACTION:DISPLAY",
            "DESCRIPTION:AstroLotto – heute ist ein Hochscore-Ziehungstag!",
            "TRIGGER:-PT0S",
            "END:VALARM",
            # Zusätzliche Erinnerung 1 Stunde vorher (optional)
            "BEGIN:VALARM",
            "ACTION:DISPLAY",
            "DESCRIPTION:AstroLotto – in 1 Stunde Erinnerung (Hochscore-Tag)",
            "TRIGGER:-PT1H",
            "END:VALARM",
            "END:VEVENT",
        ])
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


# ---------------------------------------------------------------------------
# UI – Clean Fortune Dashboard
# ---------------------------------------------------------------------------

if "profiles" not in st.session_state:
    st.session_state.profiles = []

# Splash screen: once per visit, ~2.7s
if not st.session_state.get("splash_done"):
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"], [data-testid="stHeader"], [data-testid="stToolbar"] {
            display: none !important;
        }
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
            background: #050508 !important;
        }
        .alsplash {
            position: fixed; inset: 0; z-index: 999999;
            background:
                repeating-linear-gradient(0deg, transparent, transparent 39px, rgba(0,229,255,0.06) 40px),
                repeating-linear-gradient(90deg, transparent, transparent 39px, rgba(0,229,255,0.06) 40px),
                #050508;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            font-family: Inter, system-ui, sans-serif;
        }
        .alsplash-k { width: 220px; height: 220px; margin-bottom: 0.4rem;
            filter: drop-shadow(0 0 18px rgba(0,229,255,0.55)); }
        .alsplash-title {
            font-size: 3.1rem; font-weight: 800; color: #ffffff; letter-spacing: -0.03em;
            margin: 0.15rem 0 0 0; line-height: 1.05;
        }
        .alsplash-sub {
            font-size: 1.05rem; font-weight: 700; color: #00e5ff;
            letter-spacing: 0.42em; margin: 0.35rem 0 1.35rem 0;
        }
        .alsplash-badge {
            display: inline-flex; align-items: center; gap: 0.55rem;
            padding: 0.4rem 0.95rem 0.4rem 0.45rem; border-radius: 999px;
            background: #0a0a0a; border: 1px solid rgba(0,229,255,0.4);
            box-shadow: 0 0 14px rgba(0,229,255,0.18);
            color: #e2e8f0; font-size: 0.95rem; font-weight: 500;
        }
        .alsplash-badge strong { color: #00e5ff; }
        .alsplash-bar {
            width: min(420px, 70vw); height: 8px; margin-top: 2.2rem;
            background: #111827; border-radius: 999px; overflow: hidden;
            box-shadow: 0 0 16px rgba(0,229,255,0.18);
        }
        .alsplash-bar > span {
            display: block; height: 100%; width: 0;
            background: linear-gradient(90deg, #00b8d4, #00e5ff);
            border-radius: 999px;
            animation: alsplash-load 2.5s ease-in-out forwards;
        }
        .alsplash-note { margin-top: 1.35rem; color: #64748b; font-size: 0.85rem; }
        @keyframes alsplash-load { from { width: 0; } to { width: 100%; } }
        </style>
        <div class="alsplash">
          <svg class="alsplash-k" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="48" cy="30" r="5" fill="#00E5FF"/>
            <circle cx="48" cy="70" r="4.5" fill="#00E5FF"/>
            <circle cx="48" cy="100" r="6" fill="#00E5FF"/>
            <circle cx="48" cy="130" r="4.5" fill="#00E5FF"/>
            <circle cx="48" cy="170" r="5" fill="#00E5FF"/>
            <circle cx="78" cy="70" r="4" fill="#00E5FF"/>
            <circle cx="95" cy="55" r="3.5" fill="#00E5FF"/>
            <circle cx="112" cy="40" r="4.5" fill="#00E5FF"/>
            <circle cx="135" cy="28" r="5" fill="#00E5FF"/>
            <circle cx="78" cy="130" r="4" fill="#00E5FF"/>
            <circle cx="95" cy="145" r="3.5" fill="#00E5FF"/>
            <circle cx="112" cy="160" r="4.5" fill="#00E5FF"/>
            <circle cx="135" cy="172" r="5" fill="#00E5FF"/>
            <circle cx="70" cy="100" r="3.5" fill="#00E5FF"/>
            <circle cx="100" cy="100" r="5" fill="#00E5FF"/>
            <g stroke="#00E5FF" stroke-width="1.4" stroke-linecap="round" opacity="0.9">
              <line x1="48" y1="30" x2="48" y2="70"/>
              <line x1="48" y1="70" x2="48" y2="100"/>
              <line x1="48" y1="100" x2="48" y2="130"/>
              <line x1="48" y1="130" x2="48" y2="170"/>
              <line x1="48" y1="100" x2="70" y2="100"/>
              <line x1="70" y1="100" x2="100" y2="100"/>
              <line x1="48" y1="70" x2="78" y2="70"/>
              <line x1="78" y1="70" x2="95" y2="55"/>
              <line x1="95" y1="55" x2="112" y2="40"/>
              <line x1="112" y1="40" x2="135" y2="28"/>
              <line x1="48" y1="100" x2="95" y2="55"/>
              <line x1="100" y1="100" x2="112" y2="40"/>
              <line x1="48" y1="130" x2="78" y2="130"/>
              <line x1="78" y1="130" x2="95" y2="145"/>
              <line x1="95" y1="145" x2="112" y2="160"/>
              <line x1="112" y1="160" x2="135" y2="172"/>
              <line x1="48" y1="100" x2="95" y2="145"/>
              <line x1="100" y1="100" x2="112" y2="160"/>
            </g>
          </svg>
          <div class="alsplash-title">AstroLotto</div>
          <div class="alsplash-sub">SCORE</div>
          <div class="alsplash-badge">
            Made by <strong>Kaisersoft.ai</strong>
          </div>
          <div class="alsplash-bar"><span></span></div>
          <div class="alsplash-note">Nur zur Unterhaltung · keine Gewinngarantie</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    time_module.sleep(2.7)
    st.session_state.splash_done = True
    st.rerun()

# Custom CSS – Dark Fortune (white on black)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root, html, body, .stApp {
        color-scheme: dark only !important;
    }

    html, body, .stApp {
        background-color: #050508 !important;
        color: #f8fafc !important;
        font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
    }
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stMain"],
    .stApp > header {
        background: transparent !important;
        color: #f8fafc !important;
    }
    [data-testid="stToolbar"] {
        color: #e2e8f0 !important;
    }

    /* Sternenhimmel + Sternschnuppen (hinter der UI) */
    .als-sky {
        position: fixed;
        inset: 0;
        z-index: 0;
        pointer-events: none;
        overflow: hidden;
        background:
            radial-gradient(ellipse 80% 50% at 15% 0%, rgba(40, 60, 140, 0.28), transparent 55%),
            radial-gradient(ellipse 70% 45% at 90% 100%, rgba(20, 30, 90, 0.32), transparent 50%),
            radial-gradient(ellipse 50% 40% at 50% 40%, rgba(8, 12, 40, 0.4), transparent 60%),
            #050508;
    }
    .als-star {
        position: absolute;
        background: #ffffff;
        border-radius: 50%;
        box-shadow: 0 0 6px 1px rgba(180, 230, 255, 0.55);
        animation: als-twinkle 3.4s ease-in-out infinite;
    }
    .als-star.bright {
        background: #e0f7ff;
        box-shadow: 0 0 10px 2px rgba(0, 229, 255, 0.55);
    }
    @keyframes als-twinkle {
        0%, 100% { opacity: 0.25; transform: scale(0.75); }
        50% { opacity: 1; transform: scale(1.2); }
    }
    .als-shoot {
        position: absolute;
        width: 110px;
        height: 2px;
        background: linear-gradient(90deg, rgba(255,255,255,0.95), rgba(0,229,255,0.55), transparent);
        border-radius: 999px;
        transform: rotate(-32deg);
        opacity: 0;
        filter: drop-shadow(0 0 6px rgba(0, 229, 255, 0.8));
        animation: als-shoot 8s linear infinite;
    }
    .als-shoot::after {
        content: "";
        position: absolute;
        right: -2px;
        top: 50%;
        width: 6px;
        height: 6px;
        margin-top: -3px;
        border-radius: 50%;
        background: #fff;
        box-shadow: 0 0 10px 3px rgba(0, 229, 255, 0.9);
    }
    @keyframes als-shoot {
        0% {
            transform: translate3d(0, 0, 0) rotate(-32deg);
            opacity: 0;
        }
        4% { opacity: 1; }
        18% {
            transform: translate3d(-55vw, 38vh, 0) rotate(-32deg);
            opacity: 0;
        }
        100% { opacity: 0; }
    }
    [data-testid="stAppViewContainer"] > .main,
    [data-testid="stMain"] {
        position: relative;
        z-index: 1;
        background: transparent !important;
    }
    [data-testid="stDecoration"] {
        background: transparent !important;
    }

    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div,
    [data-testid="stSidebarContent"] {
        background-color: #0a0a0f !important;
        color: #f8fafc !important;
        border-right: 1px solid #1e293b !important;
    }

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    section[data-testid="stSidebar"] small {
        color: #f1f5f9 !important;
        opacity: 1 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    section[data-testid="stSidebar"] .stCaption {
        color: #94a3b8 !important;
    }

    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] textarea,
    [data-testid="stAppViewContainer"] input,
    [data-testid="stAppViewContainer"] textarea,
    div[data-baseweb="input"],
    div[data-baseweb="input"] > div,
    div[data-baseweb="base-input"],
    div[data-baseweb="base-input"] input,
    .stDateInput input,
    .stTimeInput input,
    .stTextInput input,
    .stNumberInput input {
        background-color: #111827 !important;
        background: #111827 !important;
        color: #f8fafc !important;
        -webkit-text-fill-color: #f8fafc !important;
        caret-color: #00e5ff !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        opacity: 1 !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="input"],
    section[data-testid="stSidebar"] div[data-baseweb="base-input"],
    section[data-testid="stSidebar"] .stDateInput > div > div,
    section[data-testid="stSidebar"] .stTimeInput > div > div,
    section[data-testid="stSidebar"] .stTextInput > div > div {
        background-color: #111827 !important;
        background: #111827 !important;
        border-color: #334155 !important;
        color: #f8fafc !important;
    }

    div[data-baseweb="select"] > div,
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
    .stSelectbox div[data-baseweb="select"] > div,
    .stMultiSelect div[data-baseweb="select"] > div {
        background-color: #111827 !important;
        background: #111827 !important;
        color: #f8fafc !important;
        border-color: #334155 !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div {
        color: #f8fafc !important;
        -webkit-text-fill-color: #f8fafc !important;
    }
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    ul[role="listbox"],
    ul[role="listbox"] li,
    div[role="listbox"],
    li[role="option"],
    div[role="option"] {
        background-color: #0f172a !important;
        color: #f8fafc !important;
    }
    li[role="option"]:hover,
    div[role="option"]:hover {
        background-color: #1e293b !important;
        color: #f8fafc !important;
    }
    span[data-baseweb="tag"],
    [data-baseweb="tag"] {
        background-color: #042f2e !important;
        color: #5eead4 !important;
    }

    .stRadio label,
    .stCheckbox label,
    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] .stCheckbox label {
        color: #f8fafc !important;
        opacity: 1 !important;
    }

    .stButton > button[kind="primary"],
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background-color: #00c4d4 !important;
        border: 1px solid #00e5ff !important;
        color: #050508 !important;
        -webkit-text-fill-color: #050508 !important;
        font-weight: 600 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #00e5ff !important;
        border-color: #67f6ff !important;
        color: #050508 !important;
    }
    section[data-testid="stSidebar"] .stButton > button {
        background-color: #111827 !important;
        color: #f8fafc !important;
        -webkit-text-fill-color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
    }
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background-color: #00c4d4 !important;
        color: #050508 !important;
        -webkit-text-fill-color: #050508 !important;
        border: 1px solid #00e5ff !important;
    }
    .stButton > button:not([kind="primary"]) {
        background-color: #111827 !important;
        color: #f8fafc !important;
        -webkit-text-fill-color: #f8fafc !important;
        border: 1px solid #334155 !important;
    }
    .stDownloadButton > button {
        background-color: #111827 !important;
        color: #f8fafc !important;
        -webkit-text-fill-color: #f8fafc !important;
        border: 1px solid #334155 !important;
    }
    .stDownloadButton > button[kind="primary"] {
        background-color: #00c4d4 !important;
        color: #050508 !important;
        -webkit-text-fill-color: #050508 !important;
        border-color: #00e5ff !important;
    }

    [data-testid="stDataFrame"],
    [data-testid="stDataFrame"] *,
    [data-testid="stDataFrameResizable"],
    .stDataFrame {
        background-color: #0b1220 !important;
        color: #f8fafc !important;
    }
    [data-testid="stDataFrame"] [role="gridcell"],
    [data-testid="stDataFrame"] [role="columnheader"] {
        background-color: #0b1220 !important;
        color: #f8fafc !important;
        border-color: #1e293b !important;
    }
    [data-testid="stDataFrame"] [role="columnheader"] {
        background-color: #111827 !important;
        color: #e2e8f0 !important;
        font-weight: 600 !important;
    }

    [data-testid="stExpander"] {
        background-color: #0b1220 !important;
        border: 1px solid #1e293b !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
    }
    [data-testid="stExpander"] * {
        color: #f8fafc !important;
    }
    div[data-testid="stAlert"] {
        background-color: #0b1b33 !important;
        color: #bfdbfe !important;
        border: 1px solid #1e3a8a !important;
    }
    div[data-testid="stAlert"] * {
        color: #bfdbfe !important;
    }

    .cf-metric {
        background: #0b1220 !important;
        border-radius: 16px;
        padding: 1.25rem 1.35rem;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.06);
        border: 1px solid #1e293b;
        border-top: 3px solid #22c55e;
        text-align: left;
        min-height: 110px;
        color: #f8fafc !important;
    }
    .cf-metric.amber { border-top-color: #f59e0b; }
    .cf-metric.green { border-top-color: #22c55e; }
    .cf-metric.red { border-top-color: #ef4444; }
    .cf-metric .label { font-size: 0.8rem !important; color: #94a3b8 !important; font-weight: 500 !important; }
    .cf-metric .value { font-size: 2rem !important; font-weight: 800 !important; letter-spacing: -0.03em; line-height: 1.15; }
    .cf-metric .sub { font-size: 0.75rem !important; color: #94a3b8 !important; margin-top: 0.35rem; }

    .cf-pills { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0.75rem 0 1.25rem 0; }
    .cf-pill {
        display: inline-flex; align-items: center; gap: 0.35rem;
        background: #0b1220 !important; border: 1px solid #334155 !important;
        border-radius: 999px; padding: 0.35rem 0.85rem;
        font-size: 0.8rem !important; font-weight: 500 !important; color: #e2e8f0 !important;
    }
    .cf-pill.ok { border-color: #166534 !important; background: #052e16 !important; color: #86efac !important; }
    .cf-pill.warn { border-color: #854d0e !important; background: #1c1408 !important; color: #fde68a !important; }
    .cf-pill.bad { border-color: #7f1d1d !important; background: #1c0a0a !important; color: #fca5a5 !important; }

    .cf-weather {
        background: #0b1220 !important; border-radius: 14px; padding: 1.1rem 1rem;
        box-shadow: 0 0 16px rgba(0, 229, 255, 0.05); border: 1px solid #1e293b !important;
        text-align: center; min-height: 140px; color: #f8fafc !important;
    }
    .cf-weather .wd { font-size: 0.75rem !important; color: #94a3b8 !important; font-weight: 500 !important; }
    .cf-weather .sc { font-size: 1.5rem !important; font-weight: 800 !important; margin: 0.35rem 0; }
    .cf-weather .tag { font-size: 0.8rem !important; color: #cbd5e1 !important; }
    .cf-weather .jp { font-size: 0.75rem !important; color: #94a3b8 !important; margin-top: 0.4rem; }

    .cf-section { font-size: 1.05rem !important; font-weight: 700 !important; color: #f8fafc !important; margin: 1.5rem 0 0.35rem 0; }
    .cf-section-sub { font-size: 0.85rem !important; color: #94a3b8 !important; margin-bottom: 0.85rem; }
    .cf-made-by { margin-bottom: 0.85rem; }
    .cf-made-by-sidebar { margin-bottom: 0; margin-top: 0.15rem; }
    .cf-made-by-sidebar .cf-made-link {
        width: 100%;
        box-sizing: border-box;
        justify-content: flex-start;
    }
    .cf-made-link {
        display: inline-flex;
        align-items: center;
        gap: 0.55rem;
        text-decoration: none !important;
        padding: 0.35rem 0.75rem 0.35rem 0.4rem;
        border-radius: 999px;
        background: #0a0a0a !important;
        border: 1px solid rgba(0, 229, 255, 0.35) !important;
        box-shadow: 0 0 12px rgba(0, 229, 255, 0.15);
        transition: box-shadow 0.2s ease, border-color 0.2s ease;
    }
    .cf-made-link:hover {
        border-color: rgba(0, 229, 255, 0.7) !important;
        box-shadow: 0 0 18px rgba(0, 229, 255, 0.35);
    }
    .cf-made-logo {
        display: inline-flex;
        width: 28px;
        height: 28px;
        flex-shrink: 0;
    }
    .cf-made-logo svg {
        width: 28px;
        height: 28px;
        filter: drop-shadow(0 0 6px rgba(0, 229, 255, 0.55));
    }
    .cf-made-text {
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        color: #e2e8f0 !important;
        -webkit-text-fill-color: #e2e8f0 !important;
        letter-spacing: 0.01em;
    }
    .cf-made-text strong {
        color: #00e5ff !important;
        -webkit-text-fill-color: #00e5ff !important;
        font-weight: 700 !important;
    }

    .cf-hero-title { font-size: 1.5rem !important; font-weight: 800 !important; color: #f8fafc !important; letter-spacing: -0.03em; margin-bottom: 0.15rem; }
    .cf-hero-sub { font-size: 0.9rem !important; color: #94a3b8 !important; margin-bottom: 1.25rem; }
    .cf-logo-title { font-weight: 800 !important; font-size: 1.2rem !important; color: #f8fafc !important; letter-spacing: -0.02em; }
    .cf-logo-sub { font-size: 0.7rem !important; color: #00e5ff !important; font-weight: 600 !important; letter-spacing: 0.04em; }

    [data-testid="stAppViewContainer"] .stMarkdown p,
    [data-testid="stAppViewContainer"] .stMarkdown span,
    [data-testid="stAppViewContainer"] [data-testid="stCaptionContainer"] {
        color: #e2e8f0 !important;
    }
    [data-testid="stAppViewContainer"] [data-testid="stCaptionContainer"],
    [data-testid="stAppViewContainer"] .stCaption {
        color: #94a3b8 !important;
    }

    div[data-testid="stRadio"] { background-color: transparent !important; }
    div[data-testid="stRadio"] > div {
        background-color: #111827 !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        padding: 0.4rem 0.6rem !important;
    }
    div[data-testid="stRadio"] label {
        background-color: transparent !important;
        color: #f8fafc !important;
        -webkit-text-fill-color: #f8fafc !important;
        opacity: 1 !important;
    }
    div[data-testid="stRadio"] label p,
    div[data-testid="stRadio"] label span,
    div[data-testid="stRadio"] label div {
        color: #f8fafc !important;
        -webkit-text-fill-color: #f8fafc !important;
        opacity: 1 !important;
    }
    div[data-testid="stRadio"] [data-baseweb="radio"],
    div[data-testid="stRadio"] input[type="radio"] {
        accent-color: #00e5ff !important;
    }

    [data-testid="stArrowVegaLiteChart"],
    [data-testid="stVegaLiteChart"],
    [data-testid="stAltairChart"],
    .stVegaLiteChart,
    .stAltairChart,
    .vega-embed,
    .vega-embed summary,
    canvas.marks {
        background-color: #050508 !important;
        background: #050508 !important;
    }
    .vega-embed details,
    .vega-embed summary {
        background: #050508 !important;
        color: #f8fafc !important;
    }
    .js-plotly-plot, .plotly, .plot-container {
        background: #050508 !important;
    }

    [data-testid="stTable"] table,
    .stTable table {
        background-color: #0b1220 !important;
        color: #f8fafc !important;
        border-collapse: collapse !important;
        width: 100% !important;
    }
    [data-testid="stTable"] th,
    .stTable th {
        background-color: #111827 !important;
        color: #e2e8f0 !important;
        font-weight: 600 !important;
        padding: 0.6rem 0.75rem !important;
        border-bottom: 1px solid #1e293b !important;
    }
    [data-testid="stTable"] td,
    .stTable td {
        background-color: #0b1220 !important;
        color: #f8fafc !important;
        padding: 0.55rem 0.75rem !important;
        border-bottom: 1px solid #1e293b !important;
    }
    [data-testid="stTable"] tr:hover td {
        background-color: #111827 !important;
    }

    hr { border-color: #1e293b !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


def _starfield_html() -> str:
    """Fester Sternenhimmel mit zwinkernden Sternen und Sternschnuppen."""
    rng = random.Random(42)
    stars = []
    for _ in range(90):
        x = rng.uniform(0, 100)
        y = rng.uniform(0, 100)
        size = rng.choice([1, 1, 1, 2, 2, 3])
        delay = rng.uniform(0, 4.5)
        duration = rng.uniform(2.4, 4.8)
        cls = "als-star bright" if size >= 3 else "als-star"
        stars.append(
            f'<span class="{cls}" style="left:{x:.2f}%;top:{y:.2f}%;'
            f'width:{size}px;height:{size}px;animation-delay:{delay:.2f}s;'
            f'animation-duration:{duration:.2f}s"></span>'
        )
    shoots = []
    for i in range(7):
        top = rng.uniform(2, 52)
        left = rng.uniform(28, 98)
        delay = i * 1.15 + rng.uniform(0, 0.6)
        duration = rng.uniform(7.2, 10.5)
        shoots.append(
            f'<span class="als-shoot" style="top:{top:.1f}%;left:{left:.1f}%;'
            f'animation-delay:{delay:.2f}s;animation-duration:{duration:.2f}s"></span>'
        )
    return (
        '<div class="als-sky" aria-hidden="true">'
        + "".join(stars)
        + "".join(shoots)
        + "</div>"
    )


st.markdown(_starfield_html(), unsafe_allow_html=True)


def _metric_border(score: float) -> str:
    if score >= 70:
        return "green"
    if score >= 50:
        return "amber"
    return "red"


def _metric_html(label: str, value: float, sub: str) -> str:
    cls = _metric_border(value)
    color = score_color(value)
    return f"""
    <div class="cf-metric {cls}">
        <div class="label">{label}</div>
        <div class="value" style="color:{color} !important;">{value:.1f} %</div>
        <div class="sub">{sub}</div>
    </div>
    """


def _pill(text: str, kind: str = "") -> str:
    k = f" {kind}" if kind else ""
    return f'<span class="cf-pill{k}">{text}</span>'


def _weather_card(
    weekday: str, date_str: str, score: float, jackpot: float, tips: float, close_str: str = ""
) -> str:
    color = score_color(score)
    if score >= 70:
        tag = "Sehr gut"
    elif score >= 55:
        tag = "Gut"
    else:
        tag = "Mäßig"
    close_html = f'<div class="jp">Abgabe bis {close_str}</div>' if close_str else ""
    return f"""
    <div class="cf-weather">
        <div class="wd">{weekday}<br>{date_str}</div>
        <div class="sc" style="color:{color} !important;">{score:.1f} %</div>
        <div class="tag">{tag} {luck_symbol(score)}</div>
        <div class="jp">Jackpot ≈ {jackpot} Mio. € · Tipps ≈ {tips} Mio.</div>
        {close_html}
    </div>
    """


# ---- Sidebar: Inputs ----
with st.sidebar:
    st.markdown(
        """
        <div class="cf-made-by cf-made-by-sidebar">
          <a href="https://github.com/kaisersoft" target="_blank" rel="noopener noreferrer" class="cf-made-link">
            <span class="cf-made-logo" aria-hidden="true">
              <svg viewBox="0 0 200 200" width="26" height="26" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="48" cy="30" r="5" fill="#00E5FF"/>
                <circle cx="48" cy="70" r="4.5" fill="#00E5FF"/>
                <circle cx="48" cy="100" r="6" fill="#00E5FF"/>
                <circle cx="48" cy="130" r="4.5" fill="#00E5FF"/>
                <circle cx="48" cy="170" r="5" fill="#00E5FF"/>
                <circle cx="78" cy="70" r="4" fill="#00E5FF"/>
                <circle cx="95" cy="55" r="3.5" fill="#00E5FF"/>
                <circle cx="112" cy="40" r="4.5" fill="#00E5FF"/>
                <circle cx="135" cy="28" r="5" fill="#00E5FF"/>
                <circle cx="78" cy="130" r="4" fill="#00E5FF"/>
                <circle cx="95" cy="145" r="3.5" fill="#00E5FF"/>
                <circle cx="112" cy="160" r="4.5" fill="#00E5FF"/>
                <circle cx="135" cy="172" r="5" fill="#00E5FF"/>
                <circle cx="70" cy="100" r="3.5" fill="#00E5FF"/>
                <circle cx="100" cy="100" r="5" fill="#00E5FF"/>
                <g stroke="#00E5FF" stroke-width="1.4" stroke-linecap="round" opacity="0.9">
                  <line x1="48" y1="30" x2="48" y2="70"/>
                  <line x1="48" y1="70" x2="48" y2="100"/>
                  <line x1="48" y1="100" x2="48" y2="130"/>
                  <line x1="48" y1="130" x2="48" y2="170"/>
                  <line x1="48" y1="100" x2="70" y2="100"/>
                  <line x1="70" y1="100" x2="100" y2="100"/>
                  <line x1="48" y1="70" x2="78" y2="70"/>
                  <line x1="78" y1="70" x2="95" y2="55"/>
                  <line x1="95" y1="55" x2="112" y2="40"/>
                  <line x1="112" y1="40" x2="135" y2="28"/>
                  <line x1="48" y1="100" x2="95" y2="55"/>
                  <line x1="100" y1="100" x2="112" y2="40"/>
                  <line x1="48" y1="130" x2="78" y2="130"/>
                  <line x1="78" y1="130" x2="95" y2="145"/>
                  <line x1="95" y1="145" x2="112" y2="160"/>
                  <line x1="112" y1="160" x2="135" y2="172"/>
                  <line x1="48" y1="100" x2="95" y2="145"/>
                  <line x1="100" y1="100" x2="112" y2="160"/>
                </g>
              </svg>
            </span>
            <span class="cf-made-text">Made by <strong>Kaisersoft.ai</strong></span>
          </a>
        </div>
        <div style="display:flex;align-items:center;gap:0.5rem;margin:0.75rem 0 0.5rem 0;">
            <span style="font-size:1.6rem;">🍀</span>
            <div>
                <div class="cf-logo-title">AstroLotto</div>
                <div class="cf-logo-sub">SCORE</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Astrologische Bewertung für deine Lotto-Ziehungen.")

    # Profile defaults
    if st.session_state.profiles:
        labels = [
            f"{p['birth_date']} {p['birth_time']} · {p['city']}" for p in st.session_state.profiles
        ]
        choice = st.selectbox("Profil laden", ["— Neu eingeben —"] + labels, label_visibility="collapsed")
        if choice != "— Neu eingeben —":
            idx = labels.index(choice)
            p = st.session_state.profiles[idx]
            default_bdate = date.fromisoformat(p["birth_date"])
            default_btime = datetime.strptime(p["birth_time"], "%H:%M").time()
            default_city = p["city"]
        else:
            default_bdate = date(1980, 12, 12)
            default_btime = datetime.strptime("04:59", "%H:%M").time()
            default_city = "Bonn"
    else:
        default_bdate = date(1980, 12, 12)
        default_btime = datetime.strptime("04:59", "%H:%M").time()
        default_city = "Bonn"

    birth_date = st.date_input("Geburtsdatum", value=default_bdate)
    birth_time = st.time_input("Geburtszeit", value=default_btime)
    query_date = st.date_input("Abfrage-Datum", value=date.today())

    city_names = sorted(CITY_DATA.keys())
    try:
        default_idx = city_names.index(default_city)
    except ValueError:
        default_idx = city_names.index("Bonn")
    city_choice = st.selectbox("Geburtsort (Stadt)", city_names, index=default_idx)
    lat, lon, tz_name = CITY_DATA[city_choice]
    st.caption(f"{lat:.2f}°, {lon:.2f}° · {tz_name}")

    st.markdown("**Lotto-Modus**")
    if "lottery_mode" not in st.session_state:
        st.session_state.lottery_mode = "eurojackpot"
    b1, b2 = st.columns(2)
    with b1:
        if st.button(
            "Eurojackpot",
            key="btn_ej",
            use_container_width=True,
            type="primary" if st.session_state.lottery_mode == "eurojackpot" else "secondary",
        ):
            st.session_state.lottery_mode = "eurojackpot"
            st.rerun()
    with b2:
        if st.button(
            "6aus49",
            key="btn_649",
            use_container_width=True,
            type="primary" if st.session_state.lottery_mode == "6aus49" else "secondary",
        ):
            st.session_state.lottery_mode = "6aus49"
            st.rerun()
    lottery_mode = st.session_state.lottery_mode

    render_deadline_timer(lottery_mode, tz_name)

    save_profile = st.checkbox("Profil speichern", value=True)

    calculate = st.button("✨ Score berechnen", type="primary", use_container_width=True)

    st.markdown("---")
    with st.expander("Regelwerk v5", expanded=False):
        st.markdown(
            """
            **50 % Allgemein + 50 % Persönlich**

            Porphyry-Häuser · Aspektmuster · Progressionen ·
            Solar Return · Nordknoten/Chiron · VoC ·
            Merkur-Details · anwendende Aspekte ·
            Tagesherrscher · Planetenstunden · Eklipsen
            """
        )
    with st.expander("Hinweis", expanded=False):
        st.markdown(
            "Nur zur Unterhaltung. Keine Gewinngarantie. "
            "Ephemeriden: skyfield + JPL DE421."
        )
    if st.session_state.profiles:
        st.caption(f"{len(st.session_state.profiles)} Profil(e)")
        if st.button("Profile löschen", use_container_width=True):
            st.session_state.profiles = []
            st.rerun()


# ---- Main content ----
st.markdown(
    '<div class="cf-hero-title">Dein AstroLotto Score</div>'
    '<div class="cf-hero-sub">Astrologische Bewertung für deine Lotto-Ziehungen.</div>',
    unsafe_allow_html=True,
)

if calculate:
    with st.spinner("Berechne Ephemeriden, Progressionen & Scores …"):
        birth_naive = datetime.combine(birth_date, birth_time)
        birth_dt = make_aware(birth_naive, tz_name)
        query_naive = datetime.combine(query_date, time(12, 0))
        query_dt = make_aware(query_naive, tz_name)

        if save_profile:
            entry = {
                "birth_date": birth_date.isoformat(),
                "birth_time": birth_time.strftime("%H:%M"),
                "city": city_choice,
            }
            st.session_state.profiles = [p for p in st.session_state.profiles if p != entry]
            st.session_state.profiles.insert(0, entry)
            st.session_state.profiles = st.session_state.profiles[:8]

        gen_score, gen_reasons = score_general(query_dt, lat, lon)
        per_score, per_reasons = score_personal(birth_dt, query_dt, lat, lon)
        comb_score = (gen_score + per_score) / 2.0

        phase_frac = moon_phase_fraction(query_dt)
        phase_label = moon_phase_label(phase_frac)
        merc_rx = mercury_retrograde(query_dt)
        merc_stat = mercury_stationary(query_dt)
        merc_comb = mercury_combust(query_dt)
        voc = is_void_of_course(query_dt)
        day_ruler_name, _ = get_day_ruler(query_dt)
        hour_ruler_name, _ = get_planetary_hour(query_dt, lat, lon)
        eclipse = nearest_eclipse(query_dt)
        eclipse_ui = None
        if eclipse and eclipse.get("decay", 0) > 0:
            eclipse_ui = {
                "kind": eclipse["kind"],
                "label": eclipse["label"],
                "strength_label": eclipse["strength_label"],
                "hours": eclipse["hours"],
                "node_orb": round(eclipse["node_orb"], 1),
            }

        jackpots = fetch_jackpots()
        draws = build_draw_info(lottery_mode, query_date, jackpots)

        draw_scores = []
        for dr in draws:
            local_naive = datetime.combine(
                dr["date"], time(dr["draw_hour"], dr.get("draw_minute", 0))
            )
            dr_dt = make_aware(local_naive, tz_name)
            g, _ = score_general(dr_dt, lat, lon)
            p, _ = score_personal(birth_dt, dr_dt, lat, lon)
            draw_scores.append(round((g + p) / 2.0, 1))

        trend_dates = []
        trend_scores = []
        for i in range(14):
            d = query_date + timedelta(days=i)
            dt_i = make_aware(datetime.combine(d, time(12, 0)), tz_name)
            g, _ = score_general(dt_i, lat, lon)
            p, _ = score_personal(birth_dt, dt_i, lat, lon)
            trend_dates.append(d.strftime("%d.%m."))
            trend_scores.append(round((g + p) / 2.0, 1))

        high_score_draws = find_high_score_draws(
            birth_dt, lat, lon, lottery_mode, query_date, tz_name, threshold=75.0
        )

        # Persist results so UI interactions (calendar select) don't wipe the page
        st.session_state.results = {
            "gen_score": gen_score,
            "per_score": per_score,
            "comb_score": comb_score,
            "gen_reasons": gen_reasons,
            "per_reasons": per_reasons,
            "phase_label": phase_label,
            "merc_rx": merc_rx,
            "merc_stat": merc_stat,
            "merc_comb": merc_comb,
            "voc": voc,
            "eclipse_ui": eclipse_ui,
            "day_ruler_name": day_ruler_name,
            "hour_ruler_name": hour_ruler_name,
            "draws": draws,
            "draw_scores": draw_scores,
            "trend_dates": trend_dates,
            "trend_scores": trend_scores,
            "high_score_draws": high_score_draws,
            "lottery_mode": lottery_mode,
            "query_date": query_date,
            "birth_date": birth_date,
            "birth_time": birth_time,
            "city_choice": city_choice,
            "tz_name": tz_name,
            "lat": lat,
            "lon": lon,
        }
        # reset calendar form selection on new calculation
        st.session_state.pop("cal_form_labels", None)

# ---- Display persisted results ----
if st.session_state.get("results"):
    R = st.session_state.results
    gen_score = R["gen_score"]
    per_score = R["per_score"]
    comb_score = R["comb_score"]
    gen_reasons = R["gen_reasons"]
    per_reasons = R["per_reasons"]
    phase_label = R["phase_label"]
    merc_rx = R["merc_rx"]
    merc_stat = R["merc_stat"]
    merc_comb = R["merc_comb"]
    voc = R["voc"]
    eclipse_ui = R.get("eclipse_ui")
    day_ruler_name = R["day_ruler_name"]
    hour_ruler_name = R["hour_ruler_name"]
    draws = R["draws"]
    draw_scores = R["draw_scores"]
    trend_dates = R["trend_dates"]
    trend_scores = R["trend_scores"]
    high_score_draws = R["high_score_draws"]
    lottery_mode = R["lottery_mode"]
    query_date = R["query_date"]
    birth_date = R["birth_date"]
    birth_time = R["birth_time"]
    city_choice = R["city_choice"]
    tz_name = R["tz_name"]

    # --- Metric tiles ---
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(
            _metric_html("Kombiniert", comb_score, f"{luck_symbol(comb_score)} Astrologie + Transite"),
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            _metric_html("Allgemein", gen_score, "Aktuelle Astro-Einflüsse"),
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            _metric_html("Persönlich", per_score, "Individuell auf dich abgestimmt"),
            unsafe_allow_html=True,
        )

    # --- Status pills ---
    if merc_stat:
        merc_txt, merc_kind = "☿ Merkur stationär", "bad"
    elif merc_rx:
        merc_txt, merc_kind = "☿ Merkur rückläufig", "warn"
    else:
        merc_txt, merc_kind = "☿ Merkur direktläufig", "ok"
    voc_txt, voc_kind = ("Void of Course", "warn") if voc else ("nicht VoC", "ok")
    comb_txt, comb_kind = ("Merkur verbrannt", "warn") if merc_comb else ("", "")

    pills = [
        _pill(f"🌙 {phase_label}"),
        _pill(merc_txt, merc_kind),
        _pill(voc_txt, voc_kind),
        _pill(f"♥ Tagesherrscher {day_ruler_name}"),
        _pill(f"◎ Planetenstunde {hour_ruler_name}"),
    ]
    if comb_txt:
        pills.append(_pill(comb_txt, comb_kind))
    if eclipse_ui:
        ecl_kind = "warn"
        icon = "☀" if eclipse_ui["kind"] == "solar" else "🌑"
        when = "heute" if abs(eclipse_ui["hours"]) < 12 else (
            f"in {abs(eclipse_ui['hours'])} h" if eclipse_ui["hours"] > 0 else f"vor {abs(eclipse_ui['hours'])} h"
        )
        pills.append(
            _pill(
                f"{icon} {eclipse_ui['label']} ({eclipse_ui['strength_label']}, {when})",
                ecl_kind,
            )
        )
    st.markdown(f'<div class="cf-pills">{"".join(pills)}</div>', unsafe_allow_html=True)

    render_deadline_timer(lottery_mode, tz_name, height=122)

    # --- AstroWeather ---
    st.markdown(
        f'<div class="cf-section">AstroWeather – {LOTTERY_CONFIG[lottery_mode]["label"]}</div>'
        f'<div class="cf-section-sub">Astrologische Score-Vorschau für deine nächsten Ziehungen.</div>',
        unsafe_allow_html=True,
    )
    src = draws[0]["source"] if draws else "fallback"
    if src == "lotto.de":
        st.caption("Jackpots: live von lotto.de")
    else:
        st.caption("Jackpots: Fallback-Werte")

    if draw_scores:
        best_idx = draw_scores.index(max(draw_scores))
        best = draws[best_idx]
        st.markdown(
            f"**Bester Tag:** {best['weekday_name']} {best['date'].strftime('%d.%m.%Y')} "
            f"({draw_scores[best_idx]:.1f} %)"
        )

    wcols = st.columns(3)
    for i, (col, dr, sc) in enumerate(zip(wcols, draws, draw_scores)):
        with col:
            st.markdown(
                _weather_card(
                    dr["weekday_name"],
                    dr["date"].strftime("%d.%m.%Y"),
                    sc,
                    dr["jackpot_mio"],
                    dr["tips_mio"],
                    close_str=f"{dr.get('close_hour', 18):02d}:{dr.get('close_minute', 0):02d} Uhr",
                ),
                unsafe_allow_html=True,
            )

    # --- 14-day trend ---
    st.markdown(
        '<div class="cf-section">14-Tage Score-Trend</div>'
        '<div class="cf-section-sub">Dein kombinierter Score im Verlauf der nächsten 14 Tage.</div>',
        unsafe_allow_html=True,
    )
    import pandas as pd
    import altair as alt

    df_trend = pd.DataFrame({"Datum": trend_dates, "Score": trend_scores})
    trend_chart = (
        alt.Chart(df_trend)
        .mark_line(point=True, color="#16a34a", strokeWidth=2.5)
        .encode(
            x=alt.X("Datum:N", title=None, axis=alt.Axis(labelColor="#94a3b8", tickColor="#1e293b")),
            y=alt.Y(
                "Score:Q",
                title="Score %",
                scale=alt.Scale(domain=[0, 100]),
                axis=alt.Axis(labelColor="#94a3b8", gridColor="#1e293b", tickColor="#1e293b"),
            ),
            tooltip=["Datum", "Score"],
        )
        .properties(height=240)
        .configure(background="#050508")
        .configure_view(strokeWidth=0, fill="#050508")
        .configure_axis(grid=True, domainColor="#1e293b")
    )
    st.altair_chart(trend_chart, use_container_width=True)
    best_i = trend_scores.index(max(trend_scores))
    st.caption(
        f"Höchster Wert: **{trend_scores[best_i]} %** am {trend_dates[best_i]}"
    )

    # --- High scores + calendar form (no mid-selection wipe) ---
    st.markdown(
        f'<div class="cf-section">Beste Tage (High Scores) – Rest {query_date.year}</div>'
        f'<div class="cf-section-sub">'
        f'{LOTTERY_CONFIG[lottery_mode]["label"]}, kombinierter Score &gt; 75 %. '
        f'Tage auswählen und in Google Kalender exportieren.'
        f'</div>',
        unsafe_allow_html=True,
    )

    if high_score_draws:
        df_high = pd.DataFrame(
            [
                {
                    "Datum": r["date"].strftime("%d.%m.%Y"),
                    "Wochentag": r["weekday_name"],
                    "Kombiniert %": r["score"],
                    "Allgemein %": r["general"],
                    "Persönlich %": r["personal"],
                    "Symbol": luck_symbol(r["score"]),
                }
                for r in high_score_draws
            ]
        )
        st.table(df_high.set_index("Datum"))
        st.caption(f"**{len(high_score_draws)}** Tag(e) gefunden.")

        label_to_row = {
            f"{r['date'].strftime('%d.%m.%Y')} ({r['weekday_name']}) – {r['score']:.1f} %": r
            for r in high_score_draws
        }
        all_labels = list(label_to_row.keys())

        with st.form("calendar_export_form", clear_on_submit=False):
            select_all = st.checkbox("Alle auswählen", value=False)
            chosen_labels = st.multiselect(
                "Tage für Google-Kalender auswählen",
                options=all_labels,
                default=all_labels if False else [],
                help="Mehrere Tage markieren, dann unten auf „Auswahl übernehmen“ klicken.",
            )
            submitted = st.form_submit_button(
                "Auswahl übernehmen",
                use_container_width=True,
                type="secondary",
            )

        if submitted:
            if select_all:
                st.session_state.cal_form_labels = all_labels
            else:
                st.session_state.cal_form_labels = chosen_labels

        chosen_final = st.session_state.get("cal_form_labels", [])
        if select_all and submitted:
            chosen_final = all_labels

        selected_rows = [label_to_row[lb] for lb in chosen_final if lb in label_to_row]
        st.caption(f"**{len(selected_rows)}** Tag(e) für Export vorgemerkt")

        cfg = LOTTERY_CONFIG[lottery_mode]
        if selected_rows:
            ics_data = build_google_calendar_ics(
                selected_rows=selected_rows,
                lottery_label=cfg["label"],
                draw_hour=cfg["draw_hour"],
                draw_minute=cfg.get("draw_minute", 0),
                tz_name=tz_name,
                city=city_choice,
            )
            st.download_button(
                label=f"📅 {len(selected_rows)} Tag(e) in Google Kalender (.ics)",
                data=ics_data.encode("utf-8"),
                file_name=f"astrolotto_hochscore_{query_date.isoformat()}.ics",
                mime="text/calendar",
                use_container_width=True,
                type="primary",
            )
            with st.expander("So importierst du in Google Kalender"):
                st.markdown(
                    "1. `.ics`-Datei herunterladen  \n"
                    "2. [Google Kalender](https://calendar.google.com) → Zahnrad → **Einstellungen**  \n"
                    "3. **Importieren & exportieren** → Datei wählen → Importieren  \n\n"
                    f"Events um **09:00** Ortszeit mit Erinnerung. "
                    f"Ziehung ({cfg['label']}): ca. "
                    f"{cfg['draw_hour']:02d}:{cfg.get('draw_minute', 0):02d} Uhr."
                )
        else:
            st.caption("Tage auswählen und **Auswahl übernehmen** klicken, dann exportieren.")
    else:
        st.info("Keine Ziehungstage mit Score > 75 % im Rest des Jahres gefunden.")

    with st.expander("Allgemeine Faktoren (gewichtet)"):
        st.text(format_reasons(gen_reasons))
    with st.expander("Persönliche Faktoren (gewichtet)"):
        st.text(format_reasons(per_reasons))

    export_text = f"""AstroLotto Score v5 – Export
Abfrage: {query_date.isoformat()}
Geburt: {birth_date.isoformat()} {birth_time.strftime('%H:%M')} · {city_choice} ({tz_name})
Lotterie: {LOTTERY_CONFIG[lottery_mode]['label']}

Kombinierter Score: {comb_score:.1f} %
Allgemein: {gen_score:.1f} %
Persönlich: {per_score:.1f} %

Mondphase: {phase_label}
Merkur: {"stationär" if merc_stat else ("rückläufig" if merc_rx else "direktläufig")}
Merkur verbrannt: {"ja" if merc_comb else "nein"}
Void of Course: {"ja" if voc else "nein"}
Eklipse: {f"{eclipse_ui['label']} ({eclipse_ui['strength_label']}, {eclipse_ui['node_orb']}° Knoten)" if eclipse_ui else "keine im 3-Tage-Fenster"}
Tagesherrscher: {day_ruler_name}
Planetenstunde: {hour_ruler_name}

Nächste 3 Ziehungen:
""" + "\n".join(
        f"  {dr['weekday_name']} {dr['date'].isoformat()}: Score {sc:.1f} % · Jackpot ≈ {dr['jackpot_mio']} Mio. € · Tipps ≈ {dr['tips_mio']} Mio."
        for dr, sc in zip(draws, draw_scores)
    ) + f"""

Hochscore-Ziehungstage Rest {query_date.year} (> 75 %):
""" + (
        "\n".join(
            f"  {r['weekday_name']} {r['date'].isoformat()}: {r['score']:.1f} % "
            f"(Allg. {r['general']:.1f} / Pers. {r['personal']:.1f})"
            for r in high_score_draws
        )
        if high_score_draws
        else "  (keine)"
    ) + f"""

Allgemeine Faktoren:
{format_reasons(gen_reasons)}

Persönliche Faktoren:
{format_reasons(per_reasons)}

14-Tage-Verlauf:
""" + "\n".join(f"  {d}: {s} %" for d, s in zip(trend_dates, trend_scores))

    st.download_button(
        "Ergebnis als Text exportieren",
        data=export_text.encode("utf-8"),
        file_name=f"astrolotto_{query_date.isoformat()}.txt",
        mime="text/plain",
        use_container_width=True,
    )
    st.caption(
        "Ephemeriden: skyfield + JPL DE421 · Häuser: Porphyry · "
        "Nordknoten/Chiron: Näherung · Nur Unterhaltung"
    )

else:
    st.info(
        "Links in der Sidebar Geburtsdaten eingeben und **Score berechnen** klicken."
    )
