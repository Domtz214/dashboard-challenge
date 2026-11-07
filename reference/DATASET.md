# Dataset guide

**The Gilded Ace is fictional; its data is synthetic and calibrated to public aggregates.** The world around it is real: files in `data/4_context/real_sources/` are unmodified public data (Las Vegas tourism, NOAA weather, Missouri slot benchmarks). Real and synthetic rows never share a file.

> **Status: `0.9.0-draft`.** Tables, keys and definitions are stable. Calibration approval is pending; values may change before `1.0.0`. NOAA reuse terms are documented; LVCVA and Missouri redistribution evidence is still required (see [SOURCES.md](SOURCES.md)).

## Where to start

1. Open `data/1_prepared_views/prepared_daily_view` (one row per machine per day, already joined and in dollars) and `property_day` (one row per day). Together with `data/2_machine_decision/action_catalog` they give a first dashboard with no joins.
2. Use `player_period` for tracked player results per month.
3. Drill into the source tables to test one explanation.

## Layout

```
data/
  1_prepared_views/     start here: prepared_daily_view, player_period, property_day
  2_machine_decision/   calendar_day, floor_locations, floor_walkways, machines, game_math,
                        placements, machine_day, operations, cost_rules, action_catalog
  3_guests/             players, sessions, trips, loyalty_ledger, fnb_transactions  (POS includes uncarded sales)
  4_context/            zone_traffic_hourly, events
    real_sources/       weather_daily, city_visitation_monthly, visitor_profile_summary,
                        visitor_profile_segments, benchmark_public (+ property/state totals)
  5_optional/           machine_hour, security_incidents, shift_roster, visitor_profile_monthly
  manifest.json         every data file with row count and SHA-256 (verify downloads)
GUIDE.md                participant guide: the challenge, setup, common issues, submission
reference/
  DATASET.md            this file: layout, row counts, conventions, money definitions
  DATA_DICTIONARY.md    every table and column
  SOURCES.md            provenance of the real files
```

Every table comes as **`.parquet`** (typed, recommended) and **`.csv.gz`** (the same rows; pandas and DuckDB read it directly; unzip it first for Excel or Tableau). No file is over 100 MB.

| Folder | Table | One row per | Rows |
| --- | --- | --- | ---: |
| 1_prepared_views | prepared_daily_view | machine × gaming date | 56,110 |
| | player_period | tracked player × month | 148,893 |
| | property_day | gaming date | 181 |
| 2_machine_decision | calendar_day | gaming date | 181 |
| | floor_locations | zone, bank, slot, outlet or entrance | 378 |
| | floor_walkways | walkway between zones | 10 |
| | machines | machine | 310 |
| | game_math | game configuration | 10 |
| | placements | machine × location/config interval | 314 |
| | machine_day | machine × gaming date | 56,110 |
| | operations | repair, move, install or retirement | 1,226 |
| | cost_rules | supplied cost rule | 9 |
| | action_catalog | action the budget can buy | 13 |
| 3_guests | players | loyalty account | 113,890 |
| | sessions | carded session segment | 776,297 |
| | trips | observed property visit | 351,729 |
| | loyalty_ledger | points award or redemption | 782,773 |
| | fnb_transactions | POS ticket | 227,833 |
| 4_context | zone_traffic_hourly | sensor × hour | 30,401 |
| | events | event | 8 |
| real_sources | weather_daily | calendar day | 181 |
| | city_visitation_monthly | month | 6 |
| | visitor_profile_summary | survey metric | 74 |
| | visitor_profile_segments | metric × segment | 1,406 |
| | benchmark_public | Missouri casino × slot category × month | 700 |
| | benchmark_property_monthly | Missouri casino × month (published totals) | 78 |
| | benchmark_state_monthly | month (published state totals) | 6 |
| 5_optional | machine_hour | machine × hour | 1,321,908 |
| | security_incidents | reported incident | 3,865 |
| | shift_roster | staff assignment | 10,317 |
| | visitor_profile_monthly | fictional survey metric × month | 42 |

## Conventions

- **Window:** gaming dates January 1 to June 30, 2025.
- **Gaming day:** runs 06:00 to 06:00 local time (America/Los_Angeles). Timestamps ending `_utc` are UTC; `_local` is local time. Gaming date 2025-03-08 has 23 hours because of daylight saving. Use `scheduled_seconds`, never assume 24 h.
- **Money:** `_cents` columns are integer cents; `_usd` columns are dollars. Ratios are fractions (0.095 = 9.5%).
- **Tracked vs all play:** `sessions`, `players`, `trips` and `player_period` cover carded play only. `machine_day` covers all play, with carded totals in separate `carded_*` columns. A carded guest may also play uncarded.
- **Visits:** `trips` means observed property visits, not complete Las Vegas trips. Some visits and players have F&B or loyalty activity but no carded gaming.
- **Counters:** `zone_traffic_hourly.entries_count` counts sensor crossings, not unique people. A missing count is not zero (`counter_status`).
- **Off-floor rows:** `prepared_daily_view` and `machine_day` have one row for every machine on every date. On 1,018 rows the machine was not yet installed or already retired, so `location_id`, `availability_ratio` and similar columns are null. Exclude these rows; they are not zero performance.
- **Zeros are real:** zero play is valid. So are negative daily house win and observed payout above 100%. Compute ratios from sums.
- **Joins:** join `machine_day` to `placements` on the interval `[effective_from_utc, effective_to_utc)`. Aggregate guest tables before joining them to machine-day; never sum after joining two fact tables.

### Money definitions

| Metric | Definition |
| --- | --- |
| Coin-in | Sum of paid wagers, including replayed winnings |
| Total game payout | Sum returned from game outcomes, with jackpot/handpay counted once |
| Player gaming net | Payout − coin-in; label `tracked` when coverage is partial |
| House gaming win | Coin-in − payout; exactly the opposite sign |
| Theo / modeled expected loss | Sum of `bet × (1 − configured_RTP)`; an exposure-based benchmark, not a guaranteed personal loss |
| Luck residual | Player tables: player gaming net + theo. Machine tables: house win − theo (opposite sign). |
| Observed hold | Sum house gaming win / sum coin-in; undefined when denominator is zero |
| Average bet | Sum coin-in / sum paid spins |
| Hit rate | Payout-positive spins / paid spins; a positive payout can still be less than the wager |
| Tracked contribution | Tracked gaming win + linked F&B cash receipts − linked F&B cost of goods − other redeemed benefit costs |
| Comp reinvestment | Redeemed comp economic cost / theo, with zero-denominator handling and stated time period |

Example: a guest funds play with $100, wagers $500 through replay, receives $460 in game payouts, and cashes out $60. Gaming net is **−$40**, not +$460. At 92% RTP, theo is $40.

## Known limitations

- Synthetic data is a curated challenge world. It is not an estimate of any real casino's performance.
- Uncarded play is invisible at the person level. Concentration, ahead rates and comp ratios are about tracked guests only.
- Supplied costs are partial (no rent, taxes, depreciation or full staffing). Use "contribution after supplied costs."
- Visitor-profile and tourism figures describe all Las Vegas visitors, not this casino's guests, and were published after 2025.
- Action costs are fictional inputs. No action has a guaranteed uplift.

## Verify your download

From the repository folder, with Python and DuckDB installed:

```sh
python -m pip install duckdb
python scripts/verify_data.py
python scripts/verify_semantics.py
```

These check every file against the manifest, compare CSV and Parquet rows, and verify accounting and temporal invariants. They may take a minute on a laptop. Organizers must also run `python scripts/check_release.py` and review the evidence described in [READINESS.md](READINESS.md) before publication.
