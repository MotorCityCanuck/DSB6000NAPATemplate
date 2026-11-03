# Data Lineage

**Purpose:** Maintain traceable evidence for the flow **Raw → Bronze → Silver → Gold → Olympic Recommendations**. Lineage supports reproducibility, governance, validation, and defensible business recommendations by connecting each output to its source data, processing rules, quality evidence, and execution record.

The Bronze and Silver entries below describe the supplied construction specifications. They are not proof that a team's generated code or deployed Databricks resources conform to those specifications.

## Dataset Profiles and Naming

The same parameterized engineering lineage applies independently to all five full-refresh profiles:

- `napa_5k_clean`
- `napa_5k_tainted`
- `napa_50k_clean`
- `napa_50k_tainted`
- `napa_250k_production`

Resolve `<catalog>`, `<raw_schema>`, `<bronze_schema>`, `<silver_schema>`, `<silver_reject_schema>`, and `<team_prefix>_ops` from team configuration. Record fully qualified deployed names during verification; do not substitute illustrative defaults for observed resources.

## Expected Lineage — Based on Supplied Construction Specifications

### Raw to Bronze

`docs/raw_to_bronze_prompt.md` is authoritative for this layer. Each selected profile supplies 13 Parquet files and a colocated `manifest.json`. The manifest is delivery and validation evidence, not a Bronze table.

For every source, Bronze retains all business rows and columns in source order, including duplicates and invalid values, and appends the ten prescribed operational metadata columns. It performs no business cleansing, filtering, joins, sorting, deduplication, or feature engineering. Publication is a selected-profile full refresh.

| Raw source file | Source profile | Bronze destination | Significant ingestion or preservation behavior | Mandatory certification and validation controls |
|---|---|---|---|---|
| `regions.parquet` | Any approved profile | `<catalog>.<bronze_schema>.regions` | Raw-preserving copy with ingestion metadata appended | Manifest inventory, checksum, row count, ordered schema/hash, readability, and Raw/Bronze reconciliation |
| `clubs.parquet` | Any approved profile | `<catalog>.<bronze_schema>.clubs` | Raw-preserving copy with ingestion metadata appended | Same required readiness and reconciliation controls |
| `club_memberships.parquet` | Any approved profile | `<catalog>.<bronze_schema>.club_memberships` | Raw-preserving copy with ingestion metadata appended | Same required readiness and reconciliation controls |
| `player_master.parquet` | Any approved profile | `<catalog>.<bronze_schema>.player_master` | Raw-preserving copy with ingestion metadata appended | Same required readiness and reconciliation controls |
| `player_registrations.parquet` | Any approved profile | `<catalog>.<bronze_schema>.player_registrations` | Raw-preserving copy with ingestion metadata appended | Same required readiness and reconciliation controls |
| `player_assessment_history.parquet` | Any approved profile | `<catalog>.<bronze_schema>.player_assessment_history` | Raw-preserving copy with ingestion metadata appended | Same required readiness and reconciliation controls |
| `teams.parquet` | Any approved profile | `<catalog>.<bronze_schema>.teams` | Raw-preserving copy with ingestion metadata appended | Same required readiness and reconciliation controls |
| `team_memberships.parquet` | Any approved profile | `<catalog>.<bronze_schema>.team_memberships` | Raw-preserving copy with ingestion metadata appended | Same required readiness and reconciliation controls |
| `matches.parquet` | Any approved profile | `<catalog>.<bronze_schema>.matches` | Raw-preserving copy with ingestion metadata appended | Same required readiness and reconciliation controls |
| `match_teams.parquet` | Any approved profile | `<catalog>.<bronze_schema>.match_teams` | Raw-preserving copy with ingestion metadata appended | Same required readiness and reconciliation controls |
| `match_team_players.parquet` | Any approved profile | `<catalog>.<bronze_schema>.match_team_players` | Raw-preserving copy with ingestion metadata appended | Same required readiness and reconciliation controls |
| `match_games.parquet` | Any approved profile | `<catalog>.<bronze_schema>.match_games` | Raw-preserving copy with ingestion metadata appended | Same required readiness and reconciliation controls |
| `monthly_batches.parquet` | Any approved profile | `<catalog>.<bronze_schema>.monthly_batches` | Raw-preserving copy with ingestion metadata appended | Same required readiness and reconciliation controls |

