#!/usr/bin/env python3
"""Build entry.png: fill the HTML template (adding a world map drawn from Natural Earth
land polygons kept OUTSIDE the repo), screenshot it with headless Chrome at 1024x1024,
then shrink the PNG with Pillow.

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

# Map window (equirectangular), in degrees, and its pixel size on the page.
LON0, LON1, LAT0, LAT1 = -128.0, 152.0, -38.0, 64.0
MAP_W, MAP_H = 300, 110

# Pins: number, lon, lat, label dx/dy (badge offset from the true point, in px).
PINS = [
    (1, -73.99, 40.69, -14, -10),   # Brooklyn: Huawei verdict
    (4, -74.01, 40.71, -16, 9),     # Wall Street
    (2, 46.68, 24.71, 12, 10),      # Riyadh
    (3, 121.47, 31.23, 13, 4),      # Shanghai
    (5, 2.35, 48.86, -15, -6),      # Paris: Sanofi
    (6, 34.45, 31.50, -14, 10),     # Gaza
    (7, 35.14, 47.84, 8, -10),      # Zaporizhzhia
    (8, 7.75, 48.58, 6, -11),       # Strasbourg: ECHR
    (9, -17.45, 14.69, -13, 6),     # Senegal (AFCON title)
    (11, 25.0, -2.5, 10, 9),        # DR Congo: Ebola vaccine
]


def proj(lon, lat):
    x = (lon - LON0) / (LON1 - LON0) * MAP_W
    y = (LAT1 - lat) / (LAT1 - LAT0) * MAP_H
    return x, y


def land_path(geojson_path):
    with open(geojson_path, encoding="utf-8") as f:
        data = json.load(f)
    parts = []
    for feat in data["features"]:
        geom = feat["geometry"]
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        for poly in polys:
            for ring in poly[:1]:  # outer rings only; 110m land has no holes worth drawing
                pts = [proj(lon, lat) for lon, lat in ring]
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                if max(xs) < 0 or min(xs) > MAP_W or max(ys) < 0 or min(ys) > MAP_H:
                    continue
                d = "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z"
                parts.append(d)
    return "".join(parts)


def map_svg(geojson_path):
    d = land_path(geojson_path)
    out = [f'<svg class="map" viewBox="0 0 {MAP_W} {MAP_H}" width="{MAP_W}" height="{MAP_H}">',
           f'<rect width="{MAP_W}" height="{MAP_H}" fill="#dfe7ea"/>',
           f'<path d="{d}" fill="#c9c1ad" stroke="#b3aa94" stroke-width="0.4"/>']
    for n, lon, lat, dx, dy in PINS:
        x, y = proj(lon, lat)
        bx, by = x + dx, y + dy
        col = "#b3261e" if n <= 3 else "#1d1d1d"
        out.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{col}" stroke-width="0.9"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.8" fill="{col}"/>')
        out.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="6.2" fill="{col}" stroke="#fff" stroke-width="0.8"/>')
        out.append(f'<text x="{bx:.1f}" y="{by + 3.1:.1f}" text-anchor="middle" '
                   f'font-family="Barlow Condensed" font-weight="700" font-size="9" fill="#fff">{n}</text>')
    out.append("</svg>")
    return "".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--land", default="/workspace/news-image/cache/ne_110m_land.geojson")
    ap.add_argument("--chrome", default="/usr/bin/google-chrome")
    args = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(HERE, "template.html"), encoding="utf-8") as f:
        html = f.read()
    html = html.replace("<!--MAP-->", map_svg(args.land))
    page = os.path.join(OUT, "page.html")
    with open(page, "w", encoding="utf-8") as f:
        f.write(html)

    raw = os.path.join(OUT, "raw.png")
    subprocess.run([args.chrome, "--headless=new", "--no-sandbox", "--disable-gpu",
                    "--hide-scrollbars", "--force-device-scale-factor=1",
                    "--window-size=1024,1024", "--default-background-color=00000000",
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
    print(f"wrote {dst}: {size} bytes", file=sys.stderr)


if __name__ == "__main__":
    main()
