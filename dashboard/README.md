# Dashboard Royale prototype

Open `dashboard/index.html` in any browser (double-click works; no server or install needed).
It reads `dashboard/data.js`, which is generated from `data/` by:

```sh
python -m pip install duckdb pandas pyarrow numpy
python analysis/build_dashboard_data.py
```

Sections: verdict → bottom 10 (naive vs fair) → location → payout check → downtime →
demand & forecast model → players → floor remix → priced actions → method & claims.
Filters at the top (period, zone, bank, guest tier/age/region) scope everything below them.
