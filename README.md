# world-news-24nov2026

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/sayanget/world-news-24nov2026/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/sayanget/world-news-24nov2026/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

One image summing up the world's news on **Tuesday 24 November 2026**, laid out as a one-page broadsheet. It carries 37 stories from six regions plus global reports, and covers the whole day, including the US afternoon and evening.

The page has:
- three lead stories with drawn graphics;
- ten secondary stories, each with an illustrated banner;
- a count of stories by region;
- a timeline of the day in UTC and a row of key numbers;
- a locator map and 24 one-line items;
- a date check naming the big stories left out because they fell on 23 or 25 November.

Each story carries a status tag (confirmed, official, reported or claim) and names its sources.

Every story was checked against dated reports from that day: Reuters, AP, AFP, Bloomberg, Al Jazeera, BBC, DPA, ESA, CAS, the UN and others. The notes and source links are in [`research/stories.md`](research/stories.md), which also lists the dropped stories and a log of each render-and-fix pass.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

`main.ts` (Node 22, standard library only) checks that `entry.png` is a PNG or JPEG under 1 MiB, then copies it to `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`). It makes no network calls, and the output is the same bytes on every run.

## How the image is built

- `render/template.html` is the page: HTML, CSS and inline SVG drawings written by hand, set in locally installed fonts (Playfair Display, Source Serif Pro, Barlow Condensed, Inter).
- `render/build.py` draws the UTC timeline, measuring every label with the real font so none overlap. It draws the locator map from Natural Earth 1:110m land polygons, which are read from a cache outside the repo and not committed. It then screenshots the page at 1024×1024 with headless Google Chrome and saves `entry.png` as a lossless PNG with Pillow.

```sh
python3 -I render/build.py --land /path/to/ne_110m_land.geojson
```

Bounty: https://make.fun/bounty/news-image-20261124
