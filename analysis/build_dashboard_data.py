"""Build every number the Dashboard Royale prototype shows.

Run from the repository root:
    python -m pip install duckdb pandas pyarrow numpy
    python analysis/build_dashboard_data.py

Writes dashboard/data.js (window.DATA = {...}) and prints the headline findings.
All money is US dollars. Ratios are computed as ratio of sums, never mean of ratios.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import duckdb
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data"
OUT = ROOT / "dashboard" / "data.js"

con = duckdb.connect()


def t(path: str) -> str:
    return f"'{(D / path).as_posix()}.parquet'"


def rows(sql: str) -> list[dict]:
    df = con.sql(sql).df()
    out = []
    for rec in df.to_dict(orient="records"):
        clean = {}
        for k, v in rec.items():
            if hasattr(v, "isoformat"):
                v = v.isoformat()[:10]
            elif isinstance(v, float) and math.isnan(v):
                v = None
            elif hasattr(v, "item"):
                v = v.item()
            if isinstance(v, float):
                v = round(v, 4)
            clean[k] = v
        out.append(clean)
    return out


# Views ---------------------------------------------------------------------
con.execute(f"create view pdv as select * from {t('1_prepared_views/prepared_daily_view')} where location_id is not null")
con.execute(f"create view pd as select * from {t('1_prepared_views/property_day')}")
con.execute(f"create view md as select * from {t('2_machine_decision/machine_day')} where location_id is not null")
con.execute(f"create view gm as select * from {t('2_machine_decision/game_math')}")
con.execute(f"create view ev as select * from {t('4_context/events')}")

# 1. Property day + forecast model -----------------------------------------------
# Big-weekend rule is defined from the event *type*, which was announced months
# ahead (events.announced_date), so it is known on the forecast date.
BIG_TYPES = ("sports_viewing", "festival", "property_promotion")
con.execute(f"""
create table day as
select p.gaming_date, p.local_weekday wd, p.events_active,
  exists (select 1 from ev where p.gaming_date between ev.start_date and ev.end_date
          and ev.event_type in {BIG_TYPES} and ev.announced_date < p.gaming_date) big_event,
  p.coin_in_usd::double ci, p.payout_usd::double payout, p.house_win_usd::double hw,
  p.theo_usd::double theo, p.available_machine_hours avh, p.occupied_machine_hours occh,
  p.pos_cash_usd::double fnb, p.comp_cost_usd::double comp, p.faults_opened faults,
  p.contribution_after_supplied_costs_usd::double contrib, p.active_machines machines,
  p.gaming_date < date '2025-05-01' train
from pd p order by 1
""")
const_mean = con.sql("select avg(ci) from day where train").fetchall()[0][0]
wd_mean = dict(con.sql("select wd, avg(ci) from day where train group by 1").fetchall())
wd_quiet = dict(con.sql("select wd, avg(ci) from day where train and not big_event group by 1").fetchall())
lift = con.sql(
    "select avg(ci / f - 1) from day join (select wd, avg(ci) f from day where train and not big_event group by 1) b using(wd) where train and big_event"
).fetchall()[0][0]

day = rows("select * from day")
for r in day:
    r["f_const"] = round(const_mean)
    r["f_wd"] = round(wd_mean[r["wd"]])
    r["f_wd_event"] = round(wd_quiet[r["wd"]] * (1 + (lift if r["big_event"] else 0)))
test = [r for r in day if not r["train"]]


def mae(key: str) -> float:
    return sum(abs(r["ci"] - r[key]) for r in test) / len(test)


forecast = {
    "train": "2025-01-01 to 2025-04-30",
    "test": "2025-05-01 to 2025-06-30",
    "n_test": len(test),
    "mae_const": round(mae("f_const")),
    "mae_wd": round(mae("f_wd")),
    "mae_wd_event": round(mae("f_wd_event")),
    "event_lift": round(lift, 4),
    "mean_test": round(sum(r["ci"] for r in test) / len(test)),
    "big_types": list(BIG_TYPES),
}

# Event lift vs same-weekday quiet days (all six months, descriptive) -----------
events = rows("""
with base as (select local_weekday, avg(theo_usd) bt, stddev(theo_usd) sdt from pd where events_active is null group by 1)
select e.event_id, e.name, e.event_type, e.start_date, e.end_date, count(*) n_days,
  sum(p.theo_usd - b.bt) extra_theo, avg((p.theo_usd - b.bt)/b.bt) lift, avg((p.theo_usd-b.bt)/b.sdt) z
