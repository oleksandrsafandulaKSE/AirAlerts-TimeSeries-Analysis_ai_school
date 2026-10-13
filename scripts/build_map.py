"""M8: SVG map of Ukraine from geoBoundaries ADM1 (plans/M8.md §3), built offline once.

    python scripts/build_map.py   # data/raw/geoboundaries/*.geojson -> site_src/map_ukraine.json

Source: geoBoundaries gbOpen UKR ADM1 (boundaryID UKR-ADM1-14850775, commit 9469f09), derived from OpenStreetMap,
licence ODbL 1.0 -> attribution "(c) OpenStreetMap contributors (ODbL), via geoBoundaries" shown on the page.
Download (once):  curl -L -o data/raw/geoboundaries/geoBoundaries-UKR-ADM1_simplified.geojson \\
  https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/UKR/ADM1/geoBoundaries-UKR-ADM1_simplified.geojson
Shapes are mapped to units by their exact ISO 3166-2 code (no name matching); Luhanska and Crimea + Sevastopol are kept
as grey "not forecast" shapes. Projection: equirectangular scaled by cos(48.5 deg); pure-Python Douglas-Peucker.
"""
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "raw" / "geoboundaries" / "geoBoundaries-UKR-ADM1_simplified.geojson"
SHA256 = "4a5947e7497574d51f93255dfa7e03dce0c7acf6ecee52d25773a5205854a399"
OUT = ROOT / "site_src" / "map_ukraine.json"
REGIONS = ROOT / "netlify" / "live" / "data" / "regions.json"

ISO_TO_UNIT = {
    "UA-30": "kyiv_city", "UA-74": "chernihivska", "UA-59": "sumska", "UA-63": "kharkivska", "UA-14": "donetska",
    "UA-12": "dnipropetrovska", "UA-23": "zaporizka", "UA-65": "khersonska", "UA-48": "mykolaivska", "UA-32": "kyivska",
    "UA-18": "zhytomyrska", "UA-05": "vinnytska", "UA-71": "cherkaska", "UA-53": "poltavska", "UA-35": "kirovohradska",
    "UA-51": "odeska", "UA-68": "khmelnytska", "UA-56": "rivnenska", "UA-07": "volynska", "UA-46": "lvivska",
    "UA-61": "ternopilska", "UA-26": "ivano_frankivska", "UA-21": "zakarpatska", "UA-77": "chernivetska",
}
GREY = {"UA-09": "luhanska", "UA-43": "crimea", "UA-40": "crimea"}      # not forecast (D-008 / not in the data)
WIDTH = 1000.0
LAT0 = 48.5
TOL = 0.45                                                                 # px, Douglas-Peucker tolerance
MAX_BYTES = 150_000


def project(lon, lat, box):
    x0, y1, k = box
    return ((lon - x0) * k * math.cos(math.radians(LAT0)), (y1 - lat) * k)


def dp(pts, tol):
    """Douglas-Peucker on an open polyline (iterative)."""
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        (ax, ay), (bx, by) = pts[a], pts[b]
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy)
        best, idx = -1.0, None
        for i in range(a + 1, b):
            px, py = pts[i]
            d = abs(dy * (px - ax) - dx * (py - ay)) / L if L else math.hypot(px - ax, py - ay)
            if d > best:
                best, idx = d, i
        if idx is not None and best > tol:
            keep[idx] = True
            stack += [(a, idx), (idx, b)]
    return [p for p, k in zip(pts, keep) if k]


def inside(x, y, rings):
    """Even-odd point-in-polygon over all rings."""
    c = False
    for r in rings:
        for i in range(len(r) - 1):
            (x1, y1), (x2, y2) = r[i], r[i + 1]
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                c = not c
    return c


