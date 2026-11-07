# Data dictionary

Every table ships as `.parquet` (typed) and `.csv.gz` (same rows). Keys, units and grain are listed per table. Money: `_cents` columns are integer cents; `_usd` columns are dollars. Timestamps: `_utc` is UTC, `_local` is America/Los_Angeles. A **gaming date** runs 06:00 to 06:00 local; 2025-03-08 has 23 hours (DST).

## `data/1_prepared_views/`

Start here. Joined, dollar-denominated views; no temporal joins needed.

### player_period

Starter table: tracked results per player per month. Tracked only; uncarded play is invisible.

Rows: 148,893 · Key: `player_id, period_month`

| Column | Type | Meaning |
| --- | --- | --- |
| `player_id` | VARCHAR | Loyalty account (opaque) |
| `period_month` | VARCHAR | YYYY-MM by gaming date |
| `home_region` | VARCHAR | Coarse home region |
| `age_band` | VARCHAR | Coarse age band |
| `opening_tier` | VARCHAR | Tier at the start of the window |
| `tier_end` | VARCHAR | Tier after the last ledger event so far |
| `observed_visits` | BIGINT | Recorded property visits |
| `incomplete_visits` | BIGINT | Visits still open at window end |
| `sessions` | BIGINT | Distinct logical sessions |
| `carded_play_hours` | DOUBLE | Hours of carded play |
| `tracked_coin_in_usd` | DECIMAL(18,2) | Coin-in on carded play, dollars |
| `tracked_payout_usd` | DECIMAL(18,2) | Payout on carded play, dollars |
| `tracked_net_usd` | DECIMAL(18,2) | Player view: payout - coin-in |
| `theo_usd` | DECIMAL(18,4) | Theoretical win: wager x (1 - configured RTP), dollars |
| `luck_residual_usd` | DECIMAL(18,4) | tracked net + theo |
| `linked_pos_cash_usd` | DECIMAL(18,2) | POS cash linked to the player card, dollars |
| `linked_pos_cogs_usd` | DECIMAL(18,2) | Includes comp costs |
| `comps_redeemed` | BIGINT | Comps redeemed |
| `comp_face_value_usd` | DECIMAL(18,2) | Menu value of comped items, dollars (not cash revenue) |
| `comp_cost_usd` | DECIMAL(18,2) | Already inside linked_pos_cogs_usd; do not subtract twice |
| `points_earned` | BIGINT | Loyalty points awarded |
| `points_redeemed` | BIGINT | Loyalty points spent |
| `tracked_contribution_usd` | DECIMAL(18,2) | coin-in - payout + POS cash - POS cogs |

### prepared_daily_view

Starter table: one row per machine-day with history, costs and context already joined, in dollars.

Rows: 56,110 · Key: `machine_id, gaming_date`

| Column | Type | Meaning |
| --- | --- | --- |
| `machine_id` | VARCHAR | Machine key |
| `gaming_date` | DATE | Gaming day: 06:00 local to 06:00 next day |
| `month` | VARCHAR | Calendar or gaming month, YYYY-MM |
| `local_weekday` | VARCHAR | Weekday of the gaming date |
| `is_weekend` | BOOLEAN | Saturday or Sunday |
| `federal_holiday` | VARCHAR | US federal holiday name, if any |
| `events_active` | VARCHAR | Event names active that gaming date |
| `zone_id` | VARCHAR | Zone key (floor_locations) |
| `zone_name` | VARCHAR | Readable zone name |
| `bank_id` | VARCHAR | Bank key |
| `location_id` | VARCHAR | Slot position key (floor_locations) |
| `config_id` | VARCHAR | Game configuration key (game_math) |
| `theme` | VARCHAR | Fictional game title |
| `configured_rtp` | DECIMAL(10,8) | Configured return to player (long-run) |
| `volatility_class` | VARCHAR | Payout dispersion class: low / medium / high / very_high |
| `manufacturer` | VARCHAR | Fictional manufacturer |
| `lease_class` | VARCHAR | owned / leased_fixed / leased_revenue_share |
| `active` | BOOLEAN | Installed and on the floor that day |
| `meter_status` | VARCHAR | reported / not_installed / retired |
| `available_hours` | DOUBLE | Hours available (not down) |
| `occupied_hours` | DOUBLE | Hours with a player seated |
| `availability_ratio` | DOUBLE | available / scheduled |
| `occupancy_ratio` | DOUBLE | occupied / available |
| `paid_spins` | BIGINT | Number of paid spins |
| `coin_in_usd` | DECIMAL(18,2) | Total wagered, dollars, including replayed winnings |
| `payout_usd` | DECIMAL(18,2) | Amount paid back to players, dollars |
| `house_win_usd` | DECIMAL(18,2) | Coin-in minus payout, dollars (can be negative) |
| `theo_usd` | DECIMAL(18,4) | Theoretical win: wager x (1 - configured RTP), dollars |
| `observed_hold` | DOUBLE | house win / coin-in; null without play |
| `theo_hold` | DOUBLE | theo / coin-in |
| `luck_residual_usd` | DECIMAL(18,4) | house win - theo |
| `carded_coin_in_usd` | DECIMAL(18,2) | Coin-in on carded play, dollars |
| `carded_share` | DOUBLE | carded / all coin-in |
| `faults_opened` | BIGINT | fault_repair tickets opened that day |
| `zone_entries_observed` | BIGINT | Counter entries for the zone that day (observed) |
| `zone_counter_coverage_hours` | DOUBLE | Counter coverage that day |
| `lease_cost_usd` | DECIMAL(18,2) | Lease cost from cost_rules, dollars |
| `service_cost_usd` | DECIMAL(18,2) | Manufacturer service contract cost, dollars |
| `power_cost_usd` | DECIMAL(18,2) | Utilities cost, dollars |
| `repair_cost_usd` | DECIMAL(18,2) | Direct repair cost, dollars |
| `contribution_after_supplied_costs_usd` | DECIMAL(18,2) | house win minus the supplied machine costs above |
| `lag_coin_in_7d_mean_usd` | DOUBLE | Mean of the previous 7 gaming days (model-safe) |
| `lag_downtime_7d_hours` | DOUBLE | Downtime over the previous 7 gaming days (model-safe) |
| `lag_house_win_28d_usd` | DOUBLE | House win over the previous 28 gaming days (model-safe) |