Certification must fail when required inventory, manifest agreement, Parquet readability, checksum, count, ordered schema, or reconciliation requirements fail. Successful finalization requires all 13 expected Bronze tables and matching run evidence. See the prompt for the exact metadata columns, build order, failure behavior, schema reset, audit tables, and acceptance tests.

The shared operations schema also records Raw-to-Bronze lineage in `pipeline_runs`, `table_runs`, `schema_snapshots`, `reconciliation_results`, and `run_messages`. These tables retain run, source/target, schema, reconciliation, and diagnostic evidence; they are not Bronze business tables.

### Bronze to Silver

`docs/bronze_to_silver_prompt.md` is authoritative for this layer. The mapping applies to all five profiles. Each row produces an accepted table in `<silver_schema>` and a corresponding `<target>_exceptions` table in `<silver_reject_schema>`, including declared empty outputs.

Common mandatory controls apply to every mapping: preserve source-row multiplicity through validation; reject every occurrence of a duplicate non-null primary key; use safe conversions; retain diagnostic source values; resolve required parents against accepted Silver records; separate accepted and rejected occurrences; append prescribed metadata; and reconcile `Bronze = accepted + rejected`. Expected record-level defects do not independently fail execution, while missing evidence, technical errors, failed publication, or unexplained reconciliation differences do.

| Bronze source and required dependencies | Silver accepted and exception destinations | Important prescribed lineage | Mandatory quality controls |
|---|---|---|---|
| `monthly_batches` | `monthly_batches`; `monthly_batches_exceptions` | Normalize batch ID/type/status; safely parse dates and sequence; derive year, month, and quarter | Key, date, and sequence validation |
| `regions` | `regions`; `regions_exceptions` | Normalize identifiers and geographic attributes; standardize country to USA/CAN | Key, name, and country validation |
| `player_master` + accepted `regions` | `players`; `players_exceptions` | Normalize player attributes, dates, rating/confidence, country, status, and home region; derive snapshot age/group and active flag | Key, birth date, parent region, domains, and numeric conversion validation |
| `clubs` + accepted `regions` | `clubs`; `clubs_exceptions` | Normalize club identity, region, country, and lifecycle dates; preserve specified club attributes | Key/name, parent region, country, date, and interval validation |
| `teams` | `teams`; `teams_exceptions` | Preserve source team attributes; standardize category, identity, country, status, and lifecycle dates; derive snapshot age and active flag | Key, domain, date, interval, and release-boundary validation |
| `player_registrations` + accepted `players` and populated `monthly_batches` | `player_registrations`; `player_registrations_exceptions` | Normalize registration/batch identifiers and dates; derive status, current flag, duration, and sequence | Key, parent, conversion, and interval validation |
| `player_assessment_history` + accepted `players` and `monthly_batches` | `player_assessment_history`; `player_assessment_history_exceptions` | Normalize assessment identifiers, date/type, value, and confidence while preserving historical context | Key, parent, date boundary, numeric conversion, and required coverage validation |
| `club_memberships` + accepted `players` and `clubs` | `club_memberships`; `club_memberships_exceptions` | Normalize membership intervals; derive duration/current flag; identify overlap warnings | Key, parent, date, interval, and overlap controls |
| `team_memberships` + accepted `teams` and `players` | `team_memberships`; `team_memberships_exceptions` | Normalize membership intervals, role, and position; derive current flag and supported duration; identify overlap warnings | Key, parent, date, interval, position, and overlap controls |
| `matches` + accepted `monthly_batches`/`regions`; Bronze `match_teams` for winner-side mapping | `matches`; `matches_exceptions` | Normalize match attributes/date/category; preserve persistent winner; derive winner side, completion, year, and month | Key, parent, date, winner mapping, contract, and snapshot-boundary validation |
| `match_teams` + accepted `matches` and `teams` | `match_teams`; `match_teams_exceptions` | Normalize side and pre-match rating; inherit match context; derive winner and side-cardinality warning flags | Key, parent, side, rating, and match-structure validation |
| `match_team_players` + accepted `match_teams` and `players`; membership history for warning evidence | `match_team_players`; `match_team_players_exceptions` | Preserve match-time rating; normalize position/rating; inherit match context; derive event-time age/group and membership-history warning | Key, parent, position/rating, participant-cardinality, cross-side, and event-time controls |
| `match_games` + accepted `matches` | `match_games`; `match_games_exceptions` | Safely convert game/score fields; derive score margin, total points, close-game, and supported extended-game fields | Key, parent, game number, scores, winner consistency, optional target/win-by/share, and per-match game uniqueness controls |

