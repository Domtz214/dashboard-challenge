# Real sources and provenance

Files in `data/4_context/real_sources/` are real public data. They are **unmodified** except for reshaping into rows: no values are edited, scaled or mixed with synthetic rows. Each row keeps its `source_url`, `source_sha256` and sheet/cell reference.

> **Redistribution status: blocked for LVCVA and Missouri; NOAA terms documented.** See the [publisher terms review](SOURCE_TERMS.md). LVCVA's published terms require written permission for broader copying; no permission is recorded here. Missouri redistribution terms remain unestablished. Do not publish these tables until cleared. Removing them instead requires a tested normalization recipe and updated manifest and documentation; the download instructions below are not that recipe.

| Original file | Publisher | Period | Revision / published | Retrieved | Used in | SHA-256 (first 12) | URL |
| --- | --- | --- | --- | --- | --- | --- | --- |
| lvcva_2025.xlsx | LVCVA | 2025 | 2026-08-20 | 2026-11-03 | city_visitation_monthly | `3485f53699e7` | [link](https://assets.simpleviewcms.com/simpleview/raw/upload/v1/clients/lasvegas/Year_to_Date_Summary_for_2025_revised_cd675d1a-2e15-4a20-aeeb-e6a6d871b10a.xlsx) |
| lvcva_visitor_profile_2025.pdf | LVCVA | 2025 | 2026-03-10 | 2026-11-04 | cross-check for visitor_profile_* | `7ae5a363cbf7` | [link](https://assets.simpleviewcms.com/simpleview/image/upload/v1/clients/lasvegas/2025_Las_Vegas_Visitor_Profile_Study_db57c923-1f87-4ab8-868d-d6fc0bf2f972.pdf) |
| lvcva_visitor_segments_2025.xlsx | LVCVA | 2025 | 2026-03-10 | 2026-11-04 | visitor_profile_summary, visitor_profile_segments | `e4dfc65c9152` | [link](https://assets.simpleviewcms.com/simpleview/raw/upload/v1/clients/lasvegas/2025_LasVegasVPS_Matrix_Snapshot_Excel_41461651-2aa7-464a-9b23-744c984c4e9b.xlsx) |
| missouri_2025_02.xlsx | Missouri Gaming Commission | 2025-02 |  | 2026-11-04 | benchmark_* (2025-02) | `3a7a58fc5eea` | [link](https://www.mgc.dps.mo.gov/Casino_Gaming/rb_financials/FY25_FinReport/03_Mar/detail0225.xlsx) |
| missouri_2025_03.xlsx | Missouri Gaming Commission | 2025-03 |  | 2026-11-04 | benchmark_* (2025-03) | `7ffd332af43b` | [link](https://www.mgc.dps.mo.gov/Casino_Gaming/rb_financials/FY25_FinReport/04_Apr/detail0325.xlsx) |
| missouri_2025_04.xlsx | Missouri Gaming Commission | 2025-04 |  | 2026-11-04 | benchmark_* (2025-04) | `5a504c611b1a` | [link](https://www.mgc.dps.mo.gov/Casino_Gaming/rb_financials/FY25_FinReport/05_May/detail0425.xlsx) |
| missouri_2025_05.xlsx | Missouri Gaming Commission | 2025-05 |  | 2026-11-04 | benchmark_* (2025-05) | `0e78c4741e87` | [link](https://www.mgc.dps.mo.gov/Casino_Gaming/rb_financials/FY25_FinReport/06_Jun/detail0525.xlsx) |
| missouri_2025_06.xlsx | Missouri Gaming Commission | 2025-06 |  | 2026-11-04 | benchmark_* (2025-06) | `e9b3797fbfd2` | [link](https://www.mgc.dps.mo.gov/Casino_Gaming/rb_financials/FY26_FinReport/07_Jul/detail0625.xlsx) |
| missouri_jan2025.xlsx | Missouri Gaming Commission | 2025-01 |  | 2026-11-03 | benchmark_* (Jan) | `b9a72f59ecd2` | [link](https://www.mgc.dps.mo.gov/Casino_Gaming/rb_financials/FY25_FinReport/02_Feb/detail0125.xlsx) |
| noaa_USW00023169_2025H1.csv | NOAA NCEI Access Data Service (GHCN-Daily daily-summaries) | 2025-01-01..2025-06-30 |  | 2026-11-04 | weather_daily | `bbc1693cd624` | [link](https://www.ncei.noaa.gov/access/services/data/v1?dataset=daily-summaries&stations=USW00023169&startDate=2025-01-01&endDate=2025-06-30&dataTypes=TMAX,TMIN,PRCP&units=metric&format=csv&includeAttributes=true) |

## Interpretation notes

- **Weather:** NOAA station USW00023169 (Harry Reid airport). Dates are calendar dates, not casino gaming dates (06:00–06:00). Trace precipitation and missing values are distinguished by the NOAA flags.
- **Tourism:** LVCVA revised workbook (August 20, 2026 revision). Divide monthly counts by days in month before comparing daily intensity. Airport passengers are en/deplaned movements, not unique visitors.
- **Visitor profile:** destination-wide survey of Las Vegas visitors, not customers of this casino. Each value is conditioned on the population in `denominator_note`. Segment columns overlap; do not add them up.
- **Missouri benchmark:** all 13 Missouri casinos, January–June 2025, by reported slot category. H1 weighted actual hold = 9.633%. `benchmark_property_monthly` and `benchmark_state_monthly` are published totals; do not add them to the category rows. Negative AGR and payout above 100% are real reported values.
- **As-of caution:** these are later revisions and retrospective publications. A model that claims to forecast as of a 2025 date may only use what was published by then.

## Original-file download references (not a normalization recipe)

NOAA: `https://www.ncei.noaa.gov/access/services/data/v1?dataset=daily-summaries&stations=USW00023169&startDate=2025-01-01&endDate=2025-06-30&dataTypes=TMAX,TMIN,PRCP&units=metric&format=csv&includeAttributes=true`

Other files: download the URLs above and compare SHA-256.