### property_day

Starter table: one row per gaming day for the whole property.

Rows: 181 · Key: `gaming_date`

| Column | Type | Meaning |
| --- | --- | --- |
| `gaming_date` | DATE | Gaming day: 06:00 local to 06:00 next day |
| `local_weekday` | VARCHAR | Weekday of the gaming date |
| `events_active` | VARCHAR | Events from the events table active that day |
| `active_machines` | BIGINT | Machines installed that day |
| `coin_in_usd` | DECIMAL(18,2) | Total wagered, dollars, including replayed winnings |
| `payout_usd` | DECIMAL(18,2) | Amount paid back to players, dollars |
| `house_win_usd` | DECIMAL(18,2) | Coin-in minus payout, dollars (can be negative) |
| `theo_usd` | DECIMAL(18,4) | Theoretical win: wager x (1 - configured RTP), dollars |
| `observed_hold` | DOUBLE | House win / coin-in (null when no coin-in) |
| `available_machine_hours` | DOUBLE | Machine-hours available (not down/closed) |
| `occupied_machine_hours` | DOUBLE | Machine-hours with a player seated |
| `carded_coin_in_share` | DOUBLE | Carded coin-in / all coin-in |
| `pos_cash_usd` | DECIMAL(18,2) | POS cash received, dollars |
| `pos_cogs_usd` | DECIMAL(18,2) | POS cost of goods incl. comped items, dollars |
| `comp_face_value_usd` | DECIMAL(18,2) | Menu value of comped items, dollars (not cash revenue) |
| `comp_cost_usd` | DECIMAL(18,2) | Inside pos_cogs_usd |
| `faults_opened` | BIGINT | Fault tickets opened |
| `incidents_reported` | BIGINT | Security incidents reported that day |
| `entrance_zone_entries_observed` | BIGINT | Entries in zones with doors |
| `total_zone_entries_observed` | BIGINT | Sum of all zone counter entries (crossings, not unique people) |
| `counter_coverage_share` | DOUBLE | Share of sensor-minutes with a working counter |
| `machine_supplied_costs_usd` | DECIMAL(18,2) | Lease, service, power and repair |
| `tech_labor_cost_usd` | DECIMAL(18,2) | Scheduled slot-technician labour cost, dollars |
| `contribution_after_supplied_costs_usd` | DECIMAL(18,2) | house win + POS cash - POS cogs - supplied costs |

## `data/2_machine_decision/`

Floor, machines, game math, daily meters, operations, supplied costs and the action price list.

### action_catalog

What the $100,000 / 30-day budget can buy. No uplift is promised.

Rows: 13 · Key: `action_type_id`

| Column | Type | Meaning |
| --- | --- | --- |
| `action_type_id` | VARCHAR | Action |
| `name` | VARCHAR | Description |
| `unit` | VARCHAR | Unit of quantity |
| `unit_cost_cents` | BIGINT | One-time cost per unit |
| `recurring_cost_cents_per_day` | BIGINT | Per unit per day |
| `lead_days` | INTEGER | Days before it takes effect |
| `downtime_minutes` | INTEGER | Machine downtime per unit |
| `quantity_limit` | INTEGER | Max units |
| `incompatibility_group` | VARCHAR | Actions in one group conflict on the same target |
| `notes` | VARCHAR | Constraints |

