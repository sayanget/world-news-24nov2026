#!/usr/bin/env python3
"""Build entry.png: fill the HTML template with a UTC timeline and a locator map (drawn from
Natural Earth land polygons kept OUTSIDE the repo), screenshot it with headless Chrome at
1024x1024, then save a lossless PNG with Pillow.

Usage: python3 -I render/build.py [--land /path/to/ne_110m_land.geojson]
"""
import argparse
import json
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "out")

# ---------------------------------------------------------------- timeline
# (UTC hour, time label, text, row: -1 above the axis / +1 below, anchor, colour key).
# Times are of the event, or of the first dated report where the event time is not public
# (drawn as hollow dots). Labels are measured with the real font so that no two on a row overlap.
TL_W, TL_H, TL_FS = 912, 36, 11.5
EVENTS = [
    (1.00, "01:00", "Hanoi gas blast", -1, "start", "--as"),
    (1.55, "01:32", "Nepal M5.3 quake", 1, "start", "--as"),
    (5.50, "05:30", "Sanofi–Insmed deal", -1, "start", "--eu"),
    (11.00, "11:00", "UNAIDS report out", -1, "end", "--gl"),
    (11.23, "11:14", "Ariane 6 lifts off", 1, "start", "--am"),
    (14.50, "14:30", "CAS: Senegal title", -1, "end", "--af"),
    (15.58, "15:35", "Gaza security chief killed", 1, "start", "--me"),
    (16.10, "16:06", "Magyar meets Zelenskyy", -1, "start", "--eu"),
    (21.00, "21:00", "Dow closes at 50,018.70", 1, "start", "--am"),
]
REPORTED_AT = {"14:30", "15:35", "16:06"}  # time of first dated report, not of the event
COL = {"--as": "#c06a00", "--gl": "#6b4f1d", "--eu": "#5b3f8f", "--am": "#1f5f9e", "--af": "#23804a", "--me": "#b3261e"}
FONT_DIR = "/usr/share/fonts/truetype/sand-box/google/Barlow Condensed/"


def text_w(s, weight):
    try:
        from PIL import ImageFont
        f = ImageFont.truetype(FONT_DIR + f"BarlowCondensed-{weight}.ttf", int(TL_FS * 4))
        return f.getlength(s) / 4
    except OSError:
        return len(s) * TL_FS * 0.45


def timeline_svg():
    x0, x1 = 6, TL_W - 6
    ay = TL_H / 2
    sx = lambda h: x0 + h / 24 * (x1 - x0)
    o = [f'<svg viewBox="0 0 {TL_W} {TL_H}" width="{TL_W}" height="{TL_H}">',
         f'<line x1="{x0}" y1="{ay}" x2="{x1}" y2="{ay}" stroke="#161616" stroke-width="1.6"/>']
    for h in range(0, 25, 3):
        x = sx(h)
        o.append(f'<line x1="{x:.1f}" y1="{ay - 3}" x2="{x:.1f}" y2="{ay + 3}" stroke="#161616" stroke-width="1"/>')
    spans = {-1: [], 1: []}
    for h, tm, txt, row, anchor, c in EVENTS:
        x = sx(h)
        col = COL[c]
        w = text_w(tm, "ExtraBold") + text_w(" " + txt, "SemiBold")
        a = x - 2 if anchor == "start" else x + 2
        lo, hi = (a, a + w) if anchor == "start" else (a - w, a)
        assert lo >= 0 and hi <= TL_W, (tm, lo, hi)
        for plo, phi, ptm in spans[row]:
            assert hi + 6 < plo or lo > phi + 6, f"timeline labels overlap: {ptm} / {tm}"
        spans[row].append((lo, hi, tm))
        ty = 10 if row < 0 else TL_H - 2
        if tm in REPORTED_AT:
            o.append(f'<circle cx="{x:.1f}" cy="{ay}" r="3.2" fill="#f6f2e9" stroke="{col}" stroke-width="1.8"/>')
        else:
            o.append(f'<circle cx="{x:.1f}" cy="{ay}" r="3.6" fill="{col}" stroke="#f6f2e9" stroke-width="1"/>')
        o.append(f'<text x="{a:.1f}" y="{ty}" text-anchor="{anchor}" font-family="Barlow Condensed" font-size="{TL_FS}" fill="#161616">'
                 f'<tspan font-weight="800" fill="{col}">{tm}</tspan><tspan font-weight="600"> {txt}</tspan></text>')
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------- map
LON0, LON1, LAT0, LAT1 = -126.0, 170.0, -46.0, 68.0
MAP_W, MAP_H = 300, 116

# number, lon, lat, badge dx, dy (offset in px from the true point)
PINS = [
    (1, -73.99, 40.69, -15, -8),     # Brooklyn: Huawei verdict
    (4, -74.01, 40.71, 15, -12),     # Wall Street
    (10, -52.65, 5.24, 13, 8),       # Kourou: Ariane 6
    (5, 2.35, 48.86, -15, -10),      # Paris: Sanofi
    (12, 6.63, 46.52, -15, 8),       # Lausanne: CAS
    (13, 16.37, 48.21, -8, -13),     # Vienna: UNODC report
    (6, 22.29, 48.62, 6, -12.6),     # Uzhhorod
    (8, 35.14, 47.84, 15, -8),       # Zaporizhzhia
    (9, 34.45, 31.50, -14.5, 5.4),   # Gaza
    (7, 44.39, 35.47, 18, -4),       # Kirkuk
    (2, 46.68, 24.71, 14, 8),        # Riyadh
    (3, 121.47, 31.23, 14, -9),      # Shanghai
    (11, 159.95, -9.43, -9, 13),     # Honiara
]


