# world-news-24nov2026

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/sayanget/world-news-24nov2026/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/sayanget/world-news-24nov2026/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

One image summing up the world's news on **Tuesday 24 November 2026**, laid out as a one-page broadsheet: three lead stories with drawn graphics, eight secondary stories, a locator map, and a list of other events grouped by region. It covers the whole day, including the US afternoon and evening.

Every story was checked against dated reports from that day (Reuters, AP, AFP, Bloomberg, Al Jazeera, Euronews, ESA, CAS and others). The notes and source links are in [`research/stories.md`](research/stories.md), which also lists the stories that were dropped because they happened on another day.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

`main.ts` (Node 22, standard library only) checks that `entry.png` is a PNG or JPEG under 1 MiB, then copies it to `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`). It makes no network calls, and the output is the same bytes on every run.

## How the image is built

- `render/template.html` is the page: HTML, CSS and inline SVG drawings written by hand, set in locally installed fonts (Playfair Display, Source Serif Pro, Barlow Condensed, Inter).
- `render/build.py` draws the locator map from Natural Earth 1:110m land polygons, which are read from a cache outside the repo and not committed. It then screenshots the page at 1024×1024 with headless Google Chrome and saves `entry.png` with Pillow.

```sh
python3 -I render/build.py --land /path/to/ne_110m_land.geojson
```

Bounty: https://make.fun/bounty/news-image-20261124