### calendar_day

One row per gaming day.

Rows: 181 · Key: `gaming_date`

| Column | Type | Meaning |
| --- | --- | --- |
| `gaming_date` | DATE | Gaming day: 06:00 local to 06:00 next day |
| `gaming_day_start_utc` | TIMESTAMP | Start instant, UTC |
| `gaming_day_end_utc` | TIMESTAMP | End instant, UTC (exclusive) |
| `scheduled_seconds` | BIGINT | Elapsed seconds; 82800 on the spring DST gaming day |
| `local_weekday` | VARCHAR | Weekday of the gaming date |
| `utc_offset_start` | VARCHAR | UTC offset at start |
| `utc_offset_end` | VARCHAR | UTC offset at end |
| `month` | VARCHAR | YYYY-MM |
| `is_weekend` | BOOLEAN | Saturday or Sunday |
| `federal_holiday` | VARCHAR | US federal holiday name, if any |

### cost_rules

Supplied costs. Subtract each once.

Rows: 9 · Key: `cost_rule_id`

| Column | Type | Meaning |
| --- | --- | --- |
| `cost_rule_id` | VARCHAR | Rule |
| `entity_type` | VARCHAR | What it applies to |
| `entity_id` | VARCHAR | Which one; blank = all |
| `cost_category` | VARCHAR | lease | service_contract | utilities | labor | repair | cost_of_goods |
| `calculation_basis` | VARCHAR | How to apply the rate |
| `unit` | VARCHAR | cents | fraction | multiplier |
| `payer` | VARCHAR | property |
| `rate` | VARCHAR | Rate in the stated unit |
| `effective_from` | DATE | Start |
| `effective_to` | DATE | End; null = open |

### floor_locations

Floor hierarchy and coordinates. Walkways are in floor_walkways.

Rows: 378 · Key: `location_id`

| Column | Type | Meaning |
| --- | --- | --- |
| `location_id` | VARCHAR | Zone, bank, slot, outlet or entrance key |
| `parent_location_id` | VARCHAR | Parent node |
| `node_type` | VARCHAR | zone | bank | slot | outlet | entrance |
| `zone_id` | VARCHAR | Zone |
| `bank_id` | VARCHAR | Bank |
| `outlet_id` | VARCHAR | Outlet |
| `name` | VARCHAR | Display name |
| `x_m` | DOUBLE | Floor x, metres |
| `y_m` | DOUBLE | Floor y, metres |
| `capacity` | INTEGER | Machine positions or seats |

### floor_walkways

Walkable edges between zone hubs, with the effective-dated renovation closure.

Rows: 10 · Key: `walkway_id`

| Column | Type | Meaning |
| --- | --- | --- |
| `walkway_id` | VARCHAR | Walkway key |
| `zone_a` | VARCHAR | Zone at one end (floor_locations.zone_id) |
| `zone_b` | VARCHAR | Zone at the other end |
| `length_m` | DOUBLE | Walking length in metres |
| `closed_from_utc` | TIMESTAMP | Start of closure (inclusive), UTC; null if never closed |
| `closed_to_utc` | TIMESTAMP | End of closure (exclusive), UTC |
| `closure_reason` | VARCHAR | Why the walkway was closed |

### game_math



Rows: 10 · Key: `config_id`

| Column | Type | Meaning |
| --- | --- | --- |
| `config_id` | VARCHAR | Published game configuration |
| `theme` | VARCHAR | Game title |
| `configured_rtp` | DECIMAL(10,8) | Long-run expected return per unit wagered |
| `payout_multiplier_variance` | DECIMAL(18,8) | Variance of payout/bet per spin |
| `hit_probability` | DECIMAL(10,6) | Probability a spin pays more than zero (may be less than the bet) |
| `max_multiplier` | DECIMAL(12,2) | Largest fixed award as a multiple of the bet |
| `min_bet_cents` | BIGINT | Smallest bet |
| `max_bet_cents` | BIGINT | Largest bet |
| `bet_options_cents` | VARCHAR | Allowed fixed bets, pipe separated |
| `payout_increment_cents` | INTEGER | All payouts are multiples of this |
| `volatility_class` | VARCHAR | Qualitative |

### machine_day

Every machine x every gaming day, including zero-play and not-yet-installed days.

Rows: 56,110 · Key: `machine_id, gaming_date`