from ev e join pd p on p.gaming_date between e.start_date and e.end_date
join base b using(local_weekday) group by all order by lift desc
""")

# 2. Machine × month (filterable on the dashboard) -------------------------------
# var_usd2 = sum(bet^2) × payout-multiplier variance, the variance of house win
# implied by the game's own math. z = (house win − theo) / sqrt(var) is the luck test.
mm = rows("""
select d.machine_id id, strftime(d.gaming_date, '%Y-%m') as "month", p.zone_id as "zone", p.bank_id bank, d.location_id loc,
  count(*) n_days, sum(d.available_seconds)/3600.0 avh, sum(d.occupied_seconds)/3600.0 occh,
  sum(d.coin_in_cents)/100.0 ci, sum(d.house_win_cents)/100.0 hw, sum(d.theo_cents)::double/100.0 theo,
  sum(d.sum_bet_squared)*any_value(g.payout_multiplier_variance)::double/10000.0 var_usd2,
  sum(d.paid_spins) spins, sum(d.payout_positive_spins) hits,
  sum(p.faults_opened) faults, sum(p.contribution_after_supplied_costs_usd)::double contrib,
  sum(p.repair_cost_usd + p.lease_cost_usd + p.service_cost_usd + p.power_cost_usd)::double costs
from md d join gm g using(config_id)
join pdv p on p.machine_id = d.machine_id and p.gaming_date = d.gaming_date
group by all order by 1, 2
""")

machines = rows(f"""
select m.machine_id id, m.manufacturer mfr, m.theme, m.install_date, m.retire_date, m.lease_class,
  c.config_id cfg, g.configured_rtp::double rtp, g.hit_probability::double hit_p, g.volatility_class vol
from {t('2_machine_decision/machines')} m
join (select machine_id, any_value(config_id) config_id from md group by 1) c using(machine_id)
join gm g on g.config_id = c.config_id order by 1
""")

zones = rows(f"""
select zone_id id, zone_id name, avg(x_m) x, avg(y_m) y from {t('2_machine_decision/floor_locations')}
where node_type = 'slot' group by 1, 2 order by 1
""")
zone_names = {r["id"]: r["name"] for r in rows("select distinct zone_id id, zone_name name from pdv")}
for z in zones:
    z["name"] = zone_names.get(z["id"], z["name"])
banks = rows(f"""
select bank_id id, zone_id as "zone", avg(x_m) x, avg(y_m) y, count(*) slots
from {t('2_machine_decision/floor_locations')} where node_type='slot' group by 1, 2 order by 1
""")
walkways = rows(f"select * exclude (closed_from_utc, closed_to_utc), closed_from_utc::date closed_from, closed_to_utc::date closed_to from {t('2_machine_decision/floor_walkways')}")

# Whole-period luck / payout test per machine (also recomputed client-side)
payout = rows("""
select d.machine_id id, sum(house_win_cents)/100.0 hw, sum(theo_cents)::double/100.0 theo,
  (sum(house_win_cents) - sum(theo_cents)::double) / sqrt(sum(sum_bet_squared) * any_value(g.payout_multiplier_variance)::double) z,
  sum(payout_positive_spins)*1.0/sum(paid_spins) hit, any_value(g.hit_probability)::double hit_p,
  (sum(payout_positive_spins)*1.0/sum(paid_spins) - any_value(g.hit_probability)::double)
   / sqrt(any_value(g.hit_probability)::double*(1-any_value(g.hit_probability)::double)/sum(paid_spins)) z_hit