# Places of the one-liners ("Also on Tuesday 24 November"), drawn as small grey dots.
DOTS = [
    (-120.5, 46.6), (-97.7, 30.5), (-75.5, 10.4),                      # Washington st., Dell (Texas), Cartagena
    (11.6, 48.1), (7.75, 48.58), (2.13, 48.8), (-0.13, 51.5), (-3.7, 40.4), (6.14, 46.2),  # Europe
    (7.5, 9.06), (-17.45, 14.7), (15.3, -4.3),                         # Abuja, Dakar, Kinshasa
    (55.9, 25.8), (51.4, 35.7), (51.5, 25.3),                          # Ras Al Khaimah, Tehran, Doha
    (105.85, 21.0), (87.67, 27.35), (98.5, 39.7), (90.4, 23.8), (121.0, 14.6), (116.4, 39.9),  # Asia
]


def proj(lon, lat):
    return (lon - LON0) / (LON1 - LON0) * MAP_W, (LAT1 - lat) / (LAT1 - LAT0) * MAP_H


def land_path(geojson_path):
    with open(geojson_path, encoding="utf-8") as f:
        data = json.load(f)
    parts = []
    for feat in data["features"]:
        geom = feat["geometry"]
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        for poly in polys:
            ring = poly[0]
            pts = [proj(lon, lat) for lon, lat in ring]
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            if max(xs) < 0 or min(xs) > MAP_W or max(ys) < 0 or min(ys) > MAP_H:
                continue
            parts.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z")
    return "".join(parts)


def map_svg(geojson_path):
    o = [f'<svg class="map" viewBox="0 0 {MAP_W} {MAP_H}" width="{MAP_W}" height="{MAP_H}">',
         f'<defs><clipPath id="mc"><rect width="{MAP_W}" height="{MAP_H}"/></clipPath></defs>',
         f'<rect width="{MAP_W}" height="{MAP_H}" fill="#dbe5ea"/>']
    if geojson_path and os.path.exists(geojson_path):
        o.append(f'<path clip-path="url(#mc)" d="{land_path(geojson_path)}" fill="#cdc4ae" stroke="#b1a78f" stroke-width="0.4"/>')
    else:
        print(f"warning: no land polygons at {geojson_path}; map drawn without coastlines", file=sys.stderr)
    for lon, lat in DOTS:
        x, y = proj(lon, lat)
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.9" fill="#6a6a6a" stroke="#fff" stroke-width="0.6"/>')
    for n, lon, lat, dx, dy in PINS:
        x, y = proj(lon, lat)
        bx, by = x + dx, y + dy
        col = "#b3261e" if n <= 3 else "#161616"
        o.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{col}" stroke-width="0.9"/>')
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.8" fill="{col}"/>')
        o.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="6.6" fill="{col}" stroke="#fff" stroke-width="0.9"/>')
        o.append(f'<text x="{bx:.1f}" y="{by + 3.2:.1f}" text-anchor="middle" font-family="Barlow Condensed" '
                 f'font-weight="700" font-size="{9.5 if n < 10 else 8.6}" fill="#fff">{n}</text>')
    o.append("</svg>")
    return "".join(o)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--land", default="/workspace/news-image/cache/ne_110m_land.geojson")
    ap.add_argument("--chrome", default="/usr/bin/google-chrome")
    args = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(HERE, "template.html"), encoding="utf-8") as f:
        html = f.read()
    html = html.replace("<!--MAP-->", map_svg(args.land)).replace("<!--TIMELINE-->", timeline_svg())
    page = os.path.join(OUT, "page.html")
    with open(page, "w", encoding="utf-8") as f:
        f.write(html)

    raw = os.path.join(OUT, "raw.png")
    subprocess.run([args.chrome, "--headless=new", "--no-sandbox", "--disable-gpu",
                    "--hide-scrollbars", "--force-device-scale-factor=1",
                    "--window-size=1024,1024", "--default-background-color=00000000",
                    "--virtual-time-budget=3000",
                    f"--screenshot={raw}", "file://" + page],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    im = Image.open(raw).convert("RGB")
    assert im.size == (1024, 1024), im.size
    dst = os.path.join(ROOT, "entry.png")
    im.save(dst, optimize=True)
    size = os.path.getsize(dst)
    if size > 900_000:  # keep well under the 1 MiB gate
        im.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(dst, optimize=True)
        size = os.path.getsize(dst)
    im.resize((300, 300), Image.LANCZOS).save(os.path.join(OUT, "small300.png"))
    print(f"wrote {dst}: {size} bytes", file=sys.stderr)


if __name__ == "__main__":
    main()