| Column | Type | Meaning |
| --- | --- | --- |
| `machine_id` | VARCHAR | Machine |
| `gaming_date` | DATE | Gaming day |
| `location_id` | VARCHAR | Placement at day start |
| `config_id` | VARCHAR | Configuration |
| `active` | BOOLEAN | On the floor for any part of the day |
| `meter_status` | VARCHAR | reported | not_installed | retired |
| `scheduled_seconds` | BIGINT | Seconds on the floor during the day |
| `available_seconds` | BIGINT | Scheduled minus outage, repair, move and install downtime |
| `occupied_seconds` | BIGINT | Seconds inside play segments |
| `paid_spins` | BIGINT | All play |
| `payout_positive_spins` | BIGINT | Spins with payout > 0 |
| `coin_in_cents` | BIGINT | All wagers incl. replayed winnings |
| `payout_cents` | BIGINT | All game payouts |
| `house_win_cents` | BIGINT | coin_in - payout; may be negative |
| `theo_cents` | DECIMAL(24,8) | Sum of bet x (1 - configured_rtp) |
| `sum_bet_squared` | DOUBLE | Sum of bet^2 (cents^2) |
| `carded_coin_in_cents` | BIGINT | Subset recorded to a loyalty card |
| `carded_payout_cents` | BIGINT | Carded subset |
| `carded_spins` | BIGINT | Carded subset |
| `carded_theo_cents` | DECIMAL(24,8) | Carded subset |

### machines



Rows: 310 · Key: `machine_id`

| Column | Type | Meaning |
| --- | --- | --- |
| `machine_id` | VARCHAR | Machine key; carries no location or performance meaning |
| `manufacturer` | VARCHAR | Fictional |
| `theme` | VARCHAR | Game title |
| `install_date` | DATE | Install date |
| `retire_date` | DATE | Removal date, if any |
| `lease_class` | VARCHAR | owned | leased_fixed | leased_revenue_share |

### operations



Rows: 1,226 · Key: `operation_id`

| Column | Type | Meaning |
| --- | --- | --- |
| `operation_id` | VARCHAR | Ticket |
| `machine_id` | VARCHAR | Machine |
| `location_id` | VARCHAR | Location (destination for a move) |
| `event_type` | VARCHAR | fault_repair | scheduled_maintenance | move | install | retire |
| `opened_at_utc` | TIMESTAMP | Machine became unavailable |
| `opened_at_local` | TIMESTAMP | Same, local clock |
| `recorded_at_utc` | TIMESTAMP | Ticket entered |
| `work_started_at_utc` | TIMESTAMP | Technician started work |
| `available_at_utc` | TIMESTAMP | Available again |
| `direct_cost_cents` | BIGINT | Supplied direct cost |

### placements



Rows: 314 · Key: `placement_id`

| Column | Type | Meaning |
| --- | --- | --- |
| `placement_id` | VARCHAR | Interval key |
| `machine_id` | VARCHAR | Machine |
| `location_id` | VARCHAR | Slot |
| `config_id` | VARCHAR | Configuration |
| `effective_from_utc` | TIMESTAMP | Start (inclusive), a gaming-day boundary |
| `effective_to_utc` | TIMESTAMP | End (exclusive); null = still placed |

## `data/3_guests/`

Player activity is loyalty-card (tracked) only. `fnb_transactions` includes all POS sales, with null player IDs for uncarded sales. Uncarded gaming appears only in machine meters.

### fnb_transactions

All POS tickets, carded or not.

Rows: 227,833 · Key: `transaction_id`

| Column | Type | Meaning |
| --- | --- | --- |
| `transaction_id` | VARCHAR | POS ticket |
| `outlet_id` | VARCHAR | Outlet |
| `event_at_utc` | TIMESTAMP | Sale |
| `event_at_local` | TIMESTAMP | Sale, local clock |
| `local_hour` | INTEGER | Local clock hour (America/Los_Angeles) of the start time |
| `utc_offset` | VARCHAR | Local UTC offset at that instant, e.g. -08:00 or -07:00 |
| `recorded_at_utc` | TIMESTAMP | Ticket close |
| `player_id` | VARCHAR | Card presented |
| `observed_visit_id` | VARCHAR | Recorded visit, if carded |
| `item` | VARCHAR | Item |
| `face_value_cents` | BIGINT | Menu price |
| `cash_receipt_cents` | BIGINT | Cash; 0 for comps |
| `cogs_cents` | BIGINT | Cost of goods |
| `comp_id` | VARCHAR | Redemption that paid for it |

### loyalty_ledger



Rows: 782,773 · Key: `loyalty_event_id`