from md d join gm g using(config_id) group by 1 order by z
""")

# 3. Location: same game across zones, walkway closure, the one move --------------
same_game = rows("""
select config_id cfg, zone_id as "zone", count(distinct machine_id) machines,
  sum(theo_usd)/sum(available_hours) theo_avh, sum(occupied_hours)/sum(available_hours) occ
from pdv group by all order by 1, 2
""")
closure = rows("""
select case when gaming_date < date '2025-03-04' then 'Before (Jan 1 – Mar 3)'
            when gaming_date <= date '2025-04-06' then 'Walkway closed (Mar 4 – Apr 6)'
            else 'After (Apr 7 – Jun 30)' end as "period",
  min(gaming_date) as "start",
  sum(theo_usd) filter (where zone_id='Z-B40') / sum(available_hours) filter (where zone_id='Z-B40') b40,
  sum(theo_usd) filter (where zone_id<>'Z-B40') / sum(available_hours) filter (where zone_id<>'Z-B40') rest,
  sum(theo_usd) / count(distinct gaming_date) floor_theo_day
from pdv group by 1 order by 2
""")
moves = rows("""
select machine_id id, zone_id as "zone", location_id loc, min(gaming_date) as "start", max(gaming_date) as "stop", count(*) n_days,
  sum(theo_usd)/sum(available_hours) theo_avh, sum(occupied_hours)/sum(available_hours) occ