The prompt also requires 11 cross-table checks and run-linked evidence for release, key, relationship, match, game, temporal, historical, and eligibility quality. Refer to the prompt for exact rule order, identifiers, severities, source contracts, and temporal behavior rather than reproducing those specifications here.

#### Prescribed Silver convenience views

| View | Expected lineage and purpose |
|---|---|
| `vw_players_current` | Filter accepted `players` to rows with a true current active flag |
| `vw_current_team_memberships` | Filter accepted `team_memberships` to true current membership rows |
| `vw_team_rosters` | Combine teams, current memberships, and players to expose roster cardinality and member structures; it does not recommend teams |
| `vw_match_results` | Combine accepted matches, sides, games, regions, and batches for match-result context |
| `vw_player_match_history` | Combine accepted participants, sides, matches, players, and opponents for historical participation context |

#### Prescribed Silver operational evidence

The shared `<team_prefix>_ops` schema records `b2s_pipeline_runs`, `b2s_table_runs`, `b2s_quality_results`, `b2s_reconciliation_results`, `b2s_schema_snapshots`, and `b2s_run_messages`. These tables provide run, quality, reconciliation, schema, and diagnostic lineage; they are not Gold analytical outputs.

## Verified Lineage — Student Record

Verify expected lineage against the generated implementation and deployed Databricks resources for each profile. Do not mark an entry verified from documentation alone.

| Profile and layer | Expected mapping reference | Implementation status | Actual fully qualified source(s) | Actual fully qualified destination(s) | Run ID or validation evidence | Deviation and disposition | Verified by/date |
|---|---|---|---|---|---|---|---|
|  |  | Not started / implemented / verified |  |  |  |  |  |

Record deviations without silently changing the expected specification. Resolve Bronze or Silver deviations against the applicable construction prompt and retain evidence of any approved decision.

## Gold Lineage — Team-Completed Template

Gold design is entirely team-defined. Add one row per Gold table, feature set, analytical output, figure, or recommendation artifact; do not treat the examples of required fields as a prescribed architecture or method.

| Silver source tables/views | Team-defined Gold destination or analytical output | Derived features and measures | Transformations and business logic | Validation and quality controls | Recommendation connection | Run/evidence reference | Owner/status |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |

For every analytical output, document the dataset profile, source grain, joins, date window, assumptions, exclusions, uncertainty, and relevant quality findings. Final production recommendations should be traceable to `napa_250k_production` Silver evidence.

Use the following coverage register to connect team-defined Gold evidence to required business decisions without prescribing how those decisions are calculated:

| Country | Doubles category | Primary roster evidence | Alternate evidence | Development-camp evidence | Final recommendation artifact |
|---|---|---|---|---|---|
| USA | Men's doubles |  |  |  |  |
| USA | Women's doubles |  |  |  |  |
| USA | Mixed doubles |  |  |  |  |
| Canada | Men's doubles |  |  |  |  |
| Canada | Women's doubles |  |  |  |  |
| Canada | Mixed doubles |  |  |  |  |

## Known Lineage Gaps and Follow-up

| Gap or unresolved deviation | Affected profile/layer/output | Business or validation impact | Owner | Next action | Status |
|---|---|---|---|---|---|
|  |  |  |  |  |  |