| Column | Type | Meaning |
| --- | --- | --- |
| `loyalty_event_id` | VARCHAR | Event |
| `player_id` | VARCHAR | Card |
| `event_at_utc` | TIMESTAMP | When |
| `available_at_utc` | TIMESTAMP | When the system knew |
| `event_type` | VARCHAR | award | redeem |
| `benefit_id` | VARCHAR | Redeemed benefit |
| `points_delta` | BIGINT | Points change (balance starts at 0 each year) |
| `tier_before` | VARCHAR | Tier before |
| `tier_after` | VARCHAR | Tier after (tiers use lifetime points) |
| `face_value_cents` | BIGINT | Menu price (not revenue) |
| `economic_cost_cents` | BIGINT | Cost to the house; equals the linked POS cogs, count once |
| `redeemed_pos_id` | VARCHAR | Linked fnb transaction |
| `source_segment_id` | VARCHAR | Segment that earned an award |

### players



Rows: 113,890 · Key: `player_id`

| Column | Type | Meaning |
| --- | --- | --- |
| `player_id` | VARCHAR | Random loyalty identity |
| `enrolled_at_utc` | TIMESTAMP | Enrollment |
| `home_region` | VARCHAR | Coarse region |
| `age_band` | VARCHAR | Coarse band; missing for some |
| `opening_lifetime_points` | BIGINT | Lifetime points on 2025-01-01 (0 if new) |
| `opening_tier` | VARCHAR | Tier on 2025-01-01 |
| `observed_through_utc` | TIMESTAMP | End of recording window |

### sessions

Carded play only.

Rows: 776,297 · Key: `session_segment_id`

| Column | Type | Meaning |
| --- | --- | --- |
| `session_segment_id` | VARCHAR | Carded play segment |
| `logical_session_id` | VARCHAR | Physical session; split at 06:00 |
| `machine_id` | VARCHAR | Machine |
| `config_id` | VARCHAR | Configuration |
| `location_id` | VARCHAR | Location |
| `gaming_date` | DATE | Gaming day |
| `start_utc` | TIMESTAMP | First spin start |
| `end_utc` | TIMESTAMP | Last spin end |
| `start_local` | TIMESTAMP | First spin start, local clock |
| `local_hour` | INTEGER | Local clock hour (America/Los_Angeles) of the start time |
| `utc_offset` | VARCHAR | Local UTC offset at that instant, e.g. -08:00 or -07:00 |
| `fixed_bet_cents` | BIGINT | Bet on every spin |
| `paid_spins` | BIGINT | Spins |
| `payout_positive_spins` | BIGINT | Spins with payout > 0 |
| `coin_in_cents` | BIGINT | Wagers |
| `payout_cents` | BIGINT | Game payouts |
| `theo_cents` | DECIMAL(24,8) | Expected house win |
| `sum_bet_squared` | DOUBLE | Sum of bet^2 |
| `player_id` | VARCHAR | Card used |
| `observed_visit_id` | VARCHAR | Recorded visit |

### trips



Rows: 351,729 · Key: `observed_visit_id`

| Column | Type | Meaning |
| --- | --- | --- |
| `observed_visit_id` | VARCHAR | Recorded property visit (not a whole Las Vegas trip) |
| `player_id` | VARCHAR | Card |
| `first_observed_at_utc` | TIMESTAMP | First carded activity |
| `first_observed_local` | TIMESTAMP | Same, local clock |
| `last_observed_at_utc` | TIMESTAMP | Last carded activity (not a confirmed departure) |
| `grouping_method` | VARCHAR | recorded_visit_key |
| `observation_complete` | BOOLEAN | False if still open at window end |
| `observed_through_utc` | TIMESTAMP | End of recording window |

## `data/4_context/`

Synthetic counters and the event calendar. `real_sources/` holds unmodified real public data (separate files, never mixed with synthetic rows).

### events

Calendar events; real dates verified, property promotions fictional.

Rows: 8 · Key: `event_id`

| Column | Type | Meaning |
| --- | --- | --- |
| `event_id` | VARCHAR | Event |
| `name` | VARCHAR | Name |
| `event_type` | VARCHAR | convention | sports_viewing | festival | property_promotion |
| `start_date` | DATE | First local date |
| `end_date` | DATE | Last local date |
| `announced_date` | DATE | When it was known |
| `source_type` | VARCHAR | organizer_listing | public_calendar | fictional_property |
| `source_url` | VARCHAR | Where dates were checked |
| `local_scope` | VARCHAR | citywide | property |

### zone_traffic_hourly

Noisy door/zone counters. Seated players do not cross sensors.

Rows: 30,401 · Key: `sensor_id, hour_start_utc`

