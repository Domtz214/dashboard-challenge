"""Repeat challenge accounting, key, date, rollup and lag checks (DuckDB)."""
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]


def main():
    con = duckdb.connect()
    for name, path in {
        "prepared": "1_prepared_views/prepared_daily_view",
        "player": "1_prepared_views/player_period",
        "property": "1_prepared_views/property_day",
        "machine": "2_machine_decision/machine_day",
        "calendar": "2_machine_decision/calendar_day",
    }.items():
        con.read_parquet(str(ROOT / "data" / (path + ".parquet"))).create_view(name)

    checks = {
        "unique machine-day keys": """SELECT count(*) = count(DISTINCT (machine_id, gaming_date))
            AND count(machine_id) = count(*) AND count(gaming_date) = count(*) FROM machine""",
        "date window": """SELECT min(gaming_date) = DATE '2025-01-01'
            AND max(gaming_date) = DATE '2025-06-30'
            AND count(DISTINCT gaming_date) = 181 FROM machine""",
        "off-floor rows": "SELECT count(*) = 1018 FROM prepared WHERE location_id IS NULL",
        "active floor range": "SELECT min(active_machines) = 300 AND max(active_machines) = 308 FROM property",
        "machine integer accounting": "SELECT count(*) = 0 FROM machine WHERE house_win_cents IS DISTINCT FROM coin_in_cents - payout_cents",
        "prepared accounting": """SELECT count(*) = 0 FROM prepared WHERE
            abs(house_win_usd - (coin_in_usd - payout_usd)) > 0.000001 OR
            abs(luck_residual_usd - (house_win_usd - theo_usd)) > 0.000001 OR
            abs(contribution_after_supplied_costs_usd - (house_win_usd - lease_cost_usd
                - service_cost_usd - power_cost_usd - repair_cost_usd)) > 0.000001""",
        "player accounting": """SELECT count(*) = 0 FROM player WHERE
            abs(tracked_net_usd - (tracked_payout_usd - tracked_coin_in_usd)) > 0.000001 OR
            abs(luck_residual_usd - (tracked_net_usd + theo_usd)) > 0.000001 OR
            abs(tracked_contribution_usd - (-tracked_net_usd + linked_pos_cash_usd
                - linked_pos_cogs_usd)) > 0.000001""",
        "property accounting": """SELECT count(*) = 0 FROM property WHERE
            abs(house_win_usd - (coin_in_usd - payout_usd)) > 0.000001 OR
            abs(contribution_after_supplied_costs_usd - (house_win_usd + pos_cash_usd
                - pos_cogs_usd - machine_supplied_costs_usd
                - tech_labor_cost_usd)) > 0.000001""",
        "daily rollups": """WITH daily AS (SELECT gaming_date, sum(coin_in_usd) coin,
            sum(payout_usd) payout, sum(available_hours) available_total FROM prepared GROUP BY 1)
            SELECT count(*) = 0 FROM daily FULL JOIN property USING (gaming_date)
            WHERE daily.gaming_date IS NULL OR property.gaming_date IS NULL OR
            abs(coin - coin_in_usd) > 0.000001 OR abs(payout - payout_usd) > 0.000001 OR
            abs(available_total - available_machine_hours) > 0.000001""",
        "prior-seven-day feature": """WITH lagged AS (SELECT *, avg(coin_in_usd) OVER
            (PARTITION BY machine_id ORDER BY gaming_date ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING)
            expected FROM prepared) SELECT count(*) = 0 FROM lagged WHERE
            (expected IS NULL) != (lag_coin_in_7d_mean_usd IS NULL) OR
            abs(expected - lag_coin_in_7d_mean_usd) > 0.000001""",
        "daylight saving": """SELECT count(*) = 1 AND min(scheduled_seconds) = 82800
            FROM calendar WHERE gaming_date = DATE '2025-03-08'""",
    }
    failures = []
    for name, sql in checks.items():
        passed = con.sql(sql).fetchall()[0][0] is True
        print(f"{'PASS' if passed else 'FAIL'}: {name}")
        if not passed:
            failures.append(name)
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