def seg_dist(px, py, a, b):
    (ax, ay), (bx, by) = a, b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def label_point(rings, holes=()):
    """Interior point farthest from the boundary (grid search, then a finer pass): labels never sit on a neighbour."""
    xs = [x for r in rings for x, _ in r]
    ys = [y for r in rings for _, y in r]
    edges = [(r[i], r[i + 1]) for r in list(rings) + list(holes) for i in range(len(r) - 1)]
    best, step = None, max(max(xs) - min(xs), max(ys) - min(ys)) / 30
    cands = [(min(xs) + i * step, min(ys) + j * step) for i in range(31) for j in range(31)]
    for _ in range(2):
        for x, y in cands:
            if not inside(x, y, rings) or (holes and inside(x, y, holes)):
                continue
            d = min(seg_dist(x, y, a, b) for a, b in edges)
            if best is None or d > best[0]:
                best = (d, x, y)
        step /= 6
        cands = [(best[1] + i * step, best[2] + j * step) for i in range(-6, 7) for j in range(-6, 7)]
    return [round(best[1], 1), round(best[2], 1)]


def polygons(geom):
    if geom["type"] == "Polygon":
        return [geom["coordinates"]]
    if geom["type"] == "MultiPolygon":
        return geom["coordinates"]
    raise ValueError(f"unexpected geometry {geom['type']}")


def build(src=SRC):
    raw = src.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise ValueError(f"{src.name}: sha256 differs from the pinned release")
    gj = json.loads(raw)
    feats = gj["features"]
    isos = [f["properties"]["shapeISO"] for f in feats]
    if sorted(isos) != sorted(set(ISO_TO_UNIT) | set(GREY)):
        raise ValueError(f"ISO codes differ from the mapping table: {sorted(set(isos) ^ (set(ISO_TO_UNIT) | set(GREY)))}")
    units = json.loads(REGIONS.read_text())["units"]
    if sorted(ISO_TO_UNIT.values()) != sorted(units):
        raise ValueError("ISO table does not cover exactly the 24 units of regions.json")
    lons = [c[0] for f in feats for poly in polygons(f["geometry"]) for ring in poly for c in ring]
    lats = [c[1] for f in feats for poly in polygons(f["geometry"]) for ring in poly for c in ring]
    k = WIDTH / ((max(lons) - min(lons)) * math.cos(math.radians(LAT0)))
    box = (min(lons), max(lats), k)
    height = (max(lats) - min(lats)) * k
    shapes, labels, grey, rings = {}, {}, {}, {}
    for f in feats:
        iso = f["properties"]["shapeISO"]
        tol = TOL / 3 if iso == "UA-30" else TOL                          # Kyiv City is ~20 px wide
        parts, kept = [], []
        for poly in polygons(f["geometry"]):
            for ring in poly:
                s = dp([project(lon, lat, box) for lon, lat in ring], tol)
                if len(s) < 4:
                    continue
                parts.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in s[:-1]) + "Z")
                kept.append(s)
        d = "".join(parts)
        rings[iso] = kept
        if iso in ISO_TO_UNIT:
            shapes[ISO_TO_UNIT[iso]] = d
        else:
            grey[GREY[iso]] = grey.get(GREY[iso], "") + d
    for iso, u in ISO_TO_UNIT.items():                                    # Kyiv City is an enclave of Kyivska
        labels[u] = label_point(rings[iso], rings["UA-30"] if u == "kyivska" else ())
    out = {"viewBox": [0, 0, round(WIDTH, 1), round(height, 1)], "units": shapes, "labels": labels, "grey": grey,
           "attribution": "Boundaries: © OpenStreetMap contributors (ODbL), via geoBoundaries (UKR ADM1, 2023 build)",
           "source_sha256": SHA256}
    text = json.dumps(out, separators=(",", ":"))
    if len(text) > MAX_BYTES:
        raise ValueError(f"map is {len(text):,} bytes > {MAX_BYTES:,}: raise TOL")
    return out, text


def main():
    out, text = build()
    OUT.write_text(text)
    print(f"[map] {len(out['units'])} units + grey {sorted(out['grey'])}, viewBox {out['viewBox']}, {len(text):,} bytes -> {OUT}")


if __name__ == "__main__":
    sys.exit(main())