| Column | Type | Meaning |
| --- | --- | --- |
| `sensor_id` | VARCHAR | Counter |
| `zone_id` | VARCHAR | Zone |
| `hour_start_utc` | TIMESTAMP | Hour start |
| `hour_start_local` | TIMESTAMP | Hour start, local clock |
| `local_hour` | INTEGER | Local clock hour (America/Los_Angeles) of the start time |
| `utc_offset` | VARCHAR | Local UTC offset at that instant, e.g. -08:00 or -07:00 |
| `entries_count` | BIGINT | Zone entries counted; null when offline. Not unique visitors |
| `counter_status` | VARCHAR | ok | partial | offline |
| `coverage_minutes` | INTEGER | Minutes the counter was working |
| `recorded_at_utc` | TIMESTAMP | Feed arrival |

## `data/4_context/real_sources/`

Synthetic counters and the event calendar. `real_sources/` holds unmodified real public data (separate files, never mixed with synthetic rows).

### benchmark_property_monthly

**Real data, unmodified.** Missouri published property slot totals (do not add to benchmark_public).

Rows: 78

| Column | Type | Meaning |
| --- | --- | --- |
| `month` | VARCHAR | Calendar or gaming month, YYYY-MM |
| `source_id` | VARCHAR | Original file name in the provenance register |
| `source_sheet` | VARCHAR | Original workbook sheet |
| `source_url` | VARCHAR | Where the original file was downloaded |
| `retrieved_date` | DATE | Date the source file was downloaded |
| `source_sha256` | VARCHAR | SHA-256 of the original downloaded file |
| `property_id` | VARCHAR | Stable casino key |
| `property_name_as_reported` | VARCHAR | Casino name exactly as in the source |
| `slot_units` | BIGINT | Reported number of slot machines |
| `handle_usd` | DECIMAL(24,2) | Reported slot handle (amount wagered), dollars |
| `agr_usd` | DECIMAL(24,2) | Reported adjusted gross receipts (house win), dollars |
| `actual_payout_ratio` | DECIMAL(18,10) | Reported actual payout share of handle |
| `derived_hold_ratio` | DECIMAL(18,10) | AGR / handle, computed from reported totals; null when handle missing |
| `source_cells` | VARCHAR | Sheet/cell references of the original values |

### benchmark_public

**Real data, unmodified.** Missouri Gaming Commission slot detail, property x category x month, Jan-Jun 2025, all 13 casinos.

Rows: 700

| Column | Type | Meaning |
| --- | --- | --- |
| `month` | VARCHAR | Calendar or gaming month, YYYY-MM |
| `source_id` | VARCHAR | Original file name in the provenance register |
| `source_sheet` | VARCHAR | Original workbook sheet |
| `source_url` | VARCHAR | Where the original file was downloaded |
| `retrieved_date` | DATE | Date the source file was downloaded |
| `source_sha256` | VARCHAR | SHA-256 of the original downloaded file |
| `property_id` | VARCHAR | Stable casino key |
| `property_name_as_reported` | VARCHAR | Casino name exactly as in the source |
| `category` | VARCHAR | Reported slot category (denomination group) |
| `category_kind` | VARCHAR | category or adjustment row |
| `slot_units` | BIGINT | Reported number of slot machines |
| `handle_usd` | DECIMAL(24,2) | Reported slot handle (amount wagered), dollars |
| `agr_usd` | DECIMAL(24,2) | Reported adjusted gross receipts (house win), dollars |
| `actual_payout_ratio` | DECIMAL(18,10) | Reported actual payout share of handle |
| `derived_hold_ratio` | DECIMAL(18,10) | AGR / handle, computed from reported totals; null when handle missing |
| `source_cells` | VARCHAR | Sheet/cell references of the original values |

### benchmark_state_monthly

**Real data, unmodified.** Missouri published statewide slot totals.

Rows: 6

| Column | Type | Meaning |
| --- | --- | --- |
| `month` | VARCHAR | Calendar or gaming month, YYYY-MM |
| `source_id` | VARCHAR | Original file name in the provenance register |
| `source_sheet` | VARCHAR | Original workbook sheet |
| `source_url` | VARCHAR | Where the original file was downloaded |
| `retrieved_date` | DATE | Date the source file was downloaded |
| `source_sha256` | VARCHAR | SHA-256 of the original downloaded file |
| `slot_units` | BIGINT | Reported number of slot machines |
| `handle_usd` | DECIMAL(24,2) | Reported slot handle (amount wagered), dollars |
| `agr_usd` | DECIMAL(24,2) | Reported adjusted gross receipts (house win), dollars |
| `source_cells` | VARCHAR | Sheet/cell references of the original values |

### city_visitation_monthly

**Real data, unmodified.** LVCVA 2025 tourism indicators (Aug 20, 2026 revision): visitors, convention attendance, hotel occupancy, airport passengers.

Rows: 6

