[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/kingpoogh-stack/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/kingpoogh-stack/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

# The World Today — Tuesday, 24 November 2026

An entry for make.fun's [“Sum up 24 November's world news in one image” bounty](https://make.fun/bounty/news-image-20261124).

A one-page broadsheet front page summing up Tuesday, 24 November
2026's world news in a single 1024×1024 image. The date runs in the
folio line, the World in Brief header band and the running order of
the page, so the day is named wherever a reader's eye lands.

The lead story is the Strait of Hormuz crisis: three oil tankers set
ablaze by sea mines, as reported by Iran's Revolutionary Guard, with
a wide strait panel — three burning tankers, a US escort warship and
the far shore — a caption and credit, a Gulf Bureau byline, two full
columns of report and a pull-quote rail carrying a shipping
analyst's words on the decoy “Line Breaker” tanker that has been
broadcasting false positions in the strait. Around it, each with its
own panel, headline and column text: President Zelenskyy's call for
four-way talks after the Shenzhen trilateral summit (flags panel);
Washington's blacklisting of Singapore's Megaspeed in the Nvidia
spy scandal, with Jensen Huang reinstated (dealing-room panel); the
Banten candy-factory fire, whose death toll rose to 24 (floodlit
factory panel); Norway's supreme court voiding disputed oil
licences as the fallout from the COP31 collapse spread (plenary
panel); and the Pentagon's rebuke of Canada over defence spending
and the F-35 review (Capitol panel). A boxed Sport section covers
the seven-goal thriller at San Siro that stunned Inter, Australia's
command of the deciding Test against South Africa, and FIFA's
confirmation of the 2031 and 2035 Women's World Cup hosts. A
“Markets at a Glance” data box (Brent, WTI, gold, VIX, Nikkei,
KOSPI, S&P 500, Nasdaq) sits beside a six-city weather box, and a
six-item World in Brief strip covers South Korea, China, Sudan, the
Ebola outbreak, Russia and South Africa.

## How it works

- `tools/render_page.py` — build-time renderer (uses Pillow on the
  build machine only). It draws the page at twice its final size and
  downscales it, for a smoother printed finish: masthead and folio
  line, markets ticker, an “Inside today” strip, procedurally drawn
  press-illustration panels with captions and credits, stories set
  in real newspaper columns with column rules, a pull-quote box, a
  markets data box and a weather box. It writes
  `assets/final-page.png`.
- `assets/final-page.png` — the committed front-page image
  (1024×1024, well under the 1 MiB limit).
- `main.py` — the entry point. Pure Python 3 standard library only:
  it copies `assets/final-page.png` to `entry.png` in the output
  directory (`$MAKEFUN_OUTPUT_DIR` if set, otherwise `/output`). It
  runs from any working directory and always produces byte-identical
  output.