from pdv where machine_id in (select machine_id from pdv group by 1 having count(distinct location_id) > 1)
group by all order by 1, 4
""")

# 4. Floor-remix model: theo per available hour = exp(a + zone + game) ----------
# Fit on Jan–Apr machine×zone totals, validate on May–Jun against a game-only baseline.
def fit_remix(train_sql: str):
    data = con.sql(train_sql).df()
    zs = sorted(data.zone.unique())
    cs = sorted(data.cfg.unique())
    X = np.zeros((len(data), 1 + len(zs) - 1 + len(cs) - 1))
    X[:, 0] = 1
    for i, (z, c) in enumerate(zip(data.zone, data.cfg)):
        if zs.index(z) > 0:
            X[i, zs.index(z)] = 1
        if cs.index(c) > 0:
            X[i, len(zs) - 1 + cs.index(c)] = 1
    w = data.avh.values
    y = np.log(np.maximum(data.theo_avh.values, 0.01))
    sw = np.sqrt(w)
    beta, *_ = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)
    zf = {z: (0.0 if i == 0 else beta[i]) for i, z in enumerate(zs)}
    cf = {c: (0.0 if i == 0 else beta[len(zs) - 1 + i]) for i, c in enumerate(cs)}
    return beta[0], zf, cf


MZ_SQL = """
select machine_id, zone_id as "zone", config_id cfg, sum(available_hours) avh, sum(theo_usd)::double/sum(available_hours) theo_avh
from pdv where {w} group by all having sum(available_hours) > 200
"""
a0, zf, cf = fit_remix(MZ_SQL.format(w="gaming_date < date '2025-05-01'"))
hold = con.sql(MZ_SQL.format(w="gaming_date >= date '2025-05-01'")).df()
train_cfg = con.sql(
    "select config_id cfg, sum(theo_usd)::double/sum(available_hours) v from pdv where gaming_date < date '2025-05-01' group by 1"
).df().set_index("cfg").v.to_dict()
pred_model = np.exp([a0 + zf[z] + cf[c] for z, c in zip(hold.zone, hold.cfg)])
pred_base = np.array([train_cfg[c] for c in hold.cfg])
wts = hold.avh.values
remix_validation = {
    "n_machines": int(len(hold)),
    "wmae_game_only": round(float(np.average(np.abs(hold.theo_avh - pred_base), weights=wts)), 3),
    "wmae_zone_game": round(float(np.average(np.abs(hold.theo_avh - pred_model), weights=wts)), 3),
    "mean_actual": round(float(np.average(hold.theo_avh, weights=wts)), 3),
}
zone_factor = {z: round(math.exp(v - zf["Z-B40"]), 3) for z, v in zf.items()}  # relative to Back Forty

# Refit on all six months for July planning
a0, zf, cf = fit_remix(MZ_SQL.format(w="true"))
cur = con.sql("""
select p.machine_id id, p.zone_id as "zone", p.bank_id bank, p.location_id loc, p.config_id cfg, p.manufacturer mfr
from pdv p where gaming_date = date '2025-06-30'
""").df()
cur = cur[cur.id != "M-1158"]  # under inspection; do not move


def pred(z, c):
    return math.exp(a0 + zf[z] + cf[c])


cands = []
low = cur[cur.zone == "Z-B40"]
high = cur[cur.zone.isin(["Z-ENT", "Z-PIT"])]
for _, a in low.iterrows():
    for _, b in high.iterrows():
        gain = pred(b.zone, a.cfg) + pred(a.zone, b.cfg) - pred(a.zone, a.cfg) - pred(b.zone, b.cfg)
        if gain > 0:
            cands.append((gain, a, b))
cands.sort(key=lambda x: -x[0])
used: set[str] = set()
swaps = []
for gain, a, b in cands:
    if a.id in used or b.id in used:
        continue
    used |= {a.id, b.id}
    days = 30 - 2  # 2-day lead time for single-machine moves
    swaps.append({
        "a": a.id, "a_zone": a.zone, "a_loc": a["loc"], "a_cfg": a.cfg,
        "b": b.id, "b_zone": b.zone, "b_loc": b["loc"], "b_cfg": b.cfg,
        "gain_per_hour": round(gain, 2), "gain_july": round(gain * 24 * days * 0.996),
        "cost": 2 * 1800,
    })
    if len(swaps) == 6:
        break
# Upper bound: re-sort the whole floor (assignment by rank) — needs ~all machines moved
loc_f = sorted([zf[z] for z in cur.zone], reverse=True)
cfg_f = sorted([cf[c] for c in cur.cfg], reverse=True)
best = sum(math.exp(a0 + l + c) for l, c in zip(loc_f, cfg_f))
now = sum(pred(z, c) for z, c in zip(cur.zone, cur.cfg))
remix_upper = {"now_theo_per_hour": round(now), "sorted_theo_per_hour": round(best), "uplift": round(best / now - 1, 4)}

# 5. Downtime and technicians -------------------------------------------------------
con.execute(f"""
create view rep as select o.*, m.manufacturer mfr,
  date_diff('minute', recorded_at_utc, work_started_at_utc) wait_min,
  date_diff('minute', opened_at_utc, available_at_utc) down_min,
  extract(hour from opened_at_local) h
from {t('2_machine_decision/operations')} o join {t('2_machine_decision/machines')} m using(machine_id)
where event_type = 'fault_repair'
""")
downtime_mfr = rows("""
select manufacturer mfr, count(distinct machine_id) machines, count(*) machine_days, sum(faults_opened) faults,
  sum(faults_opened)*1.0/count(*) faults_per_mday, avg(availability_ratio) avail,
  sum(repair_cost_usd)::double repair_cost, sum(scheduled) sched_h, sum(available_hours) avh
from (select *, 24.0 scheduled from pdv) group by 1 order by faults_per_mday desc
""")
shift_wait = rows("""
select case when h >= 6 and h < 14 then 'Day 06–14' when h >= 14 and h < 22 then 'Swing 14–22' else 'Grave 22–06' end as "shift",
  strftime(opened_at_local, '%Y-%m') as "month", count(*) n, avg(wait_min) wait, sum(down_min)/60.0 down_h
