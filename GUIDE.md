# Participant Guide

**Dashboard Royale** A dashboard challenge set in a fictional Las Vegas casino.

This page has everything you need to get started: what the challenge is, how to load the data, what each dataset holds, the mistakes most teams make, and how to submit.

| Step | Section                                                                       | Time   |
| :--: | ----------------------------------------------------------------------------- | ------ |
|  1   | [The challenge in 2 minutes](#1-the-challenge-in-2-minutes)                   | 2 min  |
|  2   | [Set up](#2-set-up)                                                           | 10 min |
|  3   | [The datasets](#3-the-datasets)                                               | 10 min |
|  4   | [Five ideas to know before you start](#4-five-ideas-to-know-before-you-start) | 5 min  |
|  5   | [Common issues](#5-common-issues)                                             | 5 min  |
|  6   | [The $100,000 budget](#6-the-100000-budget)                                   | 3 min  |
|  7   | [How you're judged](#7-how-youre-judged)                                      | 3 min  |
|  8   | [What to submit on Devpost](#8-what-to-submit-on-devpost)                     | 2 min  |
|  9   | [Rules and getting help](#9-rules-and-getting-help)                           | 1 min  |

> [!NOTE]
> **The casino is fictional and all of its data is synthetic.** The world around it is real: Las Vegas tourism, weather and Missouri casino benchmarks for January–June 2025. Data release `0.9.0-draft`: tables and columns are stable, but values may change before `1.0.0`.

---

## 1. The challenge in 2 minutes

You've just joined **The Gilded Ace**, a 300-machine casino, as its floor analytics lead.

**The situation.** The general manager plans to replace the **10 machines that earned the least** between January 1 and June 30, 2025.

**The catch.** A machine can earn little for many reasons. It might be unlucky, in a quiet spot, often broken, or paying out differently than expected. Replacing it only helps if the machine itself is the problem.

**Your job.** Build a dashboard that answers:

1. Which machines are _truly_ underperforming once you account for exposure, availability and luck?
2. What changed in demand across the floor over the six months, and why?
3. How much play was lost to downtime, and when?
4. What did tracked players wager, get back and net, and how concentrated are those results?
5. What did the loyalty (comp) program cost, and did anything about it change?
6. Which actions would you fund with **$100,000**, and how would you know they worked?

These six questions are the minimum. Well-supported findings beyond them earn credit too.

> [!TIP]
> The investigation starts with a question: **luck, location, or a leak?** Strong teams test all three explanations before picking one.

---

## 2. Set up

### Get the data

```sh
git clone --depth 1 https://github.com/tamu-datathon-org/dashboard-royale.git
cd dashboard-royale
```

`--depth 1` skips old versions of the files. Allow at least 1 GB of free space for the download, extracted CSVs and your work. You can also click **Code → Download ZIP** on GitHub.

Every table comes in two formats with identical rows:

| Format     | Best for                                                                              |
| ---------- | ------------------------------------------------------------------------------------- |
| `.parquet` | Python, R, DuckDB, Power BI, Tableau. Typed, small and fast. **Recommended for code** |
| `.csv.gz`  | Anything else. Unzip it first to get a plain `.csv`                                   |

### Load it in your tool

<details open>
<summary><b>Python (pandas)</b></summary>

```sh
# Run these in a terminal from the repository folder.
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell (instead of the line above):
# .venv\Scripts\Activate.ps1
python -m pip install pandas pyarrow
```

Use Python 3.11 or newer. If `python` is unavailable on macOS/Linux, use `python3`. Save the following as `explore.py` in the repository folder and run `python explore.py`, or run it in a notebook opened in that folder.

```python
import pandas as pd

daily = pd.read_parquet("data/1_prepared_views/prepared_daily_view.parquet")
print(daily.shape)   # (56110, 44): one row per machine per day
print(daily.head())
```

</details>

<details>
<summary><b>SQL (DuckDB): query files directly, no import step</b></summary>

```sh
python -m pip install duckdb
```

```python
import duckdb

duckdb.sql("""
    SELECT machine_id,
           SUM(house_win_usd)                    AS house_win,
           SUM(theo_usd)                         AS expected_win,
           SUM(house_win_usd) / NULLIF(SUM(coin_in_usd), 0) AS observed_hold,
           SUM(available_hours) /
               (SUM(c.scheduled_seconds) / 3600.0) AS availability
    FROM 'data/1_prepared_views/prepared_daily_view.parquet' AS d
    JOIN 'data/2_machine_decision/calendar_day.parquet' AS c
      USING (gaming_date)
    WHERE d.active
    GROUP BY machine_id
    ORDER BY house_win
    LIMIT 10
""").show()
```

Run the Python snippet in a script or notebook from the repository folder. This is the manager's "bottom 10" list. Your job is to find out whether it's right.

</details>

<details>
<summary><b>R</b></summary>

```r
install.packages("arrow")
library(arrow)
daily <- read_parquet("data/1_prepared_views/prepared_daily_view.parquet")
```

</details>

<details>
<summary><b>Tableau, Power BI, Excel, Looker Studio</b></summary>

1. Unzip the `.csv.gz` file you need: double-click it on macOS, or use 7-Zip on Windows.
2. Load the resulting `.csv`. Parquet support depends on your tool and version; use CSV if you cannot open Parquet.
3. Start with the three files in `data/1_prepared_views/`, which are already joined and small.

**Size limits:**

- Excel stops at 1,048,576 rows, so `machine_hour` (1.3M rows) won't fit. Aggregate it first or use another tool.
- Looker Studio file uploads are capped at 100 MB.
- Tableau Public dashboards are public by default.

</details>

### Your first dashboard in 3 files

You don't need any joins to start:

| File                                        | One row =     | Use it for                                                        |
| ------------------------------------------- | ------------- | ----------------------------------------------------------------- |
| `data/1_prepared_views/prepared_daily_view` | machine × day | Machine performance, availability, costs, context, all in dollars |
| `data/1_prepared_views/property_day`        | day           | Whole-floor trends                                                |
| `data/2_machine_decision/action_catalog`    | action        | What the $100,000 can buy                                         |

---

## 3. The datasets

The data is organized in five numbered folders. **Lower numbers are the more important ones.**

```
data/
├── 1_prepared_views/    ⭐ start here: joined, in dollars
├── 2_machine_decision/  the floor, machines, meters, repairs, costs, actions
├── 3_guests/            loyalty-card players only
├── 4_context/           traffic counters, events
│   └── real_sources/    🌎 real public data (tourism, weather, benchmarks)
└── 5_optional/          extra detail, for deeper dives
```

### 1 · Prepared views ⭐

| Table                 | One row =      | What's in it                                                                        |    Rows |
| --------------------- | -------------- | ----------------------------------------------------------------------------------- | ------: |
| `prepared_daily_view` | machine × day  | Meters, location, game settings, availability, costs, events, 7- and 28-day history |  56,110 |
| `property_day`        | day            | Floor totals: wagers, payouts, food and drink, comps, faults, traffic, costs        |     181 |
| `player_period`       | player × month | Each card holder's wagers, results, expected loss, points, comps                    | 148,893 |

### 2 · Machine decision

| Table             | One row =           | What's in it                                               |   Rows |
| ----------------- | ------------------- | ---------------------------------------------------------- | -----: |
| `machines`        | machine             | Manufacturer, game title, install and retire dates         |    310 |
| `game_math`       | game setting        | Published payout rate (RTP), volatility, bet sizes         |     10 |
| `placements`      | machine × time span | Which slot a machine was in, and when. **Machines move**   |    314 |
| `floor_locations` | zone / bank / slot  | Floor layout with coordinates                              |    378 |
| `floor_walkways`  | walkway             | Walkways connecting zones                                  |     10 |
| `machine_day`     | machine × day       | Raw meters in cents, covering **all** play (carded or not) | 56,110 |
| `operations`      | ticket              | Faults, repairs, maintenance, moves, installs              |  1,226 |
| `cost_rules`      | cost rule           | Leases, service, power, repairs                            |      9 |
| `action_catalog`  | action              | The 13 things you can spend the budget on                  |     13 |
| `calendar_day`    | day                 | Gaming days, weekdays, holidays, length in seconds         |    181 |

### 3 · Guests (loyalty-card holders only)

| Table              | One row =              | What's in it                                       |    Rows |
| ------------------ | ---------------------- | -------------------------------------------------- | ------: |
| `players`          | card holder            | Home region, age band, starting tier               | 113,890 |
| `sessions`         | play session segment   | One stretch of carded play on one machine          | 776,297 |
| `trips`            | recorded visit         | One card's activity during one visit to the casino | 351,729 |
| `loyalty_ledger`   | points event           | Points earned and redeemed                         | 782,773 |
| `fnb_transactions` | food and drink receipt | Every sale, carded or not                          | 227,833 |

### 4 · Context

| Table                 | One row =     | What's in it                                               |   Rows |
| --------------------- | ------------- | ---------------------------------------------------------- | -----: |
| `zone_traffic_hourly` | sensor × hour | Door and zone entry counts (imperfect, see below)          | 30,401 |
| `events`              | event         | Conventions, sports weekends, festivals, casino promotions |      8 |

**🌎 Real sources** (`4_context/real_sources/`), unmodified public data:

| Table                                   | Source                     | What's in it                                                               |
| --------------------------------------- | -------------------------- | -------------------------------------------------------------------------- |
| `city_visitation_monthly`               | LVCVA                      | Las Vegas visitors, conventions, hotel occupancy, airport traffic by month |
| `visitor_profile_summary` / `_segments` | LVCVA survey               | How Las Vegas visitors gamble, spend and stay                              |
| `weather_daily`                         | NOAA                       | Daily temperature and rain at the Las Vegas airport                        |
| `benchmark_public` + monthly totals     | Missouri Gaming Commission | Real slot results from 13 Missouri casinos                                 |

### 5 · Optional

| Table                     | One row =        | What's in it                              |      Rows |
| ------------------------- | ---------------- | ----------------------------------------- | --------: |
| `machine_hour`            | machine × hour   | Hourly meters; add up to `machine_day`    | 1,321,908 |
| `shift_roster`            | staff assignment | Who worked which shift, by role           |    10,317 |
| `security_incidents`      | report           | Incidents that someone reported           |     3,865 |
| `visitor_profile_monthly` | month × metric   | The casino's own (fictional) guest survey |        42 |

**Which table answers which question?**

| Question                | Start with                            | Go deeper with                           |
| ----------------------- | ------------------------------------- | ---------------------------------------- |
| Q1: truly weak machines | `prepared_daily_view`                 | `machine_day`, `game_math`, `placements` |
| Q2: demand changes      | `property_day`, `zone_traffic_hourly` | `events`, `real_sources/`                |
| Q3: downtime            | `prepared_daily_view` (availability)  | `operations`, `shift_roster`             |
| Q4: player outcomes     | `player_period`                       | `sessions`, `trips`                      |
| Q5: comp program        | `player_period`, `property_day`       | `loyalty_ledger`, `fnb_transactions`     |
| Q6: actions             | `action_catalog`, `cost_rules`        | everything above                         |

For every column, see the [data dictionary](reference/DATA_DICTIONARY.md). For conventions and exact money definitions, see the [dataset reference](reference/DATASET.md).

---

## 4. Five ideas to know before you start

**1. Gaming day = 6 a.m. to 6 a.m.** Casinos close their books at 6 a.m. local time, so a session at 2 a.m. on Saturday belongs to Friday's gaming day. Daily tables have a `gaming_date` column. Event tables have timestamps (`_utc` and `_local`) instead, so convert them to a gaming date before grouping by day.

**2. Carded vs. all play.** Machine meters (`machine_day`) count **everyone**. Player tables (`sessions`, `players`, `trips`, `player_period`) only see guests who used a **loyalty card**. The two will never match, and that's expected.

**3. The money words.**

| Term              | Meaning                                        | Example |
| ----------------- | ---------------------------------------------- | ------- |
| **Coin-in**       | Total wagered, including winnings bet again    | $500    |
| **Payout**        | Total paid back by the game                    | $460    |
| **House win**     | Coin-in − payout                               | $40     |
| **Hold**          | House win ÷ coin-in                            | 8%      |
| **RTP**           | The game's long-run payout rate                | 92%     |
| **Theo**          | _Expected_ house win = coin-in × (1 − RTP)     | $40     |
| **Luck residual** | Actual result vs. expected; luck shows up here |         |

**4. Luck is real.** Slot results swing a lot, especially on high-volatility games. Compare **actual house win against theo** before calling a machine bad.

**5. Exposure matters.** A machine that was broken, newly installed or in a quiet spot had fewer chances to earn. Compare per available hour or per unit of play, not raw totals.

---

## 5. Common issues

| ❌ Mistake                                                              | ✅ Do this instead                                                                                                                                                            |
| ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Ranking machines by total house win                                     | Adjust for luck (theo), availability and how long the machine was on the floor                                                                                                |
| "Player totals don't match machine totals, the data is broken"          | Expected: player tables only include carded play. Use the `carded_*` columns in `machine_day` to compare                                                                      |
| Averaging daily ratios (mean of each day's hold)                        | Use **ratio of sums**: `SUM(house_win) / SUM(coin_in)`                                                                                                                        |
| Joining `sessions` to `fnb_transactions` row by row, then summing       | Money gets counted multiple times. **Aggregate each table first, then join**                                                                                                  |
| Counting days a machine wasn't on the floor as zero sales               | 1,018 rows in `prepared_daily_view` are days before a machine was installed or after it was retired (`location_id` is empty). Leave them out, or compare per day on the floor |
| Assuming a machine always sat in the same place                         | Machines move. Use `placements` (or `prepared_daily_view`) for location on a given date                                                                                       |
| Assuming every day has 24 hours                                         | March 8, 2025 has 23 hours (daylight saving). Use `scheduled_seconds` from `calendar_day`                                                                                     |
| Treating a missing traffic count as zero                                | Missing means the counter was offline. Check `counter_status`                                                                                                                 |
| Treating traffic counts as unique visitors                              | They count entries; one guest can be counted many times, and seated players aren't counted                                                                                    |
| Mixing up cents and dollars                                             | `_cents` columns are integer cents; `_usd` columns are dollars                                                                                                                |
| Subtracting `comp_cost_usd` _and_ `linked_pos_cogs_usd`                 | Comp cost is already included in cogs. Subtract it once                                                                                                                       |
| "Negative house win, that must be an error"                             | A machine can lose money on a day. That's real, and luck                                                                                                                      |
| Treating `trips` as whole Las Vegas trips                               | They are visits to _this casino_ only                                                                                                                                         |
| Applying LVCVA survey numbers to this casino's guests                   | They describe all Las Vegas visitors, not this property's customers                                                                                                           |
| Random train/test split for a model                                     | Split by **time**: train on earlier months, test on later ones                                                                                                                |
| Using information from the future in a model (e.g. next week's repairs) | Only use what was known on the prediction date. The `lag_*` columns use prior days; for a multi-day forecast, do not use holdout-day results to compute future inputs         |
| "This machine pays out too much, someone is cheating"                   | An unusual pattern is a reason to **inspect**, not proof of wrongdoing                                                                                                        |

> [!WARNING]
> **Large files:**
>
> - `machine_hour`, `sessions` and `loyalty_ledger` are each 750,000+ rows.
> - Use Parquet and DuckDB/pandas, or aggregate them before loading into a BI tool.

---

## 6. The $100,000 budget

You control a pretend **$100,000** for the **30 days from July 1, 2025**. Fund **up to 3 action types** from `action_catalog`, or keep the money. Each type may have multiple units up to its `quantity_limit`; list the quantity and targets. Keeping unspent money does not use an action slot.

**Why it matters:** each possible cause needs a different fix. Good spending shows that you found the real cause.

| If low earnings come from… | The money might go to…                            |
| -------------------------- | ------------------------------------------------- |
| Luck                       | Nothing. **Keeping the budget is a valid answer** |
| Location                   | Moving machines, or new signs for a zone          |
| Downtime                   | Another technician, or preventive maintenance     |
| Payout settings            | Inspecting machines                               |
| Comps or guests            | A comp policy test or change                      |

| Action                                   |             Cost | Limit                  |
| ---------------------------------------- | ---------------: | ---------------------- |
| Move one machine                         |           $1,800 | 24                     |
| Move a whole bank                        |           $9,500 | 3                      |
| Replace with a leased machine            | $2,500 + $55/day | 20                     |
| Replace with a purchased machine         |          $22,000 | 10                     |
| Add a technician to a shift (30 days)    |          $11,520 | 3                      |
| Preventive maintenance, one manufacturer |           $9,000 | 3                      |
| Inspect a machine and verify its payout  |           $1,200 | 15                     |
| New signs for a zone                     |           $7,500 | 2                      |
| Comp policy pilot with a control group   |           $4,000 | 1                      |
| Change the comp rate floor-wide          |           $1,500 | 1 (not with the pilot) |
| Promotion weekend                        |          $15,000 | 2                      |
| Bigger guest survey                      |           $3,500 | 1 month                |
| Keep the budget                          |               $0 | always                 |

Use the catalogue's `lead_days`, downtime and incompatibilities in your plan. Do not assign conflicting moves or replacements to the same machine, or combine the comp pilot with the floor-wide comp change. Count purchased machines' full cost against the budget.

For a lease ordered on July 1 with a 14-day lead, use 16 operating days in the July 1–30 horizon: one unit costs $2,500 + 16 × $55 = **$3,380**. In general, budget `quantity × (unit_cost_cents + recurring_cost_cents_per_day × max(0, 30 − lead_days)) / 100`. Fixed package costs (such as the technician package) are charged in full; estimate benefits only for the days remaining after the lead time. Include any additional comp costs you propose in your budget and state your assumptions.

The catalogue gives **prices and limits, not results**. You estimate the benefit from the data and say how confident you are.

For each action, state its **cost, expected effect, uncertainty, and how you'd measure it**.

---

## 7. How you're judged

Chart count, model complexity and the number of patterns found **don't** score points. Any analytical approach can earn full marks.

| Criterion                         | Weight | What earns top marks                                                                                                                     |
| --------------------------------- | -----: | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **Analytical validity**           |    30% | Correct money math; fair comparisons that account for exposure, availability and luck; uncertainty shown; a competing explanation tested |
| **Dashboard and communication**   |    25% | A clear path from question to decision that a manager can follow; accessible visuals; every claim traceable to data                      |
| **Modeling and validation**       |    20% | One sensible model that changes a decision, compared honestly with a simple baseline on a time-based holdout, with no leakage            |
| **Recommendations and tradeoffs** |    15% | Priced actions within budget, assumptions and sensitivity, a measurement plan                                                            |
| **Originality**                   |    10% | An unexpected, useful finding someone else could reproduce                                                                               |

**A beginner-friendly modeling route:** use January–April to choose a simple forecast of daily floor coin-in (for example, average coin-in by weekday). Compare it with a constant training-period daily mean on May–June. Report mean absolute error (MAE: average absolute prediction error, in dollars), show predictions against actuals, and explain how the result changes a staffing or promotion decision. Freeze both forecasts before testing; later-published tourism and survey data cannot be inputs to a forecast made in 2025. A simple time-series method satisfies the requirement; advanced ML is optional.

**Judges do these 4 things with every dashboard.** Make sure yours handles them:

1. Change the analysis period.
2. Drill into one bank or one guest group.
3. Find how the model was validated.
4. Trace one recommendation back to its evidence.

> [!TIP]
> Your model doesn't have to beat the baseline. Honest validation and a sensible decision from the result still earn credit.

---

## 8. What to submit on Devpost

- [ ] **A public interactive dashboard** that judges can open: a link or a file, any tool
- [ ] **Video walkthrough**, 2 minutes or less, showcasing your dashboard and explaining your priced actions
- [ ] **Write-up**, 400 words or less
- [ ] **One ML or time-series method** that informs a decision, compared with a simple baseline on a time-based holdout
- [ ] **All code** or transformation steps
- [ ] **Up to 3 priced action types** from `action_catalog`, each with cost, expected effect, uncertainty and measurement plan
- [ ] **AI-use disclosure**: what you used and for what (include in the appendix)
- [ ] **Claims & Evidence appendix**: for each claim, the table/query → result → alternative explanation → limitation

The 400-word limit applies to the main write-up; the Claims & Evidence appendix and AI disclosure are separate. Provide the appendix as an attached file or public link. Test your dashboard link in a private browser window; file submissions must include opening instructions and any required software.

Use DevPost for submissions and its event page for deadlines and upload details.

---

## 9. Rules and getting help

**Rules**

- The casino and its people are fictional. Don't present any finding as a fact about a real casino.
- Some patterns have more than one reasonable explanation. Show the alternative you tested.
- No accusations. Unusual payouts or incidents are leads to inspect, not proof of wrongdoing.
- Report player outcomes honestly. Don't design ideas that push heavy losers to gamble more; protective ideas are welcome.
- AI tools are allowed with disclosure.
- Outside data is allowed if it's public and cited.

**Questions?** Use **Help Queue**, TAMU Datathon's help-channel.

**Quick answers**

| Question                                         | Answer                                                                                                                           |
| ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| Is any casino data real?                         | No. Only the files in `4_context/real_sources/` are real                                                                         |
| Why 310 machines in a 300-machine casino?        | Some machines were retired or replaced during the six months. Between 300 and 308 are on the floor on any given day              |
| Why are timestamps in UTC?                       | So no hour is lost or doubled at daylight-saving changes. Tables with timestamps also give the main one in local time (`_local`) |
| Can carded net win be bigger than total net win? | Yes. Uncarded players can win as a group                                                                                         |
| Does a low-hold machine mean it's broken?        | Not necessarily. Check exposure, volatility and availability first                                                               |
| Does the action catalogue say what works?        | No. It only gives prices and limits                                                                                              |
