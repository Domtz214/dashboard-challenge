# Dashboard Royale

## Luck, Location, or a Leak?

> Management is about to replace the ten machines that earned the least. Your dashboard could stop an expensive mistake—or show that management is right.
>
> Investigate six months at a fictional 300-machine casino. Explain what changed in demand, payouts, availability, and contribution. Show what tracked players wagered, received back, and actually won or lost. Recommend up to three actions within a $100,000 operations budget for the next 30 days, with evidence, uncertainty, and a way to measure success. Include one useful basic ML or time-series method. You may recommend an experiment, an inspection, or preserving the budget.

Fictional casino; synthetic data calibrated to public aggregates.

> **Draft release:** the data is `0.9.0-draft`. See the [release readiness review](reference/READINESS.md) for outstanding organizer tasks before sharing publicly.

**New here? Start with the [participant guide](GUIDE.md).** It covers the challenge, setup, the datasets, common mistakes and how to submit.

🎰 **[View the example dashboard](https://tamu-datathon-org.github.io/dashboard-royale/example-dashboard.html)** (layout only; all values are placeholders)

| | |
| --- | --- |
| 📘 [Participant guide](GUIDE.md) | The challenge, setup, datasets, common issues, submission |
| 📂 [`data/`](data/) | All tables, as `.parquet` and `.csv.gz` |
| 📑 [Dataset reference](reference/DATASET.md) | Layout, row counts, conventions, money definitions |
| 📖 [Data dictionary](reference/DATA_DICTIONARY.md) | Every table and column |
| 🔗 [Sources](reference/SOURCES.md) | Where the real-world files come from |

Original documentation, scripts and synthetic data use the [MIT license](LICENSE).
Third-party source tables are excluded; see [publisher terms](reference/SOURCE_TERMS.md).

Before publishing, run `python scripts/verify_data.py` and
`python scripts/check_release.py` (requires Python 3.11+ and DuckDB).
The release check currently reports missing calibration and publisher evidence.