from rep group by all order by 1, 2
""")
tech = rows(f"""
select shift, strftime(gaming_date,'%Y-%m') as "month", avg(planned_headcount) planned, avg(actual_headcount) actual
from {t('5_optional/shift_roster')} where role = 'slot_tech' group by all order by 1, 2
""")

# 6. Players (carded only) ------------------------------------------------------------
players = rows(f"""
select period_month as "month", opening_tier tier, coalesce(age_band,'Unknown') age, home_region region,
  count(*) player_months, count(*) filter (where tracked_coin_in_usd > 0) gaming_pm,
  count(*) filter (where tracked_net_usd > 0) ahead_pm,
  sum(tracked_coin_in_usd)::double ci, sum(tracked_net_usd)::double net, sum(theo_usd)::double theo,
  sum(comp_cost_usd)::double comp, sum(linked_pos_cash_usd)::double fnb,
  sum(tracked_contribution_usd)::double contrib, sum(observed_visits) visits
from {t('1_prepared_views/player_period')} group by all
""")
con.execute(f"""create table pl as select player_id, sum(tracked_coin_in_usd) ci, sum(tracked_net_usd) net
 from {t('1_prepared_views/player_period')} group by 1 having sum(tracked_coin_in_usd) > 0""")
conc = con.sql("""
with r as (select net, row_number() over (order by net) rn, count(*) over () n from pl)
select count(*) n, avg(case when net > 0 then 1.0 else 0 end) share_ahead, median(net) median_net,
  sum(net) filter (where rn <= n*0.01) / sum(net) filter (where net < 0) top1,
  sum(net) filter (where rn <= n*0.10) / sum(net) filter (where net < 0) top10
from r""").df().iloc[0].to_dict()
player_summary = {k: (round(float(v), 4)) for k, v in conc.items()}
hist = rows("""
select case when net <= -5000 then '≤ −$5k' when net <= -1000 then '−$5k to −$1k' when net <= -250 then '−$1k to −$250'
  when net < 0 then '−$250 to $0' when net < 250 then '$0 to $250' when net < 1000 then '$250 to $1k' else '≥ $1k' end bucket,
  min(net) lo, count(*) players
from pl group by 1 order by lo
""")

# 7. M-1158 detail ----------------------------------------------------------------------
m1158 = rows("""
select strftime(gaming_date,'%Y-%m') as "month", sum(coin_in_cents)/100.0 ci, sum(house_win_cents)*1.0/sum(coin_in_cents) hold,
  sum(theo_cents)::double/sum(coin_in_cents) theo_hold, sum(payout_positive_spins)*1.0/sum(paid_spins) hit
from md where machine_id = 'M-1158' group by 1 order by 1
""")

actions = rows(f"select * from {t('2_machine_decision/action_catalog')}")

DATA = {
    "generated": "from data/ v0.9.0-draft by analysis/build_dashboard_data.py",
    "day": day, "forecast": forecast, "events": events,
    "mm": mm, "machines": machines, "payout": payout,
    "zones": zones, "banks": banks, "walkways": walkways,
    "same_game": same_game, "closure": closure, "moves": moves,
    "remix": {"validation": remix_validation, "zone_factor": zone_factor, "swaps": swaps, "upper": remix_upper},
    "downtime_mfr": downtime_mfr, "shift_wait": shift_wait, "tech": tech,
    "players": players, "player_summary": player_summary, "player_hist": hist,
    "m1158": m1158, "actions": actions,
}
OUT.parent.mkdir(exist_ok=True)
OUT.write_text("window.DATA = " + json.dumps(DATA, separators=(",", ":"), default=str) + ";\n")
print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size/1e6:.2f} MB)")
print("forecast", forecast)
print("remix validation", remix_validation, "zone factors", zone_factor)
print("remix upper", remix_upper)
for s in swaps:
    print("swap", s)
print("players", player_summary)
print("closure", closure)
print("worst z", payout[:3])