| Column | Type | Meaning |
| --- | --- | --- |
| `month` | VARCHAR | Calendar or gaming month, YYYY-MM |
| `geography` | VARCHAR | Area the figure covers |
| `days_in_month` | INTEGER | Calendar days in month |
| `visitor_volume` | BIGINT | Las Vegas visitors in the month |
| `mean_visitors_per_calendar_day` | DECIMAL(18,6) | visitor_volume / days in month |
| `visitor_yoy_ratio` | DECIMAL(18,10) | Reported change vs same month of prior year |
| `convention_attendance` | BIGINT | Las Vegas convention attendance in the month |
| `hotel_occupancy_ratio` | DECIMAL(18,10) | Las Vegas hotel occupancy |
| `airport_en_deplaned_passengers` | BIGINT | Harry Reid airport passenger movements (not unique visitors) |
| `source_revision` | VARCHAR | Publisher revision date |
| `source_url` | VARCHAR | Where the original file was downloaded |
| `source_id` | VARCHAR | Original file name in the provenance register |
| `source_sha256` | VARCHAR | SHA-256 of the original downloaded file |
| `source_cells` | VARCHAR | Sheet/cell references of the original values |
| `as_of_limitation` | VARCHAR | Why the value may not have been known at the time |

### visitor_profile_segments

**Real data, unmodified.** LVCVA 2025 Visitor Profile matrix, metric x segment column. Segments overlap.

Rows: 1,406

| Column | Type | Meaning |
| --- | --- | --- |
| `source_year` | INTEGER | Survey year |
| `metric_id` | VARCHAR | Stable metric key |
| `section` | VARCHAR | Report section |
| `metric_label` | VARCHAR | Metric wording as published |
| `segment_group` | VARCHAR | Segment family (segments overlap across groups) |
| `segment` | VARCHAR | Segment column label |
| `value` | VARCHAR | Reported value as published (string keeps source precision) |
| `unit` | VARCHAR | Unit of value |
| `denominator_note` | VARCHAR | Population the value is conditioned on |
| `value_status` | VARCHAR | Whether the value is reported, not applicable, etc. |
| `source_cell` | VARCHAR | Sheet/cell reference of the original value |
| `source_id` | VARCHAR | Original file name in the provenance register |
| `source_sha256` | VARCHAR | SHA-256 of the original downloaded file |
| `source_url` | VARCHAR | Where the original file was downloaded |
| `publication_date` | DATE | Date the source was published |
| `limitation` | VARCHAR | Known caveat for this value |

### visitor_profile_summary

**Real data, unmodified.** LVCVA 2025 Visitor Profile, overall metrics with conditioning population and source cell.

Rows: 74

| Column | Type | Meaning |
| --- | --- | --- |
| `source_year` | INTEGER | Survey year |
| `metric_id` | VARCHAR | Stable metric key |
| `section` | VARCHAR | Report section |
| `metric_label` | VARCHAR | Metric wording as published |
| `segment_group` | VARCHAR | Segment family (segments overlap across groups) |
| `segment` | VARCHAR | Segment column label |
| `value` | VARCHAR | Reported value as published (string keeps source precision) |
| `unit` | VARCHAR | Unit of value |
| `denominator_note` | VARCHAR | Population the value is conditioned on |
| `value_status` | VARCHAR | Whether the value is reported, not applicable, etc. |
| `source_cell` | VARCHAR | Sheet/cell reference of the original value |
| `source_id` | VARCHAR | Original file name in the provenance register |
| `source_sha256` | VARCHAR | SHA-256 of the original downloaded file |
| `source_url` | VARCHAR | Where the original file was downloaded |
| `publication_date` | DATE | Date the source was published |
| `limitation` | VARCHAR | Known caveat for this value |

### weather_daily

**Real data, unmodified.** NOAA GHCN-Daily, station USW00023169 (Las Vegas airport), daily TMAX/TMIN/PRCP with source flags. Calendar dates, not gaming dates.

Rows: 181

| Column | Type | Meaning |
| --- | --- | --- |
| `station_id` | VARCHAR | NOAA station |
| `source_date` | DATE | Calendar date of the observation |
| `tmax_c` | DECIMAL(8,1) | Daily maximum temperature, deg C |
| `tmax_mflag` | VARCHAR | NOAA measurement flag |
| `tmax_qflag` | VARCHAR | NOAA quality flag |
| `tmax_sflag` | VARCHAR | NOAA source flag |
| `tmax_observation_time` | VARCHAR | NOAA observation time |
| `tmin_c` | DECIMAL(8,1) | Daily minimum temperature, deg C |
| `tmin_mflag` | VARCHAR | NOAA measurement flag |
| `tmin_qflag` | VARCHAR | NOAA quality flag |
| `tmin_sflag` | VARCHAR | NOAA source flag |
| `tmin_observation_time` | VARCHAR | NOAA observation time |
| `prcp_mm` | DECIMAL(8,1) | Daily precipitation, mm |
| `prcp_mflag` | VARCHAR | NOAA measurement flag (T = trace) |
| `prcp_qflag` | VARCHAR | NOAA quality flag |
| `prcp_sflag` | VARCHAR | NOAA source flag |
| `prcp_observation_time` | VARCHAR | NOAA observation time |
| `observation_period` | VARCHAR | NOAA observation period |
| `source_revision` | VARCHAR | Publisher revision date |
| `source_id` | VARCHAR | Original file name in the provenance register |
| `source_url` | VARCHAR | Where the original file was downloaded |
| `source_sha256` | VARCHAR | SHA-256 of the original downloaded file |
| `as_of_limitation` | VARCHAR | Why the value may not have been known at the time |

## `data/5_optional/`

Extra detail for optional routes (hourly meters, incidents, staffing, a fictional survey).

### machine_hour

Every machine x every hour while installed. Sums to machine_day.

Rows: 1,321,908 · Key: `machine_id, hour_start_utc`

| Column | Type | Meaning |
| --- | --- | --- |
| `machine_id` | VARCHAR | Machine |
| `hour_start_utc` | TIMESTAMP | Hour start |
| `hour_start_local` | TIMESTAMP | Local clock |
| `local_hour` | INTEGER | Local clock hour (America/Los_Angeles) of the start time |
| `utc_offset` | VARCHAR | Local UTC offset at that instant, e.g. -08:00 or -07:00 |
| `gaming_date` | DATE | Gaming day |
| `location_id` | VARCHAR | Location |
| `active` | BOOLEAN | On the floor in this hour |
| `available_seconds` | BIGINT | Available seconds in the hour |
| `occupied_seconds` | BIGINT | Seconds inside play segments |
| `paid_spins` | BIGINT | Spins started in the hour |
| `payout_positive_spins` | BIGINT | Spins with payout > 0 |
| `coin_in_cents` | BIGINT | Wagers |
| `payout_cents` | BIGINT | Payouts |
| `carded_coin_in_cents` | BIGINT | Carded subset |
| `carded_payout_cents` | BIGINT | Carded subset |
| `carded_spins` | BIGINT | Carded subset |

### security_incidents

Reported incidents only. Unreported events are not here. Reports are leads, not verdicts.

Rows: 3,865 · Key: `incident_id`

| Column | Type | Meaning |
| --- | --- | --- |
| `incident_id` | VARCHAR | Report |
| `zone_id` | VARCHAR | Zone |
| `machine_id` | VARCHAR | Machine, if one was involved |
| `occurred_at_utc` | TIMESTAMP | Estimated occurrence |
| `occurred_at_local` | TIMESTAMP | Local clock |
| `local_hour` | INTEGER | Local clock hour (America/Los_Angeles) of the start time |
| `utc_offset` | VARCHAR | Local UTC offset at that instant, e.g. -08:00 or -07:00 |
| `reported_at_utc` | TIMESTAMP | Report time |
| `report_source` | VARCHAR | surveillance | floor_staff | slot_tech | patron |
| `category` | VARCHAR | Reported category; not a finding of wrongdoing |
| `severity` | INTEGER | 1 low .. 3 high |

### shift_roster

Role-level staffing. Slot techs drive repair capacity.

Rows: 10,317 · Key: `assignment_id`

| Column | Type | Meaning |
| --- | --- | --- |
| `assignment_id` | VARCHAR | Assignment |
| `gaming_date` | DATE | Gaming day |
| `shift` | VARCHAR | day | swing | grave |
| `role` | VARCHAR | slot_tech | floor_attendant | beverage_server | security_officer |
| `zone_id` | VARCHAR | Zone; null = floor-wide |
| `start_utc` | TIMESTAMP | Shift start |
| `end_utc` | TIMESTAMP | Shift end |
| `planned_headcount` | INTEGER | Planned |
| `actual_headcount` | INTEGER | Worked |

### visitor_profile_monthly

Fictional exit-intercept survey of ALL guests, carded or not.

Rows: 42 · Key: `month, survey_metric`

| Column | Type | Meaning |
| --- | --- | --- |
| `month` | VARCHAR | YYYY-MM |
| `survey_metric` | VARCHAR | Metric |
| `estimate` | DOUBLE | Estimate |
| `standard_error` | DOUBLE | Sampling SE |
| `sample_size` | INTEGER | Respondents |
| `unit` | VARCHAR | share | minutes | usd |
| `eligibility` | VARCHAR | Who could be sampled |
| `measurement_method` | VARCHAR | How it was measured |
